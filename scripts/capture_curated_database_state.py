import argparse
import json
from pathlib import Path

from sqlalchemy import select

from app.core.database import SessionLocal, engine
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.real_data_qualification import (
    CURATED_MATERIAL_COUNT,
    canonical_sha256,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture the immutable curated-row state for MG-DE-007."
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-database-name", required=True)
    return parser


def validate_environment(expected_database_name: str) -> None:
    actual = engine.url.database or ""
    if actual != expected_database_name:
        raise ValueError("configured database does not match the expected name")
    lowered = actual.lower()
    if "test" not in lowered or "mg_de_007" not in lowered:
        raise ValueError("MG-DE-007 requires a dedicated mg_de_007 test database")
    if engine.dialect.name != "postgresql":
        raise ValueError("MG-DE-007 requires PostgreSQL")


def capture() -> dict:
    with SessionLocal() as db:
        materials = list(
            db.scalars(
                select(Material)
                .where(Material.id <= CURATED_MATERIAL_COUNT)
                .order_by(Material.id)
            )
        )
        if len(materials) != CURATED_MATERIAL_COUNT:
            raise ValueError("the 28 curated material identities are not present")
        links = list(
            db.execute(
                select(
                    MaterialElement.material_id,
                    MaterialElement.element_id,
                    MaterialElement.fraction,
                    MaterialElement.fraction_known,
                )
                .where(MaterialElement.material_id <= CURATED_MATERIAL_COUNT)
                .order_by(
                    MaterialElement.material_id,
                    MaterialElement.element_id,
                )
            ).all()
        )
        records = [
            {
                "id": row.id,
                "mp_id": row.mp_id,
                "formula": row.formula,
                "pretty_formula": row.pretty_formula,
                "material_type": row.material_type,
                "band_gap": row.band_gap,
                "energy_above_hull": row.energy_above_hull,
                "formation_energy_per_atom": row.formation_energy_per_atom,
                "density": row.density,
                "is_stable": row.is_stable,
                "source": row.source,
                "raw_data": row.raw_data,
            }
            for row in materials
        ]
        element_links = [list(link) for link in links]
        protected = {"materials": records, "material_elements": element_links}
        return {
            "schema_version": 1,
            "database": engine.url.database,
            "material_count": len(records),
            "material_ids": [row["id"] for row in records],
            "mp_ids": [row["mp_id"] for row in records],
            "records_sha256": canonical_sha256(protected),
        }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validate_environment(args.expected_database_name)
    if args.output.exists():
        raise ValueError(f"refusing to overwrite {args.output}")
    result = capture()
    args.output.write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
