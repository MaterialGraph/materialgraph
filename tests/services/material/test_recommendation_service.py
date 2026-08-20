from unittest.mock import Mock

import pytest

from app.services.material.recommendation_service import (
    MaterialRecommendationService,
)


@pytest.fixture
def service() -> MaterialRecommendationService:
    return MaterialRecommendationService.__new__(
        MaterialRecommendationService
    )


def build_candidate(
    criticality_direction: str,
    criticality_delta: float | None,
) -> dict:
    return {
        "similarity_score": 100.0,
        "criticality_direction": criticality_direction,
        "criticality_delta": criticality_delta,
        "shared_element_count": 0,
        "shared_application_count": 0,
        "is_stable": False,
        "energy_above_hull": None,
    }


def build_full_candidate(
    material_id: int,
    *,
    similarity_score: float,
    criticality_delta: float | None,
) -> dict:
    direction = "UNKNOWN"
    if criticality_delta is not None:
        if criticality_delta < 0:
            direction = "LOWER_CRITICALITY"
        elif criticality_delta > 0:
            direction = "HIGHER_CRITICALITY"
        else:
            direction = "SAME_CRITICALITY"

    return {
        "material_id": material_id,
        "mp_id": f"mp-{material_id}",
        "pretty_formula": f"M{material_id}",
        "formula": f"M{material_id}",
        "material_type": "test",
        "is_stable": False,
        "energy_above_hull": None,
        "similarity_score": similarity_score,
        "criticality_score": None,
        "criticality_delta": criticality_delta,
        "criticality_direction": direction,
        "shared_element_count": 1,
        "shared_application_count": 0,
        "relationship_types": ["SHARED_ELEMENT"],
    }


@pytest.mark.parametrize(
    (
        "criticality_direction",
        "criticality_delta",
        "expected_reason",
    ),
    [
        (
            "LOWER_CRITICALITY",
            -12.0,
            "similarity score 100.0; lower criticality by 12.0; "
            "recommendation score 124.0",
        ),
        (
            "HIGHER_CRITICALITY",
            8.0,
            "similarity score 100.0; higher criticality by 8.0; "
            "recommendation score 84.0",
        ),
        (
            "SAME_CRITICALITY",
            0.0,
            "similarity score 100.0; same criticality; "
            "recommendation score 100.0",
        ),
        (
            "UNKNOWN",
            None,
            "similarity score 100.0; recommendation score 100.0",
        ),
    ],
)
def test_build_recommendation_reason_describes_criticality_comparison(
    service,
    criticality_direction,
    criticality_delta,
    expected_reason,
):
    candidate = build_candidate(
        criticality_direction=criticality_direction,
        criticality_delta=criticality_delta,
    )

    recommendation_score = service._calculate_recommendation_score(
        candidate=candidate,
        prefer_lower_criticality=True,
    )

    reason = service._build_recommendation_reason(
        candidate=candidate,
        recommendation_score=recommendation_score,
        prefer_lower_criticality=True,
    )

    assert reason == expected_reason


@pytest.mark.parametrize(
    (
        "criticality_direction",
        "criticality_delta",
        "expected_score",
    ),
    [
        ("LOWER_CRITICALITY", -12.0, 124.0),
        ("HIGHER_CRITICALITY", 8.0, 84.0),
        ("SAME_CRITICALITY", 0.0, 100.0),
        ("UNKNOWN", None, 100.0),
    ],
)
def test_recommendation_score_uses_delta_not_direction(
    service,
    criticality_direction,
    criticality_delta,
    expected_score,
):
    candidate = build_candidate(
        criticality_direction=criticality_direction,
        criticality_delta=criticality_delta,
    )

    score = service._calculate_recommendation_score(
        candidate=candidate,
        prefer_lower_criticality=True,
    )

    assert score == expected_score


def test_recommendation_reason_labels_non_scoring_criticality_as_context(
    service,
):
    candidate = build_candidate(
        criticality_direction="LOWER_CRITICALITY",
        criticality_delta=-12.0,
    )

    recommendation_score = service._calculate_recommendation_score(
        candidate=candidate,
        prefer_lower_criticality=False,
    )

    reason = service._build_recommendation_reason(
        candidate=candidate,
        recommendation_score=recommendation_score,
        prefer_lower_criticality=False,
    )

    assert recommendation_score == 100.0
    assert "context: lower criticality by 12.0" in reason
    assert "lower criticality by 12.0" not in reason.split("context:")[0]


def test_recommendation_reason_includes_low_energy_score_contribution(
    service,
):
    candidate = build_candidate(
        criticality_direction="UNKNOWN",
        criticality_delta=None,
    )
    candidate["energy_above_hull"] = 0.01

    recommendation_score = service._calculate_recommendation_score(
        candidate=candidate,
        prefer_lower_criticality=False,
    )

    reason = service._build_recommendation_reason(
        candidate=candidate,
        recommendation_score=recommendation_score,
        prefer_lower_criticality=False,
    )

    assert recommendation_score == 105.0
    assert "low energy above hull" in reason


def test_recommendation_reason_labels_similarity_basis(
    service,
):
    candidate = build_candidate(
        criticality_direction="UNKNOWN",
        criticality_delta=None,
    )
    candidate["shared_element_count"] = 3
    candidate["shared_application_count"] = 1

    recommendation_score = service._calculate_recommendation_score(
        candidate=candidate,
        prefer_lower_criticality=False,
    )

    reason = service._build_recommendation_reason(
        candidate=candidate,
        recommendation_score=recommendation_score,
        prefer_lower_criticality=False,
    )

    assert "similarity basis: shares 3 element(s), shares 1 application(s)" in reason


def test_recommendations_use_complete_similarity_pool_before_limit():
    service = MaterialRecommendationService.__new__(
        MaterialRecommendationService
    )
    service.similarity_service = Mock()
    service.similarity_service.get_similar_materials.return_value = {
        "material_id": 1,
        "mp_id": "mp-1",
        "pretty_formula": "M1",
        "formula": "M1",
        "criticality_score": 30.0,
        "similar_materials": [
            build_full_candidate(
                2,
                similarity_score=100.0,
                criticality_delta=10.0,
            ),
            build_full_candidate(
                3,
                similarity_score=90.0,
                criticality_delta=-20.0,
            ),
        ],
    }

    result = service.get_recommendations(
        material_id=1,
        limit=1,
        prefer_lower_criticality=True,
    )

    service.similarity_service.get_similar_materials.assert_called_once_with(
        material_id=1,
        limit=None,
    )
    assert result["candidate_pool_count"] == 2
    assert result["returned_count"] == 1
    assert result["recommendations"][0]["material_id"] == 3
    assert result["ranking_policy"]["prefer_lower_criticality"] is True


def test_recommendations_are_neutral_by_default():
    service = MaterialRecommendationService.__new__(
        MaterialRecommendationService
    )
    service.similarity_service = Mock()
    service.similarity_service.get_similar_materials.return_value = {
        "material_id": 1,
        "mp_id": "mp-1",
        "pretty_formula": "M1",
        "formula": "M1",
        "criticality_score": 30.0,
        "similar_materials": [
            build_full_candidate(
                2,
                similarity_score=100.0,
                criticality_delta=10.0,
            ),
            build_full_candidate(
                3,
                similarity_score=90.0,
                criticality_delta=-20.0,
            ),
        ],
    }

    result = service.get_recommendations(material_id=1, limit=1)

    assert result["recommendations"][0]["material_id"] == 2
    assert result["ranking_policy"] == {
        "prefer_lower_criticality": False,
        "criticality_delta_multiplier": 0.0,
        "candidate_pool": "all_similar_materials_before_limit",
        "final_tie_breaker": "material_id_asc",
    }