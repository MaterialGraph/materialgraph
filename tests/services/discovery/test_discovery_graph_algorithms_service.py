from app.services.discovery.graph_algorithms_service import (
    DiscoveryGraphAlgorithmsService,
)

def test_bfs_returns_traversal_order(db_session):
    service = DiscoveryGraphAlgorithmsService(db_session)

    result = service.bfs(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert result["algorithm"] == "bfs"
    assert result["start_material_id"] == 5
    assert result["visited_count"] >= 1
    assert result["traversal_order"][0] == 5


def test_dfs_returns_traversal_order(db_session):
    service = DiscoveryGraphAlgorithmsService(db_session)

    result = service.dfs(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert result["algorithm"] == "dfs"
    assert result["start_material_id"] == 5
    assert result["visited_count"] >= 1
    assert result["traversal_order"][0] == 5


def test_shortest_path_returns_response(db_session):
    service = DiscoveryGraphAlgorithmsService(db_session)

    result = service.shortest_path(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert result["algorithm"] == "shortest_path"
    assert result["start_material_id"] == 5
    assert result["target_material_id"] == 7
    assert "path_found" in result
    assert "path" in result

def test_weighted_shortest_path_returns_response(db_session):
    service = DiscoveryGraphAlgorithmsService(db_session)

    result = service.weighted_shortest_path(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    assert result["algorithm"] == "weighted_shortest_path"
    assert result["start_material_id"] == 5
    assert result["target_material_id"] == 7
    assert "path_found" in result
    assert "path" in result
    assert "path_cost" in result


def test_weighted_shortest_path_preserves_shallower_state(
    db_session,
    monkeypatch,
):
    service = DiscoveryGraphAlgorithmsService(db_session)
    graph = {
        "nodes": [
            {"material_id": material_id}
            for material_id in (1, 2, 3, 4, 5)
        ],
        "edges": [
            {
                "source_material_id": 1,
                "target_material_id": 2,
                "test_cost": 1.0,
            },
            {
                "source_material_id": 2,
                "target_material_id": 4,
                "test_cost": 1.0,
            },
            {
                "source_material_id": 1,
                "target_material_id": 4,
                "test_cost": 5.0,
            },
            {
                "source_material_id": 4,
                "target_material_id": 5,
                "test_cost": 1.0,
            },
        ],
    }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        lambda **_: graph,
    )
    monkeypatch.setattr(
        service,
        "_calculate_edge_cost",
        lambda edge, target_node: edge["test_cost"],
    )

    result = service.weighted_shortest_path(
        start_material_id=1,
        target_material_id=5,
        max_depth=2,
    )

    assert result["path_found"] is True
    assert result["path"] == [1, 4, 5]
    assert result["hop_count"] == 2
    assert result["path_cost"] == 6.0
    assert result["hop_count"] <= 2