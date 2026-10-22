"""Same-formula records are distinguishable (Release 1, R1-6).

Objective ranked candidates carry the MP identifier of the chain material
they were ranked from, so records sharing a formula (for example two NaFePO4
entries) are not presented identically.
"""


def test_ranked_candidates_carry_the_source_identifier_of_their_material(client):
    response = client.post(
        "/api/v1/materials/5/discovery/objective/explore",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "max_hops": 2,
                "limit": 20,
            },
            "mode": "balanced",
            "limit": 20,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ranked_candidates"]

    chain_identifiers = {
        material["material_id"]: material["mp_id"]
        for chain in data["chains"]
        for material in chain["materials"]
    }
    for candidate in data["ranked_candidates"]:
        assert candidate["mp_id"], candidate
        assert candidate["mp_id"].startswith("mp-")
        if candidate["material_id"] in chain_identifiers:
            assert candidate["mp_id"] == chain_identifiers[candidate["material_id"]]
