from app.schemas.comparison import (
    CandidateComparisonUnavailable,
    CandidateComparisonUnavailableCandidate,
)
from app.services.candidate_comparison_service import (
    CandidateComparisonService,
)


def test_compare_materials_api(client):
    response = client.post(
        "/api/v1/comparison/materials",
        json={
            "material_a_id": 6,
            "material_b_id": 12,
            "scarce_elements": ["Li"],
            "avoid_elements": ["Co"],
            "require_stable": True,
            "max_energy_above_hull": 0.05,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["winner_material_id"] in {6, 12}
    assert data["score_difference"] >= 0
    assert len(data["reasons"]) > 0


def test_compare_materials_api_not_found(client):
    response = client.post(
        "/api/v1/comparison/materials",
        json={
            "material_a_id": 6,
            "material_b_id": 999999,
            "scarce_elements": ["Li"],
            "avoid_elements": ["Co"],
        },
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["comparison_type"] == "unavailable"
    assert detail["unavailable_candidates"] == [
        {
            "material_id": 999999,
            "disposition": "material_not_found",
            "reason": "Material does not exist.",
        }
    ]


def test_compare_materials_api_distinguishes_filtered_candidate(
    client,
    monkeypatch,
):
    def compare_candidates(self, request):
        return CandidateComparisonUnavailable(
            unavailable_candidates=[
                CandidateComparisonUnavailableCandidate(
                    material_id=request.material_b_id,
                    disposition="filtered_unstable",
                    reason=(
                        "Material was excluded because stable material "
                        "was required."
                    ),
                )
            ]
        )

    monkeypatch.setattr(
        CandidateComparisonService,
        "compare_candidates",
        compare_candidates,
    )

    response = client.post(
        "/api/v1/comparison/materials",
        json={
            "material_a_id": 6,
            "material_b_id": 12,
            "require_stable": True,
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == {
        "comparison_type": "unavailable",
        "unavailable_candidates": [
            {
                "material_id": 12,
                "disposition": "filtered_unstable",
                "reason": (
                    "Material was excluded because stable material "
                    "was required."
                ),
            }
        ],
    }