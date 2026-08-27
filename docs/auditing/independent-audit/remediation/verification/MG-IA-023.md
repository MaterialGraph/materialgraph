# MG-IA-023 Remediation Verification

## Title

README distinguishes internal graph-job primitives from public routes

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. The README no longer advertises PostgreSQL-backed graph-job routes as a
   current public capability.
2. The README accurately identifies the implemented graph-job persistence and
   lifecycle primitives.
3. The README explicitly discloses that public graph-job routes are
   intentionally unregistered.
4. The public OpenAPI schema contains no graph-job paths.
5. A regression test binds the documentation claim to the actual API surface.
6. No router, service, schema, database, or deployment behavior changes.
7. The complete test suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `52f1c20`.
`README.md` still listed “PostgreSQL-backed graph-job routes and persistence”
under “Current Capabilities — v1.9.6”. In `app/api/v1/api.py`, both the
graph-job router import and registration remained commented out. The dormant
router used the `/graph-jobs` prefix, and the registered application exposed
no matching OpenAPI path. The frozen finding remained fully applicable.

## Implemented changes

- Replaced the inaccurate graph-job route capability claim with an accurate
  description of persistence and lifecycle primitives.
- Documented why public graph-job routes remain intentionally unregistered.
- Added a project-configuration test that asserts the OpenAPI graph-job path
  set is empty.
- Added a documentation assertion that rejects the former claim and requires
  the explicit non-public disclosure.

## Verification results

Commands:

```powershell
pytest tests/test_project_configuration.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused configuration verification: **7 passed in 0.66 seconds**;
- complete test suite: **720 passed in 18.08 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; the reported LF-to-CRLF message was
  an informational working-tree conversion warning, not a diff error.

## Change boundary

The verified implementation boundary contains two modified files:
`README.md` and `tests/test_project_configuration.py`. It makes no runtime,
model, migration, seed-data, or deployment change.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-023` is verified as remediated.
