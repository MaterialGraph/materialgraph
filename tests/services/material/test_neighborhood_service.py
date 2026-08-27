from unittest.mock import Mock, call

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


def test_limit_bounds_neighbor_expansion() -> None:
    service = _service()

    result = service.get_neighborhood(
        material_id=1,
        depth=2,
        limit=2,
    )

    assert {
        node["material_id"]
        for node in result["nodes"]
    } == {1, 2}

    assert service.neighbor_service.get_neighbors.call_args_list == [
        call(1),
        call(2),
    ]


def test_limit_one_does_not_expand_descendants() -> None:
    service = _service()

    result = service.get_neighborhood(
        material_id=1,
        depth=2,
        limit=1,
    )

    assert [node["material_id"] for node in result["nodes"]] == [1]
    assert service.neighbor_service.get_neighbors.call_count == 1
    service.neighbor_service.get_neighbors.assert_called_once_with(1)


def test_bounded_traversal_is_deterministic() -> None:
    first_service = _service()
    second_service = _service()

    first = first_service.get_neighborhood(
        material_id=1,
        depth=2,
        limit=3,
    )
    second = second_service.get_neighborhood(
        material_id=1,
        depth=2,
        limit=3,
    )

    assert first["nodes"] == second["nodes"]
    assert first["edges"] == second["edges"]


def test_permuted_ties_preserve_membership_expansion_and_edge_order() -> None:
    def build_service(root_neighbor_ids: list[int]) -> MaterialNeighborhoodService:
        service = MaterialNeighborhoodService(Mock())
        responses = {
            1: _response(
                1,
                [_neighbor(neighbor_id, 100) for neighbor_id in root_neighbor_ids],
            ),
            2: _response(2, []),
            3: _response(3, []),
        }
        service.neighbor_service.get_neighbors = Mock(
            side_effect=lambda material_id: responses[material_id]
        )
        return service

    first_service = build_service([3, 2])
    second_service = build_service([2, 3])

    first = first_service.get_neighborhood(material_id=1, depth=2, limit=3)
    second = second_service.get_neighborhood(material_id=1, depth=2, limit=3)

    assert first == second
    assert [node["material_id"] for node in first["nodes"]] == [1, 2, 3]
    assert [
        (edge["source_material_id"], edge["target_material_id"])
        for edge in first["edges"]
    ] == [(1, 2), (1, 3)]
    assert first_service.neighbor_service.get_neighbors.call_args_list == [
        call(1),
        call(2),
        call(3),
    ]
    assert second_service.neighbor_service.get_neighbors.call_args_list == [
        call(1),
        call(2),
        call(3),
    ]


def test_depth_remains_maximum_expansion_depth() -> None:
    service = _service()

    result = service.get_neighborhood(
        material_id=1,
        depth=1,
        limit=10,
    )

    assert {
        node["material_id"]
        for node in result["nodes"]
    } == {1, 2, 3}

    assert service.neighbor_service.get_neighbors.call_count == 1
    service.neighbor_service.get_neighbors.assert_called_once_with(1)