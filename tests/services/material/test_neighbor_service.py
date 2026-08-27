from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.services.material.neighbor_service import MaterialNeighborService


def _neighbor(
    material_id: int,
    score: int,
    shared_applications: int,
    shared_elements: int,
) -> dict:
    return {
        "material_id": material_id,
        "neighbor_score": score,
        "shared_application_count": shared_applications,
        "shared_element_count": shared_elements,
    }


@pytest.mark.parametrize(
    "candidate_order",
    [
        [4, 3, 2, 5],
        [5, 2, 3, 4],
        [3, 4, 5, 2],
    ],
)
def test_neighbor_ranking_resolves_complete_ties_by_material_id(
    candidate_order,
) -> None:
    candidates = {
        2: _neighbor(2, 5, 2, 0),
        3: _neighbor(3, 5, 2, 0),
        4: _neighbor(4, 5, 1, 1),
        5: _neighbor(5, 6, 0, 3),
    }
    service = MaterialNeighborService(Mock())
    service.db.get.return_value = SimpleNamespace(
        id=1,
        mp_id="mp-1",
        pretty_formula="M1",
        formula="M1",
        material_type="test",
        is_stable=True,
        energy_above_hull=0.0,
    )
    service._get_material_element_ids = Mock(return_value=set())
    service._get_material_application_ids = Mock(return_value=set())
    service._collect_element_neighbors = Mock()
    service._collect_application_neighbors = Mock()
    service._get_materials_by_id = Mock(return_value={})
    service._build_neighbors = Mock(
        return_value=[candidates[material_id] for material_id in candidate_order]
    )

    result = service.get_neighbors(1)

    assert [item["material_id"] for item in result["neighbors"]] == [5, 2, 3, 4]