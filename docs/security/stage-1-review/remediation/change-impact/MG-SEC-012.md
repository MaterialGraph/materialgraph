# MG-SEC-012 Change Impact — Backup and Recovery Readiness

## Status

Approved design; implementation not started.

## Before

- Neon retains six hours of production history.
- No manual or scheduled snapshot exists.
- No independent database backup exists.
- No restore test, recovery runbook, RPO, or RTO exists.

## Intended after state

- A compressed logical production backup is created daily and retained for 30
  days in a private off-host S3 bucket.
- Backup upload uses encrypted transport and S3-managed encryption at rest.
- The EC2 backup identity can create and inspect timestamped backup objects but
  cannot delete them.
- A systemd timer runs the backup without embedding secrets in tracked files or
  command-line arguments.
- A documented isolated restore completes within four hours and loses no more
  than 24 hours of committed production state under the defined schedule.
- Quarterly and material-change restore tests keep the recovery procedure
  current.

## Expected impact

- Scientific results: **No intended change**.
- API schemas and responses: **No intended change**.
- Database schema or production rows: **No intended change during backup**.
- Production restore: **Not part of initial verification**.
- Infrastructure: **Yes** — private S3 storage, constrained AWS access, backup
  service and timer, and an owner-only temporary working directory.
- Operations: **Yes** — daily backups, bounded retention, failure evidence,
  quarterly restore tests, and documented recovery ownership.
- Cost: **Low and usage-based** — no always-running recovery compute, paid Neon
  upgrade, AWS Backup plan, customer-managed KMS key, or replica is introduced.

## Risks and controls

| Change risk | Required control |
|---|---|
| Secret exposure through process arguments or logs | Pass connection material through a protected runtime environment; never print commands with expanded values |
| Plaintext temporary dump | Owner-only directory and file; remove only after verified upload |
| Public or cross-account backup exposure | S3 Block Public Access, bucket-owner enforcement, private policy, and no ACL-based sharing |
| Host compromise deletes every backup | Timestamped objects, versioning, lifecycle-managed deletion, and no delete permission for the EC2 backup identity |
| Backup exists but cannot restore | Initial and recurring isolated restore tests with integrity evidence |
| Backup process changes scientific data | Use read-only logical export behavior and compare representative restored outputs |
| Unexpected recurring cost | Thirty-day lifecycle, compressed dumps, no persistent restore compute, and periodic usage review |

## Rollback boundary

Repository scripts and units can be disabled or reverted without modifying
production data. A failed backup must leave the prior verified S3 objects
untouched. An isolated restore target can be removed only after evidence is
captured and production connectivity is reconfirmed.

## Observed impact

Pending implementation and verification.
