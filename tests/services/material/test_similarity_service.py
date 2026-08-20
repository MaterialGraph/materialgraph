from unittest.mock import Mock

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


def _neighbor(
    material_id: int,
    criticality_test_score: int = 1,
) -> dict:
    return {
        "material_id": material_id,
        "mp_id": f"mp-{material_id}",
        "pretty_formula": f"M{material_id}",
        "formula": f"M{material_id}",
        "material_type": "test",
        "is_stable": True,
        "energy_above_hull": 0.0,
        "shared_element_count": criticality_test_score,
        "shared_application_count": 0,
        "relationship_types": ["SHARED_ELEMENT"],
    }


def _neighbor_response(neighbors: list[dict]) -> dict:
    return {
        "material_id": 1,
        "mp_id": "mp-1",
        "pretty_formula": "M1",
        "formula": "M1",
        "material_type": "test",
        "is_stable": True,
        "energy_above_hull": 0.0,
        "neighbors": neighbors,
    }


def test_similarity_bulk_loads_criticality_once() -> None:
    service = MaterialSimilarityService.__new__(
        MaterialSimilarityService
    )
    service.neighbor_service = Mock()
    service.criticality_service = Mock()

    service.neighbor_service.get_neighbors.return_value = (
        _neighbor_response(
            [
                _neighbor(2, 3),
                _neighbor(3, 2),
                _neighbor(4, 1),
            ]
        )
    )
    service.criticality_service.get_material_criticality_bulk.return_value = {
        1: {"criticality_score": 30.0},
        2: {"criticality_score": 20.0},
        3: {"criticality_score": None},
        4: {"criticality_score": 40.0},
    }

    result = service.get_similar_materials(
        material_id=1,
        limit=2,
    )

    service.criticality_service.get_material_criticality_bulk.assert_called_once_with(
        material_ids=[1, 2, 3, 4]
    )
    service.criticality_service.get_material_criticality.assert_not_called()

    assert result["criticality_score"] == 30.0
    assert [
        item["material_id"]
        for item in result["similar_materials"]
    ] == [2, 3]

    candidate_by_id = {
        item["material_id"]: item
        for item in result["similar_materials"]
    }

    assert candidate_by_id[2]["criticality_score"] == 20.0
    assert candidate_by_id[2]["criticality_delta"] == -10.0
    assert (
        candidate_by_id[2]["criticality_direction"]
        == "LOWER_CRITICALITY"
    )

    assert candidate_by_id[3]["criticality_score"] is None
    assert candidate_by_id[3]["criticality_delta"] is None
    assert candidate_by_id[3]["criticality_direction"] == "UNKNOWN"
    assert result["candidate_pool_count"] == 3
    assert result["returned_count"] == 2
    assert result["ranking_policy"]["candidate_pool"] == (
        "all_structured_neighbors_before_limit"
    )


def test_similarity_scores_complete_neighbor_pool_before_limit() -> None:
    service = MaterialSimilarityService.__new__(MaterialSimilarityService)
    service.neighbor_service = Mock()
    service.criticality_service = Mock()

    service.neighbor_service.get_neighbors.return_value = _neighbor_response(
        [_neighbor(2, 1), _neighbor(3, 3)]
    )
    service.criticality_service.get_material_criticality_bulk.return_value = {
        1: {"criticality_score": 30.0},
        2: {"criticality_score": 30.0},
        3: {"criticality_score": 30.0},
    }

    result = service.get_similar_materials(material_id=1, limit=1)

    assert result["candidate_pool_count"] == 2
    assert result["returned_count"] == 1
    assert result["similar_materials"][0]["material_id"] == 3
    service.criticality_service.get_material_criticality_bulk.assert_called_once_with(
        material_ids=[1, 2, 3]
    )


def test_missing_source_skips_bulk_criticality_lookup() -> None:
    service = MaterialSimilarityService.__new__(
        MaterialSimilarityService
    )
    service.neighbor_service = Mock()
    service.criticality_service = Mock()

    service.neighbor_service.get_neighbors.return_value = {
        "material_id": 999,
        "mp_id": None,
        "neighbors": [],
    }

    result = service.get_similar_materials(material_id=999)

    assert result == service._empty_similarity_response(999)
    service.criticality_service.get_material_criticality_bulk.assert_not_called()
    service.criticality_service.get_material_criticality.assert_not_called()