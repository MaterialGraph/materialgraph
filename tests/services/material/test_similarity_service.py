import pytest

from app.services.material.similarity_service import MaterialSimilarityService


@pytest.fixture
def service() -> MaterialSimilarityService:
    return MaterialSimilarityService.__new__(MaterialSimilarityService)


@pytest.mark.parametrize(
    (
        "source_criticality_score",
        "neighbor_criticality_score",
        "expected_delta",
    ),
    [
        (32.0, 20.0, -12.0),
        (32.0, 40.0, 8.0),
        (32.0, 32.0, 0.0),
        (32.123, 40.126, 8.0),
        (None, 20.0, None),
        (32.0, None, None),
        (None, None, None),
    ],
)
def test_calculate_criticality_delta(
    service,
    source_criticality_score,
    neighbor_criticality_score,
    expected_delta,
):
    result = service._calculate_criticality_delta(
        source_criticality_score=source_criticality_score,
        neighbor_criticality_score=neighbor_criticality_score,
    )

    assert result == expected_delta


@pytest.mark.parametrize(
    ("criticality_delta", "expected_direction"),
    [
        (-12.0, "LOWER_CRITICALITY"),
        (8.0, "HIGHER_CRITICALITY"),
        (0.0, "SAME_CRITICALITY"),
        (None, "UNKNOWN"),
    ],
)
def test_criticality_direction(
    service,
    criticality_delta,
    expected_direction,
):
    assert service._criticality_direction(criticality_delta) == expected_direction


def test_similarity_ranking_prefers_known_criticality_over_unknown(
    service,
):
    known = {
        "material_id": 2,
        "similarity_score": 100.0,
        "criticality_delta": 5.0,
    }
    unknown = {
        "material_id": 1,
        "similarity_score": 100.0,
        "criticality_delta": None,
    }

    ranked = sorted(
        [unknown, known],
        key=service._similarity_ranking_key,
        reverse=True,
    )

    assert [item["material_id"] for item in ranked] == [2, 1]


def test_similarity_ranking_prefers_smaller_known_delta(
    service,
):
    closer = {
        "material_id": 2,
        "similarity_score": 100.0,
        "criticality_delta": -2.0,
    }
    farther = {
        "material_id": 1,
        "similarity_score": 100.0,
        "criticality_delta": 5.0,
    }

    ranked = sorted(
        [farther, closer],
        key=service._similarity_ranking_key,
        reverse=True,
    )

    assert [item["material_id"] for item in ranked] == [2, 1]


def test_similarity_ranking_is_deterministic_for_complete_tie(
    service,
):
    higher_id = {
        "material_id": 20,
        "similarity_score": 100.0,
        "criticality_delta": -2.0,
    }
    lower_id = {
        "material_id": 10,
        "similarity_score": 100.0,
        "criticality_delta": -2.0,
    }

    ranked = sorted(
        [higher_id, lower_id],
        key=service._similarity_ranking_key,
        reverse=True,
    )

    assert [item["material_id"] for item in ranked] == [10, 20]