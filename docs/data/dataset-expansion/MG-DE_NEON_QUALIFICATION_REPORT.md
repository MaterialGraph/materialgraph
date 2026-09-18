# MG-DE-008 Isolated Neon Qualification Report

**Status:** Closed
**Execution date:** 2026-09-18
**Closure date:** 2026-09-19
**Repository commit:** `ef0955bcd13dea624b87746a87a86c46a7d6e8f4`
**Production import authorized:** No
**Production deployment authorized:** No

## Scope and conclusion

The exact approved 1,727-identity Materials Project manifest was qualified on
an isolated, auto-expiring Neon branch. Identity, connection, migration,
import, recovery, performance, and resource gates passed within the reviewed
contract. The production branch and production endpoint were not contacted.

Independent review reproduced the archive hash, verified every inventoried
file, and reconciled the retained gate evidence. The qualification branch was
then deleted, its absence was independently confirmed, credentials were
cleared, and exact temporary-resource paths were removed. MG-DE-008 is closed.

## Reviewed resource identity

| Field | Qualification value |
|---|---|
| Project | `nameless-art-61629272` (`materialgraph`) |
| Branch | `br-frosty-violet-aoleln66` (`mg-de-008-qualification-test`) |
| Endpoint | `ep-odd-king-ao5fopux` |
| Database | `neondb` |
| Direct migration role | `neondb_owner` |
| Pooled runtime role | `materialgraph_runtime` |
| Parent branch | `production` |
| Displayed expiration | September 19, 2026, 5:20 pm |

The production denylist contained branch `br-old-credit-ao7cn4h7` and endpoint
`ep-long-mud-ao7wdhiw`. The qualification branch and endpoint differed from
both production identifiers.

## Immutable input

| Property | Value |
|---|---|
| Manifest identities | 1,727 |
| Manifest file SHA-256 | `7939dcfd0fab9a8e7e43f7395c59c874673ed19aaf49d1a942650a69595e3daa` |
| Manifest payload digest | `902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9` |
| Duplicate source identities | 0 |
| Rejections | 0 |
| Planned chunk size | 100 |
| Planned chunks | 18 |

The production loader and candidate parser validated the manifest offline
before a database connection was opened. Offline validation performed no
network access and no database write.

## Gate results

| Gate | Result | Evidence summary |
|---|---|---|
| Gate 0: authorization and identity | Passed | Contract, branch, endpoint, database, manifest, roles, TLS requirements, budgets, and production denylist reconciled |
| Gate A: connection management | Passed | Direct and pooled paths, separate roles, TLS, bounded pool, timeouts, rollback recovery, and sequential connection behavior verified |
| Gate B: exact import and recovery | Passed | Exact import, identical rerun, failed-first-chunk recovery, and committed-chunk recovery reconciled without duplicate identities or events |
| Gate C: remote performance | Passed with findings | All 12 sequential scenarios completed; remote round-trip-heavy pathways were materially slower than the local reference |
| Gate D: resource and cost boundary | Passed | Measured duration, provider storage graph, logical database size, and connection observations remained below contract ceilings |
| Gate E: cleanup and evidence | Passed | Sanitized archive independently verified; qualification branch deletion, credential clearing, and temporary-resource removal proved |

## Connection and TLS evidence

Both URLs used `postgresql+psycopg`, `sslmode=verify-full`, a trusted CA
bundle, and `channel_binding=require`. The direct URL used the owner role and
non-pooler endpoint. The pooled URL used `materialgraph_runtime` and the pooler
endpoint.

The psycopg client reported TLS in use for direct and pooled connections.
OpenSSL independently established TLS 1.3 with hostname and certificate
verification for both endpoints. Behind the pooled endpoint, `pg_stat_ssl`
reported the pooler backend hop rather than the client-to-pooler session and
therefore returned `ssl=false`; this does not override the client-side and
OpenSSL TLS evidence.

Connection qualification was sequential and observed at most one simultaneous
connection. The runtime pool used size 1, overflow 0, a five-second pool
timeout, pre-ping, and a 300-second recycle interval. Transaction-local
timeouts were 25 seconds for statements, five seconds for locks, and 30
seconds for idle transactions. Deliberate transaction failure followed by
rollback recovered cleanly.

## Schema migration

The qualification branch advanced from Alembic revision `7a4c2e91b6d8` to
`c8f3a2d7e901`. The migration created the four dataset-lifecycle tables:

- `dataset_import_runs`
- `material_source_records`
- `material_source_memberships`
- `material_import_events`

Post-migration reconciliation confirmed that all four tables existed and were
initially empty. The original 28 curated materials, nine elements, and 94
material-element rows remained intact. Migration duration is unavailable
because the post-command shell timing capture contained a syntax error; the
successful transactional migration and resulting revision were independently
verified afterward.

The execution also found and fixed an Alembic configuration defect: percent-
encoded URL components were interpreted by `ConfigParser`. The migration
configuration now escapes percent signs before calling `set_main_option`, with
regression coverage. The complete repository suite passed with 918 tests and
one skip before the remote run.

## Import and recovery reconciliation

The initial import completed in 785,335 ms with the expected conflict exit
code:

| Outcome | Count |
|---|---:|
| Processed | 1,727 |
| Inserted | 1,699 |
| Protected curated conflicts | 28 |
| Updated | 0 |
| Unchanged | 0 |
| Rejected | 0 |
| Retired | 0 |
| Verified present | 1,699 |

Final state after the initial import contained 1,727 materials, 1,699 source
records, 1,699 active memberships, and 1,727 unique import events. The import
run completed with the expected `completed_with_conflicts` status.

The identical rerun processed all 1,727 identities in 26,122 ms, producing
1,699 unchanged records and the same 28 protected conflicts. A controlled
failure before the first chunk resumed in 25,057 ms. A controlled interruption
after the second chunk committed but before its checkpoint update resumed in
23,714 ms. Both recovery paths completed with 1,727 distinct event keys and no
duplicate active source identity.

The curated-state SHA-256 remained
`56930eaf013600fc4966e618acc01895c3b1b5ea650547199225a81d3533296d`
before and after import, rerun, and recovery. Curated IDs 1 through 28 and the
`mp-19017` sentinel were preserved.

## Remote performance

The bounded runner executed one cold and two warm sequential requests for each
scenario. It performed no concurrency or load test and made no database write.
All 12 scenarios returned successfully.

| Scenario | Cold wall ms | Warm median ms | Warm DB median ms | Queries |
|---|---:|---:|---:|---:|
| Material list | 600.373 | 424.495 | 276.788 | 3 |
| Material detail | 465.600 | 437.901 | 305.671 | 4 |
| Neighbors | 1,969.272 | 1,678.247 | 941.226 | 8 |
| Similar | 4,242.669 | 4,466.873 | 1,878.406 | 11 |
| Family | 1,355.106 | 1,023.530 | 578.392 | 7 |
| Recommendations | 4,378.056 | 4,770.275 | 2,079.849 | 11 |
| Screening | 2,735.291 | 2,459.952 | 1,020.953 | 6 |
| Substitution | 2,231.167 | 2,243.057 | 849.947 | 6 |
| Discovery candidates | 1,355.941 | 1,206.295 | 662.860 | 7 |
| Discovery graph | 2,768.419 | 2,778.405 | 1,818.798 | 25 |
| Discovery path | 14,528.142 | 14,321.077 | 8,590.328 | 98 |
| Scientific pathways | 9,213.796 | 9,313.751 | 6,341.405 | 82 |

No pass threshold was approved before execution, so the following are
performance findings rather than retroactive failures:

- Discovery-path warm median was 14,321.077 ms versus the approximate local
  reference of 8,950 ms, an increase of 60.01%.
- Scientific-pathways warm median was 9,313.751 ms versus the approximate
  local reference of 5,600 ms, an increase of 66.32%.
- A representative formula lookup had no dedicated `materials.formula` index,
  read 346 shared blocks, and executed in 32.5 ms. This is a follow-up
  optimization candidate, not a schema change authorized by MG-DE-008.

Response-level identity and formula-crowding evidence was retained. The run did
not collapse formula-equivalent material identities.

## Resource boundary

Measured import, rerun, recovery, and performance operations totaled
1,006,485 ms, leaving 2,593,515 ms of the 3,600-second active-compute budget.
The runner used one active actor and observed at most one simultaneous database
connection against the ceiling of five.

The final logical database size was 19,177,472 bytes (18.289 MiB), below the
entire 256 MiB storage-delta ceiling. Neon monitoring showed `neondb` growing
from approximately 8-9 MiB to approximately 18-19 MiB. A conservative visual
upper bound of 12 MiB for provider-observed growth remains below the ceiling.
Provider graphs also showed zero deadlocks, low CPU utilization, RAM below
approximately 1 GiB, and pooler client and server active-connection peaks of
one. Some direct PostgreSQL connection metrics were unavailable in the console,
and cumulative provider compute seconds were not exposed; those limitations
are recorded rather than inferred away.

## Evidence archive

The sanitized final evidence archive was downloaded outside the qualification
host and independently verified:

| Property | Value |
|---|---|
| Archive | `mg-de-008-final-evidence.tar.gz` |
| Size | 375,715 bytes |
| SHA-256 | `2961ea28fd3cb5f1ad33fab35f7b00ba7e6540948ace12354ec3dec9abc53040` |
| Inventoried files | 89 |
| Inventory verification | Every recorded file size and SHA-256 matched |
| Secret scan | 0 findings across 88 files |
| Independent semantic review | Passed |

The independent review reconciled the immutable manifest, migration revision,
import totals, rerun and recovery outcomes, protected curated-state hash,
performance measurements, execution plans, resource ceilings, and production
denylist. Required evidence entries were present and internally consistent.
The archive contains no complete database URL, generated Neon password,
private key, or AWS access-key identifier detected by the bounded secret scan.
The scan supplements rather than replaces the independent evidence review.

Provider monitoring screenshots remain separately retained because they were
captured outside the EC2 evidence directory. They establish the reviewed
branch identity and expiration, bounded connection behavior, low observed
compute use, storage growth, row activity, and zero deadlocks.

## Cleanup and deletion proof

After the archive was independently downloaded and hash-verified, the exact
qualification branch `br-frosty-violet-aoleln66`
(`mg-de-008-qualification-test`) was deleted. A post-deletion Neon console
capture showed only the production branch `br-old-credit-ao7cn4h7`; the
qualification branch was absent. The production branch and endpoint were not
deleted, reset, restored, or written under this work item.

All local `MG_DE_008*` connection variables and the qualification
`DATABASE_MIGRATION_URL` were cleared. A qualification `DATABASE_URL`, when
present, was also cleared. The EC2 directories
`/tmp/materialgraph-mg-de-008-953Y4x` and
`/tmp/materialgraph-mg-de-008-fresh-cOGOVk` were removed only after the final
archive was verified off-host. Their absence was checked, and the host retained
approximately 10 GiB free afterward.

## Closure decision

MG-DE-008 is closed because all reviewed gates passed, the retained archive
passed independent integrity and semantic review, deletion was independently
proved, and credential and temporary-resource cleanup completed.

Closure retains the recorded limitations and findings. In particular, it does
not convert remote latency observations into an unreviewed pass threshold, does
not claim provider compute precision that Neon did not expose, and does not
authorize a formula index solely from one representative plan.

MG-DE-008 does not authorize production import, deployment, publication,
backup restoration, concurrency or load testing, or a production canary. Each
requires its own reviewed authorization and rollback boundary.
