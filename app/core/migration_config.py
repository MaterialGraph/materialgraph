import os
from collections.abc import Mapping, MutableMapping


def escape_alembic_config_value(value: str) -> str:
    return value.replace("%", "%%")


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


def prepare_migration_database_environment(
    environ: MutableMapping[str, str] | None = None,
) -> str:
    environment = os.environ if environ is None else environ
    database_url = resolve_migration_database_url(environment)

    if not environment.get("DATABASE_URL", "").strip():
        # Model imports construct application settings. Give that import the
        # already selected migration URL only inside the Alembic process.
        environment["DATABASE_URL"] = database_url

    return database_url
