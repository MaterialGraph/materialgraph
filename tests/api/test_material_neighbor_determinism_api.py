from app.services.material.neighbor_service import MaterialNeighborService


def _neighbor(material_id: int) -> dict:
    return {
        "material_id": material_id,
        "mp_id": f"mp-{material_id}",
        "pretty_formula": f"M{material_id}",
        "formula": f"M{material_id}",
        "material_type": "test",
        "is_stable": True,
        "energy_above_hull": 0.0,
        "shared_element_count": 1,
        "shared_application_count": 0,
        "relationship_types": ["SHARED_ELEMENT"],
        "neighbor_score": 2,
    }


def test_neighbor_api_resolves_permuted_ties_by_material_id(
    client,
    monkeypatch,
) -> None:
    candidate_orders = iter(
        [
            [_neighbor(3), _neighbor(2)],
            [_neighbor(2), _neighbor(3)],
        ]
    )

    def build_neighbors(self, neighbor_scores, materials_by_id):
        return next(candidate_orders)

    monkeypatch.setattr(
        MaterialNeighborService,
        "_build_neighbors",
        build_neighbors,
    )

    first = client.get("/api/v1/materials/1/neighbors")
    second = client.get("/api/v1/materials/1/neighbors")

    assert first.status_code == 200
    assert second.status_code == 200
    assert [
        item["material_id"]
        for item in first.json()["neighbors"]
    ] == [2, 3]
    assert first.json()["neighbors"] == second.json()["neighbors"]