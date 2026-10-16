"""Contract tests for objective_coverage (contract version 1).

Golden case: byte-exact copy of the frozen production Case Study 01 post-deploy
response (docs/product/literature-case-study-01/qualification/
production-2026-10-09/post-deploy-20261009T034841Z/cs01_response.json).
No live data is fetched.
"""

import hashlib
import json
from pathlib import Path

import pytest

from app.schemas.discovery import ResearchObjective
from app.schemas.research_objective_exploration import ObjectiveCoverage
from app.services.research.objective_coverage import (
    AVOID_POLICY_EXPLANATIONS,
    BASE_LIMITATIONS,
    TRUNCATION_LIMITATION,
    build_objective_coverage,
)

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "objective_coverage"
    / "cs01_production_post_deploy_response.json"
)
FIXTURE_SHA256 = (
    "0ae32ba28607714224d07d5ed609c7195337a2c6d16fa68b50c3f9767ea473ac"
)


def _objective(**overrides) -> ResearchObjective:
    values = {
        "avoid_elements": [],
        "prefer_elements": [],
        "preserve_elements": [],
        "target_family": None,
        "max_hops": 2,
        "limit": 5,
        "prefer_lower_criticality": False,
        "require_stable_materials": False,
    }
    values.update(overrides)
    return ResearchObjective(**values)


def _material(material_id: int, formula: str | None) -> dict:
    return {
        "material_id": material_id,
        "mp_id": None,
        "pretty_formula": formula,
        "formula": formula,
    }


def _chain(*materials: dict) -> dict:
    return {"hop_count": len(materials) - 1, "materials": list(materials)}


def _candidate(material_id: int, formula: str | None, score: float = 50.0) -> dict:
    return {
        "material_id": material_id,
        "formula": formula,
        "score": score,
        "reasons": [],
        "warnings": [],
    }


def _build(objective, ranked, chains, *, mode="balanced", pool=None,
           base_formula="LiFePO4", result_truncated=False,
           search_truncated=False) -> dict:
    coverage = build_objective_coverage(
        material_id=5,
        base_formula=base_formula,
        objective=objective,
        mode=mode,
        ranked_candidates=ranked,
        chains=chains,
        ranked_material_pool_count=len(ranked) if pool is None else pool,
        result_truncated=result_truncated,
        search_truncated=search_truncated,
    )
    # Every result must satisfy the frozen response schema.
    ObjectiveCoverage.model_validate(coverage)
    return coverage


def _by_element(entries: list[dict]) -> dict[str, dict]:
    return {entry["element"]: entry for entry in entries}


# --------------------------------------------------------------- golden CS01

def _golden_response() -> dict:
    raw = FIXTURE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256
    return json.loads(raw)


def _golden_coverage() -> dict:
    response = _golden_response()
    return _build(
        ResearchObjective(**response["objective"]),
        response["ranked_candidates"],
        response["chains"],
        mode=response["mode"],
        base_formula=response["base_formula"],
        result_truncated=response["search_metadata"]["result_truncated"],
        search_truncated=response["search_metadata"]["search_truncated"],
    )


def test_golden_case_study_01_preferred_elements():
    preferred = _by_element(_golden_coverage()["preferred_elements"])
    assert list(preferred) == ["Na", "K"]
    assert preferred["Na"] == {
        "element": "Na", "unit": "returned_ranked_materials",
        "containing_count": 5, "evaluated_count": 5, "not_evaluated_count": 0,
        "total_count": 5, "status": "represented", "coverage_complete": True,
    }
    assert preferred["K"]["containing_count"] == 0
    assert preferred["K"]["evaluated_count"] == 5
    assert preferred["K"]["status"] == "not_represented"


def test_golden_case_study_01_avoided_elements_in_ranked_materials():
    avoided = _by_element(
        _golden_coverage()["avoided_elements_in_ranked_materials"]
    )
    assert list(avoided) == ["Li", "Co"]
    for element in ("Li", "Co"):
        assert avoided[element]["containing_count"] == 0
        assert avoided[element]["evaluated_count"] == 5
        assert avoided[element]["status"] == "not_observed"
        assert avoided[element]["coverage_complete"] is True


def test_golden_case_study_01_avoided_elements_in_returned_chains():
    coverage = _golden_coverage()
    chains = _by_element(coverage["avoided_elements_in_returned_chains"])
    assert chains["Li"] == {
        "element": "Li", "unit": "returned_chains_excluding_source",
        "containing_chain_count": 3, "evaluated_chain_count": 5,
        "not_evaluated_chain_count": 0, "total_chain_count": 5,
        "chain_positions": [3, 4, 5], "status": "present",
        "coverage_complete": True,
    }
    assert chains["Co"]["containing_chain_count"] == 0
    assert chains["Co"]["status"] == "not_observed"

    flagged = [
        detail["materials_with_avoided_elements"]
        for detail in coverage["chain_avoidance"]
    ]
    assert flagged[0] == [] and flagged[1] == []
    assert [entry[0]["material_id"] for entry in flagged[2:]] == [1, 2, 3]
    assert all(
        entry == [{
            "material_id": entry[0]["material_id"],
            "chain_material_index": 1,
            "role": "intermediate",
            "avoided_elements": ["Li"],
        }]
        for entry in flagged[2:]
    )


def test_golden_case_study_01_source_and_scope_disclosure():
    coverage = _golden_coverage()
    assert coverage["source_material"] == {
        "material_id": 5,
        "excluded_from_counts": True,
        "avoided_elements_present": ["Li"],
    }
    assert coverage["returned_ranked_material_count"] == 5
    assert coverage["returned_chain_count"] == 5
    assert coverage["terms_not_evaluated"] == [
        "preserve_elements", "target_family",
    ]
    assert coverage["avoid_policy_explanation"] == (
        AVOID_POLICY_EXPLANATIONS["balanced"]
    )
    # Production response had result_truncated=True.
    assert TRUNCATION_LIMITATION in coverage["limitations"]


def test_golden_ranked_materials_are_not_equated_with_chain_endpoints():
    response = _golden_response()
    chain_members = {
        material["material_id"]
        for chain in response["chains"]
        for material in chain["materials"][1:]
    }
    ranked_ids = [item["material_id"] for item in response["ranked_candidates"]]
    assert [m for m in ranked_ids if m not in chain_members] == [7, 8, 9]
    coverage = _golden_coverage()
    assert coverage["returned_ranked_material_count"] == len(ranked_ids)


# --------------------------------------------------------------- edge cases

def test_empty_results_are_not_evaluated():
    coverage = _build(
        _objective(avoid_elements=["Li"], prefer_elements=["Na"]), [], []
    )
    assert coverage["preferred_elements"][0]["status"] == "not_evaluated"
    assert coverage["preferred_elements"][0]["total_count"] == 0
    assert coverage["avoided_elements_in_ranked_materials"][0]["status"] == (
        "not_evaluated"
    )
    assert coverage["avoided_elements_in_returned_chains"][0]["status"] == (
        "not_evaluated"
    )
    assert coverage["chain_avoidance"] == []


@pytest.mark.parametrize("formula", [None, "", "Xx2O", "LiFe(PO4", "Fe2O3·H2O"])
def test_unevaluable_ranked_formula_is_never_counted_as_absent(formula):
    ranked = [_candidate(6, "NaFePO4"), _candidate(7, formula)]
    coverage = _build(
        _objective(avoid_elements=["Li"], prefer_elements=["K"]), ranked, []
    )
    prefer = coverage["preferred_elements"][0]
    assert (prefer["containing_count"], prefer["evaluated_count"],
            prefer["not_evaluated_count"], prefer["total_count"]) == (0, 1, 1, 2)
    assert prefer["status"] == "not_represented"
    assert prefer["coverage_complete"] is False
    avoid = coverage["avoided_elements_in_ranked_materials"][0]
    assert (avoid["evaluated_count"], avoid["not_evaluated_count"]) == (1, 1)
    assert avoid["status"] == "not_observed"
    assert avoid["coverage_complete"] is False


def test_all_ranked_unevaluable_gives_not_evaluated():
    coverage = _build(
        _objective(prefer_elements=["Na"]), [_candidate(6, None)], []
    )
    assert coverage["preferred_elements"][0]["status"] == "not_evaluated"


def test_multiple_preferred_and_avoided_elements_keep_request_order():
    ranked = [_candidate(6, "NaFePO4"), _candidate(7, "KCoO2")]
    coverage = _build(
        _objective(prefer_elements=["K", "Na", "Mg"],
                   avoid_elements=["Co", "Li"]),
        ranked, [],
    )
    assert [e["element"] for e in coverage["preferred_elements"]] == [
        "K", "Na", "Mg",
    ]
    assert [e["status"] for e in coverage["preferred_elements"]] == [
        "represented", "represented", "not_represented",
    ]
    avoided = coverage["avoided_elements_in_ranked_materials"]
    assert [(e["element"], e["containing_count"], e["status"]) for e in avoided] == [
        ("Co", 1, "present"), ("Li", 0, "not_observed"),
    ]


def test_chain_counts_are_per_chain_and_material_counts_per_material():
    source = _material(5, "LiFePO4")
    shared_end = _material(6, "Na3Fe(PO4)2")
    chains = [
        _chain(source, _material(1, "LiFe(PO3)3"), shared_end),
        _chain(source, _material(2, "LiFe(PO3)4"), shared_end),
        _chain(source, shared_end),
    ]
    ranked = [_candidate(6, "Na3Fe(PO4)2")]
    coverage = _build(_objective(avoid_elements=["Li"]), ranked, chains)
    chain_li = coverage["avoided_elements_in_returned_chains"][0]
    assert (chain_li["containing_chain_count"], chain_li["total_chain_count"],
            chain_li["chain_positions"]) == (2, 3, [1, 2])
    material_li = coverage["avoided_elements_in_ranked_materials"][0]
    assert (material_li["containing_count"], material_li["total_count"]) == (0, 1)


def test_chain_with_unevaluable_member_and_avoided_member_is_present():
    chain = _chain(_material(5, "LiFePO4"), _material(1, "LiFeP2O7"),
                   _material(9, "Xx2O"))
    coverage = _build(_objective(avoid_elements=["Li"]), [], [chain])
    entry = coverage["avoided_elements_in_returned_chains"][0]
    assert (entry["containing_chain_count"], entry["not_evaluated_chain_count"],
            entry["status"]) == (1, 0, "present")
    assert coverage["chain_avoidance"][0]["not_evaluated_material_ids"] == [9]


def test_chain_with_unevaluable_member_and_no_avoided_member_is_not_evaluated():
    chain = _chain(_material(5, "LiFePO4"), _material(6, "NaFePO4"),
                   _material(9, None))
    coverage = _build(_objective(avoid_elements=["Li"]), [], [chain])
    entry = coverage["avoided_elements_in_returned_chains"][0]
    assert (entry["containing_chain_count"], entry["evaluated_chain_count"],
            entry["not_evaluated_chain_count"], entry["status"],
            entry["coverage_complete"]) == (0, 0, 1, "not_evaluated", False)


def test_pretty_formula_fallback_for_chain_material_only_when_formula_empty():
    material = {"material_id": 1, "mp_id": None,
                "pretty_formula": "LiFeP2O7", "formula": ""}
    chain = _chain(_material(5, "LiFePO4"), material)
    coverage = _build(_objective(avoid_elements=["Li"]), [], [chain])
    assert coverage["avoided_elements_in_returned_chains"][0][
        "containing_chain_count"] == 1


def test_source_is_excluded_from_chain_counts_and_disclosed():
    chain = _chain(_material(5, "LiFePO4"), _material(6, "NaFePO4"))
    coverage = _build(_objective(avoid_elements=["Li", "Co"]), [], [chain])
    entry = _by_element(coverage["avoided_elements_in_returned_chains"])["Li"]
    assert (entry["containing_chain_count"], entry["status"]) == (
        0, "not_observed",
    )
    assert coverage["source_material"]["avoided_elements_present"] == ["Li"]
    assert "Pathway counts exclude the source material." in (
        coverage["limitations"]
    )


def test_unevaluable_source_formula_is_reported_as_unknown():
    coverage = _build(_objective(avoid_elements=["Li"]), [], [],
                      base_formula=None)
    assert coverage["source_material"]["avoided_elements_present"] is None


def test_final_and_intermediate_roles_follow_chain_position():
    chain = _chain(_material(5, "LiFePO4"), _material(1, "LiFeP2O7"),
                   _material(3, "LiCoO2"))
    coverage = _build(_objective(avoid_elements=["Co", "Li"]), [], [chain])
    flagged = coverage["chain_avoidance"][0]["materials_with_avoided_elements"]
    assert flagged == [
        {"material_id": 1, "chain_material_index": 1, "role": "intermediate",
         "avoided_elements": ["Li"]},
        {"material_id": 3, "chain_material_index": 2, "role": "final",
         "avoided_elements": ["Co", "Li"]},
    ]


@pytest.mark.parametrize("mode", ["balanced", "exploratory", "strict"])
def test_mode_explanations_are_backend_owned(mode):
    coverage = _build(_objective(avoid_elements=["Li"]), [], [], mode=mode)
    assert coverage["mode"] == mode
    assert coverage["avoid_policy_explanation"] == AVOID_POLICY_EXPLANATIONS[mode]
    assert "satisf" not in coverage["avoid_policy_explanation"].lower()


def test_tied_ranked_scores_do_not_change_coverage_under_permutation():
    ranked = [_candidate(6, "NaFePO4", 125.0), _candidate(7, "KFePO4", 125.0),
              _candidate(8, "LiFePO4", 125.0)]
    objective = _objective(prefer_elements=["Na", "K"], avoid_elements=["Li"])
    first = _build(objective, ranked, [])
    second = _build(objective, list(reversed(ranked)), [])
    for key in ("preferred_elements", "avoided_elements_in_ranked_materials"):
        assert first[key] == second[key]


def test_truncation_adds_limitation_and_reports_pool():
    ranked = [_candidate(6, "NaFePO4")]
    plain = _build(_objective(prefer_elements=["Na"]), ranked, [])
    assert plain["limitations"] == list(BASE_LIMITATIONS)
    truncated = _build(_objective(prefer_elements=["Na"]), ranked, [], pool=9,
                       search_truncated=True)
    assert truncated["ranked_material_pool_count"] == 9
    assert truncated["returned_ranked_material_count"] == 1
    assert truncated["limitations"][-1] == TRUNCATION_LIMITATION


def test_no_avoid_or_prefer_inputs_invent_no_statuses():
    chain = _chain(_material(5, "LiFePO4"), _material(6, "NaFePO4"))
    coverage = _build(_objective(), [_candidate(6, "NaFePO4")], [chain])
    assert coverage["preferred_elements"] == []
    assert coverage["avoided_elements_in_ranked_materials"] == []
    assert coverage["avoided_elements_in_returned_chains"] == []
    assert coverage["chain_avoidance"][0]["materials_with_avoided_elements"] == []
    assert coverage["terms_not_evaluated"] == []


def test_no_overall_satisfaction_status_exists():
    coverage = _golden_coverage()
    assert "status" not in coverage
    assert "satisf" not in json.dumps(coverage).lower()


# --------------------------------------------------------------- service wiring

class _StubObjectiveService:
    def __init__(self, chains):
        self.chains = chains

    def generate_chains_for_objective(self, material_id, objective,
                                      include_ranked_pool=False,
                                      hard_avoid_admission=False,
                                      objective_aware_prefer_allocation=False):
        from app.services.research.objective_service import (
            ResearchObjectiveService,
        )
        return {
            "material_id": material_id,
            "base_formula": "LiFePO4",
            "objective": objective,
            "objective_policy": ResearchObjectiveService._build_objective_policy(
                objective
            ),
            "search_metadata": {
                "search_policy": "bounded_breadth_first",
                "requested_result_limit": objective.limit,
                "expansion_limit_per_material": 6,
                "search_state_budget": 200,
                "expanded_state_count": len(self.chains),
                "generated_chain_count": len(self.chains),
                "returned_chain_count": len(self.chains),
                "search_truncated": False,
                "result_truncated": False,
                "scientific_completeness_guaranteed": False,
            },
            "chains": self.chains,
        }


def _stub_chain(*materials):
    chain = _chain(*materials)
    chain.update({
        "transitions": [], "chain_reason": "Stub chain.",
        "scientific_usefulness_score": 0.0, "score_breakdown": {},
        "usefulness_reason": "Stub ranking.",
    })
    return chain


def test_explore_adds_coverage_without_changing_existing_fields():
    from app.schemas.research_objective_exploration import (
        ResearchObjectiveExplorationRequest,
        ResearchObjectiveExplorationResponse,
    )
    from app.services.research.objective_exploration_service import (
        ResearchObjectiveExplorationService,
    )

    source = _material(5, "LiFePO4")
    chains = [
        _stub_chain(source, _material(6, "NaFePO4")),
        _stub_chain(source, _material(1, "LiFeP2O7"), _material(6, "NaFePO4")),
        _stub_chain(source, _material(8, "Na3Fe(PO4)2")),
    ]
    service = ResearchObjectiveExplorationService.__new__(
        ResearchObjectiveExplorationService
    )
    service.objective_service = _StubObjectiveService(chains)
    request = ResearchObjectiveExplorationRequest(
        objective=_objective(avoid_elements=["Li"], prefer_elements=["Na"],
                             limit=2),
        mode="balanced",
        limit=2,
    )

    result = service.explore(material_id=5, request=request)

    assert list(result)[:-1] == [
        "material_id", "base_formula", "objective", "objective_policy", "mode",
        "constraint_policy", "search_metadata", "ranked_candidates", "chains",
        "warnings", "explanation",
    ]
    coverage = result["objective_coverage"]
    assert coverage["returned_ranked_material_count"] == len(
        result["ranked_candidates"]
    )
    # Ranked pool = distinct non-source materials of all eligible chains: 6, 1, 8.
    assert coverage["ranked_material_pool_count"] == 3
    assert coverage["returned_chain_count"] == len(result["chains"]) == 2
    chains_li = coverage["avoided_elements_in_returned_chains"][0]
    assert (chains_li["containing_chain_count"], chains_li["chain_positions"]) == (
        1, [2],
    )
    ResearchObjectiveExplorationResponse.model_validate(result)
