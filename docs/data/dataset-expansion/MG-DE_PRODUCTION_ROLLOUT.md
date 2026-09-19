# MG-DE-009 Production Rollout Readiness Plan

**Status:** Planning safeguards implemented; production execution unauthorized
**Production migration authorized:** No
**Production import authorized:** No
**Production restore authorized:** No
**Service restart authorized:** No

## Purpose

MG-DE-008 qualified the exact approved 1,727-identity manifest on an isolated
Neon branch and then proved cleanup. MG-DE-009 defines the separate controls
required before the production database may be migrated or imported. It is a
rollout-readiness gate, not production execution and not a production canary.

## Immutable input and expected outcome

The only permitted dataset input is the MG-DE-005 manifest with file SHA-256
`7939dcfd0fab9a8e7e43f7395c59c874673ed19aaf49d1a942650a69595e3daa`
and payload digest
`902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`.

The reviewed outcome remains 1,727 processed identities, 1,699 inserts, and 28
protected curated conflicts, with no update, rejection, or retirement. Any
different manifest, baseline, or expected outcome requires a new reviewed
contract.

## Offline contract

Start from `MG-DE_PRODUCTION_ROLLOUT_CONTRACT.example.json`. The completed
non-secret contract must name the exact production project, branch, endpoint,
database, pooled runtime role, and direct migration role. URLs stay in
environment variables and never enter the contract or evidence.

The offline validator requires:

- the exact production branch name and reviewed provider identifiers;
- distinct pooled runtime and direct migration paths and roles;
- `postgresql+psycopg`, `sslmode=verify-full`, and
  `channel_binding=require`;
- the exact manifest file and payload digests;
- the expected Alembic transition from `7a4c2e91b6d8` to
  `c8f3a2d7e901`;
- an independently captured 28-material curated hash, nine elements, 94
  material-element rows, and the `mp-19017` sentinel at material ID 5;
- mandatory backup, hash, archive-listing, pre-import snapshot, and observation
  controls;
- sequential execution within the reviewed connection, compute, storage, and
  wall-clock ceilings; and
- all production execution authorization flags set to false.

Validation performs no network access, backup, migration, database write,
restore, service restart, or infrastructure mutation. A valid readiness
contract is necessary but does not authorize production execution.

## Gate 0: reviewed identity and authorization

An operator and independent reviewer must reconcile provider metadata to the
contract before credentials are used. The review must identify the production
branch and endpoint positively; a database name or SQL query alone is
insufficient.

MG-DE-009 readiness closes with execution flags still false. Migration, import,
restore, and service restart require a later, explicit execution authorization
bound to the reviewed commit, contract digest, manifest digests, evidence
location, operator, reviewer, and time window.

## Gate A: read-only production preflight

After separate authorization for read-only production access:

1. prove direct and pooled URLs resolve to the reviewed endpoint and roles;
2. verify TLS and channel binding from the client;
3. record Alembic revision, PostgreSQL version, database size, role flags,
   transaction defaults, timeouts, and connection limits;
4. capture exact curated rows and relationships, counts, and the material ID 5
   sentinel in a read-only transaction;
5. capture current endpoint health and representative read-only API responses;
6. record provider storage and compute state; and
7. stop on any contract mismatch without attempting a corrective write.

The existing MG-DE-007 capture script is test-database-specific and must not be
used against production. MG-DE-009 requires a production-specific read-only
capture with exact endpoint guards before this gate can execute.

## Gate B: backup and rollback boundary

Before any migration or import, a separately authorized execution must create
a production backup through the reviewed direct endpoint, record its tool and
server versions, hash it, validate its archive listing, and retain it outside
the production host.

Backup creation does not authorize restoration. Restoration remains a separate
incident decision because it is destructive and may overwrite newer state.
The execution plan must define stop conditions and forward-recovery versus
restore decision ownership before the write window opens.

## Gate C: performance decision

MG-DE-008 recorded discovery-path and scientific-pathways warm medians of
14.321 and 9.314 seconds. Before production rollout authorization, compare
these findings with the deployed request deadlines and user-facing behavior.
Any query reduction or index change requires its own tests and plan comparison;
MG-DE-009 does not authorize a speculative formula index.

## Gate D: bounded migration and import

Only a separately approved execution may:

1. migrate through the direct owner endpoint to `c8f3a2d7e901`;
2. reconcile the four lifecycle tables before import;
3. apply the exact manifest sequentially with one actor and a durable
   checkpoint;
4. treat the expected conflict exit code as success only when exactly 28
   protected curated conflicts reconcile; and
5. stop on any unexpected update, rejection, retirement, identity total,
   curated hash change, duplicate event key, or source-identity mismatch.

No concurrency, load test, provider chaos test, dependency upgrade,
infrastructure resize, or unrelated deployment belongs in the write window.

## Gate E: observation and closure

After import, retain database totals, lifecycle counts, runtime-role access,
curated hash, sentinel responses, endpoint health, representative latency,
provider resource state, and application logs for at least the reviewed
observation period. Clear credentials and temporary artifacts only after the
evidence is independently retained.

MG-DE-009 production execution can close only after independent reconciliation
and a separate decision on whether the expanded dataset may remain active.

## Current closure boundary

This planning change closes no production gate. It provides offline safeguards
for preparing a reviewed contract. Production network access, backup,
migration, import, restore, restart, deployment, publication, and canary
remain unauthorized.
