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


def test_core_domain_upgrade_backfills_source_for_existing_material() -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("The production migration contract is PostgreSQL-specific")

    schema = f"mg_ia_003_{uuid4().hex}"

    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
            connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')

            _run_upgrade(
                connection,
                "4368e3ecc291_create_initial_material_tables.py",
            )
            connection.execute(
                text(
                    """
                    INSERT INTO materials (
                        mp_id,
                        formula,
                        pretty_formula,
                        is_stable
                    )
                    VALUES (
                        'legacy-material',
                        'LiFePO4',
                        'LiFePO4',
                        true
                    )
                    """
                )
            )

            _run_upgrade(
                connection,
                "1d204c6d38c0_create_core_domain_models.py",
            )

            source = connection.execute(
                text(
                    "SELECT source FROM materials "
                    "WHERE mp_id = 'legacy-material'"
                )
            ).scalar_one()
            source_is_nullable = connection.execute(
                text(
                    """
                    SELECT is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = :schema
                      AND table_name = 'materials'
                      AND column_name = 'source'
                    """
                ),
                {"schema": schema},
            ).scalar_one()

            assert source == "legacy_unknown"
            assert source_is_nullable == "NO"
        finally:
            if transaction.is_active:
                transaction.rollback()