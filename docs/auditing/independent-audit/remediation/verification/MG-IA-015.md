# MG-IA-015 Remediation Verification

## Title

Weighted and public path searches construct graphs to their effective depth

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. A requested two-hop weighted search receives a graph containing validated
   second-hop edges.
2. Weighted search and graph construction use the same effective depth.
3. The public discovery-path service selects multi-hop path construction.
4. Path-search construction supports the public one-to-three-hop boundary.
5. Requests beyond the internal weighted helper cap are explicitly truncated
   rather than silently misrepresented.
6. Weighted success and failure results disclose requested depth, effective
   depth, and truncation state.
7. The normal graph-response cap remains one hop.
8. The analytics cap remains two hops.
9. Conflicting graph-construction modes are rejected.
10. Existing traversal, analytics, K-best, ranking, and API behavior remains
    regression-safe.

## Current-baseline confirmation

The finding was re-evaluated against GitHub commit `94fcb35` before
implementation. Current `weighted_shortest_path()` passed the caller's depth to
normal `build_graph()`, which reduced it through `MAX_ALLOWED_DEPTH = 1`.
`DiscoveryTraversalService.get_path()` also used normal graph construction.
The heap/BFS loops retained the larger caller limit, and the existing weighted
two-hop regression replaced `build_graph`, so the production mismatch remained
applicable.

## Implemented changes

- Added a distinct `path_search_mode` to `DiscoveryGraphBuilder`.
- Added `MAX_PATH_SEARCH_DEPTH = 3`, aligned with the existing path API bound.
- Preserved standard and analytics caps at one and two hops respectively.
- Rejected simultaneous analytics and path-search modes.
- Computed weighted effective depth before graph construction and used that
  same value in heap expansion.
- Added requested/effective depth and truncation metadata to weighted results.
- Selected path-search mode in `DiscoveryTraversalService.get_path()`.
- Added a production-builder regression whose target exists only through
  `5 -> 6 -> 7` and is found with `max_depth=2`.
- Added cap-disclosure, mode-boundary, conflict, and public-caller regressions.

## Reproduction after remediation

The focused real-builder test limits candidates to `5 -> 6` and `6 -> 7` and
uses the actual `DiscoveryGraphBuilder.build_graph()` implementation. Weighted
search with depth two returns `[5, 6, 7]`, hop count two, and cost two. This
directly covers the integration path that the former handcrafted-graph test
could not exercise.

## Verification results

Commands:

```powershell
pytest tests/services/discovery/test_discovery_graph_builder.py tests/services/discovery/test_discovery_graph_algorithms_service.py tests/services/discovery/test_discovery_traversal_service.py -v
pytest tests/services/discovery/test_discovery_graph_analytics_service.py tests/services/discovery/test_discovery_k_best_path_service.py tests/services/discovery/test_discovery_path_ranking_service.py tests/api/test_discovery_validation_api.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused graph-builder, graph-algorithm, and traversal tests:
  **36 passed in 1.47 seconds**;
- adjacent analytics, K-best, path-ranking, and validation API tests:
  **56 passed in 2.04 seconds**;
- complete test suite: **667 passed in 18.19 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

The suite increased from 663 to 667 tests through four new graph-depth and
weighted-integration regressions. Two existing public-path tests were extended
to verify selection of path-search mode.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-015` is verified as remediated.
