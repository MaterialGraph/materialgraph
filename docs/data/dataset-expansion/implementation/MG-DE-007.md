# MG-DE-007 Implementation Record

**Baseline:** `c82c96e778b48512d16fa74252debd36542a28ae`
**Status:** Implementation in progress; independent execution pending
**Database synchronization authorized:** Disposable local PostgreSQL only

## Implemented boundary

- exact approved-manifest constants and fail-closed contract evaluation;
- canonical protected-state capture for curated material IDs 1 through 28 and
  their material-element relationships;
- exact import-run, event, source-record, membership, total-material, and
  `mp-19017` collision reconciliation;
- bounded representative endpoint execution using the established MG-DE-004
  measurement harness;
- response-level identity and formula crowding measurements without changing
  ranking or collapsing identities;
- analyzed PostgreSQL plan capture for a real formula-equivalence lookup;
- tests for manifest binding, curated invariants, collision semantics,
  recursive response inspection, and crowding calculations.

## Deliberately manual evidence

Clean import, fresh rerun, failure injection, committed interruption, curated
API comparison, backup creation/listing, and environment measurements remain
operator-controlled. This prevents a repository test from creating databases,
injecting failures, or writing backups implicitly.

## Authorization boundary

The tooling requires a dedicated local database name containing `test` and
`mg_de_007`. It grants no Neon, production, deployment, publication, restore,
or concurrency authorization.

## Rollback

No schema or production data is changed. Delete the disposable databases and
external evidence after closure once durable evidence has been preserved.
Before integration, delete the branch. After integration, revert the MG-DE-007
implementation commit if the tooling must be removed.
