# Neighborhood API Performance Diagnosis

**Status:** Diagnosis complete; no remediation implemented

**Scope:** `GET /api/v1/materials/{material_id}/neighborhood`

**Trigger:** MG-DE-009 production observation of `16,242.222 ms`

**Diagnostic checkout:** `918abe01c444e5346b6e895dc42d2d7037f718f7`

**Production access or mutation:** None

## Decision summary

The primary cause is a request-scoped N+1 query pattern in depth-two
neighborhood traversal, amplified by dense association materialization and
remote database round trips.

For the default local diagnostic request (`material_id=1`, `depth=2`,
`limit=25`), the service admitted 25 nodes and called
`MaterialNeighborService.get_neighbors()` 25 times. Each call issued six SQL
queries, producing 150 queries for a 25-node response. The same fixture at
`depth=1`, `limit=25` returned a similarly sized payload after only the root
expansion: six queries and an 81.794 ms warm median rather than 150 queries and
1,638.338 ms.

On the local fixture, adding 100 ms of artificial delay before each SQL
execution increased end-to-end latency from 1,697.022 ms to 16,749.582 ms,
close to the independent MG-DE-009 production observation. This sensitivity
test is not a production measurement, but it supports the causal conclusion:
query round-trip multiplication explains the remote-scale symptom.

Serialization, response size, and final neighborhood graph assembly are not
material causes at the measured scale. Serialization was approximately
0.2 ms, the JSON payload was 9,657 bytes, and final graph work outside neighbor
calls was approximately 25 ms.

## Boundaries and method

The diagnosis used:

- a deterministic synthetic fixture with the production material count of
  1,727;
- 4,144 material-element rows and 128 material-application rows, including a
  deliberately dense common-element neighborhood;
- a disposable local SQLite database guarded by a required
  `neighborhood_perf_test` filename;
- sequential requests only;
- one cold and three warm service measurements for the primary request;
- SQLAlchemy query instrumentation;
- separate measurements for service execution, database execution events,
  neighbor construction/scoring, graph assembly, Pydantic serialization,
  payload size, and FastAPI end-to-end latency; and
- controlled per-query delay of 0, 25, 50, and 100 ms to measure sensitivity
  to remote round trips.

The committed diagnostic runner is
`scripts/diagnose_neighborhood_performance.py`. It refuses PostgreSQL and any
SQLite database whose name does not contain `neighborhood_perf_test`.

The fixture matches production row count, not the exact Materials Project
cohort. SQLite does not reproduce PostgreSQL execution plans, Neon transport,
or production-host capacity. The MG-DE-009 report does not retain the exact
neighborhood query parameters, so this diagnosis exercises the endpoint
defaults. No concurrency or load conclusion is made.

## Primary benchmark

Default request: `material_id=1`, `depth=2`, `limit=25`.

| Measurement | Result |
|---|---:|
| Materials | 1,727 |
| Returned nodes / edges | 25 / 25 |
| Neighbor-service calls | 25 |
| SQL queries | 150 |
| Queries per expanded node | 6 |
| Warm median service latency | 1,638.338 ms |
| Median direct SQL execution time | 9.874 ms |
| Median neighbor build/scoring | 254.379 ms |
| Median query materialization/collection estimate | 1,455.240 ms |
| Median final graph assembly estimate | 24.610 ms |
| Serialization | 0.162–0.190 ms warm |
| Payload | 9,657 bytes |
| Repeated-result equality | Exact |

`database_execute_ms` measures cursor execution callbacks and does not include
all ORM row fetching, object construction, and Python aggregation. Those costs
are represented in the materialization/collection estimate. This distinction
prevents the small cursor-execution number from being misread as the complete
database-related cost.

### Limit and depth scaling

| Depth | Limit | Neighbor calls | SQL queries | Warm median service ms | Payload bytes |
|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 1 | 6 | 66.519 | 336 |
| 2 | 5 | 5 | 30 | 298.746 | 2,043 |
| 2 | 10 | 10 | 60 | 649.084 | 3,945 |
| 2 | 25 | 25 | 150 | 1,638.338 | 9,657 |
| 2 | 50 | 50 | 300 | 4,538.827 | 19,262 |
| 1 | 25 | 1 | 6 | 81.794 | 9,454 |

The query count is exactly `6 × expanded nodes` in this fixture. At depth one,
only the root is expanded even though 25 nodes are returned. At depth two,
every admitted node is expanded, making latency scale with the response limit.

### Remote-round-trip sensitivity

| Artificial delay per query | SQL queries | End-to-end ms | Payload SHA-256 unchanged |
|---:|---:|---:|:---:|
| 0 ms | 150 | 1,697.022 | Yes |
| 25 ms | 150 | 5,514.719 | Yes |
| 50 ms | 150 | 9,325.920 | Yes |
| 100 ms | 150 | 16,749.582 | Yes |

The added latency closely follows `query count × delay`. As an inference, the
MG-DE-009 value is consistent with roughly 97 ms of effective additional cost
per query after subtracting this local fixture's no-delay endpoint time. This
is explanatory sensitivity evidence, not a measurement of Neon latency.

## Query and computation path

Each expanded material currently performs:

1. material lookup;
2. source material-element lookup;
3. source material-application lookup;
4. all matching material-element association loading;
5. all matching material-application association loading; and
6. neighbor material loading.

The neighborhood cache prevents duplicate expansion of the same material in a
single request, but it does not batch different admitted materials. Dense
common elements therefore cause large association result sets to be loaded and
aggregated repeatedly. Deterministic sorting and bounded admission correctly
control returned membership; they do not make the underlying data access
set-oriented.

## Root causes

### RC-1 — Per-node SQL expansion (high confidence)

Depth-two traversal performs six queries for every admitted node. Query count
therefore grows with `limit`, reaching 150 at the default limit and 300 at 50.
The controlled-delay experiment reproduces the observed latency class.

### RC-2 — Repeated dense association materialization (high confidence)

The local no-delay request still takes about 1.6 seconds. Most measured time is
inside neighbor collection and ORM materialization, not final graph assembly.
Each expansion reloads broad shared-element rows and reconstructs neighbor
scores in Python.

### RC-3 — Payload and serialization (ruled out at this scale)

The response is under 10 KiB at the default limit and serialization takes less
than 0.3 ms. Depth-one and depth-two payload sizes are similar while service
latencies and query counts differ sharply.

### RC-4 — Final graph assembly and deterministic ordering (secondary only)

Final graph assembly is approximately 25 ms at the default request. Sorting
and closure filtering must remain intact, but they do not explain 16.2 seconds.

## Remediation options

No option below is implemented by this diagnosis.

### Option A — Batch neighbor inputs and adjacency by traversal level

Add a set-oriented internal loader that fetches material metadata,
material-element memberships, material-application memberships, and matching
associations for the bounded frontier in batches. Reconstruct the existing
per-material neighbor dictionaries with the current score formula and
`neighbor_ranking_key`, then retain the existing BFS admission and response
assembly.

This is the recommended first implementation because it addresses both query
round trips and repeated ORM work while keeping public schemas and traversal
semantics explicit. Care is required to preserve sequential BFS membership
when ties and the node limit interact; batching may prefetch data, but it must
not alter admission order.

### Option B — Database-aggregated neighbor scoring

Use grouped SQL to return per-source/per-neighbor shared-element and
shared-application counts with material metadata. This can reduce transferred
association rows as well as query count. It offers a stronger ceiling for
dense datasets but has higher semantic and database-portability risk. Exact
handling of duplicate associations, relationship types, missing evidence, and
tie ordering must be proven.

### Option C — Recursive or fully composed SQL neighborhood query

Express traversal and scoring in a recursive CTE or a small number of composed
queries. This could minimize round trips, but it couples BFS limit semantics
and deterministic ordering tightly to SQL. It is not the preferred first move
because equivalence is harder to review and maintain.

### Option D — Cache completed neighborhoods

A versioned result cache may improve repeated identical requests, but it does
not fix cold-request cost and creates invalidation/provenance concerns. It
should be considered only after the underlying query path is bounded.

### Option E — Reduce application/database network distance

Co-location can reduce the multiplier but leaves 150–300-query behavior and
local materialization cost intact. It is an operational complement, not the
code-level remediation.

No speculative index is recommended from this SQLite diagnosis. Index changes
require PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)` evidence on a disposable
production-sized database.

## Acceptance criteria for a later fix

The following criteria are defined before implementation:

### Semantic and compatibility gates

1. Existing neighbor, neighborhood, API determinism, graph-closure, limit, and
   missing-material tests pass unchanged.
2. Before/after JSON is exactly equal for a matrix covering depths 1 and 2;
   limits 1, 5, 10, 25, 50, and 100; dense, sparse, tied-score, unknown-value,
   and missing-root fixtures.
3. Node membership, BFS depth, `best_score`, edge membership, relationship
   types, score formula, deterministic node/edge ordering, null/unknown fields,
   and response schema remain unchanged.
4. Repeated runs over identical state produce byte-equivalent canonical JSON.
5. Public status codes, query-parameter bounds, and response compatibility do
   not change.

### Performance gates

1. The 1,727-material default diagnostic request uses no more than 12 SQL
   queries at depth two and query count does not grow linearly with `limit`.
2. Warm median service latency on the committed local fixture is at most
   500 ms for `depth=2`, `limit=25`—at least a threefold improvement over the
   1,638.338 ms diagnostic baseline.
3. With 100 ms artificial per-query delay, the same endpoint completes within
   3,000 ms and returns the exact baseline payload hash.
4. Serialization remains below 5 ms and payload bytes are unchanged for an
   equivalent response.
5. `limit=50` and `limit=100` complete within the application's 20-second
   deadline on the local production-count fixture without unbounded memory or
   query growth.

### PostgreSQL and operational gates

1. Re-run sequentially on disposable PostgreSQL with the exact 1,727-material
   manifest when available; retain query counts, stage timings, payload hashes,
   and relevant `EXPLAIN (ANALYZE, BUFFERS)` output.
2. No concurrency claim is made until a separately scoped concurrency test is
   approved and executed.
3. Production validation requires separate authorization and begins with
   bounded read-only measurement. Diagnosis does not authorize deployment,
   restart, database write, index creation, provider change, or production
   access.

## Verification completed

- Four repeated default service results were identical.
- All artificial-delay endpoint responses had the same payload SHA-256:
  `50f22e6a428bd19f7569f169361e71cf5d019056c23e07d75cf2af97a2f2fd11`.
- The focused existing neighborhood service suite passed: `9 passed`.
- Ruff passed for the diagnostic runner.
- Runtime endpoint code, schemas, scoring, ordering, and database schema were
  not modified.
