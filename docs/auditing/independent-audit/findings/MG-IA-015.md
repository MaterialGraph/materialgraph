# MG-IA-015 — Weighted shortest path silently searches only one hop

- Classification: graph-algorithm contract and reachability defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/services/discovery/graph_algorithms_service.py`
- `app/services/discovery/graph_builder.py`
- graph-algorithm tests and callers

## Exact evidence

`weighted_shortest_path(max_depth=N)` passes `N` to `DiscoveryGraphBuilder.build_graph`. In normal mode, `build_graph` immediately clamps depth through `get_effective_max_depth` and `MAX_ALLOWED_DEPTH = 1`. The weighted search then runs over that one-hop graph while its own loop and returned contract continue to use the caller's larger `max_depth`.

Unweighted `shortest_path`, BFS, DFS, and K-best paths use `build_adjacency`, which does not apply the one-hop clamp. The same depth parameter therefore has different reachability semantics across algorithms.

The supplied two-hop weighted-path test monkeypatches `build_graph` with a handcrafted graph, bypassing the real clamp; it proves the heap search can consume a two-hop graph but not that production construction supplies one.

## Expected versus actual

When weighted shortest path accepts `max_depth=2` or `3`, it should search paths up to that depth or explicitly return an effective-depth/truncation contract. It currently searches only direct edges without disclosure.

## Impact

Reachable multi-hop targets can be reported unreachable by the weighted algorithm while unweighted and K-best algorithms find them under the same requested depth. This undermines cross-service consistency and explainability.

## Reproduction

Construct a graph where the target is reachable only through `start -> intermediate -> target`. Call the real weighted service with `max_depth=2`. `build_graph` clamps to one, so the intermediate's outgoing edge is absent and `path_found` is false. Calling unweighted shortest path over `build_adjacency(max_depth=2)` can return the path.

## Tests

Existing database-backed weighted coverage uses depth one. The two-hop unit test replaces graph construction and cannot detect the integration defect. Missing regression coverage should use the real builder or assert the effective depth passed through the complete service.

## Recommended remediation scope

Unify graph-construction depth semantics across algorithms, or expose requested/effective depth and truncation explicitly. Add end-to-end parity tests for one-, two-, and three-hop reachability and for intentional deployment caps.
