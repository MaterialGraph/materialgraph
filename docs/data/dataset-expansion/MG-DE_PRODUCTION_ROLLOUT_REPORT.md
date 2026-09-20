# MG-DE-009 Production Rollout Closure Report

**Status:** Closed
**Execution date:** 2026-09-20
**Reviewed repository commit:** `71e6cf37d7ca23984ff6b98d7db0392b085905d4`
**Expanded dataset active:** Yes
**Further database writes authorized:** No
**Restore authorized or performed:** No
**Deployment or service restart performed:** No

## Scope

MG-DE-009 migrated the reviewed production database from Alembic revision
`7a4c2e91b6d8` to `c8f3a2d7e901` and applied the exact MG-DE-005
Materials Project manifest. The execution preserved the existing curated
cohort, retained the `mp-19017` sentinel, and introduced no deployment,
service restart, restore, infrastructure resize, or provider-configuration
change.

The closure decision permits the expanded dataset to remain active. It does
not authorize another migration, import, database write, restore, deployment,
service restart, or provider change.

## Production identity

| Property | Verified value |
|---|---|
| Neon project | `nameless-art-61629272` |
| Branch | `production` (`br-old-credit-ao7cn4h7`) |
| Endpoint | `ep-long-mud-ao7wdhiw` |
| Database | `neondb` |
| Direct migration/import role | `neondb_owner` |
| Pooled runtime role | `materialgraph_runtime` |
| Native branch protection | Unavailable under the current Neon plan |

Provider identity was reconciled against the contract, database observations,
and retained screenshots. The absence of native branch protection was
explicitly accepted with compensating controls; no paid-plan upgrade or
provider mutation was performed.

## Immutable input

| Input | SHA-256 or value |
|---|---|
| Manifest file | `7939dcfd0fab9a8e7e43f7395c59c874673ed19aaf49d1a942650a69595e3daa` |
| Manifest payload | `902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9` |
| Candidate identities | 1,727 |
| Chunk size | 100 |
| Expected inserts | 1,699 |
| Expected protected conflicts | 28 |

## Backup and migration

A custom-format production backup was created through the reviewed direct
endpoint before migration. It was non-empty, hashed, and its archive listing
was verified offline. Restoration was neither authorized nor performed.

The migration then completed from `7a4c2e91b6d8` to `c8f3a2d7e901`.
Post-migration reconciliation proved:

- the target revision was the sole active Alembic revision;
- all four lifecycle tables existed;
- the curated-state digest remained
  `56930eaf013600fc4966e618acc01895c3b1b5ea650547199225a81d3533296d`;
- the 28 curated materials, nine elements, 94 material-element rows, and
  material ID 5 sentinel remained unchanged; and
- no material import occurred during migration.

The migration evidence SHA-256 is
`b88268d654bec4dfe47f73e90bc1a993100526ef378e079c750274794854e088`.

## Pre-import snapshot

A second custom-format snapshot was captured after migration and before
import. The 51,689-byte archive has SHA-256
`ea3f5f49393dfc06a107ff0357057775d072cfce4ca382d2ce391ab171e1e94b`.
Its 126-entry archive listing passed offline verification. Snapshot evidence
has SHA-256
`e0f88ca738231fc6fe20cfdf1b4a34d59e042c631ac916b6283cab7ae0a4324f`.

## Import execution and recovery

The first import attempt used the pooled runtime role and stopped before the
first chunk because that role correctly had read-only table privileges. The
diagnostic confirmed checkpoint index zero, no committed import writes, and
no grant change.

After explicit authorization, execution resumed through the direct owner role
without widening runtime privileges. Import run
`81ffa889-40f8-4089-b8e2-e52c70caf2bd` completed with the exact reviewed
outcome:

| Outcome | Count |
|---|---:|
| Processed | 1,727 |
| Inserted | 1,699 |
| Protected conflicts | 28 |
| Updated | 0 |
| Unchanged | 0 |
| Rejected | 0 |
| Retired | 0 |
| Verified imported identities | 1,699 |
| Final material identities | 1,727 |
| Distinct material `mp_id` values | 1,727 |

The lifecycle run status is `completed_with_conflicts`. The completed
checkpoint has SHA-256
`ca89d464dd443fd3ac712b4a378269978dcbbb126a6d690bf12f85d55f985b07`.
No duplicate event key or duplicate source identity was found.

## Post-import database observation

Sixteen sequential read-only samples were captured over 901.478 seconds.
Every sample reported:

- 1,727 materials;
- stable lifecycle totals;
- preserved curated state and sentinel;
- successful pooled-runtime read access;
- no reconciliation issue; and
- database size within the reviewed 256 MiB upper bound.

The SQL observation reported a stable logical database size of 15,212,544
bytes. Provider monitoring showed the managed database metrics stabilizing
after import, zero observed deadlocks, low connection use, and the compute
returning to its suspended state. The database observation SHA-256 is
`ceda5199b1df7ca6c6b4b4a3e9865e441bf009fb653505ba230fac5799b48903`.

## API and host observation

Seven representative production API requests returned HTTP 200:

| Request | Elapsed milliseconds |
|---|---:|
| Health | 319.156 |
| Material detail | 2,100.196 |
| Neighbors | 2,426.270 |
| Similar | 3,164.993 |
| Neighborhood | 16,242.222 |
| Criticality | 636.759 |
| Discovery candidates | 1,417.121 |

The neighborhood request completed within the deployed timeout boundary but
remains an accepted performance signal. API evidence has SHA-256
`161f89832dc87fe58150d73b044439570ae441939fa8aeaed9a592dd415f3193`.

Read-only host inspection confirmed active and enabled MaterialGraph and Nginx
services, successful health response, no recent Nginx 5xx response, and no
observed traceback, critical, unhandled, segmentation-fault, or
out-of-memory marker. No host mutation, deployment, or restart was performed.
The host summary SHA-256 is
`2960a0799d06369eaaec8e811a4976e003e6809bc82c95d7172da460aa54dca8`.

## Independent reconciliation and retention decision

The final independent reconciliation matched 16 critical evidence hashes,
inventoried 53 files, and passed its bounded credential scan. The local
612,389-byte closure archive has SHA-256
`5daec8411c7621be2f982bb991ab11dcbfb60b203a350b29ebafae14d1b1fe85`.
It contains database archives and must remain outside Git and under restricted
local control.

The independent reconciliation SHA-256 is
`6db5492cede28c9d853d8332f5f72c29d8c3aed61000cf9a36903cb01091e131`;
the inventory SHA-256 is
`41930d38d071f538349dea53beb6b4c89bd3aeb94b1aae4fa1689b1d633db04d`.

The operator separately authorized the exact 1,727-material state to remain
active. That decision record has SHA-256
`a75eba645e15b7026e5aba6f1dcd167c2f26f4f688ecdea70945707edca7dea6`.

## Accepted limitations

1. Native Neon branch protection requires a paid plan and remains disabled.
2. The representative neighborhood request took approximately 16.2 seconds.
3. The production execution was intentionally sequential and does not establish
   concurrent-load capacity.
4. Restoration was not tested or authorized.
5. Scientific qualification remains bounded by the MG-DE-006 accepted cohort
   limitations, including sparse sulfide coverage, two source-zero systems,
   lithium dominance, near-stability bias, and polymorph crowding.

## Closure

MG-DE-009 is closed. The exact reviewed dataset remains active in production.
The closure does not authorize further mutation or operational change.
Future refresh, migration, restore, deployment, restart, concurrency testing,
or materially larger expansion requires a new reviewed scope and explicit
authorization.
