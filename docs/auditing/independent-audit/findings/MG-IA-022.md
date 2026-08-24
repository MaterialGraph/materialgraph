# MG-IA-022 — Alembic silently falls back to a hard-coded local database target

- Classification: migration configuration and deployment-safety defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `alembic.ini`
- `alembic/env.py`
- migration invocation and deployment documentation/tests

## Exact evidence

`alembic.ini` defines `sqlalchemy.url = postgresql+psycopg://postgres:postgres@localhost:5432/materialgraph`. `alembic/env.py` calls `load_dotenv()` and resolves `DATABASE_MIGRATION_URL` or `DATABASE_URL`. It overwrites `sqlalchemy.url` only when one of those environment variables is truthy. When both are absent, the hard-coded URL remains active and is passed to offline migration configuration or `engine_from_config` for online migrations.

Unlike application startup, this path does not instantiate the typed `Settings` model whose required `database_url` fails closed.

## Expected versus actual

Migration execution should require an explicit database target or an explicitly selected development profile. Missing migration configuration should fail before opening a connection. It currently changes semantics by silently selecting a local database with embedded default credentials.

## Impact

A migration command run with a missing or misspelled environment configuration can operate on an unintended local `materialgraph` database rather than failing. This can produce false deployment verification, apply schema changes to the wrong database, or generate misleading migration/autogeneration results.

## Reproduction

Run Alembic with both `DATABASE_MIGRATION_URL` and `DATABASE_URL` absent. `env.py` does not replace the INI value; `run_migrations_online` builds its engine from the retained localhost URL. Offline SQL generation likewise uses that URL's dialect.

## Caller trace

Both Alembic online and offline entry paths consume `config.get_main_option("sqlalchemy.url")`. No later check verifies that the URL came from an explicit environment setting, and the application `Settings` validation path is bypassed.

## Tests

No supplied test covers migration startup with absent, migration-specific, and application database variables. Existing configuration tests establish fail-closed application settings only and do not execute Alembic configuration.

## Recommended remediation scope

Remove the executable fallback URL or replace it with a nonsecret placeholder that cannot connect. In `env.py`, require an explicit `DATABASE_MIGRATION_URL` or deliberately documented `DATABASE_URL`, raise a clear error when absent, and add tests for precedence and missing-variable failure. Document the migration-specific variable if it is part of the supported deployment contract.
