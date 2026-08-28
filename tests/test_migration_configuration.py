from pathlib import Path

import pytest

from app.core.migration_config import resolve_migration_database_url


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_migration_database_url_requires_explicit_configuration():
    with pytest.raises(
        RuntimeError,
        match="requires DATABASE_MIGRATION_URL or DATABASE_URL",
    ):
        resolve_migration_database_url({})


def test_migration_database_url_prefers_migration_specific_value():
    result = resolve_migration_database_url({
        "DATABASE_MIGRATION_URL": "postgresql://direct/database",
        "DATABASE_URL": "postgresql://pooled/database",
    })

    assert result == "postgresql://direct/database"


def test_migration_database_url_falls_back_to_application_value():
    result = resolve_migration_database_url({
        "DATABASE_URL": "postgresql://application/database",
    })

    assert result == "postgresql://application/database"


def test_blank_migration_override_uses_application_value():
    result = resolve_migration_database_url({
        "DATABASE_MIGRATION_URL": "   ",
        "DATABASE_URL": " postgresql://application/database ",
    })

    assert result == "postgresql://application/database"


def test_alembic_ini_has_no_executable_database_fallback():
    alembic_ini = (PROJECT_ROOT / "alembic.ini").read_text(encoding="utf-8")
    configured_url_lines = [
        line.strip()
        for line in alembic_ini.splitlines()
        if line.strip().startswith("sqlalchemy.url")
    ]

    assert configured_url_lines == ["sqlalchemy.url ="]
    assert "postgres:postgres@localhost" not in alembic_ini