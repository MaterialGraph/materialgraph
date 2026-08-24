# MG-IA-021 — Advertised Materials Project API URL setting is silently ignored

- Classification: configuration-contract defect
- Priority: P3
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `.env.example`
- `app/core/config.py`
- `app/services/material/project_service.py`
- project-configuration tests and setup documentation

## Exact evidence

`.env.example` advertises `MP_API_URL=` as a supported environment variable. `Settings` declares `project_name`, `environment`, `database_url`, `materials_project_api_key`, and `log_level`, but no `mp_api_url`; its `SettingsConfigDict` uses `extra="ignore"`. Consequently, `MP_API_URL` is silently discarded during settings construction.

`MaterialsProjectService` accepts only `api_key` and creates `MPRester(self.api_key)` without reading a configured endpoint. Repository-wide search of the supplied implementation finds no consumer of `MP_API_URL` outside `.env.example`.

## Expected versus actual

Variables advertised by the canonical environment template should either configure the application or be clearly marked as unused/reserved. `MP_API_URL` currently appears usable but has no runtime effect and produces no validation error or warning.

## Impact

Operators can reasonably believe they have selected a Materials Project endpoint, proxy, test service, or alternate environment while the application continues using the client library default. This creates silent configuration drift and makes endpoint-dependent testing or deployment behavior misleading.

## Reproduction

Set `MP_API_URL` to any distinct value and construct `Settings`; the value is ignored because it is an extra field. Construct `MaterialsProjectService`; only an API key can be supplied, and `MPRester` receives no URL derived from settings.

## Caller trace

The import script reads `settings.materials_project_api_key` and creates `MaterialsProjectService` with that key. The service creates `MPRester` directly. No intermediate configuration layer reads or forwards `MP_API_URL`.

## Tests

The supplied project-configuration test verifies `MATERIALS_PROJECT_API_KEY` alignment across `Settings`, `.env.example`, and getting-started documentation. It does not verify that every advertised environment key maps to a settings field or runtime consumer. No test exercises a configurable Materials Project URL.

## Recommended remediation scope

Choose one explicit contract: remove `MP_API_URL` from `.env.example` and related documentation if endpoint configuration is unsupported, or add a typed settings field and deliberately pass it through the supported `mp-api` client mechanism. Add a configuration test that accounts for every advertised environment variable and, if URL configuration is retained, a service test proving that the selected endpoint reaches the client constructor.
