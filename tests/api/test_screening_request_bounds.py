import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {"scarce_elements": ["Li"] * 33},
        {"avoid_elements": ["Co"] * 33},
        {"scarce_elements": ["Lithium"]},
        {"avoid_elements": ["Xx"]},
    ],
)
def test_screening_rejects_invalid_element_collections(client, payload):
    response = client.post(
        "/api/v1/screening/candidates",
        json=payload,
    )

    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
