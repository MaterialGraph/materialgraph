from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.services.material.import_pipeline import MaterialImportPipeline


SCIENTIFIC_PROPERTIES = (
    "band_gap",
    "energy_above_hull",
    "formation_energy_per_atom",
    "density",
)


@dataclass(frozen=True)
class PropertyCoverage:
    present: int
    missing: int
    fraction: float


@dataclass(frozen=True)
class ManifestInspection:
    manifest_sha256: str
    source: str
    source_release: str
    retrieved_at: str
    selection_contract_version: str
    normalization_version: str
    license_identifier: str
    accepted: int
    rejected: int
    duplicate_source_ids: int
    pages_fetched: int
    source_records_seen: int
    source_complete: bool
    chemical_systems: tuple[str, ...]
    stable_only: bool
    maximum_energy_above_hull: float | None
    stable: int
    unstable: int
    unique_formulas: int
    polymorph_formulas: int
    polymorph_materials: int
    element_counts: dict[str, int]
    chemical_system_counts: dict[str, int]
    rejection_reason_counts: dict[str, int]
    property_coverage: dict[str, PropertyCoverage]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_material_manifest(path: Path) -> ManifestInspection:
    manifest, digest = MaterialImportPipeline._load_manifest(path)
    candidates = manifest["candidates"]
    accepted = len(candidates)

    element_counts: Counter[str] = Counter()
    chemical_system_counts: Counter[str] = Counter()
    formula_counts: Counter[str] = Counter()
    property_present: Counter[str] = Counter()
    stable = 0

    for candidate in candidates:
        elements = candidate["elements"]
        element_counts.update(elements)
        chemical_system_counts["-".join(sorted(elements))] += 1
        formula_counts[candidate["formula"]] += 1
        stable += int(candidate["is_stable"])
        for name in SCIENTIFIC_PROPERTIES:
            property_present[name] += int(candidate[name] is not None)

    polymorph_counts = [count for count in formula_counts.values() if count > 1]
    coverage = {
        name: PropertyCoverage(
            present=property_present[name],
            missing=accepted - property_present[name],
            fraction=round(property_present[name] / accepted, 6),
        )
        for name in SCIENTIFIC_PROPERTIES
    }
    dataset = manifest["dataset"]
    counts = manifest["counts"]
    scope = manifest["scope"]
    rejection_reason_counts = Counter(
        rejection["reason"] for rejection in manifest["rejections"]
    )
    return ManifestInspection(
        manifest_sha256=digest,
        source=manifest["source"],
        source_release=dataset["source_release"],
        retrieved_at=dataset["retrieved_at"],
        selection_contract_version=dataset["selection_contract_version"],
        normalization_version=dataset["normalization_version"],
        license_identifier=dataset["license_identifier"],
        accepted=counts["accepted"],
        rejected=counts["rejected"],
        duplicate_source_ids=counts["duplicate_source_ids"],
        pages_fetched=counts["pages_fetched"],
        source_records_seen=counts["source_records_seen"],
        source_complete=counts["source_complete"],
        chemical_systems=tuple(scope["chemical_systems"]),
        stable_only=scope["stable_only"],
        maximum_energy_above_hull=scope.get(
            "maximum_energy_above_hull"
        ),
        stable=stable,
        unstable=accepted - stable,
        unique_formulas=len(formula_counts),
        polymorph_formulas=len(polymorph_counts),
        polymorph_materials=sum(polymorph_counts),
        element_counts=dict(sorted(element_counts.items())),
        chemical_system_counts=dict(sorted(chemical_system_counts.items())),
        rejection_reason_counts=dict(sorted(rejection_reason_counts.items())),
        property_coverage=coverage,
    )


def evaluate_manifest_gates(
    inspection: ManifestInspection,
    *,
    minimum_materials: int,
    maximum_materials: int,
    required_elements: tuple[str, ...],
    minimum_property_coverage: float,
    require_source_complete: bool,
) -> list[str]:
    failures: list[str] = []
    if not minimum_materials <= inspection.accepted <= maximum_materials:
        failures.append("accepted_material_count")
    missing_elements = sorted(
        set(required_elements) - set(inspection.element_counts)
    )
    failures.extend(f"required_element:{element}" for element in missing_elements)
    failures.extend(
        f"property_coverage:{name}"
        for name, coverage in inspection.property_coverage.items()
        if coverage.fraction < minimum_property_coverage
    )
    if require_source_complete and not inspection.source_complete:
        failures.append("source_complete")
    return failures
