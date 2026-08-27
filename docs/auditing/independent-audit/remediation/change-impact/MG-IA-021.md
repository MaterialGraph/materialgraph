# MG-IA-021 Change Impact — Honest Materials Project Configuration

## Status

Verified locally: 6 focused configuration tests, 16 adjacent Materials Project
and import tests, 690 full-suite tests, Ruff, and Git whitespace validation
passed.

## Before

`.env.example` advertised `MP_API_URL` as a supported environment variable, but
`Settings` did not declare it and the runtime never consumed it. Because extra
settings are ignored, operators could set an endpoint override and receive no
error while the Materials Project client continued using its default endpoint.

## After

The unsupported `MP_API_URL` placeholder is removed. The supported
`MATERIALS_PROJECT_API_KEY` contract remains unchanged. A generic configuration
test now verifies that every non-commented key advertised by `.env.example`
maps to a typed `Settings` field, preventing future silent template drift.

## Impact

- Configuration honesty: **Corrected** — the environment template advertises
  only settings that MaterialGraph actually accepts.
- Runtime behavior: **Unchanged** — Materials Project access continues through
  the official client configuration already used in production.
- API key handling: **Unchanged** — `MATERIALS_PROJECT_API_KEY` remains the
  supported credential variable.
- Import behavior: **Unchanged** — material fetching, normalization,
  persistence, validation, and transaction handling are unaffected.
- Deployment: **No action required** — deployed environments did not consume
  `MP_API_URL`.
- Regression prevention: **Improved** — future advertised keys without typed
  settings support fail project-configuration tests.
- Database schema and stored data: **No change**.

## Scope decision

The remediation removes a false contract instead of adding configurable
endpoint/proxy behavior that MaterialGraph does not currently require. Such a
feature can be introduced later only with an explicit typed setting, supported
client wiring, tests, and deployment documentation.
