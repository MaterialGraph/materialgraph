# MG-SEC-012 Remediation Verification

## Status

Prepared; implementation and verification pending.

## Approved targets

- RPO: **24 hours**.
- RTO: **4 hours**.
- Backup frequency: **Daily**.
- Retention: **30 days**.
- Restore testing: **Initial, quarterly, and after material backup or schema
  process changes**.
- First restore target: **Isolated; never production**.

## Acceptance criteria

1. A private off-host backup is created from the production database at least
   once per 24-hour period.
2. Backup and manifest objects use HTTPS in transit and S3-managed encryption at
   rest.
3. S3 public access is blocked, ACL sharing is disabled, versioning is enabled,
   and lifecycle policy removes current and noncurrent data on the documented
   bounded schedule.
4. The EC2 backup identity can upload and inspect the required prefix but cannot
   delete backup objects or administer the bucket.
5. Database credentials, URLs, AWS credentials, bucket identifiers, and secret
   values do not appear in tracked files, process arguments, test output, or
   committed evidence.
6. Temporary dump and manifest files are owner-only and are removed after a
   verified upload without deleting prior recovery points.
7. The timer is persistent across host downtime, fails closed, and records a
   bounded success or failure result.
8. A selected backup restores into an isolated target in less than four hours.
9. The restored Alembic revision, table counts, key relationships, and
   representative scientific records reconcile with the source manifest.
10. Representative deterministic API outputs and ordering match the source
    checkpoint.
11. Production remains unchanged and healthy throughout isolated restoration.
12. A second operator can follow the runbook without undocumented steps.

## Required evidence

- Exact repository and deployed commits.
- Redacted S3 bucket encryption, public-access, versioning, lifecycle, and policy
  summaries.
- Redacted EC2 role policy and denied-delete test.
- PostgreSQL client and dump-format versions.
- Backup start/end timestamps, compressed size, SHA-256, and upload result.
- Timer enablement and last-run result.
- Source and restored schema revision and row-count manifest.
- Isolated restore start/end timestamps and elapsed duration.
- Representative deterministic API comparison.
- Production health result before and after restoration.
- Cleanup result for temporary local files and the isolated restore target.
- Complete project tests, Ruff, Git whitespace check, and Gitleaks result for
  repository changes.

## Verification commands and results

Pending. Commands must use placeholders or redacted output and must not expose
connection strings, passwords, AWS account details, bucket names, or object
keys containing sensitive context.

## Conclusion

Pending. Backup creation alone is insufficient; the finding remains In
remediation until isolated restoration and all integrity checks pass.
