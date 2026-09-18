from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Iterable


APPROVED_MANIFEST_SHA256 = (
    "902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9"
)
APPROVED_SOURCE = "materials_project"
APPROVED_SELECTION_CONTRACT = "materials-project-selection-v3"
APPROVED_ACCEPTED = 1_727
CURATED_MATERIAL_COUNT = 28
EXPECTED_CURATED_CONFLICTS = CURATED_MATERIAL_COUNT
COLLISION_SOURCE_ID = "mp-19017"


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class FormulaCrowdingSummary:
    result_count: int
    unique_identity_count: int
    identity_repetition_count: int
    unique_formula_count: int
    repeated_formula_count: int
    repeated_identity_count: int
    maximum_formula_multiplicity: int
    identity_diversity_fraction: float
    formula_diversity_fraction: float
    formula_multiplicities: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def summarize_formula_crowding(
    rows: Iterable[tuple[str, str]],
) -> FormulaCrowdingSummary:
    """Measure identity and formula diversity without collapsing polymorphs."""
    material_rows = list(rows)
    formulas_by_identity: dict[str, str] = {}
    for identity, formula in material_rows:
        existing_formula = formulas_by_identity.setdefault(identity, formula)
        if existing_formula != formula:
            raise ValueError(
                "one material identity resolved to multiple formulas"
            )
    formula_counts = Counter(formulas_by_identity.values())
    repeated = {
        formula: count
        for formula, count in sorted(formula_counts.items())
        if count > 1
    }
    result_count = len(material_rows)
    return FormulaCrowdingSummary(
        result_count=result_count,
        unique_identity_count=len(formulas_by_identity),
        identity_repetition_count=result_count - len(formulas_by_identity),
        unique_formula_count=len(formula_counts),
        repeated_formula_count=len(repeated),
        repeated_identity_count=sum(repeated.values()),
        maximum_formula_multiplicity=max(formula_counts.values(), default=0),
        identity_diversity_fraction=(
            round(len(formulas_by_identity) / result_count, 6)
            if result_count
            else 0.0
        ),
        formula_diversity_fraction=(
            round(len(formula_counts) / len(formulas_by_identity), 6)
            if formulas_by_identity
            else 0.0
        ),
        formula_multiplicities=repeated,
    )


def extract_identity_formula_pairs(value: Any) -> list[tuple[str, str]]:
    """Find material identities in an API document without changing it."""
    pairs: list[tuple[str, str]] = []

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            identity = item.get("mp_id") or item.get("material_id")
            formula = item.get("formula") or item.get("pretty_formula")
            if isinstance(identity, (str, int)) and isinstance(formula, str):
                pairs.append((str(identity), formula))
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return pairs


def evaluate_manifest_contract(manifest: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    counts = manifest.get("counts", {})
    dataset = manifest.get("dataset", {})
    if manifest.get("manifest_sha256") != APPROVED_MANIFEST_SHA256:
        failures.append("manifest_sha256")
    if manifest.get("source") != APPROVED_SOURCE:
        failures.append("source")
    if (
        dataset.get("selection_contract_version")
        != APPROVED_SELECTION_CONTRACT
    ):
        failures.append("selection_contract_version")
    if counts.get("accepted") != APPROVED_ACCEPTED:
        failures.append("accepted")
    if counts.get("source_complete") is not True:
        failures.append("source_complete")
    if counts.get("duplicate_source_ids") != 0:
        failures.append("duplicate_source_ids")
    return failures


def evaluate_curated_preservation(
    before: dict[str, Any],
    after: dict[str, Any],
) -> list[str]:
    failures: list[str] = []
    if before.get("material_count") != CURATED_MATERIAL_COUNT:
        failures.append("before_material_count")
    if before.get("material_count") != after.get("material_count"):
        failures.append("material_count")
    if before.get("material_ids") != after.get("material_ids"):
        failures.append("material_ids")
    if before.get("records_sha256") != after.get("records_sha256"):
        failures.append("records_sha256")
    return failures


def evaluate_collision_event(event: dict[str, Any] | None) -> list[str]:
    if event is None:
        return ["mp_19017_event"]
    failures: list[str] = []
    if event.get("source_id") != COLLISION_SOURCE_ID:
        failures.append("mp_19017_source_id")
    if event.get("outcome") != "conflicted":
        failures.append("mp_19017_outcome")
    if event.get("material_id") != 5:
        failures.append("mp_19017_material_id")
    if not event.get("reason"):
        failures.append("mp_19017_reason")
    return failures
