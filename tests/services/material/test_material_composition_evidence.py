from uuid import uuid4

import pytest

from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.composition_backfill_service import (
    MaterialCompositionBackfillService,
)
from app.services.material.import_service import MaterialImportService
from app.services.material.project_service import MaterialCandidate


def _candidate(
    composition_fractions: dict[str, float],
) -> MaterialCandidate:
    mp_id = f"mp-test-{uuid4()}"

    return MaterialCandidate(
        mp_id=mp_id,
        formula="LiFePO4",
        pretty_formula="LiFePO4",
        elements=["Li", "Fe", "P", "O"],
        band_gap=1.2,
        energy_above_hull=0.0,
        formation_energy_per_atom=-2.5,
        density=3.6,
        is_stable=True,
        raw_data={
            "material_id": mp_id,
            "formula_pretty": "LiFePO4",
            "composition": dict(composition_fractions),
        },
        composition_fractions=composition_fractions,
    )


def _links(db_session, material_id: int) -> list[MaterialElement]:
    return (
        db_session.query(MaterialElement)
        .filter(MaterialElement.material_id == material_id)
        .all()
    )


def test_structured_import_marks_fractions_known(db_session):
    service = MaterialImportService(db_session)
    candidate = _candidate(
        {
            "Li": 1.0,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        }
    )

    assert service.import_materials([candidate]) == 1

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )
    links = _links(db_session, material.id)

    assert all(link.fraction_known for link in links)
    assert sum(link.fraction for link in links) == pytest.approx(1.0)


def test_membership_only_import_marks_fractions_unknown(db_session):
    service = MaterialImportService(db_session)
    candidate = _candidate({})

    assert service.import_materials([candidate]) == 1

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )
    links = _links(db_session, material.id)

    assert all(link.fraction_known is False for link in links)
    assert all(link.fraction == 1.0 for link in links)


def test_backfill_promotes_only_validated_structured_composition(db_session):
    importer = MaterialImportService(db_session)
    candidate = _candidate({})
    importer.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )
    material.raw_data = {
        "composition": {
            "Li": 1.0,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        }
    }

    result = MaterialCompositionBackfillService(
        db_session
    ).backfill_material(material)
    links = _links(db_session, material.id)

    assert result.changed_links == 4
    assert result.previous_fraction_evidence == {
        "Fe": False,
        "Li": False,
        "O": False,
        "P": False,
    }
    assert all(link.fraction_known for link in links)
    assert sum(link.fraction for link in links) == pytest.approx(1.0)