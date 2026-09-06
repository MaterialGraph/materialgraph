# MG-SEC-007 Verification — Least-Privilege Database Roles

## Status

Verified on 2026-09-06. All twenty acceptance criteria passed.

## Acceptance criteria

| Check | Required result | Status |
|---|---|---|
| Runtime and migration identities differ | True | Pass |
| Runtime superuser | False | Pass |
| Runtime role creation | False | Pass |
| Runtime database creation | False | Pass |
| Runtime replication | False | Pass |
| Runtime RLS bypass | False | Pass |
| Runtime database ownership | False | Pass |
| Runtime `public` schema ownership and creation | False | Pass |
| Runtime table access | `SELECT` only on required tables | Pass |
| Runtime sequence access | None for current mounted API | Pass |
| Runtime data mutation and DDL probes | Rejected and rolled back | Pass |
| Backup identity administrative attributes | All false | Pass |
| Backup scoped reads and verified archive | Pass | Pass |
| Migration identity remains separate and Alembic-authorized | Pass | Pass |
| Future-object default privileges | Scoped and verified | Pass |
| Production application health | HTTP `200` | Pass |
| Representative scientific outputs and ordering | Exact match | Pass |
| Backup timer | Active and enabled | Pass |
| Credentials absent from output, logs, and Git | Pass | Pass |
| Full tests, Ruff, diff check, and Gitleaks | Pass | Pass |

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

## Verification evidence

Redacted operator-controlled production checks established:

- SQL-created `materialgraph_runtime` and `materialgraph_backup` login roles
  have no superuser, role-creation, database-creation, replication, RLS-bypass,
  or `neon_superuser` membership capability.
- Runtime has database `CONNECT`, `public` schema `USAGE`, and `SELECT` on all
  nine application tables. It has no sequence access, table mutation
  privilege, schema creation, or database creation.
- Transactionally safe runtime probes read application data and rejected both
  an update and schema DDL.
- Backup has only the scoped table and sequence reads required for manifest
  collection and `pg_dump`; its mutation probe was rejected.
- Owner-scoped default privileges grant future table reads to both restricted
  identities and future sequence reads only to backup.
- `/opt/materialgraph/.env` contains only the pooled restricted runtime URL and
  is mode `600`. The owner migration URL is isolated in root-owned mode-`600`
  `/etc/materialgraph/migration.env`; the dedicated backup URL is isolated in
  root-owned mode-`600` `/etc/materialgraph/backup.env`.
- Alembic connected successfully through the isolated migration environment.
- The backup service created and verified a new 30,967-byte, nine-table archive
  through the dedicated backup identity at deployed checkpoint `4cdfa87`.
- MaterialGraph remained active and returned HTTP `200`; its backup timer
  remained active and enabled.
- Complete parsed JSON for a material read, screening request, and discovery
  request matched exactly before and after the runtime credential switch.
- Temporary rollback copies, response captures, and shell-held credential
  values were removed after verification.
- The repository bundle is complete and matches deployed implementation commit
  `4cdfa87649d93e4f1c8040a94bf76328ea673a7e`.

No credential, URL, public IP address, database identifier, or unnecessary
infrastructure identifier is retained in this record.

## Constrained residual

Both restricted roles retain PostgreSQL's default database `TEMP` privilege.
They cannot create persistent database or `public` schema objects, and the
runtime service has no operational need to create temporary objects. Revoking
`TEMP` globally from `PUBLIC` would affect every database role and is therefore
outside this focused role-separation change. This residual is accepted for the
current public-data prototype and must be reconsidered before private tenant
data or untrusted SQL execution is introduced.

## Conclusion

The public runtime, backup, and migration paths now use separate credentials
and privilege boundaries. Runtime compromise no longer confers the original
owner identity's role creation, database creation, replication, RLS bypass,
schema ownership, DDL, or table-mutation capabilities. Backup recoverability,
migration access, application health, and deterministic scientific behavior all
remain verified. `MG-SEC-007` is Verified.
