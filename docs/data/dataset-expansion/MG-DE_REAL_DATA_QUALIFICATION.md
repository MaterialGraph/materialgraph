# MG-DE-007 Real-Data PostgreSQL Qualification Plan

**Status:** Ready for controlled implementation verification
**Approved manifest payload digest:** `902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`
**Database writes authorized:** Disposable local PostgreSQL only
**Neon or production writes authorized:** No

## Objective

Demonstrate import safety, scientific preservation, product behavior, query
behavior, and recovery using the exact 1,727-identity manifest accepted by
MG-DE-005 and MG-DE-006. A different manifest, database, source release, or
selection contract cannot substitute for this evidence.

## Isolation boundary

Create `materialgraph_test_mg_de_007` from the clean `materialgraph_test`
template. Both `DATABASE_URL` and `DATABASE_MIGRATION_URL` must name that
database, and `MATERIALGRAPH_ENV_FILE` must be disabled for the session. The
qualification tools reject non-PostgreSQL databases and names that do not
contain both `test` and `mg_de_007`.

Do not use `materialgraph`, a shared test database, Neon, or production.
Do not perform a restore under this plan.
No concurrency or load test is authorized.

## Gate A: curated-data preservation

1. Capture the protected database state for material IDs 1 through 28 before
   import with `capture_curated_database_state.py`.
2. Capture complete curated detail and criticality API JSON with the existing
   reference tool.
3. Apply the exact manifest with an unused checkpoint and exact expected
   database name.
4. Require all 28 protected identities and their material-element links to
   retain the same canonical SHA-256.
5. Require complete curated API JSON to match before and after import.
6. Require the manifest identity `mp-19017` to produce one explained
   `conflicted` event attached to curated material ID 5. It must not insert,
   update, reassign, merge, or silently accept the curated row.

Expected clean-import reconciliation is 1,726 inserted source identities, one
conflict, 1,726 active source records, 1,726 active scope memberships, and
1,754 total materials. These numbers are contract-derived; unexpected counts
fail the gate.

## Gate B: polymorph crowding

For every representative endpoint response, retain the unmodified JSON and
record:

- returned identity count and uniqueness;
- unique formula count and formula-diversity fraction;
- repeated formula and repeated identity counts;
- maximum formula multiplicity in the response;
- the repeated formula distribution.

Inspect material listing, neighbors, similarity, family, recommendations,
screening, substitution, discovery candidates, discovery graph, discovery
path, and scientific pathways. Distinct source identities remain distinct.
This work item may identify a presentation or ranking requirement, but it must
not silently collapse polymorphs or introduce an arbitrary diversity penalty.

## Gate C: real-data performance and recovery

- Record clean-import duration and result.
- Run a fresh identical import and require 1,726 unchanged plus the same one
  conflict, with no new material or source identity.
- Reproduce failed-chunk rollback and committed-chunk interruption/resume
  against the exact approved manifest in a second disposable database.
- Reconcile checkpoints, run status, event uniqueness, source identities, and
  memberships after resumption.
- Execute one cold and one to five warm sequential runs for each bounded
  endpoint; retain status, latency, query count, database time, response size,
  response digest, and traced Python peak allocation.
- Retain `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` for a real crowded-formula
  lookup and investigate observed plans rather than adding speculative indexes.
- Create a PostgreSQL custom-format backup, validate it with
  `pg_restore --list`, and record duration, size, and SHA-256. Do not restore.

## Acceptance

MG-DE-007 can close only when all three gates pass and focused/full repository
verification passes. Performance regressions, unexplained formula crowding,
curated changes, incomplete recovery, or any `mp-19017` outcome other than the
expected conflict keep the item open.

Closure authorizes planning of an isolated non-production Neon qualification.
It does not authorize Neon execution, production import, deployment, public
publication, shared-database writes, backup restoration, or production canary.
