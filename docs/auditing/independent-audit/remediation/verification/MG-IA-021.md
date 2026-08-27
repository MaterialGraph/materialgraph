# MG-IA-021 Remediation Verification

## Title

Every advertised environment key maps to a supported typed setting

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. `.env.example` no longer advertises unsupported `MP_API_URL` behavior.
2. `MATERIALS_PROJECT_API_KEY` remains advertised and mapped to `Settings`.
3. Every active key in `.env.example` maps to a typed `Settings` field.
4. Getting-started documentation retains the canonical Materials Project API
   key name.
5. Materials Project document normalization remains unchanged.
6. Material import creation, deduplication, composition validation, rollback,
   and session reuse remain regression-safe.
7. The complete test suite and lint checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `c9031f0`.
`.env.example` still contained `MP_API_URL=`, while `Settings` had no
`mp_api_url` field and used `extra="ignore"`. `MaterialsProjectService` accepted
only an API key, the import script forwarded only that key, and setup/deployment
documentation did not define endpoint override support. The frozen finding
therefore remained fully applicable.

## Implemented changes

- Removed `MP_API_URL=` from `.env.example`.
- Preserved all five supported advertised settings.
- Added a project-configuration test that parses active environment-template
  keys and requires them to be a subset of `Settings.model_fields`.
- Added an explicit assertion preventing unsupported `MP_API_URL` from being
  silently re-advertised.
- Made no runtime, service, script, dependency, or deployment change.

## Verification results

Commands:

```powershell
pytest tests/test_project_configuration.py -v
pytest tests/services/material/test_materials_project_service.py tests/services/material/test_material_import_service.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused project-configuration tests: **6 passed in 0.17 seconds**;
- adjacent Materials Project and import tests: **16 passed in 4.93 seconds**;
- complete test suite: **690 passed in 20.75 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; an LF-to-CRLF informational notice
  was reported for `.env.example`.

## Change boundary

The verified implementation boundary contains two files: `.env.example` and
`tests/test_project_configuration.py`. No runtime or deployment file changes
are required.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-021` is verified as remediated.
