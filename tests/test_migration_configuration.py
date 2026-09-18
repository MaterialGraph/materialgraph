from configparser import ConfigParser
from pathlib import Path

import pytest

from app.core.migration_config import (
    escape_alembic_config_value,
    prepare_migration_database_environment,
    resolve_migration_database_url,
)


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


def test_migration_url_supports_model_import_settings():
    environment = {
        "DATABASE_MIGRATION_URL": "postgresql://direct/database",
    }

    result = prepare_migration_database_environment(environment)

    assert result == "postgresql://direct/database"
    assert environment["DATABASE_URL"] == result


def test_existing_application_url_is_not_replaced_for_model_imports():
    environment = {
        "DATABASE_MIGRATION_URL": "postgresql://direct/database",
        "DATABASE_URL": "postgresql://pooled/database",
    }

    result = prepare_migration_database_environment(environment)

    assert result == "postgresql://direct/database"
    assert environment["DATABASE_URL"] == "postgresql://pooled/database"


def test_plain_alembic_config_value_is_unchanged():
    value = "postgresql+psycopg://user:password@host/database"

    assert escape_alembic_config_value(value) == value


def test_percent_encoded_alembic_url_survives_config_interpolation():
    value = (
        "postgresql+psycopg://user:p%40ss@host/database"
        "?sslmode=verify-full"
        "&sslrootcert=%2Fetc%2Fssl%2Fcerts%2Fca-certificates.crt"
    )

    escaped = escape_alembic_config_value(value)

    assert "p%%40ss" in escaped
    assert "sslrootcert=%%2Fetc%%2Fssl" in escaped

    parser = ConfigParser()
    parser.add_section("alembic")
    parser.set("alembic", "sqlalchemy.url", escaped)

    assert parser.get("alembic", "sqlalchemy.url") == value


def test_alembic_ini_has_no_executable_database_fallback():
    alembic_ini = (PROJECT_ROOT / "alembic.ini").read_text(encoding="utf-8")
    configured_url_lines = [
        line.strip()
        for line in alembic_ini.splitlines()
        if line.strip().startswith("sqlalchemy.url")
    ]

    assert configured_url_lines == ["sqlalchemy.url ="]
    assert "postgres:postgres@localhost" not in alembic_ini
