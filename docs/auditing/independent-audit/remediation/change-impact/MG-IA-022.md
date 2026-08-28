# MG-IA-022 Change Impact — Explicit Alembic Database Target

> Closure classification: defense-in-depth hardening for a retired proposition;
> not counted as an actionable-finding remediation. See the paired verification
> record for the import-order reachability correction.

## Status

Verified locally: focused migration-configuration and project-configuration
tests, migration coverage, the full test suite, Ruff, and Git whitespace
validation passed.

## Before

`alembic.ini` contained an executable PostgreSQL URL with default local
credentials. `alembic/env.py` replaced that URL only when
`DATABASE_MIGRATION_URL` or `DATABASE_URL` was present. If both variables were
missing or blank, Alembic silently retained the INI target for both online and
offline migration execution.

## After

Alembic resolves its database target through a pure configuration helper before
configuring either migration mode. It prefers `DATABASE_MIGRATION_URL`, falls
back deliberately to `DATABASE_URL`, ignores blank values, and raises a clear
error when neither variable is configured.

The INI file now contains an empty non-executable placeholder. Local and
deployment documentation explain the precedence and fail-closed behavior.

## Impact

- Migration safety: **Corrected** — missing configuration cannot select an
  unintended localhost database.
- Credential hygiene: **Improved** — default database credentials are removed
  from tracked Alembic configuration.
- Online/offline parity: **Corrected** — both entry paths require the same
  explicit target resolution.
- Deployment flexibility: **Preserved** — a direct migration URL may override
  the application/pooled URL.
- Application runtime and API behavior: **Unchanged**.
- Migration revisions and database schema: **Unchanged**.
- Scientific computation and stored data: **Unchanged**.

## Scope decision

Migration URL resolution is isolated in `app/core/migration_config.py` so its
failure and precedence semantics can be tested without importing Alembic's
runtime context or opening a database connection. Alembic remains responsible
for engine construction only after resolution succeeds.
