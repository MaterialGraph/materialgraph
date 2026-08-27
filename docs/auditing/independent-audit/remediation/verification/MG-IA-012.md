# MG-IA-012 Remediation Verification

## Title

Complete neighbor ties have stable material and edge ordering

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. Neighbor ranking preserves the existing scientific score hierarchy.
2. Complete neighbor ties resolve by ascending material ID.
3. Permuting tied candidates cannot change bounded-neighborhood membership.
4. Permuting tied candidates cannot change expansion order or calls.
5. Tied returned edges resolve by ascending source and target material IDs.
6. The public neighbor API returns identical ordering for permuted complete
   ties.
7. Existing neighborhood limits, depth semantics, edge filtering, similarity,
   and recommendation behavior remain regression-safe.
8. The complete test suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `c5d21ca`.
`MaterialNeighborService` still sorted only by neighbor score, shared-
application count, and shared-element count with `reverse=True`.
`MaterialNeighborhoodService` consumed that encounter order for bounded
admission and expansion, while its edge ordering used only descending edge
score. The existing deterministic test repeated one preordered mock response
without permuting complete ties. The frozen finding therefore remained fully
applicable.

## Implemented changes

- Added a shared neighbor-ranking key with descending score and relationship
  counts followed by ascending material ID.
- Applied that key to `MaterialNeighborService` output.
- Applied the same key defensively before neighborhood admission and expansion.
- Added source- and target-material-ID keys to tied edge ordering.
- Added a neighbor-service permutation regression for complete ties.
- Replaced the same-order neighborhood test gap with permutation evidence for
  stable membership, expansion calls, and edge ordering.
- Added public neighbor API permutation coverage.

## Verification results

Commands included:

```powershell
pytest tests/services/material/test_neighbor_service.py tests/services/material/test_neighborhood_service.py tests/api/test_material_neighbor_determinism_api.py tests/api/test_material_neighbors_api.py -v
pytest tests/services/material/test_similarity_service.py tests/services/material/test_recommendation_service.py tests/api/test_material_recommendations_api.py tests/api/test_material_scenario_recommendations_api.py -v
pytest -q
ruff check .
git diff --check
```

Recorded final results:

- complete test suite: **716 passed in 16.62 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

## Change boundary

The verified implementation boundary contains five files:

- `app/services/material/neighbor_service.py`
- `app/services/material/neighborhood_service.py`
- `tests/services/material/test_neighborhood_service.py`
- `tests/services/material/test_neighbor_service.py` (new)
- `tests/api/test_material_neighbor_determinism_api.py` (new)

## Conclusion

All acceptance criteria are satisfied. `MG-IA-012` is verified as remediated.

