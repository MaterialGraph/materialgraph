"""Offline reference dataset for the backend test suite (CI and local).

The suite's data-dependent tests need the materials and material-element rows
that exist in the local ``materialgraph_test`` database (originally imported
from the Materials Project). CI cannot call the Materials Project API, so this
tool exports those rows once into a checked-in JSON fixture and loads them into
an empty, migrated, test-only database.

    python -m scripts.reference_test_data export   # from materialgraph_test (read-only)
    python -m scripts.reference_test_data load     # into an empty *test* database

Load order in CI:
    alembic upgrade head
    python -m scripts.seed_core_data
    python -m scripts.seed_risk_profiles
    python -m scripts.reference_test_data load
    python -m scripts.seed_material_applications

Guarantees:
  * export refuses any database other than ``materialgraph_test`` and only reads;
  * load refuses any database whose name does not contain "test" (same rule as
    tests/conftest.py) and refuses a non-empty ``materials`` table;
  * material IDs are preserved; element links are stored by symbol;
  * output is deterministic (sorted keys and rows, no timestamps added).

Source data: Materials Project (https://materialsproject.org), licensed CC BY 4.0.
"""

from __future__ import annotations

import datetime as dt
import decimal
import json
import sys
from pathlib import Path

from sqlalchemy import MetaData, Table, func, select, text
from sqlalchemy.engine import make_url

from app.core.database import engine

FIXTURE = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "reference_dataset.json"
EXPORT_SOURCE = "materialgraph_test"


def _db_name() -> str:
    return make_url(str(engine.url)).database or ""


def _jsonable(value):
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return str(value)
    return value


def _coerce(column, value):
    if value is None:
        return None
    try:
        py = column.type.python_type
    except (NotImplementedError, AttributeError):
        return value
    if py is dt.datetime and isinstance(value, str):
        return dt.datetime.fromisoformat(value)
    if py is dt.date and isinstance(value, str):
        return dt.date.fromisoformat(value)
    if py is decimal.Decimal and isinstance(value, (str, int, float)):
        return decimal.Decimal(str(value))
    return value


def export() -> None:
    name = _db_name()
    if name != EXPORT_SOURCE:
        sys.exit(f"ABORT: export reads only from '{EXPORT_SOURCE}', not '{name}'.")

    meta = MetaData()
    materials = Table("materials", meta, autoload_with=engine)
    material_elements = Table("material_elements", meta, autoload_with=engine)
    elements = Table("elements", meta, autoload_with=engine)

    with engine.connect() as conn:
        mat_rows = [
            {k: _jsonable(v) for k, v in row._mapping.items()}
            for row in conn.execute(select(materials).order_by(materials.c.id))
        ]
        me_cols = [c for c in material_elements.c if c.name not in ("id", "element_id")]
        me_rows = [
            {**{k: _jsonable(v) for k, v in row._mapping.items() if k != "symbol"},
             "element_symbol": row._mapping["symbol"]}
            for row in conn.execute(
                select(*me_cols, elements.c.symbol)
                .join(elements, material_elements.c.element_id == elements.c.id)
                .order_by(material_elements.c.material_id, elements.c.symbol)
            )
        ]

    payload = {
        "description": "Offline reference dataset for the MaterialGraph test suite.",
        "source": "Materials Project (CC BY 4.0) via local materialgraph_test",
        "counts": {"materials": len(mat_rows), "material_elements": len(me_rows)},
        "materials": mat_rows,
        "material_elements": me_rows,
    }
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"exported {len(mat_rows)} materials, {len(me_rows)} material_elements -> {FIXTURE}")


def load() -> None:
    name = _db_name()
    if "test" not in name.lower():
        sys.exit(f"ABORT: refusing to load reference data into non-test database '{name}'.")

    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    meta = MetaData()
    materials = Table("materials", meta, autoload_with=engine)
    material_elements = Table("material_elements", meta, autoload_with=engine)
    elements = Table("elements", meta, autoload_with=engine)

    with engine.begin() as conn:
        if conn.execute(select(func.count()).select_from(materials)).scalar():
            sys.exit("ABORT: materials table is not empty.")

        symbol_to_id = dict(conn.execute(select(elements.c.symbol, elements.c.id)).all())
        missing = sorted({r["element_symbol"] for r in payload["material_elements"]} - set(symbol_to_id))
        if missing:
            sys.exit(f"ABORT: elements not seeded (run seed_core_data first): {missing}")

        mat_cols = {c.name: c for c in materials.c}
        conn.execute(materials.insert(), [
            {k: _coerce(mat_cols[k], v) for k, v in row.items() if k in mat_cols}
            for row in payload["materials"]
        ])

        me_cols = {c.name: c for c in material_elements.c}
        conn.execute(material_elements.insert(), [
            {**{k: _coerce(me_cols[k], v) for k, v in row.items() if k in me_cols},
             "element_id": symbol_to_id[row["element_symbol"]]}
            for row in payload["material_elements"]
        ])

        for table in ("materials", "material_elements"):
            conn.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
            ))

        got_m = conn.execute(select(func.count()).select_from(materials)).scalar()
        got_me = conn.execute(select(func.count()).select_from(material_elements)).scalar()

    expected = payload["counts"]
    if (got_m, got_me) != (expected["materials"], expected["material_elements"]):
        sys.exit(f"ABORT: loaded {got_m}/{got_me}, expected {expected}")
    print(f"loaded {got_m} materials, {got_me} material_elements into '{name}'")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"export", "load"}:
        sys.exit("usage: python -m scripts.reference_test_data {export|load}")
    export() if sys.argv[1] == "export" else load()
