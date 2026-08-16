import pytest


DISCOVERY_ROUTES = [
    "/api/v1/materials/5/discovery/chains",
    "/api/v1/materials/5/discovery/graph",
    "/api/v1/materials/5/discovery/path",
]


@pytest.mark.parametrize("route", DISCOVERY_ROUTES)
@pytest.mark.parametrize("parameter", ["avoid_element", "prefer_element"])
@pytest.mark.parametrize("invalid_value", ["", "Lithium"])
def test_equivalent_discovery_routes_reject_invalid_element_length(
    client,
    route,
    parameter,
    invalid_value,
):
    params = {parameter: invalid_value}

    if route.endswith("/path"):
        params["target_material_id"] = 10

    response = client.get(route, params=params)

    assert response.status_code == 422



def test_discovery_graph_reports_avoid_element_validation_location(client):
    response = client.get(
        "/api/v1/materials/5/discovery/graph",
        params={"avoid_element": "Lithium"},
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(
        error["loc"] == ["query", "avoid_element"]
        for error in errors
    )


@pytest.mark.parametrize(
    "route",
    [
        "/api/v1/materials/5/discovery/graph",
        "/api/v1/materials/5/discovery/subgraph",
    ],
)
@pytest.mark.parametrize("invalid_limit", [-1, 0, 201])
def test_discovery_analytical_routes_reject_invalid_limits(
    client,
    route,
    invalid_limit,
):
    response = client.get(route, params={"limit": invalid_limit})

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(
        error["loc"] == ["query", "limit"]
        for error in errors
    )



@pytest.mark.parametrize(
    ("endpoint", "expected_algorithm"),
    [
        (
            "/api/v1/materials/5/discovery/communities/connected",
            "connected_components",
        ),
        (
            "/api/v1/materials/5/discovery/communities/modularity",
            "greedy_modularity_communities",
        ),
    ],
)
def test_community_endpoints_return_validated_response(
    client,
    endpoint,
    expected_algorithm,
):
    response = client.get(endpoint)

    assert response.status_code == 200

    payload = response.json()
    assert payload["algorithm"] == expected_algorithm
    assert payload["community_count"] == len(payload["communities"])

    for community in payload["communities"]:
        assert community["size"] == len(community["material_ids"])
        assert community["size"] == len(community["materials"])
        assert community["community_features"]["size"] == community["size"]
        assert (
            community["community_features"]["hub_material_id"]
            == community["hub_material_id"]
        )


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/materials/{material_id}/discovery/communities/connected",
        "/api/v1/materials/{material_id}/discovery/communities/modularity",
    ],
)
def test_community_routes_declare_validated_response_model(client, path):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    operation = response.json()["paths"][path]["get"]
    success_schema = operation["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    assert success_schema == {
        "$ref": "#/components/schemas/DiscoveryCommunityResponse"
    }
