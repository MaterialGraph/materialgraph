# Neighborhood API production observation after batching

**Date:** 2026-09-21 UTC
**Scope:** Two sequential read-only observations of one endpoint after the
authorized production code update; no load or concurrency experiment.

## Identity and deployment boundary

- Production checkout before update: `9a7fb1115e00d4e3a1864bf86e1423f522af2af1`.
- Production checkout targeted and installed: `06e292f1f8643d1623aca310cb8437b19eb47dac`.
- Fast-forward contained 56 commits, including PR #15's batching change; this
  is not an isolated single-commit production experiment.
- Production database was verified in a read-only transaction before the code
  update at Alembic `c8f3a2d7e901` with 1,727 materials. No migration or
  dataset import was performed during this release.
- The production dependency lock and `pyproject.toml` did not change between
  these commits. Editable installation, `pip check`, installed lock
  reconciliation, and automation-pin validation succeeded before restart.

The service was restarted once at 15:08:43 UTC. An immediate local HTTPS
health request returned 502; a subsequent retry returned HTTP 200 with
`environment: production`. The service remained active with the same PID
`229003`. The bounded error-priority journal inspection since 15:08:30 UTC
returned no entries. Treat the initial 502 as a startup readiness observation,
not as evidence of continuous availability during restart.

## Matching request measurements

All requests used HTTPS to `materialgraph.org`, resolved to `127.0.0.1` on
the production EC2 host with certificate validation. Thus the measurements
include Nginx and the application but exclude the external client-to-host
network path. The request was
`GET /api/v1/materials/5/neighborhood?depth=2&limit=25`.

| Running code | Sequence | HTTP | Total | Time to first byte | Body bytes |
|---|---|---:|---:|---:|---:|
| `9a7fb11` | Before deployment | 200 | 18,822.275 ms | 18,822.228 ms | 9,412 |
| `06e292f` | First after deployment | 200 | 4,670.309 ms | 4,670.221 ms | 9,412 |
| `06e292f` | Second after deployment | 200 | 4,088.233 ms | 4,088.168 ms | 9,412 |

The raw response SHA-256 for **all three** requests was
`7e36463e91856fe6594a1d57ec46454b26c696199eb7a164cb4650c1c1c7609c`.
Relative to the matching pre-update request, the first post-update sample
was 75.2% faster and the second was 78.3% faster. The matching hashes establish
byte-level compatibility for this particular request and production dataset.
The earlier MG-DE-009 16,242.222 ms observation did not retain its exact
query parameters; use the 18,822.275 ms same-request sample for the direct
before/after comparison.

## Interpretation and limits

The production observation is consistent with the expected benefit from
reducing traversal round trips. Almost all measured time elapsed before the
first byte. These timings do not attribute time among SQL execution, graph
construction, scoring, and serialization on the production host; production
query counts were not measured. Two post-update requests do not establish a
stable latency distribution or concurrent capacity. The startup 502 merits a
separate readiness improvement if zero-downtime deployment becomes a product
requirement. No additional production mutation or provider change is implied
by this record.
