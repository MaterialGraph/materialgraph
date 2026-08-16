from app.services.discovery.traversal_service import DiscoveryTraversalService


def _node(material_id):
    return {
        "material_id": material_id,
        "mp_id": f"mp-{material_id}",
        "pretty_formula": f"M{material_id}",
        "formula": f"M{material_id}",
    }


def _edge(source_id, target_id):
    return {
        "source_material_id": source_id,
        "target_material_id": target_id,
        "transition_type": "shared_element_continuity",
        "family": "phosphate",
        "shared_elements": ["O", "P"],
        "preserved_framework": ["O", "P"],
        "removed_elements": [],
        "introduced_elements": [],
        "scientific_reason": (
            f"Validated transition from {source_id} to {target_id}."
        ),
    }


def _configure_path_graph(service, monkeypatch, edges):
    material_ids = {
        edge["source_material_id"]
        for edge in edges
    } | {
        edge["target_material_id"]
        for edge in edges
    }
    graph = {
        "nodes": [_node(material_id) for material_id in sorted(material_ids)],
        "edges": edges,
    }
    calls = []

    def fake_build_graph(**kwargs):
        calls.append(kwargs)
        return graph

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        fake_build_graph,
    )
    monkeypatch.setattr(
        service.path_ranking_service,
        "rank_path",
        lambda **kwargs: {
            "scientific_usefulness_score": 75.0,
            "score_breakdown": {},
            "usefulness_reason": "Ranked test path.",
        },
    )

    return calls

def test_discovery_graph_returns_nodes_and_edges(db_session):
    service = DiscoveryTraversalService(db_session)

    result = service.get_graph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=50,
    )

    assert result["material_id"] == 5
    assert result["nodes"]
    assert result["edges"]

    edge = result["edges"][0]

    assert "source_material_id" in edge
    assert "target_material_id" in edge
    assert "transition_type" in edge
    assert "preserved_framework" in edge
    assert "removed_elements" in edge
    assert "introduced_elements" in edge
    assert "scientific_reason" in edge


def test_discovery_graph_is_deterministic(db_session):
    service = DiscoveryTraversalService(db_session)

    first = service.get_graph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=50,
    )

    second = service.get_graph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=50,
    )

    assert first["nodes"] == second["nodes"]
    assert first["edges"] == second["edges"]


def test_discovery_subgraph_filters_by_family(db_session):
    service = DiscoveryTraversalService(db_session)

    result = service.get_subgraph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        family="phosphate",
        max_hops=2,
        limit=50,
    )

    assert result["edges"]

    for edge in result["edges"]:
        assert edge["family"] == "phosphate"


def test_discovery_path_returns_path_when_available(db_session):
    service = DiscoveryTraversalService(db_session)

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
    )

    assert result["path_found"] is True
    assert result["hop_count"] <= 2
    assert len(result["materials"]) == result["hop_count"] + 1
    assert len(result["transitions"]) == result["hop_count"]


def test_discovery_path_returns_two_hop_path_and_forwards_limit(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    calls = _configure_path_graph(
        service,
        monkeypatch,
        [_edge(5, 6), _edge(6, 7)],
    )

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
    )

    assert calls[0]["max_depth"] == 2
    assert result["path_found"] is True
    assert result["hop_count"] == 2
    assert [
        material["material_id"]
        for material in result["materials"]
    ] == [5, 6, 7]
    assert [
        (
            transition["source_material_id"],
            transition["target_material_id"],
        )
        for transition in result["transitions"]
    ] == [(5, 6), (6, 7)]


def test_discovery_path_returns_direct_path_with_one_hop_limit(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    _configure_path_graph(
        service,
        monkeypatch,
        [_edge(5, 7), _edge(5, 6), _edge(6, 7)],
    )

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        max_hops=1,
    )

    assert result["path_found"] is True
    assert result["hop_count"] == 1
    assert [
        material["material_id"]
        for material in result["materials"]
    ] == [5, 7]


def test_discovery_path_rejects_target_beyond_max_hops(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    calls = _configure_path_graph(
        service,
        monkeypatch,
        [_edge(5, 6), _edge(6, 7)],
    )

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        max_hops=1,
    )

    assert calls[0]["max_depth"] == 1
    assert result["path_found"] is False
    assert result["hop_count"] is None
    assert result["materials"] == []
    assert result["transitions"] == []


def test_discovery_path_prefers_deterministic_shortest_path(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    _configure_path_graph(
        service,
        monkeypatch,
        [
            _edge(5, 6),
            _edge(5, 8),
            _edge(6, 9),
            _edge(9, 7),
            _edge(8, 7),
        ],
    )

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        max_hops=3,
    )

    assert result["path_found"] is True
    assert result["hop_count"] == 2
    assert [
        material["material_id"]
        for material in result["materials"]
    ] == [5, 8, 7]


def test_discovery_path_returns_empty_for_unreachable_target(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    _configure_path_graph(
        service,
        monkeypatch,
        [_edge(5, 6), _edge(6, 8)],
    )

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        max_hops=3,
    )

    assert result["path_found"] is False


def test_discovery_path_avoids_cycles(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    _configure_path_graph(
        service,
        monkeypatch,
        [
            _edge(5, 6),
            _edge(6, 5),
            _edge(6, 7),
        ],
    )

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        max_hops=3,
    )

    assert result["path_found"] is True
    assert result["hop_count"] == 2
    assert [
        material["material_id"]
        for material in result["materials"]
    ] == [5, 6, 7]


def test_path_reason_calibrates_element_overlap_evidence():
    service = DiscoveryTraversalService.__new__(
        DiscoveryTraversalService
    )

    reason = service._build_path_reason(
        [
            {
                "transition_type": "alkali_substitution",
                "shared_elements": ["Fe", "O", "P"],
                "preserved_framework": ["Fe", "O", "P"],
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
            }
        ]
    )

    assert "shared elemental overlap across Fe-O-P" in reason
    assert "structural preservation is not validated" in reason
    assert "while preserving Fe-O-P chemistry" not in reason

def test_path_reason_calibrates_oxide_evidence():
    service = DiscoveryTraversalService.__new__(
        DiscoveryTraversalService
    )

    reason = service._build_path_reason(
        [
            {
                "transition_type": "alkali_substitution",
                "shared_elements": ["Fe", "O"],
                "preserved_framework": ["Fe", "O"],
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
            }
        ]
    )

    assert "shared elemental overlap across Fe-O" in reason
    assert "structural preservation is not validated" in reason
    assert "while preserving Fe-O chemistry" not in reason


def test_graph_reports_requested_and_effective_max_hops(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    calls = []

    def fake_build_graph(**kwargs):
        calls.append(kwargs)

        return {
            "nodes": [],
            "edges": [],
            "adjacency": {},
        }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        fake_build_graph,
    )

    result = service.get_graph(
        material_id=5,
        max_hops=3,
        limit=50,
    )

    assert result["graph_goal"]["max_hops"] == 3
    assert result["graph_goal"]["effective_max_hops"] == 1
    assert calls[0]["max_depth"] == 1


def test_graph_preserves_requested_depth_within_builder_limit(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)
    calls = []

    def fake_build_graph(**kwargs):
        calls.append(kwargs)

        return {
            "nodes": [],
            "edges": [],
            "adjacency": {},
        }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        fake_build_graph,
    )

    result = service.get_graph(
        material_id=5,
        max_hops=1,
        limit=50,
    )

    assert result["graph_goal"]["max_hops"] == 1
    assert result["graph_goal"]["effective_max_hops"] == 1
    assert calls[0]["max_depth"] == 1


def test_missing_material_reports_effective_max_hops(
    db_session,
):
    service = DiscoveryTraversalService(db_session)

    result = service.get_graph(
        material_id=999999,
        max_hops=3,
        limit=50,
    )

    assert result["graph_goal"]["max_hops"] == 3
    assert result["graph_goal"]["effective_max_hops"] == 1
    assert result["nodes"] == []
    assert result["edges"] == []


def test_graph_limit_preserves_edge_node_closure(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)

    graph = {
        "nodes": [
            _node(5),
            _node(6),
            _node(7),
        ],
        # The first edge targets node 7, which is excluded by limit=2.
        "edges": [
            _edge(5, 7),
            _edge(5, 6),
        ],
        "adjacency": {
            5: [6, 7],
        },
    }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        lambda **kwargs: graph,
    )

    result = service.get_graph(
        material_id=5,
        max_hops=2,
        limit=2,
    )

    returned_node_ids = {
        node["material_id"]
        for node in result["nodes"]
    }

    assert returned_node_ids == {5, 6}
    assert [
        (
            edge["source_material_id"],
            edge["target_material_id"],
        )
        for edge in result["edges"]
    ] == [(5, 6)]

    assert all(
        edge["source_material_id"] in returned_node_ids
        and edge["target_material_id"] in returned_node_ids
        for edge in result["edges"]
    )


def test_graph_limit_one_returns_root_without_edges(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)

    graph = {
        "nodes": [
            _node(5),
            _node(6),
        ],
        "edges": [
            _edge(5, 6),
        ],
        "adjacency": {
            5: [6],
        },
    }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        lambda **kwargs: graph,
    )

    result = service.get_graph(
        material_id=5,
        max_hops=2,
        limit=1,
    )

    assert [
        node["material_id"]
        for node in result["nodes"]
    ] == [5]
    assert result["edges"] == []
    assert result["graph_goal"]["max_hops"] == 2
    assert result["graph_goal"]["effective_max_hops"] == 1


def test_subgraph_inherits_closed_limited_graph(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)

    graph = {
        "nodes": [
            _node(5),
            _node(6),
            _node(7),
        ],
        "edges": [
            _edge(5, 7),
            _edge(5, 6),
        ],
        "adjacency": {
            5: [6, 7],
        },
    }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        lambda **kwargs: graph,
    )

    result = service.get_subgraph(
        material_id=5,
        family="phosphate",
        max_hops=2,
        limit=2,
    )

    returned_node_ids = {
        node["material_id"]
        for node in result["nodes"]
    }

    assert returned_node_ids == {5, 6}
    assert all(
        edge["source_material_id"] in returned_node_ids
        and edge["target_material_id"] in returned_node_ids
        for edge in result["edges"]
    )
    assert result["subgraph_metadata"]["node_count"] == 2
    assert result["subgraph_metadata"]["edge_count"] == 1


def test_subgraph_filters_before_applying_result_limit(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)

    nonmatching_edge = {
        **_edge(5, 6),
        "family": "oxide",
    }
    matching_edge = {
        **_edge(5, 7),
        "family": "phosphate",
    }

    graph = {
        "nodes": [
            _node(5),
            _node(6),
            _node(7),
        ],
        "edges": [
            nonmatching_edge,
            matching_edge,
        ],
        "adjacency": {
            5: [6, 7],
        },
    }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        lambda **kwargs: graph,
    )

    result = service.get_subgraph(
        material_id=5,
        family="phosphate",
        max_hops=2,
        limit=2,
    )

    returned_node_ids = {
        node["material_id"]
        for node in result["nodes"]
    }

    assert returned_node_ids == {5, 7}
    assert [
        (
            edge["source_material_id"],
            edge["target_material_id"],
        )
        for edge in result["edges"]
    ] == [(5, 7)]

    assert result["subgraph_metadata"]["node_count"] == 2
    assert result["subgraph_metadata"]["edge_count"] == 1

    assert all(
        edge["source_material_id"] in returned_node_ids
        and edge["target_material_id"] in returned_node_ids
        for edge in result["edges"]
    )

    assert result["graph_goal"]["max_hops"] == 2
    assert result["graph_goal"]["effective_max_hops"] == 1


def test_subgraph_metadata_describes_limited_response(
    db_session,
    monkeypatch,
):
    service = DiscoveryTraversalService(db_session)

    graph = {
        "nodes": [
            _node(5),
            _node(6),
            _node(7),
        ],
        "edges": [
            _edge(5, 6),
            _edge(5, 7),
        ],
        "adjacency": {
            5: [6, 7],
        },
    }

    monkeypatch.setattr(
        service.graph_builder,
        "build_graph",
        lambda **kwargs: graph,
    )

    result = service.get_subgraph(
        material_id=5,
        family="phosphate",
        max_hops=2,
        limit=2,
    )

    assert result["subgraph_metadata"]["node_count"] == len(
        result["nodes"]
    )
    assert result["subgraph_metadata"]["edge_count"] == len(
        result["edges"]
    )