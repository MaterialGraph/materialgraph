# MG-IA-024 Remediation Verification

## Title

Root Quick Start documents configuration required by its commands

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. The Quick Start directs users to create `.env` from `.env.example`.
2. It states that `DATABASE_URL` is required for migrations and startup.
3. Database preparation is identified before migration execution.
4. Materials Project import is marked optional.
5. `MATERIALS_PROJECT_API_KEY` is required only for the optional import.
6. The Quick Start links to the full Getting Started guide.
7. A regression test preserves the ordering and configuration semantics.
8. Existing MG-IA-023 documentation-contract coverage remains intact.
9. The complete test suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `622df26`. The
Quick Start still ran `alembic upgrade head` without first creating or
configuring `.env`. `app/core/config.py` required `database_url` during settings
construction. The import script still rejected a missing
`MATERIALS_PROJECT_API_KEY`, although that key remained optional for normal
application startup. The frozen finding remained fully applicable.

## Implemented changes

- Added the PostgreSQL-instance and empty-database prerequisites.
- Added `.env.example` copy instructions for Linux/macOS and PowerShell.
- Required `DATABASE_URL` configuration before Alembic migration.
- Made the Materials Project import command optional and conditional on its API
  key.
- Linked the concise sequence to the full Getting Started guide.
- Added a regression test for the required configuration, conditional key, and
  ordering contract.

## Verification results

Commands:

```powershell
pytest tests/test_project_configuration.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused configuration verification: **8 passed in 0.65 seconds**;
- complete test suite: **721 passed in 24.83 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; the LF-to-CRLF message was an
  informational working-tree conversion warning.

## Change boundary

The verified implementation boundary contains two modified files:
`README.md` and `tests/test_project_configuration.py`. It makes no runtime,
model, migration, seed-data, or deployment change.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-024` is verified as remediated.
