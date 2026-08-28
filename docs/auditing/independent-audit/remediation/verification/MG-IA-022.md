# MG-IA-022 Remediation Verification

## Title

Alembic fails closed when no migration database target is configured

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. `alembic.ini` contains no executable database URL or default credentials.
2. Alembic requires `DATABASE_MIGRATION_URL` or `DATABASE_URL` before online
   and offline configuration.
3. `DATABASE_MIGRATION_URL` deterministically takes precedence when both are
   present.
4. `DATABASE_URL` remains the documented fallback when no migration-specific
   value is configured.
5. Empty or whitespace-only values are treated as absent.
6. Missing configuration raises a clear error without constructing an engine.
7. Local and deployment documentation describe the effective policy.
8. Focused, migration, full-suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `fdc5eb3` during
the final closure review. `alembic.ini` still contained
`postgresql+psycopg://postgres:postgres@localhost:5432/materialgraph`, while
`alembic/env.py` replaced it only when one of the two environment variables was
truthy. Both online and offline paths otherwise consumed the retained URL. The
frozen finding remained fully applicable and had been accidentally omitted
from the remediation register.

## Implemented changes

- Added a pure migration database URL resolver.
- Enforced migration-specific URL precedence and application URL fallback.
- Rejected missing and blank configuration with a clear `RuntimeError`.
- Removed the executable localhost target from `alembic.ini`.
- Configured Alembic unconditionally from the resolved explicit URL.
- Documented local and deployment migration URL semantics.
- Added five regressions covering missing configuration, precedence, fallback,
  blank override handling, and removal of the INI fallback.

## Verification results

Commands included the focused migration/project configuration suites and both
migration test files, followed by:

```powershell
pytest -q
ruff check .
git diff --check
```

Results:

- focused migration and configuration verification: **passed**;
- migration regression verification: **passed**;
- complete test suite: **passed**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; LF-to-CRLF messages were
  informational working-tree conversion warnings.

## Change boundary

The verified implementation boundary contains six files: two Alembic/config
files, two setup/deployment documents, one new pure configuration module, and
one new test file. It changes no revision, model, schema, seed data, API, or
scientific calculation.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-022` is verified as remediated.
