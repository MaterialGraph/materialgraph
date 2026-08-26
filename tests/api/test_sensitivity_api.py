def test_sensitivity_analysis_api(client):
    response = client.post(
        "/api/v1/sensitivity/material",
        json={
            "material_id": 6,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 6
    assert data["baseline_score"] >= 0
    assert data["baseline_material_risk_score"] >= 0
    assert len(data["scenarios"]) == 4
    assert all(
        "adjusted_material_risk_score" in scenario
        for scenario in data["scenarios"]
    )
    assert all(
        "material_risk_delta" in scenario
        for scenario in data["scenarios"]
    )


def test_sensitivity_analysis_api_not_found(client):
    response = client.post(
        "/api/v1/sensitivity/material",
        json={
            "material_id": 999999,
        },
    )

    assert response.status_code == 404