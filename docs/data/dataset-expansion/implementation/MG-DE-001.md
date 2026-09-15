# MG-DE-001 Implementation Record

**Baseline:** `80201f92546261f7fa78492e2771ad1966d5c780`
**Status:** Verified and closed
**Production import authorized:** No

## Implemented controls

- Source results are fetched using explicit, deterministic pages ordered by
  Materials Project material identity.
- Chemical systems, page size, per-system page bound, total source-record bound,
  accepted-material bound, chunk size, retry bound, and stability scope are
  explicit manifest inputs.
- Fetch retries use bounded exponential waits; exhausted retries fail closed.
- Individual normalization failures become sanitized rejection records rather
  than exposing source payloads or exception details.
- Cross-scope duplicate source IDs are recorded and deterministically
  deduplicated.
- Accepted candidates, rejection records, scope, counts, and duplicate IDs are
  stored in a canonical SHA-256-protected JSON manifest before any database
  operation.
- Manifest creation is the command default and refuses to overwrite an existing
  manifest.
- Manifest application requires a separate `--apply` invocation, checkpoint
  path, and exact database-name confirmation.
- Non-test database application is refused unless separately and explicitly
  enabled. This implementation record does not authorize that option.
- Each configured chunk is one database transaction. Existing material and
  element identities are looked up in bulk per chunk.
- An atomic checkpoint is written after each committed chunk. Repeating the
  command resumes from the last recorded boundary.
- Final application verifies that every accepted manifest identity exists in
  the database and that processed/imported/skipped counts reconcile.

## Compatibility boundary

`MaterialImportService.import_materials()` retains its existing integer return
contract. The richer `import_materials_with_result()` contract is used by the
pipeline. Existing `mp_id` records continue to be skipped; update, conflict,
retirement, dataset-release, and normalization-version semantics remain
`MG-DE-002` work.

The checkpoint reports reconciled observed chunk outcomes. In the narrow crash
window after a database commit but before its checkpoint replacement, safe
replay can classify those identities as skipped rather than newly imported.
Final identity reconciliation remains exact; durable attribution to a named
import run is intentionally deferred to `MG-DE-002`.

## Files affected

- `app/services/material/import_pipeline.py`
- `app/services/material/import_service.py`
- `app/services/material/project_service.py`
- `scripts/import_materials_project.py`
- focused service and script tests;
- current import documentation and cumulative MG-DE records.

There is no schema migration, dependency change, API response change, deployment
configuration change, or production data change.

## Verification performed in the isolated review workspace

- Manifest/paging/checkpoint/source tests: 13 passed.
- CLI safety tests: 4 passed.
- Project-configuration tests: 33 passed without the database-cleaning fixture.
- Ruff: passed during implementation iterations.
- Automation-pin and dependency-contract checks: passed.
- `git diff --check`: passed.
- No external Materials Project request was made.
- No database manifest application was made.

A composed PostgreSQL lifecycle test is now included. It uses generated
`mp-tl-*` identities, the real `MaterialImportService`, the guarded
test session, a controlled failure before the second chunk, checkpoint/resume,
final identity reconciliation, and a second application with a fresh checkpoint
to prove idempotent skipping.

The first independent execution reached the PostgreSQL insert but stopped before
the lifecycle assertions because the generated UUID-based fixture identity was
longer than the existing `materials.mp_id` 50-character limit. The fixture now
uses a bounded 24-character `mp-tl-*` identity. This was a test-fixture defect;
no importer, schema, production, or source-data change was required.

## Independent closure verification

At commit `6dfe67d817b8ac848bb41d2783e27c7ed6b27d27`, the corrected composed
lifecycle test passed against the guarded `materialgraph_test` PostgreSQL
database. It verified the committed-chunk boundary, controlled interruption,
checkpoint value 2, resume, three-identity reconciliation, and a clean rerun
reporting zero imported and three skipped.

- PostgreSQL lifecycle test: 1 passed, 10 deselected.
- Focused importer and configuration suite: 67 passed.
- Complete suite: 860 passed, 1 skipped.
- Ruff, automation pins, dependency contract, and `git diff --check`: passed.
- GitHub Dependency Security run 11 and Secret Scan run 97: passed for the same
  commit.
- No external source request, production database operation, schema migration,
  deployment change, or production import occurred.

## Retained regression verification

1. Confirm both runtime and migration URLs name a test database.
2. Run the focused importer, pipeline, source-service, script, and project-
   configuration tests.
3. Run the complete suite, Ruff, automation-pin check, dependency-contract
   check, and `git diff --check`.
4. Confirm the composed PostgreSQL lifecycle test continues to pass, including
   interruption, resume, clean rerun, and database-ID reconciliation.
5. Do not use a real source API key or production database for repository
   integration validation.

## Rollback

Before production use, rollback is a Git fast-forward/revert decision because
no production state is changed. A test manifest application may be rolled back
by restoring or recreating the disposable test database. Do not construct a
delete-by-manifest production rollback until `MG-DE-002` defines versioned
dataset membership and refresh semantics.
