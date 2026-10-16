"""Objective coverage for Objective Explore responses (contract version 1).

Pure, deterministic computation over an already-assembled Objective Explore
response. It never changes traversal, admission, scoring, ordering or chain
selection. See docs/implementation/OBJECTIVE_COVERAGE_CONTRACT.md.
"""

from collections.abc import Mapping, Sequence

from app.utils.chemical_formula import parse_formula_elements_strict

CONTRACT_VERSION = "1"

AVOID_POLICY_EXPLANATIONS: dict[str, str] = {
    "balanced": (
        "Avoid is a soft preference in Balanced mode. Returned ranked "
        "materials or composition chains may still contain avoided elements."
    ),
    "exploratory": (
        "Avoid is a soft preference in Exploratory mode, with a smaller score "
        "penalty than Balanced. Returned ranked materials or composition "
        "chains may still contain avoided elements."
    ),
    "strict": (
        "Strict mode excludes materials containing avoided elements during "
        "search, using recorded element membership; materials without "
        "membership records are also excluded. It then removes returned chains "
        "in which any material other than the source contains an avoided "
        "element, read from formula symbols. The source material is exempt."
    ),
}

BASE_LIMITATIONS: tuple[str, ...] = (
    "Counts describe only the returned results, not the full dataset or all "
    "possible materials.",
    "Element presence is read from reported formulas; it does not establish "
    "stability, synthesis feasibility or performance.",
    "Ranked materials are not necessarily chain endpoints and may not appear "
    "in any returned chain.",
    "Pathway counts exclude the source material.",
)

TRUNCATION_LIMITATION = (
    "Results were limited; coverage may differ for unreturned results."
)


def _chain_material_formula(material: Mapping) -> str | None:
    # Same precedence as the existing Strict response filter.
    return material.get("formula") or material.get("pretty_formula")


def _material_counts(
    element: str,
    evaluated: Sequence[frozenset[str] | None],
) -> tuple[int, int, int]:
    evaluated_sets = [elements for elements in evaluated if elements is not None]
    containing = sum(1 for elements in evaluated_sets if element in elements)
    evaluated_count = len(evaluated_sets)
    return containing, evaluated_count, len(evaluated) - evaluated_count


def _prefer_status(containing: int, evaluated_count: int) -> str:
    if evaluated_count == 0:
        return "not_evaluated"
    return "represented" if containing > 0 else "not_represented"


def _avoid_status(containing: int, evaluated_count: int) -> str:
    if containing > 0:
        return "present"
    if evaluated_count == 0:
        return "not_evaluated"
    return "not_observed"


def build_objective_coverage(
    *,
    material_id: int,
    base_formula: str | None,
    objective,
    mode: str,
    ranked_candidates: Sequence[Mapping],
    chains: Sequence[Mapping],
    ranked_material_pool_count: int,
    result_truncated: bool,
    search_truncated: bool,
) -> dict:
    avoid_elements: list[str] = list(objective.avoid_elements)
    prefer_elements: list[str] = list(objective.prefer_elements)

    ranked_elements = [
        parse_formula_elements_strict(candidate.get("formula"))
        for candidate in ranked_candidates
    ]
    total_ranked = len(ranked_elements)

    preferred = []
    for element in prefer_elements:
        containing, evaluated_count, not_evaluated = _material_counts(
            element, ranked_elements
        )
        preferred.append({
            "element": element,
            "unit": "returned_ranked_materials",
            "containing_count": containing,
            "evaluated_count": evaluated_count,
            "not_evaluated_count": not_evaluated,
            "total_count": total_ranked,
            "status": _prefer_status(containing, evaluated_count),
            "coverage_complete": not_evaluated == 0,
        })

    avoided_in_materials = []
    for element in avoid_elements:
        containing, evaluated_count, not_evaluated = _material_counts(
            element, ranked_elements
        )
        avoided_in_materials.append({
            "element": element,
            "unit": "returned_ranked_materials",
            "containing_count": containing,
            "evaluated_count": evaluated_count,
            "not_evaluated_count": not_evaluated,
            "total_count": total_ranked,
            "status": _avoid_status(containing, evaluated_count),
            "coverage_complete": not_evaluated == 0,
        })

    # Non-source materials of each returned chain, in chain order.
    chain_members: list[list[tuple[int, int, frozenset[str] | None]]] = [
        [
            (
                index,
                material["material_id"],
                parse_formula_elements_strict(_chain_material_formula(material)),
            )
            for index, material in enumerate(chain.get("materials", []))
            if index > 0
        ]
        for chain in chains
    ]
    total_chains = len(chain_members)

    avoided_in_chains = []
    for element in avoid_elements:
        containing_positions: list[int] = []
        not_evaluated_chains = 0
        for position, members in enumerate(chain_members, start=1):
            if any(
                elements is not None and element in elements
                for _, _, elements in members
            ):
                containing_positions.append(position)
            elif any(elements is None for _, _, elements in members):
                not_evaluated_chains += 1
        evaluated_chains = total_chains - not_evaluated_chains
        avoided_in_chains.append({
            "element": element,
            "unit": "returned_chains_excluding_source",
            "containing_chain_count": len(containing_positions),
            "evaluated_chain_count": evaluated_chains,
            "not_evaluated_chain_count": not_evaluated_chains,
            "total_chain_count": total_chains,
            "chain_positions": containing_positions,
            "status": _avoid_status(len(containing_positions), evaluated_chains),
            "coverage_complete": not_evaluated_chains == 0,
        })

    chain_avoidance = []
    for position, members in enumerate(chain_members, start=1):
        last_index = members[-1][0] if members else 0
        flagged = []
        for index, member_id, elements in members:
            if elements is None:
                continue
            present = [element for element in avoid_elements if element in elements]
            if present:
                flagged.append({
                    "material_id": member_id,
                    "chain_material_index": index,
                    "role": "final" if index == last_index else "intermediate",
                    "avoided_elements": present,
                })
        chain_avoidance.append({
            "chain_position": position,
            "materials_with_avoided_elements": flagged,
            "not_evaluated_material_ids": [
                member_id
                for _, member_id, elements in members
                if elements is None
            ],
        })

    source_elements = parse_formula_elements_strict(base_formula)
    source_material = {
        "material_id": material_id,
        "excluded_from_counts": True,
        "avoided_elements_present": (
            None
            if source_elements is None
            else [element for element in avoid_elements if element in source_elements]
        ),
    }

    terms_not_evaluated: list[str] = []
    if objective.preserve_elements:
        terms_not_evaluated.append("preserve_elements")
    if objective.target_family is not None:
        terms_not_evaluated.append("target_family")

    limitations = list(BASE_LIMITATIONS)
    if result_truncated or search_truncated:
        limitations.append(TRUNCATION_LIMITATION)

    return {
        "contract_version": CONTRACT_VERSION,
        "scope": "returned_results_only",
        "element_evaluation_basis": "formula_symbols_strict_parse",
        "returned_ranked_material_count": total_ranked,
        "ranked_material_pool_count": ranked_material_pool_count,
        "returned_chain_count": total_chains,
        "preferred_elements": preferred,
        "avoided_elements_in_ranked_materials": avoided_in_materials,
        "avoided_elements_in_returned_chains": avoided_in_chains,
        "chain_avoidance": chain_avoidance,
        "source_material": source_material,
        "terms_not_evaluated": terms_not_evaluated,
        "mode": mode,
        "avoid_policy_explanation": AVOID_POLICY_EXPLANATIONS[mode],
        "limitations": limitations,
    }
