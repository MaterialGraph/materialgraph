# Test File Inventory Evidence

## Method

This ledger accounts for supplied test modules during the independent-audit closure pass. Files are syntax-compiled, exact repeats are hash-compared with previously reviewed copies, and newly supplied tests are inspected for the contracts they establish and the material boundaries they omit. Tests were not executed in this workspace because the exact checkout and configured test database are unavailable.

## `tests/api/` — complete supplied directory

Fourteen API test modules were supplied and syntax-compiled. Eleven are byte-for-byte identical to copies previously reviewed in their component stacks:

- `test_comparison_api.py`
- `test_discovery_candidates.py`
- `test_discovery_validation_api.py`
- `test_graph_jobs_api.py`
- `test_material_families_api.py`
- `test_material_neighbors_api.py`
- `test_material_risks_api.py`
- `test_material_scenario_recommendations_api.py`
- `test_research_objective_exploration_api.py`
- `test_research_routes.py`
- `test_scenario_ranking_api.py`

Three API tests were newly available in this closure batch:

| Test file | Positive evidence | Material missing coverage |
|---|---|---|
| `test_discovery_chains_api.py` | Confirms a valid existing-root response, echoed objective fields, result/state budgets, incomplete scientific-coverage disclosure, returned-count reconciliation, and hop-depth bound. | Does not exercise a nonexistent root, so it does not protect the expected 404 contract in `MG-IA-020`; it also does not test state-budget truncation or deterministic ordering under ties. |
| `test_sensitivity_api.py` | Confirms a valid response shape and 404 for a missing material. | Only asserts nonnegative baseline fields and four scenarios. It does not recompute scenario deltas through the baseline aggregation formula and therefore does not detect `MG-IA-010`; unknown/partial risk and component coverage are also absent. |
| `test_substitutions_api.py` | Confirms a bounded nonempty happy-path response, basic explanation fields, and 404 for a missing material. | Does not test `top_n` boundaries, deterministic tied ordering, unknown risk, incomplete stability evidence, or explanation/score reconciliation. Service-level tests cover some—but not all—of those semantics. |

## Directory-level disposition

The complete supplied `tests/api/` directory is accounted for. It establishes useful route registration, success-shape, selected validation, and missing-resource behavior. It does not constitute proof of cross-endpoint consistency or scientific correctness; known gaps remain attached to their existing findings and observations. No new `MG-IA` finding is established solely by this test-directory review.
