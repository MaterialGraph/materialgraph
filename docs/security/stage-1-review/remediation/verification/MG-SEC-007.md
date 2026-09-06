# MG-SEC-007 Verification — Least-Privilege Database Roles

## Status

In progress. No production role or credential change is yet recorded as
verified.

## Acceptance criteria

| Check | Required result | Status |
|---|---|---|
| Runtime and migration identities differ | True | Pending |
| Runtime superuser | False | Pending |
| Runtime role creation | False | Pending |
| Runtime database creation | False | Pending |
| Runtime replication | False | Pending |
| Runtime RLS bypass | False | Pending |
| Runtime database ownership | False | Pending |
| Runtime `public` schema ownership and creation | False | Pending |
| Runtime table access | `SELECT` only on required tables | Pending |
| Runtime sequence access | None for current mounted API | Pending |
| Runtime data mutation and DDL probes | Rejected and rolled back | Pending |
| Backup identity administrative attributes | All false | Pending |
| Backup scoped reads and verified archive | Pass | Pending |
| Migration identity remains separate and Alembic-authorized | Pass | Pending |
| Future-object default privileges | Scoped and verified | Pending |
| Production application health | HTTP `200` | Pending |
| Representative scientific outputs and ordering | Exact match | Pending |
| Backup timer | Active and enabled | Pending |
| Credentials absent from output, logs, and Git | Pass | Pending |
| Full tests, Ruff, diff check, and Gitleaks | Pass | Pending |

## Required negative tests

Run only transactionally safe or isolated probes. The runtime identity must be
unable to:

- create a role or database;
- create an object in `public`;
- insert, update, delete, or truncate an application table;
- alter or drop application objects;
- use replication or bypass RLS attributes; or
- execute Alembic schema changes.

Never use a production row mutation merely to prove rejection. Use privilege
functions, a transaction that is always rolled back, or an isolated database
target.

## Scientific regression boundary

Capture representative production responses before switching credentials and
repeat them after switching. At minimum compare health, a basic material read,
screening, and one discovery or research path. Compare complete JSON and stable
material/formula ordering; do not accept merely matching result counts.

## Closure rule

MG-SEC-007 remains In remediation until every row above is Pass, deployed
configuration no longer gives the public runtime the owner credential, the
backup remains recoverable, and the resolution commit and deployment checkpoint
are recorded without secret material.
