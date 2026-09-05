# Database Backup and Isolated Restore Runbook

## Status

Initial manual backup and isolated database restore completed on 2026-09-05.
Tracked daily automation is prepared for deployment; its first scheduled run
remains required before closure. Runtime values must not be committed.

## Objective

Provide a low-cost, independently retained logical backup of the current Neon
production database and prove that it can be restored without using production
as the test target.

## Recovery targets

| Control | Initial target |
|---|---|
| Recovery-point objective | 24 hours |
| Recovery-time objective | 4 hours |
| Backup schedule | Daily |
| Retention | 30 days |
| Restore-test schedule | Initial, quarterly, and after material process changes |

## Architecture

- Source: Neon production PostgreSQL.
- Export: PostgreSQL custom-format logical dump.
- Scheduler: EC2 systemd service and persistent timer.
- Temporary workspace: owner-only directory outside the repository.
- Durable destination: private S3 bucket in the EC2 region.
- Encryption: TLS for database export, HTTPS for S3 transfer, and SSE-S3 at
  rest.
- Restore target: temporary isolated Neon branch or separate database.

No paid Neon retention upgrade, replica, RDS database, AWS Backup plan, or
customer-managed KMS key is required for the initial prototype boundary.

## One-time S3 controls

Create a dedicated bucket or isolated prefix with:

1. S3 Block Public Access enabled at every level.
2. Bucket-owner-enforced object ownership and ACLs disabled.
3. Default SSE-S3 encryption.
4. A policy denying requests when `aws:SecureTransport` is false.
5. Versioning enabled.
6. Lifecycle expiration for current data after 30 days, noncurrent data after
   seven days with zero newer versions retained, and incomplete multipart
   uploads after one day. Expired delete-marker cleanup is not enabled because
   S3 does not allow it in the same rule as current-version expiration.
7. No website hosting, public access point, or cross-account grant.

Use timestamped object names and never overwrite a prior backup. Do not record
the real bucket name or AWS account number in committed evidence.

## AWS identity boundary

Prefer an EC2 instance role over static access keys. The automated backup
identity should be limited to the dedicated backup prefix and only the actions
needed to upload, list, and inspect objects. It must not receive object-delete,
bucket-policy, public-access, lifecycle, versioning-administration, or general
S3 administration permission.

Restore/download permission should remain with the administrative recovery
identity rather than the public application process.

## Secret handling

- Read the existing production database configuration without printing it.
- Do not place an expanded database URL on a command line.
- Construct the PostgreSQL subprocess environment in a protected wrapper so
  host, port, database, user, password, and TLS settings are passed without
  logging their values.
- Require encrypted database transport for the backup connection. Full
  certificate validation becomes mandatory with `MG-SEC-006`.
- Run with a restrictive umask and owner-only temporary directory.
- Log only timestamps, result state, byte count, checksum prefix if needed, and
  non-sensitive failure category.

## Backup procedure

1. Confirm the deployed repository commit and clean worktree.
2. Confirm sufficient temporary disk space and an owner-only backup directory.
3. Confirm the PostgreSQL client is compatible with the Neon server version.
4. Confirm the backup identity without printing credentials or resource IDs.
5. Record a source manifest containing:
   - UTC timestamp;
   - Alembic revision;
   - PostgreSQL major version;
   - expected application table names and row counts;
   - representative non-secret scientific record identifiers;
   - application commit.
   Export the manifest queries and dump from one PostgreSQL exported snapshot
   so concurrent writes cannot make their recorded states disagree.
6. Run `pg_dump` in custom format with ownership and access-control restoration
   excluded from the portable recovery contract.
7. Verify the dump is nonempty and inspectable with `pg_restore --list`.
8. Calculate SHA-256 for the dump and manifest.
9. Upload both to a unique timestamped S3 prefix using HTTPS and SSE-S3.
10. Inspect remote object size and creation time through prefix listing, and
    require each upload response to confirm SSE-S3. SHA-256 is stored in object
    metadata and in the separately uploaded manifest; recovery verifies it
    before restore.
11. Remove the local temporary files only after remote verification succeeds.
12. Record bounded success evidence. On failure, retain protected local data
    only long enough for diagnosis and never delete an earlier S3 recovery
    point.

## Scheduling and failure behavior

- Use a oneshot systemd service and a persistent daily timer.
- Prevent overlapping executions with an exclusive local lock.
- Apply bounded execution time and fail when dump, inspection, checksum, upload,
  or remote verification fails.
- Record failure in journald and the systemd service result. Review it daily
  until an existing or near-zero-cost external notification channel is
  approved; do not add a paid monitoring platform solely for this prototype.
- Review the newest verified object age and timer result regularly. A successful
  service exit without a remotely verified object is a failure.

## Isolated restore procedure

1. Select a verified backup within retention and record its non-sensitive UTC
   recovery point.
2. Create a temporary isolated Neon branch or separate test database. Do not
   change the production branch or its connection settings.
3. Use separate restore credentials supplied at runtime and require encrypted
   transport.
4. Download the dump and manifest through HTTPS.
5. Verify object size and SHA-256 before restoration.
6. Restore without source ownership or privilege grants.
7. Verify:
   - restore command completion;
   - Alembic revision;
   - expected tables and row counts;
   - foreign-key and key relationship integrity;
   - representative material, element, risk, application, and relationship
     records;
   - representative deterministic API responses and ordering.
8. Measure elapsed time from restore initiation through application validation.
9. Confirm production health and representative production results remain
   unchanged.
10. Record redacted evidence and limitations.
11. Remove the temporary restore target only after verification evidence is
    complete and no diagnostic need remains.

## Automation deployment

The repository supplies `scripts/backup_database.py`,
`materialgraph-backup.service`, `materialgraph-backup.timer`, and
`materialgraph-backup.env.example`. Follow the exact installation and first-run
checks in [`../../../../guide/DEPLOYMENT.md`](../../../../guide/DEPLOYMENT.md).
The installed `/etc/materialgraph/backup.env` contains only the private bucket
name, region, and prefix. Database configuration remains in the existing
protected application environment file and AWS access comes from the instance
role.

## Failure and escalation

- Backup older than 24 hours: RPO breach; investigate before risky deployment.
- Restore exceeds four hours: RTO breach; preserve evidence and revise the
  procedure or target.
- Checksum mismatch: reject the object; do not restore it.
- Missing or inconsistent rows: treat the restore as failed even when
  `pg_restore` exits successfully.
- Scientific output mismatch: stop closure and determine whether the source
  manifest, restore process, configuration, or application version differs.
- Production impact: stop the test, preserve logs without secrets, and follow
  the production incident boundary.

## Cost review

Review storage bytes, request volume, lifecycle behavior, and restore-compute
duration after the first month. Increase retention or provider capability only
when data value, user commitments, regulation, or measured recovery needs
justify the cost.

## Closure evidence

`MG-SEC-012` can become Verified only after a real backup is remotely verified,
an isolated restore completes within the RTO, source and restored integrity
checks reconcile, production remains unchanged, and the next scheduled backup
is confirmed.
