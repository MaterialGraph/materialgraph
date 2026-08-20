from app.services.discovery.path_ranking_service import (
    DiscoveryPathRankingService,
)


def _transition(
    removed=None,
    introduced=None,
):
    return {
        "transition_type": "alkali_substitution",
        "family": "phosphate",
        "shared_elements": ["Fe", "O", "P"],
        "preserved_framework": ["Fe", "O", "P"],
        "removed_elements": removed or [],
        "introduced_elements": introduced or [],
    }


class FakeMaterialQualityService:
    def __init__(self, scores):
        self.scores = scores

    def get_material_quality_bulk(self, material_ids):
        return {
            material_id: {"quality_score": self.scores[material_id]}
            for material_id in material_ids
            if material_id in self.scores
        }


def test_rank_path_scores_full_alkali_substitution_path():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
        ],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["scientific_usefulness_score"] == 85.0
    assert result["score_breakdown"]["objective_alignment"] == 25.0


def test_multi_element_objective_alignment_is_proportional_and_capped():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiCoO2"},
            {"material_id": 2, "formula": "NaCoO2"},
        ],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 12.5
    assert result["score_breakdown"]["objective_alignment"] <= 25.0


def test_multi_element_objective_full_endpoint_alignment_keeps_existing_maximum():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiCoO2"},
            {
                "material_id": 2,
                "elements": ["Na", "K", "O"],
                "formula": "NaKO",
            },
        ],
        transitions=[
            _transition(
                ["Li", "Co"],
                ["Na", "K"],
            )
        ],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 25.0


def test_multi_element_objective_alignment_is_order_independent():
    service = DiscoveryPathRankingService()
    transitions = [_transition(["Li"], ["Na"])]

    first = service.rank_path(
        materials=[],
        transitions=transitions,
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )
    second = service.rank_path(
        materials=[],
        transitions=transitions,
        avoid_elements=["Co", "Li"],
        prefer_elements=["K", "Na"],
    )

    assert (
        first["score_breakdown"]["objective_alignment"]
        == second["score_breakdown"]["objective_alignment"]
    )


def test_reason_separates_path_events_from_satisfied_endpoint_objectives():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
        ],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_elements=["Li"],
        prefer_elements=["Na"],
    )

    reason = result["usefulness_reason"]

    assert "removes Li during the path" in reason
    assert "introduces Na during the path" in reason
    assert "endpoint excludes requested avoided element(s) Li" in reason
    assert "endpoint contains requested preferred element(s) Na" in reason


def test_reason_reports_endpoint_reversal_separately_from_path_events():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
            {"material_id": 3, "formula": "LiFePO4"},
        ],
        transitions=[
            _transition(["Li"], ["Na"]),
            _transition(["Na"], ["Li"]),
        ],
        avoid_elements=["Li"],
        prefer_elements=["Na"],
    )

    reason = result["usefulness_reason"]

    assert "removes Li during the path" in reason
    assert "introduces Na during the path" in reason
    assert "endpoint still contains requested avoided element(s) Li" in reason
    assert "endpoint does not contain requested preferred element(s) Na" in reason


def test_reason_reports_partial_multi_element_endpoint_satisfaction():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiCoO2"},
            {"material_id": 2, "formula": "NaCoO2"},
        ],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    reason = result["usefulness_reason"]

    assert "endpoint excludes requested avoided element(s) Li" in reason
    assert "endpoint still contains requested avoided element(s) Co" in reason
    assert "endpoint contains requested preferred element(s) Na" in reason
    assert "endpoint does not contain requested preferred element(s) K" in reason


def test_reason_reports_unavailable_endpoint_composition():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {
                "material_id": 1,
                "formula": None,
                "pretty_formula": None,
            },
        ],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_elements=["Li"],
        prefer_elements=["Na"],
    )

    reason = result["usefulness_reason"]

    assert "removes Li during the path" in reason
    assert "introduces Na during the path" in reason
    assert "endpoint composition is unavailable" in reason
    assert "endpoint excludes requested avoided element(s)" not in reason
    assert "endpoint contains requested preferred element(s)" not in reason


def test_rank_path_handles_empty_path():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[],
        transitions=[],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert result["scientific_usefulness_score"] == 0.0
    assert result["usefulness_reason"] == (
        "No discovery path was available for ranking."
    )


def test_preferred_element_introduced_then_removed_gets_no_endpoint_credit():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
            {"material_id": 3, "formula": "LiFePO4"},
        ],
        transitions=[
            {
                "introduced_elements": ["Na"],
                "removed_elements": ["Li"],
            },
            {
                "introduced_elements": ["Li"],
                "removed_elements": ["Na"],
            },
        ],
        prefer_elements=["Na"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 0.0


def test_avoided_element_removed_then_reintroduced_gets_no_endpoint_credit():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
            {"material_id": 3, "formula": "LiFePO4"},
        ],
        transitions=[
            {
                "introduced_elements": ["Na"],
                "removed_elements": ["Li"],
            },
            {
                "introduced_elements": ["Li"],
                "removed_elements": ["Na"],
            },
        ],
        avoid_elements=["Li"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 0.0


def test_endpoint_satisfaction_drives_full_two_sided_objective_credit():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
        ],
        transitions=[
            {
                "introduced_elements": ["Na"],
                "removed_elements": ["Li"],
            },
        ],
        avoid_elements=["Li"],
        prefer_elements=["Na"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 25.0


def test_endpoint_objective_credit_is_proportional_for_multiple_elements():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiCoO2"},
            {"material_id": 2, "formula": "NaCoO2"},
        ],
        transitions=[
            {
                "introduced_elements": ["Na"],
                "removed_elements": ["Li"],
            },
        ],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    # Avoidance: Li excluded, Co remains = 6.25.
    # Preference: Na present, K absent = 6.25.
    assert result["score_breakdown"]["objective_alignment"] == 12.5


def test_missing_endpoint_composition_gets_no_objective_credit():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {
                "material_id": 1,
                "formula": None,
                "pretty_formula": None,
            },
        ],
        transitions=[
            {
                "introduced_elements": ["Na"],
                "removed_elements": ["Li"],
            },
        ],
        avoid_elements=["Li"],
        prefer_elements=["Na"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 0.0


def test_structured_endpoint_elements_take_precedence_over_formula():
    service = DiscoveryPathRankingService()

    result = service.rank_path(
        materials=[
            {
                "material_id": 1,
                "elements": [],
                "formula": "NaFePO4",
            },
        ],
        transitions=[
            {
                "introduced_elements": ["Na"],
                "removed_elements": ["Li"],
            },
        ],
        prefer_elements=["Na"],
    )

    assert result["score_breakdown"]["objective_alignment"] == 0.0


def test_equal_hop_path_with_reversal_receives_lower_efficiency():
    service = DiscoveryPathRankingService()
    direct_progress = [
        _transition(["Li"], ["Na"]),
        _transition(["Co"], ["Mn"]),
    ]
    reversed_progress = [
        _transition(["Li"], ["Na"]),
        _transition(["Na"], ["Li"]),
    ]

    productive_score = service._score_path_efficiency(direct_progress)
    reversal_score = service._score_path_efficiency(reversed_progress)

    assert productive_score == 7.5
    assert reversal_score == 3.75


def test_material_quality_preserves_endpoint_difference_with_shared_base():
    service = DiscoveryPathRankingService()
    materials = [
        {"material_id": 1},
        {"material_id": 2},
    ]

    service.material_quality_service = FakeMaterialQualityService(
        {1: 9.0, 2: 15.0}
    )
    high_endpoint_score = service._score_material_quality(materials)

    service.material_quality_service = FakeMaterialQualityService(
        {1: 9.0, 2: 12.0}
    )
    lower_endpoint_score = service._score_material_quality(materials)

    assert high_endpoint_score == 11.62
    assert lower_endpoint_score == 10.39
    assert high_endpoint_score > lower_endpoint_score


def test_material_quality_retains_weak_intermediate_as_bottleneck():
    service = DiscoveryPathRankingService()
    service.material_quality_service = FakeMaterialQualityService(
        {1: 15.0, 2: 3.0, 3: 15.0}
    )

    score = service._score_material_quality(
        [
            {"material_id": 1},
            {"material_id": 2},
            {"material_id": 3},
        ]
    )

    assert score == 6.71


def test_remediated_components_preserve_total_score_arithmetic():
    service = DiscoveryPathRankingService()
    service.material_quality_service = FakeMaterialQualityService(
        {1: 9.0, 2: 15.0}
    )

    result = service.rank_path(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
        ],
        transitions=[_transition(["Li"], ["Na"])],
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["score_breakdown"]["path_efficiency"] == 10.0
    assert result["score_breakdown"]["material_quality"] == 11.62
    assert result["scientific_usefulness_score"] == round(
        sum(result["score_breakdown"].values()),
        2,
    )