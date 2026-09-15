# MG-DE-002 Implementation Record

**Baseline:** `527ed03f6482806b8cf4879566d828679a9aab59`
**Status:** Verified and closed
**Production migration authorized:** No
**Production import authorized:** No

## Implemented contract

- Manifest schema v2 requires an authoritative source release and timezone-aware
  retrieval timestamp.
- Materials Project access verifies the declared release against the API
  heartbeat before each page and fails closed on mismatch.
- CC BY 4.0 identity and URL, normalization version, selection-contract version,
  source scope, normalized records, rejections, and counts are manifest-digested.
- The checkpoint carries one UUID import-run identity across interruption and
  resume.
- Immutable run headers preserve source release, retrieval, manifest, license,
  normalization, selection, scope, timestamps, status, and final counts.
- Current source records preserve source and normalized SHA-256 digests, active
  state, material link, release, retrieval, and latest run; separate memberships
  preserve overlapping selection-scope activity.
- Append-only events record inserted, updated, unchanged, conflicted, rejected,
  and retired outcomes without copying source payloads.
- A reconciled run with conflicts is marked `completed_with_conflicts`, and the
  CLI returns a nonzero status after printing its counts.
- Same-run chunk replay returns its already committed outcomes, covering the
  database-commit/checkpoint-replacement crash window.
- Retirement is restricted to a completed refresh with the same source,
  selection-contract version, and exact selection-scope digest.
- Empty manifests are rejected, and a manifest truncated at its material bound
  cannot retire unseen scope members.

## Scientific and identity boundary

Materials Project identities remain distinct, even where formulas match.
Polymorphs are not collapsed. Aliases are not inferred. An existing material
without matching provenance becomes a conflict and is not overwritten.

Updates replace only the importer-owned material properties and normalized
element membership. Explicit null source values remain null. Retirement marks
the source record inactive but does not delete the material; production
publication/exclusion remains a later measured gate.

## Schema effects

Migration `c8f3a2d7e901` creates:

- `dataset_import_runs`;
- `material_source_records`;
- `material_source_memberships`;
- `material_import_events`.

It does not alter or backfill existing material rows. Existing curated records
therefore remain usable and are not silently assigned provenance.

## Compatibility and operational effects

The legacy internal `import_materials()` and `import_materials_with_result()`
contracts remain available. Manifest v1 and checkpoint v1 are intentionally
rejected because they lack the evidence required for provenance-aware refresh.

There is no API response, dependency, Nginx, systemd, or current production-data
change. Applying this migration or any manifest outside the test database is
not authorized by this record.

## Verification required

1. Confirm runtime and migration URLs identify the disposable test database.
2. Run `alembic upgrade head` against that test database and verify the four
   provenance tables and constraints.
3. Run migration, manifest, importer, source-client, CLI, and configuration
   tests.
4. Reproduce one composed lifecycle containing every refresh outcome, same-run
   replay, final counts, source-record activity, and event reconciliation.
5. Run the complete suite, Ruff, automation-pin check, dependency-contract
   check, and `git diff --check`.
6. Do not use a production database or a real source API key.

## Isolated implementation validation

- Non-PostgreSQL manifest, source-client, CLI, and configuration tests: 56
  passed; 1 PostgreSQL lifecycle test deselected.
- Provenance outcome and overlapping-scope scenarios: passed against a
  disposable SQLite subset as non-authoritative smoke checks.
- Test collection: 870 tests collected.
- Alembic graph: one head at `c8f3a2d7e901`.
- PostgreSQL model DDL compilation: passed for all four new tables.
- Ruff, automation pins, dependency contract, Python compilation,
  documentation-link validation, and `git diff --check`: passed.
- No PostgreSQL migration, complete suite, external source request, or
  production operation was performed in the isolated workspace.

## Independent closure validation

At commit `3e8eb2975a679594b73dcc86c6ebe99d415864fd`, independent
verification on 2026-09-15 reported:

- both configured database URLs resolved to `materialgraph_test`;
- Alembic used PostgreSQL and reported the single head `c8f3a2d7e901` before
  and after `alembic upgrade head`;
- the PostgreSQL migration test passed without a skip;
- all 18 refresh-service tests passed;
- the PostgreSQL interruption/resume lifecycle test passed;
- the complete focused suite reported 76 passed;
- the complete repository suite reported 869 passed, 1 skipped;
- automation pins, dependency contract, Ruff, and `git diff --check` passed;
- GitHub Dependency Security run 13 and Secret Scan run 99 passed for the same
  commit.

The evidence closes MG-DE-002 for the initial expansion gate. No real source
request, production migration, production import, or production restart was
performed or authorized. Representative-scale qualification remains governed
by MG-DE-004.

## Rollback

Before production use, rollback is a Git decision plus migration downgrade in a
disposable test database. The migration downgrade drops only the new provenance
tables. Do not downgrade a database containing required import-run evidence, and
do not apply or downgrade this migration in production without a separately
approved deployment and rollback procedure.
