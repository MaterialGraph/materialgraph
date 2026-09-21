from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models.application import Application
from app.models.element import Element
from app.models.material import Material
from app.models.material_application import MaterialApplication
from app.models.material_element import MaterialElement
from app.services.material.neighbor_service import MaterialNeighborService


@pytest.fixture
def neighbor_db() -> Iterator[Session]:
    engine = create_engine("sqlite:///:memory:")
    tables = [
        Material.__table__,
        Element.__table__,
        Application.__table__,
        MaterialElement.__table__,
        MaterialApplication.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)

    with Session(engine) as db:
        db.add_all(
            [
                Material(
                    id=1,
                    mp_id="mp-1",
                    formula="AB",
                    pretty_formula="AB",
                    material_type="test",
                    is_stable=True,
                    energy_above_hull=0.0,
                ),
                Material(
                    id=2,
                    mp_id="mp-2",
                    formula="AC",
                    pretty_formula="AC",
                    material_type=None,
                    is_stable=False,
                    energy_above_hull=None,
                ),
                Material(
                    id=3,
                    mp_id="mp-3",
                    formula="BC",
                    pretty_formula="BC",
                    material_type="test",
                    is_stable=True,
                    energy_above_hull=0.1,
                ),
                Material(
                    id=4,
                    mp_id="mp-4",
                    formula="D",
                    pretty_formula="D",
                    material_type="isolated",
                    is_stable=False,
                    energy_above_hull=None,
                ),
                Element(id=1, symbol="A", name="A"),
                Element(id=2, symbol="B", name="B"),
                Element(id=3, symbol="C", name="C"),
                Element(id=4, symbol="D", name="D"),
                Application(id=1, name="storage"),
                Application(id=2, name="catalysis"),
            ]
        )
        db.flush()
        db.add_all(
            [
                MaterialElement(material_id=1, element_id=1, fraction=0.5),
                MaterialElement(material_id=1, element_id=2, fraction=0.5),
                MaterialElement(material_id=2, element_id=1, fraction=0.5),
                MaterialElement(material_id=2, element_id=3, fraction=0.5),
                MaterialElement(material_id=3, element_id=2, fraction=0.5),
                MaterialElement(material_id=3, element_id=3, fraction=0.5),
                MaterialElement(material_id=4, element_id=4, fraction=1.0),
                MaterialApplication(material_id=1, application_id=1),
                MaterialApplication(material_id=2, application_id=1),
                MaterialApplication(material_id=2, application_id=2),
                MaterialApplication(material_id=3, application_id=2),
            ]
        )
        db.commit()
        yield db

    engine.dispose()


def test_batch_neighbors_are_exactly_equal_to_individual_results(
    neighbor_db: Session,
) -> None:
    service = MaterialNeighborService(neighbor_db)
    material_ids = [1, 2, 3, 4, 999]
    expected = {
        material_id: service.get_neighbors(material_id)
        for material_id in material_ids
    }

    assert service.get_neighbors_batch(material_ids) == expected


def test_batch_neighbor_query_count_is_bounded(neighbor_db: Session) -> None:
    service = MaterialNeighborService(neighbor_db)
    query_count = 0

    def count_query(*_args, **_kwargs) -> None:
        nonlocal query_count
        query_count += 1

    event.listen(
        neighbor_db.get_bind(),
        "before_cursor_execute",
        count_query,
    )
    try:
        service.get_neighbors_batch([1, 2, 3, 4])
    finally:
        event.remove(
            neighbor_db.get_bind(),
            "before_cursor_execute",
            count_query,
        )

    assert query_count <= 6


def test_batch_neighbors_deduplicate_requested_material_ids(
    neighbor_db: Session,
) -> None:
    service = MaterialNeighborService(neighbor_db)

    assert service.get_neighbors_batch([2, 1, 2]) == {
        2: service.get_neighbors(2),
        1: service.get_neighbors(1),
    }
