# MG-SEC-007 Change Impact — Least-Privilege Database Roles

## Status

Completed and verified on 2026-09-06.

## Baseline

- Repository and deployed baseline:
  `95ac8659d213a45d4bccedac10acd4c2d0fca193`.
- Recovery prerequisite: `MG-SEC-012` Verified.
- Database transport prerequisite: `MG-SEC-006` retired after revalidation;
  `verify-full`, an explicit trusted CA bundle for backups, and required
  channel binding are deployed.

## Confirmed starting state

- Runtime uses a pooled Neon endpoint and migration uses a direct endpoint.
- Both URLs authenticate as the same identity.
- That identity owns the database, `public` schema, all nine tables, and all
  seven sequences.
- It can create roles and databases, replicate, bypass row-level security, and
  create schema objects.
- It has every inspected table privilege across all nine tables.
- The mounted production API performs database reads; the write-capable import,
  seed, backfill, and graph-job paths are operational or currently unmounted
  paths rather than public runtime routes.

## Approved target boundary

1. Retain the current owner identity for migrations and explicit administrative
   operations only.
2. Create the runtime and backup login identities with SQL, not the Neon
   Console, CLI, or API, so they do not inherit `neon_superuser` membership.
3. Give runtime only database `CONNECT`, schema `USAGE`, and `SELECT` on the
   current application tables.
4. Give backup only the scoped read permissions required for `pg_dump` and
   manifest collection on current tables and sequences.
5. Deny both identities superuser, role creation, database creation,
   replication, and row-level-security bypass attributes.
6. Define owner-scoped default privileges so future migration-created tables
   and sequences remain readable by the intended identities without granting
   schema creation or ownership.
7. Keep migration and administrative credentials out of the runtime
   `DATABASE_URL`. Coordinate persistent secret-file isolation with
   `MG-SEC-003` and the dedicated operating-system identity in `MG-SEC-004`.

## Expected impact

- Public scientific endpoints should remain byte-for-byte equivalent because
  their mounted database operations are reads.
- A compromised runtime credential should be unable to mutate or truncate
  scientific data, create persistent principals or databases, replicate data,
  bypass future RLS, or create schema objects.
- Imports, seeds, backfills, and Alembic must use the migration/administrative
  path explicitly; running them with the runtime credential should fail.
- Backups should remain behaviorally identical under a separate read-only
  credential.
- No paid Neon feature or additional infrastructure service is required.

## Rollout order

1. Record the baseline and current deterministic endpoint outputs.
2. Create non-privileged roles without changing production configuration.
3. Apply and verify scoped grants and owner-scoped default privileges.
4. Test each new credential directly without printing it.
5. Switch and restart the backup path; require a verified backup.
6. Switch the runtime path; restart MaterialGraph and require health plus
   representative deterministic endpoint equivalence.
7. Verify Alembic remains on the separate owner path.
8. Remove superseded secrets from runtime-readable configuration only after
   rollback evidence is preserved and the new paths pass.
9. Revoke or delete only credentials proven obsolete; do not remove the owner
   role or transfer production object ownership in this remediation.

## Rollback

- Preserve the working owner connection outside logs and source control until
  all checks pass.
- On runtime failure, restore only the previous `DATABASE_URL`, restart the
  service, and require HTTP `200` health before further work.
- On backup failure, restore only the previous backup connection, rerun the
  oneshot service, and require `backup_verified`.
- Grants to new roles may remain during rollback because they do not alter
  existing ownership. Drop them only after confirming they are unused.
- No destructive database operation, ownership transfer, or production restore
  is authorized by this record.

## Non-goals

- No tenant or row-level-security design before private multi-user data exists.
- No activation of graph-job routes or new write API.
- No database engine, Neon plan, region, or schema change.
- No resolution of EC2 passwordless sudo or final environment-file ownership;
  those remain `MG-SEC-004` and `MG-SEC-003`.

## Observed impact

- Runtime, migration, and backup now authenticate with separate identities.
- Runtime retains the exact reads required by the mounted public API and has no
  inspected table mutation, sequence, schema-creation, database-creation, or
  administrative capability.
- Backup retains manifest and archive reads and produced a verified nine-table
  archive through its dedicated credential.
- Alembic remains functional through an isolated root-owned migration
  environment.
- Complete material, screening, and discovery JSON matched exactly before and
  after the runtime switch; production health remained HTTP `200`.
- No paid Neon feature or additional infrastructure was introduced.
- PostgreSQL's default database `TEMP` privilege remains as a documented,
  constrained residual because a global `PUBLIC` revocation was outside scope.
