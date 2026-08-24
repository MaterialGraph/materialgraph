# MG-IA-012 — Neighbor ties make bounded neighborhood membership nondeterministic

- Classification: determinism and graph-result defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/services/material/neighbor_service.py`
- `app/services/material/neighborhood_service.py`
- `tests/services/test_neighborhood_service.py`
- neighbor, neighborhood, and downstream similarity components

## Exact evidence

`MaterialNeighborService.get_neighbors` sorts by neighbor score, shared-application count, and shared-element count, all descending, but supplies no final material identifier key. Candidate discovery queries have no database `ORDER BY`, so complete ties retain unspecified row/insertion order.

`MaterialNeighborhoodService` consumes neighbors in that order and admits the first encountered nodes until `limit` is reached. Consequently, tied neighbor order can change which material IDs are admitted and expanded. Its edge sort also uses only `edge_score`, leaving tied returned edges dependent on encounter order.

The supplied deterministic-traversal test runs twice over the same preordered mock response; it does not permute complete ties and therefore cannot detect this database-order dependency.

## Expected behavior

Identical persisted state and request parameters must produce stable neighbor ordering, bounded-neighborhood membership, expansion order, and edge order. Complete ties require a documented stable key such as ascending material ID and deterministic edge endpoint keys.

## Actual behavior

Complete neighbor and edge ties preserve unspecified query/encounter order. When a limit truncates the neighborhood, this affects membership rather than presentation alone.

## Technical impact

Repeated requests or database-plan changes can produce different graph nodes and edges from identical data. Downstream explanations, caches, comparisons, and traversal results can therefore vary without a scientific-data change.

## Reproduction

Create more equally scored root neighbors than the requested node limit. Return or insert those rows in different orders. The service admits different material IDs because the sort keys are identical and no ID key resolves the tie. The same construction with equally scored edges changes their returned order.

## Existing and missing tests

Similarity, recommendation, and family tests explicitly protect final material-ID tie-breakers. The neighborhood deterministic test does not exercise permuted complete ties, and the neighbor API test checks only response shape. Missing regression coverage should permute equally scored candidates and assert identical neighbor lists, neighborhood membership, expansion calls, and edge ordering.

## Recommended remediation scope

Add an explicit ascending material-ID tie-breaker to neighbor ranking and deterministic source/target keys to edge ranking. Document the ordering policy and add permutation-based regression tests at both service and API levels.
