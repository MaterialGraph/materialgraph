# MG-IA-004 — Criticality element ordering is nondeterministic for tied scores

- Classification: determinism and API-output risk
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Evidence

Material-element queries have no `ORDER BY`. `_build_criticality_response()` sorts only by whether a score exists and the numeric score. Equal scores and multiple unknown scores retain the unspecified database row order.

Affected file/functions: `app/services/material/criticality_service.py:get_material_criticality`, `get_material_criticality_bulk`, and `_build_criticality_response`.

## Expected versus actual

Identical data should produce a stable ordered response. Equal-key elements can change order with query plans, physical row order, or maintenance.

## Impact

API output, snapshots, explanations, comparisons, and reproducibility records can differ without scientific-data changes.

## Tests

Existing tests cover numeric and evidence behavior but not tied known scores, multiple unknown elements, or scalar/bulk tie-order parity.

## Caller trace

`MaterialQualityService` consumes scalar and bulk criticality results. The criticality response schema publicly models the ordered `elements` list. The exact FastAPI route remains to be identified.

## Reproduction

Create at least two elements with equal calculated criticality scores, vary insertion/returned query order, and compare the serialized `elements` sequence.

## Remediation scope

Add an explicit stable secondary key such as symbol and ID. Preserve legitimate ties; do not alter weights to remove them.
