# Neighborhood API: local PostgreSQL validation

**Status:** Local real-cohort validation complete; production behavior unverified
**Application baseline:** PR #15 merged as `f2fc7630c`
**Operator run:** 2026-09-21, Windows, disposable local PostgreSQL
**Endpoint:** `GET /api/v1/materials/5/neighborhood?depth=2&limit={25,100}`

## Data identity and safety

The operator copied the accepted MG-DE-005 v3 manifest outside the repository.
Its file SHA-256 was
`7939dcfd0fab9a8e7e43f7395c59c874673ed19aaf49d1a942650a69595e3daa`;
the validated *manifest payload* SHA-256 was
`902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`.
These hashes cover different byte representations and must not be interchanged.

`materialgraph_test_mg_de_007` was created from the local 28-material
`materialgraph_test` database. A pre-import canonical snapshot recorded all
28 curated identities with SHA-256
`c059b97fd88648c9755691f8625e7c887deca8876c2c23e305ceea3e2fe79ee8`.
The guarded import completed with 1,699 inserts and 28 protected conflicts,
zero updates, and 1,727 processed. Exit status 2 was the import tool's
expected conflict signal. The existing MG-DE-007 qualification script reported
12 scenarios, an unchanged curated snapshot, and `gate_failures: []`. Its
scenario set does **not** include the neighborhood endpoint.

All endpoint requests were sequential in-process FastAPI `TestClient` calls
against this local PostgreSQL database. The qualification output and four
request measurements per limit remain outside Git under
`~/MaterialGraph-evidence/neighborhood-postgresql/`:

- `qualification-first-run/qualification-report.json`
- `neighborhood-postgresql-depth2-limit25.json`
- `neighborhood-postgresql-depth2-limit100.json`
- `neighborhood-postgresql-untraced.json`

The operator supplied the command outputs for this record; the external JSON
files were not copied into this repository. No production system was queried
or changed for this validation.

## Results

The first instrumented pass used the MG-DE-004 `execute_scenario` helper,
which runs `tracemalloc` around each request. The second pass repeated one
cold and three warm requests per limit without memory tracing. SQL execution
time is the sum of SQLAlchemy cursor execute event durations; it does not
include ORM hydration or other Python work.

| Limit | Instrumented warm median | Untraced warm median | Untraced warm range | SQL queries | Untraced warm SQL time | Canonical JSON bytes |
|---:|---:|---:|---:|---:|---:|---:|
| 25 | 1,562.056 ms | 552.501 ms | 540.235–560.412 ms | 14 | 126.807–133.977 ms | 9,428 |
| 100 | 5,384.780 ms | 1,723.481 ms | 1,647.025–2,623.979 ms | 14 | 134.326–141.060 ms | 36,827 |

All 16 requests returned HTTP 200. For each limit, the response SHA-256 was
identical across both passes and all four runs:

- limit 25: `098f2284fdc18255d16a9f7b061ad1e87125387129796c75aee9ec73344b4789`
- limit 100: `b7762a25244940a966892c4cab25dfee3db38a88c5d73dd0c04fc55288ddaa09`

The earlier synthetic SQLite payload hash is not expected to match these
real-cohort payloads. The instrumented pass observed traced Python allocation
peaks of approximately 56 MB at limit 25 and 186 MB at limit 100; those are
tracer measurements, not wire payload sizes or process RSS. The much shorter
untraced latencies show that tracing substantially distorted request timing.

## Acceptance assessment

1. **Bounded query behavior: passed locally.** The query count stayed at 14
   when the response limit increased from 25 to 100. This is a different
   database and fixture from the synthetic 12-query benchmark; the counts
   should not be compared as if the workloads were identical.
2. **Determinism and response success: passed for the measured cases.** All
   requests returned 200 and repeated runs at each limit had the same canonical
   JSON hash. No before/after response snapshot on this real cohort was
   captured, so real-cohort cross-version byte compatibility was not proven
   by these measurements; focused tests and synthetic baseline comparison
   provide separate semantic evidence.
3. **Latency: qualified local pass.** The default local PostgreSQL warm median
   was 552.501 ms, above the remediation's synthetic SQLite target of 500 ms.
   That target is a synthetic-environment criterion, not a PostgreSQL pass.
   The largest observed untraced limit-100 request was 2,623.979 ms, below
   the application's 20-second deadline. Traced timings are unsuitable for
   the untraced latency decision.
4. **Residual work: observe rather than speculate.** SQL execution time was
   a small portion of request time, particularly at limit 100. Python object
   construction, ORM hydration, scoring, response assembly, and serialization
   were not separately measured on PostgreSQL. Profile these stages if a
   future deployment exhibits high latency or memory pressure; avoid adding
   an index or another behavior-changing optimization without evidence.

These measurements support integrating the query-batching remediation for
local real-cohort behavior. They do not establish production latency, network
round-trip cost, concurrency capacity, or peak process memory. A controlled
production observation requires separate authorization.
