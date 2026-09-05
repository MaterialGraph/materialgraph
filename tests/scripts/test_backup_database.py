from pathlib import Path

import pytest

from scripts.backup_database import BackupError, database_environment, safe_prefix, sha256_file


def test_safe_prefix_normalizes_expected_value():
    assert safe_prefix("/production/") == "production"


@pytest.mark.parametrize("value", ["", "/", "production/../other", "./production"])
def test_safe_prefix_rejects_unsafe_values(value):
    with pytest.raises(BackupError):
        safe_prefix(value)


def test_database_environment_keeps_credentials_out_of_command_arguments():
    environment = database_environment(
        "postgresql+psycopg://backup-user:p%40ss@db.example:5433/materialgraph"
    )

    assert environment["PGHOST"] == "db.example"
    assert environment["PGPORT"] == "5433"
    assert environment["PGDATABASE"] == "materialgraph"
    assert environment["PGUSER"] == "backup-user"
    assert environment["PGPASSWORD"] == "p@ss"
    assert environment["PGSSLMODE"] == "require"
    assert environment["PGCHANNELBINDING"] == "require"


def test_sha256_file(tmp_path: Path):
    target = tmp_path / "archive.dump"
    target.write_bytes(b"materialgraph")

    assert sha256_file(target) == (
        "851a157e06f9c4f3888028609d88ea2fb5963247954364f260a239b6b7050379"
    )
