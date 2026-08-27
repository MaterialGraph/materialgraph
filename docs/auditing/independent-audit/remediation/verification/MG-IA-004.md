# MG-IA-004 Remediation Verification

## Title

Criticality element ties have a stable total ordering

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. Elements with calculable criticality remain ahead of unknown elements.
2. Known element criticality scores remain ordered descending.
3. Equal known scores resolve by ascending symbol and element ID.
4. Multiple unknown elements resolve by ascending symbol and element ID.
5. Permuting tied input rows produces identical serialized element output.
6. Scalar and bulk criticality continue using the same response builder.
7. Criticality values, evidence metadata, quality consumers, and API schemas
   remain regression-safe.
8. The complete test suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `118258b`.
Material-element queries still supplied no ordering, and
`_build_criticality_response` sorted only on known status and numeric score with
`reverse=True`. Complete known-score ties and multiple unknown scores therefore
retained unspecified encounter order. Both scalar and bulk methods still used
that shared builder, and the public route was confirmed as
`GET /materials/{material_id}/criticality`. The frozen finding remained fully
applicable.

## Implemented changes

- Replaced the partial reverse sort with an explicit known-first tuple key.
- Preserved descending numeric score for known criticality evidence.
- Added ascending symbol and element ID as stable final keys.
- Added a regression containing two equal known scores and two unknown scores.
- Evaluated reversed and canonical row permutations and required identical
  ordered element details.
- Made no query, weight, aggregation, evidence, schema, or caller change.

## Verification results

Commands included:

```powershell
pytest tests/services/material/test_criticality_service.py -v
pytest tests/services/material/test_material_quality_service.py tests/services/material/test_material_risk_service.py tests/api/test_material_neighbors_api.py -v
pytest -q
ruff check .
git diff --check
```

Recorded final results:

- complete test suite: **717 passed in 15.21 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

## Change boundary

The verified implementation boundary contains two files:

- `app/services/material/criticality_service.py`
- `tests/services/material/test_criticality_service.py`

## Conclusion

All acceptance criteria are satisfied. `MG-IA-004` is verified as remediated.

