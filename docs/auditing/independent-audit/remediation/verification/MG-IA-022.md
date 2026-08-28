# MG-IA-022 Applicability Correction and Closure-Hardening Verification

## Title

Alembic's fail-closed target is explicit and independent of import order

## Status

Original proposition retired as not actionable; subsequent defense-in-depth
hardening verified in the local project environment on Windows with Python
3.14.5 and the configured PostgreSQL test environment.

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

## Applicability correction

The final independent-pass register retired `MG-IA-022` after import-order
correction. `alembic/env.py` imported `app.models` before URL selection;
application model imports constructed required settings, so a missing
`DATABASE_URL` failed before the INI fallback was reachable. The original
silent-fallback proposition therefore did not satisfy the audit's reachability
threshold and was not an actionable finding.

The closure review initially overlooked that indirect guard. This record
corrects the classification while preserving the useful hardening subsequently
committed at `3b3a429`.

## Closure-hardening changes

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

The explicit configuration acceptance criteria are satisfied. `MG-IA-022`
remains **Not actionable** as an audit finding; commit `3b3a429` is retained as
verified defense-in-depth hardening and is not counted among the 20 actionable
remediations.
