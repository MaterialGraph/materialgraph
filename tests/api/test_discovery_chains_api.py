def test_get_discovery_chains(client):
    response = client.get(
        "/api/v1/materials/5/discovery/chains"
        "?avoid_element=Li&prefer_element=Na&max_hops=2&limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert "base_formula" in data
    assert "discovery_goal" in data
    assert "search_metadata" in data
    assert "chains" in data

    assert data["discovery_goal"]["avoid_element"] == "Li"
    assert data["discovery_goal"]["prefer_element"] == "Na"
    assert data["discovery_goal"]["max_hops"] == 2
    assert data["discovery_goal"]["limit"] == 5
    assert data["search_metadata"]["requested_result_limit"] == 5
    assert data["search_metadata"]["search_state_budget"] == 200
    assert data["search_metadata"][
        "scientific_completeness_guaranteed"
    ] is False
    assert data["search_metadata"]["returned_chain_count"] == len(
        data["chains"]
    )

    for chain in data["chains"]:
        assert "materials" in chain
        assert "transitions" in chain
        assert "chain_reason" in chain
        assert chain["hop_count"] <= 2


def test_discovery_chains_returns_404_for_missing_material(client):
    response = client.get(
        "/api/v1/materials/999999/discovery/chains"
        "?max_hops=2&limit=5"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}


def test_objective_chains_returns_404_for_missing_material(client):
    response = client.post(
        "/api/v1/materials/999999/discovery/objective/chains",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}