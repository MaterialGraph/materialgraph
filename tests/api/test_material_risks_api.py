from app.services.material.risk_service import MaterialRiskService


def test_get_material_risk(client):
    response = client.get("/api/v1/material-risks/6")

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 6
    assert data["material_risk_score"] >= 0
    assert len(data["element_risks"]) > 0
    assert data["evidence_basis"] == "latest_element_risk_profile"
    assert data["aggregation_method"] == (
        "mean_available_dimensions_then_equal_mean_calculable_elements"
    )
    assert data["selected_profile_ids"]
    assert data["selected_profile_years"]
    assert data["selected_profile_sources"]
    assert all(
        item["risk_profile_id"] in data["selected_profile_ids"]
        and item["risk_year"] in data["selected_profile_years"]
        and item["risk_source"] in data["selected_profile_sources"]
        for item in data["element_risks"]
    )


def test_get_material_risk_not_found(client):
    response = client.get("/api/v1/material-risks/999999")

    assert response.status_code == 404


def test_get_material_risk_preserves_unknown_as_null(
    client,
    monkeypatch,
):
    def fake_get_material_risk(self, material_id):
        return {
            "material_id": material_id,
            "formula": "X",
            "pretty_formula": "X",
            "material_risk_score": None,
            "evidence_basis": "latest_element_risk_profile",
            "shared_evidence_dimensions": [
                "supply_risk_score",
                "geopolitical_risk_score",
                "toxicity_score",
            ],
            "risk_evidence_dimensions": [
                "supply_risk_score",
                "geopolitical_risk_score",
                "toxicity_score",
            ],
            "aggregation_method": (
                "mean_available_dimensions_then_equal_mean_calculable_elements"
            ),
            "selected_profile_ids": [],
            "selected_profile_years": [],
            "selected_profile_sources": [],
            "risk_profile_coverage": 0.0,
            "risk_complete_profile_coverage": 0.0,
            "risk_dimension_coverage": 0.0,
            "risk_evidence_complete": False,
            "element_risks": [],
        }

    monkeypatch.setattr(
        MaterialRiskService,
        "get_material_risk",
        fake_get_material_risk,
    )

    response = client.get("/api/v1/material-risks/123456")

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 123456
    assert data["material_risk_score"] is None
    assert data["risk_profile_coverage"] == 0.0
    assert data["risk_complete_profile_coverage"] == 0.0
    assert data["risk_dimension_coverage"] == 0.0
    assert data["risk_evidence_complete"] is False