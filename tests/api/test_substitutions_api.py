def test_substitution_analysis_api(client):
    response = client.post(
        "/api/v1/substitutions/analyze",
        json={
            "material_id": 6,
            "top_n": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["source_material_id"] == 6
    assert len(data["substitutes"]) <= 5
    assert len(data["substitutes"]) > 0
    assert data["source_selected_risk_profile_ids"]
    assert data["source_selected_risk_profile_years"]
    assert data["source_selected_risk_profile_sources"]
    assert "removed_elements" in data["substitutes"][0]
    assert "stability_band" in data["substitutes"][0]
    assert "stability_evidence_basis" in data["substitutes"][0]
    assert "stability_evidence_complete" in data["substitutes"][0]
    assert "stability_source_consistency" in data["substitutes"][0]
    assert "stability_rank_contribution" in data["substitutes"][0]
    assert "explanation" in data["substitutes"][0]
    assert "selected_risk_profile_ids" in data["substitutes"][0]
    assert "selected_risk_profile_years" in data["substitutes"][0]
    assert "selected_risk_profile_sources" in data["substitutes"][0]


def test_substitution_analysis_api_not_found(client):
    response = client.post(
        "/api/v1/substitutions/analyze",
        json={
            "material_id": 999999,
            "top_n": 5,
        },
    )

    assert response.status_code == 404