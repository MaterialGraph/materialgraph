from app.schemas.discovery import ResearchObjective
from app.services.research.objective_service import ResearchObjectiveService


def _sample_chain() -> dict:
    return {
        "hop_count": 1,
        "materials": [
            {
                "material_id": 5,
                "mp_id": "mp-19017",
                "pretty_formula": "LiFePO4",
                "formula": "LiFePO4",
            },
            {
                "material_id": 7,
                "mp_id": "mp-556540",
                "pretty_formula": "Na3Fe3(PO4)4",
                "formula": "Na3Fe3(PO4)4",
            },
        ],
        "transitions": [
            {
                "from_material_id": 5,
                "to_material_id": 7,
                "from_formula": "LiFePO4",
                "to_formula": "Na3Fe3(PO4)4",
                "transition_type": "alkali_substitution",
                "family": "phosphate",
                "reason": "Test transition.",
                "shared_elements": ["Fe", "O", "P"],
                "preserved_framework": ["Fe", "O", "P"],
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "removed_elements": ["Li"],
                "introduced_elements": ["Na"],
            }
        ],
        "chain_reason": "Test chain.",
    }


class _CapturingChainService:
    def __init__(self):
        self.calls = []

    def get_discovery_chains(self, **kwargs):
        self.calls.append(dict(kwargs))
        return {
            "material_id": kwargs["material_id"],
            "base_formula": "LiFePO4",
            "search_metadata": {
                "search_policy": "bounded_breadth_first",
                "requested_result_limit": kwargs["limit"],
                "expansion_limit_per_material": 6,
                "search_state_budget": 200,
                "expanded_state_count": 1,
                "generated_chain_count": 1,
                "returned_chain_count": 1,
                "search_truncated": False,
                "result_truncated": False,
                "scientific_completeness_guaranteed": False,
            },
            "chains": [_sample_chain()],
        }


class _CapturingPathRankingService:
    def __init__(self):
        self.calls = []

    def rank_path(self, **kwargs):
        self.calls.append(dict(kwargs))
        return {
            "scientific_usefulness_score": 85.0,
            "score_breakdown": {
                "shared_element_continuity": 30.0,
                "objective_alignment": 25.0,
                "transition_plausibility": 20.0,
                "path_efficiency": 10.0,
                "material_quality": 0.0,
            },
            "usefulness_reason": "Test ranking.",
        }


def test_research_objective_chains_include_ranking_fields(db_session):
    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
        prefer_lower_criticality=True,
        require_stable_materials=False,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    assert result["material_id"] == 5
    assert result["chains"]

    for chain in result["chains"]:
        assert "scientific_usefulness_score" in chain
        assert "score_breakdown" in chain
        assert "usefulness_reason" in chain


def test_research_objective_chains_are_sorted_by_usefulness(db_session):
    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    scores = [
        chain["scientific_usefulness_score"]
        for chain in result["chains"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_research_objective_filters_preserved_elements(db_session):
    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    required = {"Fe", "P", "O"}

    for chain in result["chains"]:
        transitions = chain["transitions"]

        assert transitions

        shared_element_sets = []

        for transition in transitions:
            elements = (
                transition["shared_elements"]
                if "shared_elements" in transition
                else transition.get("preserved_framework", [])
            )
            shared_element_sets.append(set(elements))

        continuous_elements = set.intersection(*shared_element_sets)

        assert required.issubset(continuous_elements)


def test_multi_element_objective_passes_complete_sets_to_chain_generation(
    db_session,
):
    service = ResearchObjectiveService(db_session)
    chain_service = _CapturingChainService()
    ranking_service = _CapturingPathRankingService()
    service.chain_service = chain_service
    service.path_ranking_service = ranking_service

    objective = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        preserve_elements=[],
        target_family=None,
        max_hops=2,
        limit=5,
    )

    service.generate_chains_for_objective(5, objective)

    call = chain_service.calls[0]
    assert set(call["avoid_elements"]) == {"Li", "Co"}
    assert set(call["prefer_elements"]) == {"Na", "K"}
    assert "avoid_element" not in call
    assert "prefer_element" not in call
    assert call["include_search_pool"] is True


def test_objective_filters_before_applying_result_limit(db_session):
    service = ResearchObjectiveService(db_session)
    chain_service = _CapturingChainService()
    ranking_service = _CapturingPathRankingService()
    first = _sample_chain()
    first["materials"][-1] = {
        "material_id": 6,
        "formula": "NaFeO2",
        "pretty_formula": "NaFeO2",
    }
    second = _sample_chain()
    chain_service.get_discovery_chains = lambda **kwargs: {
        "material_id": kwargs["material_id"],
        "base_formula": "LiFePO4",
        "search_metadata": {
            "search_policy": "bounded_breadth_first",
            "requested_result_limit": kwargs["limit"],
            "expansion_limit_per_material": 6,
            "search_state_budget": 200,
            "expanded_state_count": 2,
            "generated_chain_count": 2,
            "returned_chain_count": 2,
            "search_truncated": False,
            "result_truncated": True,
            "scientific_completeness_guaranteed": False,
        },
        "chains": [first, second],
    }
    service.chain_service = chain_service
    service.path_ranking_service = ranking_service
    objective = ResearchObjective(
        preserve_elements=[],
        target_family="phosphate",
        max_hops=2,
        limit=1,
    )

    result = service.generate_chains_for_objective(5, objective)

    assert len(result["chains"]) == 1
    assert result["chains"][0]["materials"][-1]["material_id"] == 7


def test_multi_element_objective_passes_complete_sets_to_path_ranking(
    db_session,
):
    service = ResearchObjectiveService(db_session)
    chain_service = _CapturingChainService()
    ranking_service = _CapturingPathRankingService()
    service.chain_service = chain_service
    service.path_ranking_service = ranking_service

    objective = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        preserve_elements=[],
        target_family=None,
        max_hops=2,
        limit=5,
    )

    service.generate_chains_for_objective(5, objective)

    call = ranking_service.calls[0]
    assert set(call["avoid_elements"]) == {"Li", "Co"}
    assert set(call["prefer_elements"]) == {"Na", "K"}
    assert "avoid_element" not in call
    assert "prefer_element" not in call


def test_multi_element_objective_list_order_no_longer_changes_effective_sets(
    db_session,
):
    service = ResearchObjectiveService(db_session)
    chain_service = _CapturingChainService()
    ranking_service = _CapturingPathRankingService()
    service.chain_service = chain_service
    service.path_ranking_service = ranking_service

    first = ResearchObjective(
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
        preserve_elements=[],
    )
    second = ResearchObjective(
        avoid_elements=["Co", "Li"],
        prefer_elements=["K", "Na"],
        preserve_elements=[],
    )

    service.generate_chains_for_objective(5, first)
    service.generate_chains_for_objective(5, second)

    assert set(chain_service.calls[0]["avoid_elements"]) == set(
        chain_service.calls[1]["avoid_elements"]
    )
    assert set(chain_service.calls[0]["prefer_elements"]) == set(
        chain_service.calls[1]["prefer_elements"]
    )


def test_preservation_requires_continuity_across_every_transition(
    db_session,
):
    service = ResearchObjectiveService(db_session)

    chain = {
        "transitions": [
            {
                "shared_elements": ["Fe", "P"],
                "preserved_framework": ["Fe", "P"],
            },
            {
                "shared_elements": ["Fe", "O"],
                "preserved_framework": ["Fe", "O"],
            },
        ],
    }

    assert service._preserves_required_elements(
        chain=chain,
        preserve_elements=["Fe"],
    )
    assert not service._preserves_required_elements(
        chain=chain,
        preserve_elements=["Fe", "P", "O"],
    )


def test_preservation_fails_when_path_has_no_transitions(
    db_session,
):
    service = ResearchObjectiveService(db_session)

    assert not service._preserves_required_elements(
        chain={"transitions": []},
        preserve_elements=["Fe"],
    )


def test_shared_elements_take_precedence_over_compatibility_alias(
    db_session,
):
    service = ResearchObjectiveService(db_session)

    chain = {
        "transitions": [
            {
                "shared_elements": [],
                "preserved_framework": ["Fe"],
            },
        ],
    }

    assert not service._preserves_required_elements(
        chain=chain,
        preserve_elements=["Fe"],
    )


def test_target_family_uses_only_endpoint_composition(db_session):
    service = ResearchObjectiveService(db_session)
    chain = {
        "materials": [
            {"material_id": 1, "elements": ["Li", "Fe", "P", "O"]},
            {"material_id": 2, "elements": ["Na", "Fe", "P", "O"]},
            {"material_id": 3, "elements": ["Na", "Co", "O"]},
        ],
        "transitions": [
            {
                "family": "phosphate",
                "transition_type": "phosphate_substitution",
                "shared_elements": ["Fe", "P", "O"],
                "scientific_reason": "Earlier phosphate transition.",
            },
            {
                "family": "oxide",
                "transition_type": "family_expansion",
                "shared_elements": ["Na", "O"],
            },
        ],
    }

    assert not service._matches_target_family(chain, "phosphate")


def test_target_family_accepts_matching_endpoint_composition(db_session):
    service = ResearchObjectiveService(db_session)
    chain = {
        "materials": [
            {"material_id": 1, "elements": ["Li", "Fe", "P", "O"]},
            {"material_id": 2, "elements": ["Na", "Fe", "P", "O"]},
        ],
        "transitions": [],
    }

    assert service._matches_target_family(chain, "PHOSPHATE")


def test_target_family_preserves_explicit_empty_endpoint_membership(db_session):
    service = ResearchObjectiveService(db_session)
    chain = {
        "materials": [
            {
                "material_id": 2,
                "elements": [],
                "formula": "NaFePO4",
            },
        ],
        "transitions": [],
    }

    assert not service._matches_target_family(chain, "phosphate")


def test_target_family_parses_formula_when_endpoint_membership_is_missing(
    db_session,
):
    service = ResearchObjectiveService(db_session)
    chain = {
        "materials": [
            {
                "material_id": 2,
                "formula": "NaFePO4",
            },
        ],
        "transitions": [],
    }

    assert service._matches_target_family(chain, "phosphate")
