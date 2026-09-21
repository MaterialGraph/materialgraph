# Neighborhood API Performance Remediation

**Status:** Local implementation and acceptance benchmarking complete

**Scope:** `GET /api/v1/materials/{material_id}/neighborhood`

**Production access or mutation:** None

## Outcome

The neighborhood traversal now preloads neighbor inputs once per BFS level and
then applies the existing sequential admission, scoring, ordering, edge
closure, and response assembly logic. For the production-count synthetic
fixture, the default depth-two request fell from 150 SQL queries to 12 while
producing the same 9,657-byte payload and payload SHA-256.

| Measurement | Diagnostic baseline | Remediation | Result |
|---|---:|---:|---:|
| SQL queries | 150 | 12 | 92% reduction |
| Warm median service latency | 1,638.338 ms | 342.218 ms | 4.79× faster |
| 100 ms/query sensitivity | 16,749.582 ms | 1,756.175 ms | 9.54× faster |
| Payload | 9,657 bytes | 9,657 bytes | unchanged |
| Payload SHA-256 | `50f22e...fd11` | `50f22e...fd11` | unchanged |

The committed machine-readable results are in
`docs/performance/neighborhood_api_remediation_benchmark.json`.

## Implementation

`MaterialNeighborService.get_neighbors_batch()`:

1. fetches all requested source materials;
2. fetches their element memberships;
3. fetches their application memberships;
4. fetches matching element associations once for the batch;
5. fetches matching application associations once for the batch; and
6. fetches all resulting neighbor materials once.

It reconstructs the same per-source score dictionaries and delegates neighbor
construction to the existing `_build_neighbors()` and score formula.

`MaterialNeighborhoodService` batches only data loading. It still processes
each frontier material and each ranked neighbor in the same deterministic BFS
sequence. Batching therefore does not change which material is admitted when
the node limit is reached.

## Semantic evidence

- Batched neighbor results equal the legacy single-material results across
  shared-element, shared-application, combined, isolated, null-valued, and
  missing-material cases.
- Tied rankings remain resolved by material ID.
- Existing depth, node-limit, deterministic-order, edge-closure, and count
  tests pass with the batch-call boundary asserted.
- Four production-count default benchmark runs were identical.
- The default endpoint payload hash exactly matches the diagnostic baseline.
- Payload hashes at limits 1, 5, 10, 25, 50, and 100 are deterministic.

## Acceptance results

All locally executable acceptance gates passed:

- depth-two query count is 12 and does not grow with limits above one;
- default warm median is below 500 ms;
- default response at 100 ms simulated query latency is below 3 seconds;
- serialization remains below 5 ms;
- payload compatibility is unchanged; and
- limits 50 and 100 complete below the 20-second request deadline.

The limit-100 request completed in 1,720.358 ms warm and 2,823.650 ms with
100 ms simulated latency.

## Remaining boundary

Disposable local PostgreSQL validation on the exact accepted 1,727-material
manifest is recorded in [the PostgreSQL evidence](neighborhood_api_postgresql_validation.md).
The default local PostgreSQL warm median was 552.501 ms without Python memory
tracing, so the synthetic SQLite 500 ms gate must not be represented as a
PostgreSQL pass. No production-latency claim, concurrency claim, deployment,
restart, production read, schema change, migration, or index change is included.
