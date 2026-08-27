# MG-IA-024 Change Impact — Reproducible Quick Start Configuration

## Status

Verified locally: eight focused configuration tests, 721 full-suite tests,
Ruff, and Git whitespace validation passed.

## Before

The root README moved directly from dependency installation to database
migration, Materials Project import, and application startup. It did not tell
users to create `.env`, configure the required `DATABASE_URL`, or prepare the
referenced PostgreSQL database. It also presented material import as an
unconditional step even though that command requires a Materials Project API
key while normal application startup does not.

## After

The Quick Start identifies a running PostgreSQL instance and an empty database
as prerequisites, provides Linux/macOS and Windows commands for copying
`.env.example`, and requires `DATABASE_URL` configuration before migration.
Materials Project import is explicitly optional and conditioned on setting
`MATERIALS_PROJECT_API_KEY`. The section links to the full Getting Started
guide for platform-specific and expanded setup instructions.

A configuration regression test verifies the required-versus-optional
contract and ensures database configuration appears before migration.

## Impact

- Setup reproducibility: **Corrected** — a clean checkout receives the minimum
  configuration needed by the documented commands.
- Configuration semantics: **Clarified** — database configuration is required;
  the external import credential is conditional.
- Secret handling: **Preserved** — users copy the tracked template and keep
  actual values in untracked `.env`.
- Runtime and API behavior: **No change**.
- Database schema and migrations: **No change**.
- Scientific computation and stored data: **No change**.

## Scope decision

The root README remains a concise Quick Start rather than duplicating the full
setup guide. It now provides a coherent minimum sequence and delegates detailed
platform, database, secret-scanning, and verification guidance through an
explicit link.
