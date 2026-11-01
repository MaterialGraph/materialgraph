"""Formula-correspondence report for objective-aware Objective Explore (SRQ-01).

Builds the R7.1 report (spec rev 3.7) from the chains and ranked candidates an
Objective Explore request has already returned. It only reads: it never
changes admission, traversal, ranking, scoring, ordering or truncation.

Compositions come from stored ``raw_data["composition"]`` in one query and
always pass through ``normalise_stored_composition``; a value it rejects is
"not evaluated" (2.1, AC13).
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material import Material
from app.services.material.formula_correspondence import (
    EFA_ALKALI_METALS,
    classify_formula_correspondence,
)
from app.services.material.search_service import TAU, normalise_stored_composition

_MP_ID = re.compile(r"^mp-(\d+)$")

LIMITATIONS = [
    "Formula correspondence compares stored element ratios only. An exact "
    "alkali formula analog shows that two reduced formulas correspond under "
    "one alkali-metal change; it does not establish crystal structure or "
    "framework, oxidation states, synthesizability, stability, electrochemical "
    "behaviour, or that any reaction between the materials is possible.",
    "Materials with distinct Materials Project IDs and the same reduced formula "
    "remain distinct materials.",
    "Only pairs that the existing composition rules already place in the "
    "candidate pool are compared. Exact alkali formula analogs that share fewer "
    "than three elements with a material are not reachable and are not "
    "reported.",
    "Formula groups and per-expansion admission counts are not yet reported.",
]


def mp_id_sort_key(mp_id: str | None, material_id: int) -> tuple:
    """R5: numeric MP ID first; other IDs after, by string, then local ID."""
    match = _MP_ID.match(mp_id or "")
    if match:
        return (0, int(match.group(1)), "", material_id)
    return (1, 0, mp_id or "", material_id)


def load_compositions(
    db: Session,
    material_ids: Iterable[int],
) -> tuple[dict[int, dict[str, float] | None], dict[int, str | None]]:
    """One query for every involved material; unusable compositions map to None."""
    ids = sorted(set(material_ids))
    fractions: dict[int, dict[str, float] | None] = {material_id: None for material_id in ids}
    mp_ids: dict[int, str | None] = {material_id: None for material_id in ids}
    if not ids:
        return fractions, mp_ids
    rows = db.execute(
        select(Material.id, Material.mp_id, Material.raw_data["composition"])
        .where(Material.id.in_(ids))
    ).all()
    for material_id, mp_id, raw in rows:
        mp_ids[material_id] = mp_id
        try:
            fractions[material_id] = normalise_stored_composition(raw)
        except ValueError:
            fractions[material_id] = None
    return fractions, mp_ids


def _correspondence(result) -> dict:
    return dataclasses.asdict(result)


# Reason wording for alkali-changing steps on objective-aware requests. It
# follows the neutral-alkali rule (S-5): it states which alkali metal differs
# and never implies that one element was exchanged for another.
_NOT_EXACT_RELATIONSHIP_TEXT = {
    "ratios_differ": "different alkali metal (element ratios differ)",
    "non_alkali_elements_differ": "different alkali metal (other elements differ)",
    "replacement_alkali_in_source": "different alkali metal (not a single alkali-metal change)",
    "replaced_alkali_in_candidate": "different alkali metal (not a single alkali-metal change)",
    "multiple_alkali_changes": "different alkali metal (not a single alkali-metal change)",
    "formula_unparsed": "different alkali metal (formula correspondence not evaluated)",
}


def correspondence_relationship_text(correspondence: dict) -> str:
    """Relationship wording for a classified alkali-changing step."""
    if correspondence["correspondence_class"] == "exact_alkali_replacement":
        return (
            f"exact formula analog (alkali metal {correspondence['replaced_from']} "
            f"\u2192 {correspondence['replaced_to']}; all other element ratios unchanged)"
        )
    return _NOT_EXACT_RELATIONSHIP_TEXT[correspondence.get("reason") or "formula_unparsed"]


def _one_alkali_change_by_elements(transition: dict) -> bool:
    """Step 2 on the transition's recorded element sets.

    Used only when a stored composition is unusable, to decide whether the
    pair would be compared at all and so must be reported as not evaluated.
    """
    shared = set(transition.get("shared_elements") or [])
    source = EFA_ALKALI_METALS & (shared | set(transition.get("removed_elements") or []))
    target = EFA_ALKALI_METALS & (shared | set(transition.get("introduced_elements") or []))
    return bool(source) and bool(target) and source != target


def classify_chain_transitions(db: Session, chains: list[dict]) -> dict[tuple[int, int], dict]:
    """Per-edge classification of every transition in ``chains``.

    Keyed by (from_material_id, to_material_id). Uses the same rules as the
    report's ``transitions``: unusable compositions yield ``not_evaluated``
    only where the recorded element sets show a one-alkali change, and pairs
    the classifier does not classify are omitted. Read-only.
    """
    involved = {
        material["material_id"]
        for chain in chains
        for material in chain.get("materials", [])
    }
    fractions, _ = load_compositions(db, involved)
    pairs: dict[tuple[int, int], dict] = {}
    for chain in chains:
        for transition in chain.get("transitions", []):
            key = (transition["from_material_id"], transition["to_material_id"])
            if key in pairs:
                continue
            source = fractions.get(key[0])
            candidate = fractions.get(key[1])
            if (source is None or candidate is None) and not _one_alkali_change_by_elements(transition):
                continue
            result = classify_formula_correspondence(source, candidate)
            if result is not None:
                pairs[key] = _correspondence(result)
    return pairs


def build_formula_correspondence_report(
    db: Session,
    *,
    source_material_id: int,
    chains: list[dict],
    ranked_candidates: list[dict],
) -> dict:
    involved = {source_material_id}
    for chain in chains:
        involved.update(material["material_id"] for material in chain.get("materials", []))
    involved.update(candidate["material_id"] for candidate in ranked_candidates)
    fractions, mp_ids = load_compositions(db, involved)
    not_evaluated: set[int] = set()

    transitions = []
    for chain_position, chain in enumerate(chains, start=1):
        for transition_index, transition in enumerate(chain.get("transitions", [])):
            from_id = transition["from_material_id"]
            to_id = transition["to_material_id"]
            source = fractions.get(from_id)
            candidate = fractions.get(to_id)
            if source is None or candidate is None:
                if not _one_alkali_change_by_elements(transition):
                    continue
                not_evaluated.update(
                    material_id for material_id, value in ((from_id, source), (to_id, candidate))
                    if value is None
                )
            result = classify_formula_correspondence(source, candidate)
            if result is None:
                continue
            transitions.append({
                "chain_position": chain_position,
                "transition_index": transition_index,
                "from_material_id": from_id,
                "to_material_id": to_id,
                "correspondence": _correspondence(result),
            })

    source_correspondence = []
    source = fractions.get(source_material_id)
    for candidate_rank, ranked in enumerate(ranked_candidates, start=1):
        material_id = ranked["material_id"]
        candidate = fractions.get(material_id)
        if source is None or candidate is None:
            not_evaluated.update(
                identifier for identifier, value in ((source_material_id, source), (material_id, candidate))
                if value is None
            )
            continue
        result = classify_formula_correspondence(source, candidate)
        if result is not None and result.correspondence_class == "exact_alkali_replacement":
            source_correspondence.append({
                "candidate_rank": candidate_rank,
                "material_id": material_id,
                "correspondence": _correspondence(result),
                "formula_group": [],
            })

    not_evaluated_ids = sorted(
        not_evaluated,
        key=lambda material_id: mp_id_sort_key(mp_ids.get(material_id), material_id),
    )
    return {
        "contract_version": "1",
        "basis": "stored_composition_fractions",
        "tolerance": TAU,
        "transitions": transitions,
        "source_correspondence": source_correspondence,
        "expansions": [],
        "formula_grouping_available": False,
        "admission_reporting_available": False,
        "not_evaluated_material_ids": not_evaluated_ids,
        "not_evaluated_count": len(not_evaluated_ids),
        "limitations": list(LIMITATIONS),
    }
