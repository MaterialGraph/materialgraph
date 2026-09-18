from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.services.material.import_pipeline import MaterialImportPipeline

ENERGY_BANDS = (
    ("stable_flag", None, None),
    ("energy_at_zero", 0.0, 0.0),
    ("energy_above_zero_to_0_025", 0.0, 0.025),
    ("energy_above_0_025_to_0_05", 0.025, 0.05),
)


@dataclass(frozen=True)
class ScientificCohortReview:
    manifest_sha256: str
    source: str
    source_release: str
    selection_contract_version: str
    accepted: int
    source_complete: bool
    duplicate_source_ids: int
    maximum_energy_above_hull: float | None
    requested_system_count: int
    represented_system_count: int
    zero_result_systems: tuple[str, ...]
    sparse_systems: dict[str, int]
    chemical_system_counts: dict[str, int]
    chemical_system_fractions: dict[str, float]
    chemistry_family_counts: dict[str, int]
    chemistry_family_fractions: dict[str, float]
    element_counts: dict[str, int]
    element_fractions: dict[str, float]
    stability_counts: dict[str, int]
    stability_fractions: dict[str, float]
    unique_formulas: int
    singleton_formulas: int
    polymorph_formulas: int
    polymorph_materials: int
    maximum_formula_multiplicity: int
    formula_multiplicity_counts: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _chemistry_family(elements: set[str]) -> str:
    if "P" in elements and "O" in elements:
        return "phosphate"
    if "Si" in elements and "O" in elements:
        return "silicate"
    if "S" in elements and "O" not in elements:
        return "sulfide"
    if "O" in elements:
        return "oxide"
    return "other"


def _fractions(counts: Counter[str], total: int) -> dict[str, float]:
    return {
        name: round(count / total, 6)
        for name, count in sorted(counts.items())
    }


def review_scientific_cohort(
    path: Path,
    *,
    sparse_system_threshold: int = 5,
) -> ScientificCohortReview:
    if sparse_system_threshold < 1:
        raise ValueError("sparse_system_threshold must be positive")

    manifest, digest = MaterialImportPipeline._load_manifest(path)
    candidates = manifest["candidates"]
    total = len(candidates)
    if total == 0:
        raise ValueError("scientific cohort review requires candidates")

    requested_systems = tuple(manifest["scope"]["chemical_systems"])
    system_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    element_counts: Counter[str] = Counter()
    formula_counts: Counter[str] = Counter()
    stability_counts: Counter[str] = Counter()

    for candidate in candidates:
        elements = set(candidate["elements"])
        system_counts["-".join(sorted(elements))] += 1
        family_counts[_chemistry_family(elements)] += 1
        element_counts.update(elements)
        formula_counts[candidate["formula"]] += 1

        energy = candidate["energy_above_hull"]
        if candidate["is_stable"]:
            stability_counts["stable_flag"] += 1
        if energy == 0.0:
            stability_counts["energy_at_zero"] += 1
        elif 0.0 < energy <= 0.025:
            stability_counts["energy_above_zero_to_0_025"] += 1
        elif 0.025 < energy <= 0.05:
            stability_counts["energy_above_0_025_to_0_05"] += 1

    complete_system_counts = Counter(
        {
            system: system_counts["-".join(sorted(system.split("-")))]
            for system in requested_systems
        }
    )
    zero_result_systems = tuple(
        system for system in requested_systems if not complete_system_counts[system]
    )
    sparse_systems = {
        system: count
        for system, count in sorted(complete_system_counts.items())
        if 0 < count < sparse_system_threshold
    }
    multiplicities = Counter(formula_counts.values())
    polymorph_multiplicities = [
        count for count in formula_counts.values() if count > 1
    ]
    dataset = manifest["dataset"]
    counts = manifest["counts"]

    ordered_stability_counts = {
        name: stability_counts[name] for name, _, _ in ENERGY_BANDS
    }
    return ScientificCohortReview(
        manifest_sha256=digest,
        source=manifest["source"],
        source_release=dataset["source_release"],
        selection_contract_version=dataset["selection_contract_version"],
        accepted=counts["accepted"],
        source_complete=counts["source_complete"],
        duplicate_source_ids=counts["duplicate_source_ids"],
        maximum_energy_above_hull=manifest["scope"].get(
            "maximum_energy_above_hull"
        ),
        requested_system_count=len(requested_systems),
        represented_system_count=len(requested_systems)
        - len(zero_result_systems),
        zero_result_systems=zero_result_systems,
        sparse_systems=sparse_systems,
        chemical_system_counts=dict(sorted(complete_system_counts.items())),
        chemical_system_fractions=_fractions(complete_system_counts, total),
        chemistry_family_counts=dict(sorted(family_counts.items())),
        chemistry_family_fractions=_fractions(family_counts, total),
        element_counts=dict(sorted(element_counts.items())),
        element_fractions=_fractions(element_counts, total),
        stability_counts=ordered_stability_counts,
        stability_fractions={
            name: round(count / total, 6)
            for name, count in ordered_stability_counts.items()
        },
        unique_formulas=len(formula_counts),
        singleton_formulas=multiplicities[1],
        polymorph_formulas=len(polymorph_multiplicities),
        polymorph_materials=sum(polymorph_multiplicities),
        maximum_formula_multiplicity=max(formula_counts.values()),
        formula_multiplicity_counts={
            str(multiplicity): count
            for multiplicity, count in sorted(multiplicities.items())
        },
    )


def evaluate_review_integrity(
    review: ScientificCohortReview,
    *,
    expected_manifest_sha256: str,
    expected_source: str,
    expected_selection_contract_version: str,
    expected_accepted: int,
) -> list[str]:
    failures: list[str] = []
    if review.manifest_sha256 != expected_manifest_sha256:
        failures.append("manifest_sha256")
    if review.source != expected_source:
        failures.append("source")
    if (
        review.selection_contract_version
        != expected_selection_contract_version
    ):
        failures.append("selection_contract_version")
    if review.accepted != expected_accepted:
        failures.append("accepted")
    if not review.source_complete:
        failures.append("source_complete")
    if review.duplicate_source_ids:
        failures.append("duplicate_source_ids")
    return failures
