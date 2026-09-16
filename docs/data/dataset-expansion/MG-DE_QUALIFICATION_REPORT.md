# MG-DE Representative-scale Qualification Report

**Execution date:** 2026-09-16
**Reviewed commit:** `69f0bda15f2a2ffe76c265ecc3bbfe60fc35f7a7`
**Fixture manifest SHA-256:** `6320e05e7a8138f7393cb2354c269d48dc0fa9fd848f805b1b51bd6a91a89701`
**Result:** Initial approximately 1,000-material test target qualified
**Production authorization:** None

## Boundary

The qualification ran against disposable local PostgreSQL databases cloned
from the 28-material curated test baseline. The fixture is synthetic and
explicitly identified as `synthetic_benchmark`; it is performance and lifecycle
evidence, not scientific source evidence. Execution was single-process and
sequential, with no concurrency or load test.

Environment: Windows AMD64, Python 3.14.5, PostgreSQL server and client 16.14.
The base session reported zero timeouts outside a transaction; application
transaction timeouts remain governed and tested separately through the
repository's `SET LOCAL` controls.

## Fixture and import lifecycle

Two independent generations produced byte-identical manifests containing
1,000 accepted identities, five duplicate source identities, five controlled
rejections, and a complete source traversal. Dense oxide, dense phosphate,
sparse, polymorph, and missing-optional-value cohorts were all present.

| Scenario | Duration | Result |
|---|---:|---|
| Clean import | 30.883 s | 1,000 inserted; 1,000 verified; 5 rejected; no conflict or retirement |
| Identical fresh-run rerun | 17.308 s | 1,000 unchanged; no insert, update, conflict, or retirement |
| Changed-source run | 19.231 s | 1 inserted, 1 updated, 997 unchanged, 1 controlled conflict, 5 rejected, 2 retired, 999 verified |
| Failed first chunk | N/A | Checkpoint stayed at zero; no candidate material, source record, or candidate event survived; 5 run-header rejection events remained |
| Resume after failed chunk | 22.729 s | 1,000 inserted and verified; run reconciled and completed |
| Post-commit interruption | N/A | Checkpoint recorded 100 while 200 unchanged candidate events were committed; run remained in progress |
| Resume after checkpoint lag | 22.598 s | Replay recognized committed work; exactly 1,000 unchanged and 5 rejected events; no duplicate source identities |

The changed-source manifest digest was
`477b6b47d68dced7c8fcb8f1ecc60760e1c9b2e7cdd3d3f34c040316c17ede31`.
The controlled conflict returned the documented CLI exit code 2 and did not
modify curated material identity `mp-19017`.

## Request measurements

The 12-scenario qualification completed in 37.451 seconds. Every request
returned HTTP 200. Times are milliseconds; query counts were stable across the
cold and two warm executions.

| Scenario | Cold | Warm 1 | Warm 2 | Queries | Peak traced Python MiB | Maximum database ms |
|---|---:|---:|---:|---:|---:|---:|
| Material list | 25.782 | 13.545 | 11.950 | 3 | 0.715 | 3.535 |
| Material detail | 14.253 | 8.603 | 8.241 | 4 | 0.187 | 3.630 |
| Neighbors | 132.719 | 151.235 | 147.505 | 7 | 3.595 | 74.166 |
| Similar | 692.086 | 566.178 | 568.771 | 10 | 9.690 | 203.891 |
| Family | 191.858 | 179.245 | 279.857 | 7 | 1.693 | 115.773 |
| Recommendations | 607.146 | 606.233 | 601.008 | 10 | 9.649 | 205.122 |
| Screening | 389.989 | 264.257 | 256.577 | 6 | 4.526 | 127.377 |
| Substitution | 290.817 | 276.105 | 267.222 | 6 | 6.520 | 76.453 |
| Discovery candidates | 206.982 | 200.713 | 202.003 | 7 | 1.888 | 114.932 |
| Discovery graph | 389.348 | 396.795 | 542.441 | 25 | 1.673 | 261.246 |
| Discovery path | 2,030.974 | 1,958.199 | 1,935.621 | 104 | 4.563 | 957.924 |
| Scientific pathways | 1,309.444 | 1,441.296 | 1,304.571 | 82 | 4.744 | 774.769 |

All measurements were below the 20-second application deadline. Standard
paths remained below the five-second investigation threshold, and graph/path
paths remained below fifteen seconds. Discovery path and scientific pathway
query counts are accepted at this target but retained as future optimization
signals rather than characterized as ideal.

The retained scoped material-element plan used an index-only scan, returned
eight rows in one loop, planned in 0.115 ms, and executed in 0.043 ms. No
unintended whole-dataset relationship materialization was demonstrated.

## Scientific regression

Complete canonical JSON for curated material 5 detail and criticality responses
matched before import, after the 1,000-record import, and after the controlled
changed-source/conflict run. The retained SHA-256 values were:

- detail: `61ace822039973dd7c4ba3d69b258d3b1b1a8cc167dfb338f3578b783125aea9`;
- criticality: `8e68508510bcd3951ecc276e28d6607e0e232f87aa081b59ae936a0a6d649c0b`.

## Backup evidence

PostgreSQL 16.14 `pg_dump --format=custom` completed in 20.511 seconds. The
archive was 374,317 bytes with SHA-256
`3eb7e7d6c5820be9416c741e05ce9c57b8fef84114d46f8749b00ffd49fe6444`.
`pg_restore --list` succeeded. No restoration was performed or claimed.

## Repository validation

Before integration, the focused suite reported 69 passed and the complete suite
reported 877 passed, 1 skipped. Ruff, automation-pin, dependency-contract, and
diff checks passed. GitHub Dependency Security run 16 and Secret Scan run 102
passed for the reviewed commit.

## Conclusion and remaining gates

MG-DE-003 and MG-DE-004 are closed for the bounded initial scale target. The
repository has evidence that deterministic ingestion, provenance, refresh,
failure recovery, selected request paths, scientific invariants, and backup
creation behave correctly at approximately 1,000 synthetic materials.

This does not authorize or prove:

- a real Materials Project acquisition or publication;
- production migration, import, synchronization, or restart;
- production EC2 or Neon capacity;
- concurrent or load behavior;
- restoration or recovery time;
- substantially larger datasets.

Those activities require their own reviewed source manifest, bounded canary,
resource evidence, and explicit authorization.
