def test_get_material_neighbors(client):
    response = client.get("/api/v1/materials/1/neighbors")

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 1
    assert "mp_id" in data
    assert "pretty_formula" in data
    assert "formula" in data
    assert "neighbors" in data
    assert isinstance(data["neighbors"], list)


def test_get_material_neighbors_not_found(client):
    response = client.get("/api/v1/materials/999999/neighbors")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"


def test_get_material_criticality_exposes_composition_evidence(client):
    response = client.get("/api/v1/materials/5/criticality")

    assert response.status_code == 200

    data = response.json()

    assert data["composition_evidence_status"] in {
        "complete",
        "partial",
        "unavailable",
    }
    assert 0.0 <= data["composition_fraction_coverage"] <= 1.0
    assert isinstance(data["composition_evidence_complete"], bool)
    assert isinstance(data["known_composition_element_count"], int)
    assert isinstance(data["unknown_composition_element_count"], int)
    assert isinstance(data["unknown_composition_elements"], list)
    assert all(
        element["fraction_known"] is (element["fraction"] is not None)
        for element in data["elements"]
    )