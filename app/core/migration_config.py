import os
from collections.abc import Mapping


def resolve_migration_database_url(
    environ: Mapping[str, str] | None = None,
) -> str:
    environment = os.environ if environ is None else environ

    for variable_name in ("DATABASE_MIGRATION_URL", "DATABASE_URL"):
        value = environment.get(variable_name)
        if value and value.strip():
            return value.strip()

    raise RuntimeError(
        "Alembic requires DATABASE_MIGRATION_URL or DATABASE_URL; "
        "no migration database target is configured."
    )