import runpy
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text

from app.core.database import engine


VERSIONS_DIR = Path(__file__).resolve().parents[2] / "alembic" / "versions"


def _run_upgrade(connection, revision_file: str) -> None:
    revision = runpy.run_path(str(VERSIONS_DIR / revision_file))
    migration_context = MigrationContext.configure(connection)

    with Operations.context(migration_context):
        revision["upgrade"]()


def test_fraction_evidence_migration_marks_predecessor_rows_unknown() -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("The production migration contract is PostgreSQL-specific")

    schema = f"mg_ia_009_{uuid4().hex}"

    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
            connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
            connection.execute(
                text(
                    """
                    CREATE TABLE material_elements (
                        id integer PRIMARY KEY,
                        material_id integer NOT NULL,
                        element_id integer NOT NULL,
                        fraction double precision NOT NULL
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO material_elements (
                        id,
                        material_id,
                        element_id,
                        fraction
                    )
                    VALUES (1, 1, 1, 1.0)
                    """
                )
            )

            _run_upgrade(
                connection,
                "7a4c2e91b6d8_add_material_element_fraction_evidence.py",
            )

            fraction_known = connection.execute(
                text(
                    "SELECT fraction_known FROM material_elements WHERE id = 1"
                )
            ).scalar_one()
            is_nullable = connection.execute(
                text(
                    """
                    SELECT is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = :schema
                      AND table_name = 'material_elements'
                      AND column_name = 'fraction_known'
                    """
                ),
                {"schema": schema},
            ).scalar_one()

            assert fraction_known is False
            assert is_nullable == "NO"
        finally:
            if transaction.is_active:
                transaction.rollback()