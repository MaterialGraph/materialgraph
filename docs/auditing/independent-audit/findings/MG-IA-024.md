# MG-IA-024 — Root README Quick Start omits configuration required by its commands

- Classification: setup documentation defect
- Priority: P3
- Confidence: high
- Disposition: confirmed

## Affected files and components

- root `README.md`, “Quick Start”
- `.env.example`
- `app/core/config.py`
- `alembic/env.py`
- `scripts/import_materials_project.py`

## Exact evidence

The Quick Start proceeds directly from dependency installation to `alembic upgrade head`, material import, and Uvicorn startup. It does not copy/configure `.env` or set `DATABASE_URL`. Module-level `Settings` requires `database_url`; both Alembic's import of `app.core.database` and application startup require it. The import script additionally raises when `MATERIALS_PROJECT_API_KEY` is absent.

## Expected versus actual

A Quick Start should either contain the minimum required configuration steps or explicitly delegate to the full setup guide before presenting executable commands. The listed sequence fails in a clean checkout unless the reader independently supplies undocumented-in-sequence environment state.

## Impact

New users cannot reproduce the documented startup path and may misdiagnose configuration failures as packaging, migration, or application defects.

## Reproduction

In a clean environment with dependencies installed but no `.env`/database variable, execute `alembic upgrade head` or `uvicorn app.main:app --reload`; required settings construction fails. With a database configured but no Materials Project key, the listed import command explicitly raises `MATERIALS_PROJECT_API_KEY is not configured`.

## Tests

Configuration tests confirm that `database_url` is required and that the API-key name aligns with settings/docs, but no clean-checkout documentation test executes the root Quick Start.

## Recommended remediation scope

Add `.env.example` copy/configuration instructions, identify required versus optional fields, describe database preparation, and make material import conditional on an API key. Link to the full Getting Started guide while keeping the minimal command sequence independently coherent.
