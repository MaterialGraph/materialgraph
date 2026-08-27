# MG-IA-020 Remediation Verification

## Title

Chain-derived material APIs return 404 for nonexistent root materials

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. Discovery chains return HTTP 404 for a nonexistent root material.
2. Objective chains return HTTP 404 for a nonexistent root material.
3. Objective exploration returns HTTP 404 for a nonexistent root material.
4. Scientific pathway analysis returns HTTP 404 for a nonexistent root
   material.
5. All affected endpoints use the same error detail.
6. Existence is determined by exact primary-key lookup, not nullable response
   fields.
7. Existing-material requests retain successful behavior.
8. Internal discovery-chain and scientific-pathway services retain safe empty
   result semantics.
9. Adjacent families, neighbors, risks, and candidates resource behavior
   remains regression-safe.
10. The complete test suite and lint checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `30512e5`.
`DiscoveryChainService` still returned an empty sentinel for a missing root,
and the basic chain, objective-chain, objective-exploration, and scientific-
pathway routes returned their service results without a material existence
check. The frozen finding therefore remained fully applicable.

## Implemented changes

- Added `ensure_material_exists(db, material_id)` to the shared route utility.
- Used `Session.get(Material, material_id)` for exact indexed existence lookup.
- Applied the helper before discovery-chain generation.
- Applied the helper before objective-chain generation.
- Applied the helper before objective exploration.
- Applied the helper before scientific pathway analysis.
- Added API regressions for all four missing-material endpoints.
- Preserved the existing result-based `ensure_material_found()` helper for
  endpoints whose response contracts already expose resource identity.
- Preserved internal service empty-response behavior.

## Verification results

Commands included:

```powershell
pytest tests/api/test_discovery_chains_api.py tests/api/test_research_objective_exploration_api.py tests/api/test_research_routes.py -v
pytest tests/services/discovery/test_discovery_chain_service.py tests/services/research/test_scientific_pathway_analysis_service.py -v
pytest tests/api/test_material_families_api.py tests/api/test_material_neighbors_api.py tests/api/test_material_risks_api.py tests/api/test_discovery_candidates.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- all focused missing-material API tests: **passed**;
- all internal empty-sentinel service tests: **passed**;
- all adjacent material resource-semantics tests: **passed**;
- complete test suite: **689 passed in 18.08 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

## Change boundary

The verified implementation boundary contains six files: the shared route
utility, two route modules, and three API test modules. No service, response
schema, database, or migration change is required.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-020` is verified as remediated.
