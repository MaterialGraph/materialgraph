from app.services.discovery.graph_builder import DiscoveryGraphBuilder

def test_discovery_graph_builder_returns_adjacency(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    adjacency = builder.build_adjacency(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert isinstance(adjacency, dict)
    assert 5 in adjacency
    assert isinstance(adjacency[5], list)
    assert adjacency[5]
    assert all(
        candidate.get("validated_transition")
        for candidate in adjacency[5]
    )


def test_discovery_graph_builder_respects_depth_zero(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    adjacency = builder.build_adjacency(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=0,
    )

    assert adjacency == {}

def test_discovery_graph_nodes_include_quality_metadata(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    result = builder.build_graph(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    node = result["nodes"][0]

    assert "stability_score" in node
    assert "energy_above_hull" in node
    assert "criticality_score" in node
    assert "risk_score" in node
    assert "quality_score" in node

def test_discovery_graph_edges_include_edge_intelligence(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    result = builder.build_graph(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    assert result["edges"]

    edge = result["edges"][0]

    assert "scientific_plausibility" in edge
    assert "edge_score" in edge
    assert edge["plausibility_basis"] == "internal_composition_heuristic"
    assert edge["substitution_mechanism_validated"] is False
    assert isinstance(edge["scientific_plausibility"], float)
    assert isinstance(edge["edge_score"], float)

def test_discovery_graph_nodes_include_canonical_elements(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    result = builder.build_graph(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    nodes_by_id = {
        node["material_id"]: node
        for node in result["nodes"]
    }

    assert nodes_by_id[5]["elements"] == ["Fe", "Li", "O", "P"]

    if 6 in nodes_by_id:
        assert nodes_by_id[6]["elements"] == ["Fe", "Na", "O", "P"]


def test_build_adjacency_excludes_invalid_transitions(
    db_session,
    monkeypatch,
):
    builder = DiscoveryGraphBuilder(db_session)

    monkeypatch.setattr(
        builder,
        "_get_candidates",
        lambda **kwargs: [
            {
                "material_id": 6,
                "mp_id": "mp-valid",
                "pretty_formula": "NaFePO4",
                "formula": "NaFePO4",
            },
            {
                "material_id": 7,
                "mp_id": "mp-invalid",
                "pretty_formula": "CoO",
                "formula": "CoO",
            },
        ],
    )
    monkeypatch.setattr(
        builder,
        "_build_transition",
        lambda **kwargs: (
            {
                "transition_type": "alkali_substitution",
                "reason": "validated",
            }
            if kwargs["to_candidate"]["material_id"] == 6
            else None
        ),
    )

    adjacency = builder.build_adjacency(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    assert [item["material_id"] for item in adjacency[5]] == [6]
    assert adjacency[5][0]["validated_transition"]["reason"] == "validated"


def test_build_graph_excludes_nodes_for_invalid_transitions(
    db_session,
    monkeypatch,
):
    builder = DiscoveryGraphBuilder(db_session)

    monkeypatch.setattr(
        builder,
        "_get_candidates",
        lambda **kwargs: [
            {
                "material_id": 6,
                "mp_id": "mp-valid",
                "pretty_formula": "NaFePO4",
                "formula": "NaFePO4",
            },
            {
                "material_id": 7,
                "mp_id": "mp-invalid",
                "pretty_formula": "CoO",
                "formula": "CoO",
            },
        ],
    )
    monkeypatch.setattr(
        builder,
        "_build_transition",
        lambda **kwargs: (
            {
                "transition_type": "alkali_substitution",
                "reason": "validated",
            }
            if kwargs["to_candidate"]["material_id"] == 6
            else None
        ),
    )

    result = builder.build_graph(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    returned_node_ids = {
        node["material_id"]
        for node in result["nodes"]
    }
    connected_node_ids = {
        endpoint
        for edge in result["edges"]
        for endpoint in (
            edge["source_material_id"],
            edge["target_material_id"],
        )
    }

    assert returned_node_ids == {5, 6}
    assert 7 not in returned_node_ids
    assert [edge["target_material_id"] for edge in result["edges"]] == [6]
    assert result["adjacency"] == {5: [6]}
    assert all(
        node_id == 5 or node_id in connected_node_ids
        for node_id in returned_node_ids
    )