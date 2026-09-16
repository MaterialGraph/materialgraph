# MG-DE-004 Representative-scale qualification framework

**Status:** Verified and closed
**Implementation baseline:** `ba19c90f627fed688e89d8d2ddca9f04cdfe8d9c`
**Production impact:** None; production import is not authorized

## Implemented controls

- `generate_dataset_expansion_fixture.py` creates a byte-deterministic,
  offline manifest containing 1,000 accepted synthetic materials.
- The fixture deliberately covers dense phosphate and oxide cohorts, sparse
  chemistry, polymorph identities, stable and unstable records, missing
  optional values, duplicate source identities, and controlled rejections.
- Synthetic records have the `mgde004-` identity prefix, explicit
  `synthetic_benchmark` provenance, and a CC0 contract. They cannot be confused
  with Materials Project evidence.
- The production import lifecycle now propagates the manifest source into new
  material rows. The existing Materials Project default remains unchanged.
- `qualify_dataset_expansion.py` refuses SQLite, a database-name mismatch, or a
  database whose name does not contain both `test` and `mg_de_004`. It executes
  requests sequentially and performs no concurrency or load test.
- The qualification report records the commit, manifest digest, database
  version/timeouts, primary row counts, import-run identity, a scoped
  `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` plan, cold and warm wall time,
  query count/database time, response size/digest, and peak traced Python
  allocation.
- Every measured response is retained as complete JSON with owner-only file
  permissions.
- Separate capture and comparison commands verify complete curated detail and
  criticality JSON before and after fixture import.

## Required isolated lifecycle

Use a disposable PostgreSQL database whose exact name includes
`test` and `mg_de_004`, for example `materialgraph_test_mg_de_004`. Seed it
from the same curated test baseline used by the repository suite. Do not point
these commands at the general test database or production.

1. Capture the curated reference before import.
2. Generate the synthetic manifest twice in separate temporary directories and
   confirm identical SHA-256 digests.
3. Apply Alembic to the disposable database.
4. Apply the manifest with the existing exact-name CLI guard and retain its
   checkpoint.
5. Rerun the identical manifest with a fresh checkpoint and reconcile the
   unchanged outcome.
6. Exercise interruption/resume and failed-chunk behavior through the existing
   PostgreSQL lifecycle tests; do not kill a database transaction manually.
7. Run the qualification harness and capture the curated reference again.
8. Compare complete pre/post curated JSON.
9. Measure a custom-format `pg_dump`, calculate its SHA-256 and size, and run
   `pg_restore --list`. Restoration is outside this bounded execution and still
   requires explicit authorization.
10. Run focused tests, the complete suite, Ruff, dependency/pin checks, and
    `git diff --check`.

## Acceptance thresholds

| Gate | Threshold |
|---|---|
| Fixture | Exactly 1,000 unique accepted identities; controlled duplicates and rejections are nonzero; manifest digest repeats exactly |
| Import | All manifest and database counts reconcile; clean apply, resume, and identical rerun terminate without duplicate active source identities |
| Curated regression | Complete detail and criticality JSON match exactly before and after import |
| Requests | Every scenario returns HTTP 200 below the existing 20-second application deadline; no timeout or pool-exhaustion response |
| SQL scope | Query counts are recorded; scoped relationship plan is retained; any demonstrated whole-dataset relationship materialization blocks acceptance |
| Memory | Peak traced Python allocation is recorded per sequential request and reviewed for disproportionate growth; host RSS remains a separately recorded environment measurement |
| Backup | `pg_dump` completes, has a nonzero digest/size, and `pg_restore --list` succeeds; duration is reviewed against the documented recovery objective |
| Validation | Focused suite, complete suite, Ruff, automation pins, dependency contract, and diff check pass |

The 20-second request limit is a hard compatibility gate, not a performance
target. Reviewers should also investigate any warm request above five seconds
or any graph/path request above fifteen seconds before accepting the initial
scale target.

## Independent closure

The required isolated lifecycle was executed on 2026-09-16 against commit
`69f0bda15f2a2ffe76c265ecc3bbfe60fc35f7a7`. Fixture determinism, clean import,
rerun, changed-source outcomes, failed-chunk rollback, committed-chunk replay,
12 request scenarios, query plan, traced allocation, curated complete-JSON
regression, and custom-format backup validation passed. See
[the qualification report](../MG-DE_QUALIFICATION_REPORT.md).

The evidence does not prove production capacity, concurrency, real-source
acquisition, restoration, or a production canary. Those remain separate gates.

## Rollback

Before integration, discard the implementation branch. After integration,
revert the focused commit. Test data cleanup is performed by destroying the
disposable MG-DE-004 database, not by deleting selected rows from a shared
database. No production rollback is required because this implementation does
not deploy or import data.
