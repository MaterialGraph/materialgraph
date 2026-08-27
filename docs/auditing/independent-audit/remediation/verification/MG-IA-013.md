# MG-IA-013 Remediation Verification

## Title

Scenario element parameters require canonical periodic-table membership

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. Required scenario `element` rejects nonexistent one- and two-letter symbols.
2. Optional `avoid_element` and `prefer_element` reject the same invalid values.
3. Valid lowercase and permitted whitespace-padded values normalize to
   canonical symbols before scenario evaluation.
4. Scenario and discovery endpoints expose the same structured HTTP 422
   unknown-symbol contract.
5. The element-symbol predicate uses authoritative periodic-table membership.
6. Existing formula extraction, scenario recommendation, discovery validation,
   and periodic-table behavior remain regression-safe.
7. No deprecated HTTP status constant or unused route import remains.
8. The complete test suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `a5f2eed`.
`is_valid_element_symbol` still accepted any value matching
`^[A-Z][a-z]?$`, while `normalize_element_symbol` checked the authoritative
`ELEMENT_SYMBOLS` set. The scenario route used the former for all three public
element parameters; discovery filters used the latter. Scenario API tests had
no coverage for well-shaped nonexistent symbols. The frozen finding therefore
remained fully applicable.

## Implemented changes

- Added reusable required and optional API element-parameter normalizers.
- Preserved the existing structured `unknown_element_symbol` response shape.
- Routed scenario `element`, `avoid_element`, and `prefer_element` through the
  shared canonical normalizer before invoking the recommendation service.
- Changed `is_valid_element_symbol` from regex-only shape validation to
  authoritative `ELEMENT_SYMBOLS` membership.
- Added scenario coverage for normalization and invalid `Q`/`Xx` inputs across
  all three parameters.
- Added discovery contract coverage for the same nonexistent symbols.
- Added direct predicate membership tests.
- Replaced the deprecated 422 constant with
  `HTTP_422_UNPROCESSABLE_CONTENT` and removed the obsolete route import.

## Verification results

Commands included:

```powershell
pytest tests/api/test_material_scenario_recommendations_api.py tests/api/test_discovery_validation_api.py tests/utils/test_chemical_formula.py tests/domain/test_periodic_table.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused and adjacent validation tests: **188 passed in 2.67 seconds** during
  implementation;
- final complete test suite: **711 passed in 35.20 seconds**;
- Ruff after removal of the obsolete `HTTPException` import: **passed**;
- Git whitespace validation: **passed**.

The initial focused run exposed a deprecated Starlette status-constant warning.
The implementation was updated to the current constant before final full-suite
and lint verification.

## Change boundary

The verified implementation boundary contains six files:

- `app/api/dependencies/element_filters.py`
- `app/api/v1/routes/material_neighbors.py`
- `app/utils/chemical_formula.py`
- `tests/api/test_discovery_validation_api.py`
- `tests/api/test_material_scenario_recommendations_api.py`
- `tests/utils/test_chemical_formula.py`

## Conclusion

All acceptance criteria are satisfied. `MG-IA-013` is verified as remediated.

