from unittest.mock import Mock

from app.services.material.neighborhood_service import (
    MaterialNeighborhoodService,
)


def _neighbor(
    material_id: int,
    score: int,
) -> dict:
    return {
        "material_id": material_id,
        "mp_id": f"mp-{material_id}",
        "pretty_formula": f"M{material_id}",
        "formula": f"M{material_id}",
        "material_type": "test",
        "is_stable": True,
        "energy_above_hull": 0.0,
        "relationship_types": ["SHARED_ELEMENT"],
        "shared_element_count": 1,
        "shared_application_count": 0,
        "neighbor_score": score,
    }


def _response(
    material_id: int,
    neighbors: list[dict],
) -> dict:
    return {
        "material_id": material_id,
        "mp_id": f"mp-{material_id}",
        "pretty_formula": f"M{material_id}",
        "formula": f"M{material_id}",
        "material_type": "test",
        "is_stable": True,
        "energy_above_hull": 0.0,
        "neighbors": neighbors,
    }


def _service() -> MaterialNeighborhoodService:
    service = MaterialNeighborhoodService(Mock())

    responses = {
        1: _response(
            1,
            [
                _neighbor(2, 100),
                _neighbor(3, 90),
            ],
        ),
        2: _response(
            2,
            [
                _neighbor(4, 10),
            ],
        ),
        # This high-scoring edge would be returned before the fix even when
        # material 3 is excluded by the node limit.
        3: _response(
            3,
            [
                _neighbor(1, 1_000),
            ],
        ),
        4: _response(4, []),
    }

    service.neighbor_service.get_neighbors = Mock(
        side_effect=lambda material_id: responses[material_id]
    )

    return service


def test_limited_neighborhood_contains_no_dangling_edges() -> None:
    result = _service().get_neighborhood(
        material_id=1,
        depth=2,
        limit=2,
    )

    returned_node_ids = {
        node["material_id"]
        for node in result["nodes"]
    }

    assert returned_node_ids == {1, 2}
    assert all(
        edge["source_material_id"] in returned_node_ids
        and edge["target_material_id"] in returned_node_ids
        for edge in result["edges"]
    )


def test_limit_one_returns_only_root_and_no_edges() -> None:
    result = _service().get_neighborhood(
        material_id=1,
        depth=2,
        limit=1,
    )

    assert [node["material_id"] for node in result["nodes"]] == [1]
    assert result["edges"] == []
    assert result["node_count"] == 1
    assert result["edge_count"] == 0


def test_large_limit_retains_all_eligible_edges() -> None:
    result = _service().get_neighborhood(
        material_id=1,
        depth=2,
        limit=10,
    )

    returned_node_ids = {
        node["material_id"]
        for node in result["nodes"]
    }

    assert returned_node_ids == {1, 2, 3, 4}
    assert len(result["edges"]) == 4
    assert all(
        edge["source_material_id"] in returned_node_ids
        and edge["target_material_id"] in returned_node_ids
        for edge in result["edges"]
    )


def test_counts_match_returned_collections() -> None:
    result = _service().get_neighborhood(
        material_id=1,
        depth=2,
        limit=2,
    )

    assert result["node_count"] == len(result["nodes"])
    assert result["edge_count"] == len(result["edges"])