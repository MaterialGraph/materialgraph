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


def test_dataset_provenance_migration_creates_auditable_refresh_tables() -> None:
    if engine.dialect.name != "postgresql":
        pytest.skip("The production migration contract is PostgreSQL-specific")

    schema = f"mg_de_002_{uuid4().hex}"
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
            connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
            connection.execute(
                text(
                    """
                    CREATE TABLE materials (
                        id integer PRIMARY KEY,
                        mp_id varchar(50) NOT NULL UNIQUE
                    )
                    """
                )
            )

            _run_upgrade(
                connection,
                "c8f3a2d7e901_add_dataset_provenance.py",
            )

            tables = {
                value
                for (value,) in connection.execute(
                    text(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = :schema
                        """
                    ),
                    {"schema": schema},
                )
            }
            assert {
                "dataset_import_runs",
                "material_import_events",
                "material_source_memberships",
                "material_source_records",
            }.issubset(tables)

            connection.execute(
                text(
                    """
                    INSERT INTO dataset_import_runs (
                        id, source, source_release, retrieved_at,
                        manifest_sha256, normalization_version,
                        selection_contract_version, selection_scope_sha256,
                        license_identifier, license_url, status, started_at
                    ) VALUES (
                        '00000000-0000-0000-0000-000000000001',
                        'materials_project', 'test-release', now(),
                        repeat('a', 64), 'normalization-v1', 'selection-v1',
                        repeat('b', 64), 'CC-BY-4.0',
                        'https://creativecommons.org/licenses/by/4.0/',
                        'running', now()
                    )
                    """
                )
            )
            status = connection.execute(
                text(
                    """
                    SELECT status
                    FROM dataset_import_runs
                    WHERE id = '00000000-0000-0000-0000-000000000001'
                    """
                )
            ).scalar_one()
            assert status == "running"
        finally:
            if transaction.is_active:
                transaction.rollback()
