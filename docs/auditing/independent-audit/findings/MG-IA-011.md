# MG-IA-011 — Neighborhood limit does not bound graph expansion

- Classification: boundedness and query-amplification defect
- Priority: P1
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/services/material/neighborhood_service.py`
- `app/services/material/neighbor_service.py`
- `tests/services/test_neighborhood_service.py`
- `GET /api/v1/materials/{material_id}/neighborhood`

## Exact evidence

`MaterialNeighborhoodService.get_neighborhood` refuses to add a newly encountered neighbor when `len(nodes) >= limit`, but it subsequently appends that same neighbor to `visited` and `frontier` outside the admission branch. At the next breadth-first iteration, `_get_neighbors` loads the excluded material's complete neighbor set.

The route describes the result as a bounded graph neighborhood and exposes `limit` as the maximum number of neighborhood materials. More decisively, `test_limit_bounds_neighbor_expansion` requires a limit of two to call the neighbor service only for materials 1 and 2, while `test_limit_one_does_not_expand_descendants` requires only the root call. The supplied implementation violates both expectations: excluded root neighbors are still queued and expanded.

## Expected behavior

Once the node budget is exhausted, materials not admitted to the bounded neighborhood must not be queued or expanded. Work should remain bounded by the admitted traversal set and the explicit depth cap.

## Actual behavior

The response is filtered to at most `limit` nodes, but traversal work is not. At depth two, every root neighbor can be queried even when `limit=1`, and each query can retrieve an unbounded neighbor collection.

## Technical impact

The public limit provides a false operational bound. High-degree materials can cause avoidable database-query amplification and large intermediate edge collections, increasing latency and resource use despite a very small requested result.

## Reproduction

Use the supplied `_service()` fixture from `test_neighborhood_service.py`. For `material_id=1`, `depth=2`, and `limit=2`, the implementation queues both neighbors 2 and 3 even though only 2 is admitted. The mock therefore receives `get_neighbors(3)`, contradicting the asserted call list `[call(1), call(2)]`. With `limit=1`, both root neighbors are still queued, contradicting the expected single root call.

## Existing and missing tests

Existing tests state the correct bounded-expansion contract and should fail against the supplied implementation. Additional regression coverage should use a wide first-hop fan-out and assert query count, frontier size, intermediate edge growth, and behavior at limits 1 and N.

## Recommended remediation scope

Queue and emit edges only for nodes admitted under the node budget, or define another explicit bounded-selection algorithm before expansion. Preserve the depth cap, document whether the root counts toward `limit`, and run the existing boundedness tests plus a wide-fan-out regression.
