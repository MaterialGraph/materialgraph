from app.utils.chemical_formula import extract_elements


def test_research_objective_exploration_api(client):
    response = client.post(
        "/api/v1/materials/5/discovery/objective/explore",
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
            },
            "mode": "balanced",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert data["mode"] == "balanced"
    assert data["constraint_policy"] == {
        "avoid_elements": "soft_penalty",
        "prefer_elements": "soft_bonus",
        "hard_rejection_scope": "none",
    }
    assert "ranked_candidates" in data
    assert "chains" in data
    assert "warnings" in data


def test_research_objective_exploration_returns_404_for_missing_material(
    client,
):
    response = client.post(
        "/api/v1/materials/999999/discovery/objective/explore",
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
            },
            "mode": "balanced",
            "limit": 5,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Material not found"}


def test_strict_research_objective_exploration_enforces_hard_avoidance(client):
    response = client.post(
        "/api/v1/materials/5/discovery/objective/explore",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": [],
                "target_family": None,
                "max_hops": 2,
                "limit": 20,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            },
            "mode": "strict",
            "limit": 20,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["constraint_policy"] == {
        "avoid_elements": "hard_rejection",
        "prefer_elements": "soft_bonus",
        "hard_rejection_scope": "all_non_root_chain_materials",
    }
    assert all(
        "Li" not in extract_elements(candidate["formula"] or "")
        for candidate in data["ranked_candidates"]
    )
    assert all(
        "Li"
        not in extract_elements(
            material.get("formula")
            or material.get("pretty_formula")
            or ""
        )
        for chain in data["chains"]
        for material in chain["materials"][1:]
    )