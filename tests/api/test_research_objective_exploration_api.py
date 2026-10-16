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

def _coverage_request(mode: str) -> dict:
    return {
        "objective": {
            "avoid_elements": ["Li", "Co"],
            "prefer_elements": ["Na", "K"],
            "preserve_elements": ["Fe", "P", "O"],
            "target_family": "phosphate",
            "max_hops": 2,
            "limit": 5,
            "prefer_lower_criticality": True,
            "require_stable_materials": False,
        },
        "mode": mode,
        "limit": 5,
    }


def test_objective_explore_returns_consistent_objective_coverage(client):
    from app.schemas.research_objective_exploration import ObjectiveCoverage

    response = client.post(
        "/api/v1/materials/5/discovery/objective/explore",
        json=_coverage_request("balanced"),
    )
    assert response.status_code == 200
    data = response.json()
    coverage = data["objective_coverage"]
    ObjectiveCoverage.model_validate(coverage)

    assert coverage["contract_version"] == "1"
    assert coverage["scope"] == "returned_results_only"
    assert coverage["returned_ranked_material_count"] == len(
        data["ranked_candidates"]
    )
    assert coverage["returned_chain_count"] == len(data["chains"])
    assert coverage["ranked_material_pool_count"] >= len(
        data["ranked_candidates"]
    )
    assert [e["element"] for e in coverage["preferred_elements"]] == ["Na", "K"]
    assert len(coverage["chain_avoidance"]) == len(data["chains"])

    ranked_ids = {item["material_id"] for item in data["ranked_candidates"]}
    for entry in coverage["preferred_elements"]:
        assert entry["evaluated_count"] + entry["not_evaluated_count"] == (
            entry["total_count"]
        )
        assert entry["total_count"] == len(ranked_ids)
    for entry in coverage["avoided_elements_in_returned_chains"]:
        assert (
            entry["containing_chain_count"]
            + (entry["evaluated_chain_count"] - entry["containing_chain_count"])
            + entry["not_evaluated_chain_count"]
        ) == entry["total_chain_count"]

    # Independent check of Li chain membership from the same response.
    expected_li_positions = [
        position
        for position, chain in enumerate(data["chains"], start=1)
        if any(
            "Li" in extract_elements(material["formula"])
            for material in chain["materials"][1:]
        )
    ]
    li = next(
        entry for entry in coverage["avoided_elements_in_returned_chains"]
        if entry["element"] == "Li"
    )
    assert li["chain_positions"] == expected_li_positions


def test_strict_objective_coverage_reports_no_avoided_elements_in_chains(client):
    response = client.post(
        "/api/v1/materials/5/discovery/objective/explore",
        json=_coverage_request("strict"),
    )
    assert response.status_code == 200
    coverage = response.json()["objective_coverage"]
    assert coverage["mode"] == "strict"
    for entry in coverage["avoided_elements_in_returned_chains"]:
        assert entry["containing_chain_count"] == 0
