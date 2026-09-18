# MG-DE-007 Real-Data PostgreSQL Qualification Report

**Decision:** Accept for isolated non-production Neon qualification planning
**Status:** Qualified with accepted limitations
**Execution date:** 2026-09-18
**Manifest payload digest:** `902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`
**Neon or production import authorized:** No

## Scope and environment

The exact MG-DE-005/MG-DE-006 manifest was exercised against dedicated local
PostgreSQL databases named for MG-DE-007. Execution was sequential and bounded;
no concurrency, load, Neon, shared-database, or production write was performed.
The source database began with the 28 protected curated materials.

## Import and curated-data result

The first import processed all 1,727 manifest identities. It inserted 1,699
new materials and emitted 28 explained conflicts because every protected
curated `mp_id` also occurred in the real manifest. The final database held
1,727 materials, 1,699 active Materials Project source records, and 1,699
active memberships. It performed no update, retirement, or rejection.

All protected curated IDs, `mp_id` values, scalar fields, raw data, and
material-element relationships retained the canonical SHA-256
`c059b97fd88648c9755691f8625e7c887deca8876c2c23e305ceea3e2fe79ee8`.
Complete detail and criticality JSON for material ID 5 matched before and after
the import. The `mp-19017` event remained attached to curated material ID 5
with outcome `conflicted` and reason `source identity already exists without
matching provenance`.

## Idempotency and recovery

An independent fresh rerun produced 1,699 `unchanged` and 28 `conflicted`
outcomes, with no insert, update, rejection, or retirement. The protected
curated hash remained unchanged.

A controlled first-chunk failure left the checkpoint at zero and committed no
candidate material, source record, membership, or candidate event. Resume then
completed with 1,699 inserted and 28 conflicted identities.

A controlled interruption after two committed chunks left 200 unique events
in the database while the durable checkpoint remained at 100. Resume safely
replayed the second chunk and completed with exactly 1,699 unchanged and 28
conflicted events. The final run contained 1,727 events and 1,727 distinct
event keys; database totals remained unchanged.

## Representative request behavior

All 12 bounded representative scenarios returned HTTP 200. The slowest
observed request was discovery path at 8,954.540 ms, followed by scientific
pathways at 5,601.441 ms. Their maximum observed database times were
2,395.660 ms and 1,583.430 ms respectively. Both remained below the 20-second
application deadline, but they are retained as optimization signals rather
than production-capacity proof. Peak traced Python allocation was 27.871 MiB.

The retained formula-equivalence plan completed in 4.120 ms after 0.210 ms of
planning and used a primary-key index scan plus a sequential scan over the
1,727-row material table. This does not justify a speculative index at the
qualified scale; the plan must be re-evaluated at materially larger scale.

## Polymorph crowding

Identity preservation remained exact: the qualification did not collapse or
rewrite polymorphs. Broad responses nevertheless showed low formula diversity:

| Scenario | Unique identities | Unique formulas | Formula diversity | Identities in repeated-formula groups | Maximum multiplicity |
|---|---:|---:|---:|---:|---:|
| Material list | 100 | 74 | 0.740000 | 41 | 6 |
| Neighbors | 1,724 | 648 | 0.375870 | 1,310 | 73 |
| Family | 840 | 293 | 0.348810 | 660 | 26 |
| Screening | 1,727 | 651 | 0.376954 | 1,310 | 73 |
| Similar | 11 | 10 | 0.909091 | 2 | 2 |
| Discovery candidates | 10 | 9 | 0.900000 | 2 | 2 |

Recommendations, substitution, and discovery graph returned one formula per
unique identity in the captured bounded responses. Scientific pathways
contained 65 identity occurrences but only six unique identities; its 59
repetitions reflect response structure and are not additional polymorphs.
Discovery path exposed no identity/formula pair and was marked not measurable.

The evidence supports preserving scientific identities while adding an
explicit grouping or diversity presentation in future product work. It does
not support silent formula collapse or an unreviewed ranking penalty.

## Backup evidence

A PostgreSQL 16 custom-format backup completed in 575 ms. The archive was
750,478 bytes with SHA-256
`63bb8ca50f42ffdfb57bb597fd1f5add985fe28e68dfdd6a7a552033a74713f3`.
`pg_restore --list` validated 124 archive entries. No restore was performed.

## Decision and remaining gates

MG-DE-007 is qualified with the following accepted limitations:

- discovery path and scientific pathways are real-data optimization signals;
- broad responses can look less diverse than their identity count because of
  scientifically meaningful polymorphs;
- measurements are sequential local evidence, not concurrency, Neon capacity,
  production-host, or production-latency evidence;
- backup restoration remains untested and unauthorized.

This result closes the initial local dataset-expansion qualification sequence.
The next work item must define and execute a separately authorized isolated
non-production Neon qualification. It must not use the production database and
must define cleanup, cost, observability, rollback, and credential boundaries
before any remote write.
