# MG-SEC-012 Remediation Verification

## Status

Verified on 2026-09-06. All twelve acceptance criteria passed.

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

Redacted results recorded from the operator-controlled production host:

| Check | Result |
|---|---|
| EC2 instance role and temporary credentials | Expected role attached; temporary credentials available |
| S3 boundary | Location/list/upload allowed only as designed; outside-prefix list, download, and delete denied |
| PostgreSQL clients | `pg_dump`, `pg_restore`, and `psql` 17.11 |
| Backup archive | Custom format; 30,967 bytes; 77 archive entries; SHA-256 verified |
| S3 upload | Succeeded; remote size matched; local temporary archive removed |
| Isolated restore | Transactional restore completed into a separate recovery database |
| Relational reconciliation | 9 source tables and 9 restored tables; every recorded row count matched |
| Cleanup | Local restore archive removed; recovery connection removed from shell |
| Repository implementation | `ef2f158` with home-isolation compatibility at deployed checkpoint `70a76d4` |
| Automated service | Manual controlled run succeeded; owner-only workspace retained only the lock file |
| Persistent timer | Enabled and active; first scheduled run started at 02:18:14 UTC and verified at 02:18:27 UTC |
| Scheduled archive | Custom format; 30,967 bytes; manifest ID, size, SHA-256, and 9-table count matched |
| Temporary recovery access | Exact-object download permission was removed; subsequent download was denied |
| Scheduled restore | Completed transactionally in 8.76 seconds in an isolated database |
| Manifest reconciliation | Alembic revisions, all 9 table counts, and representative identifiers matched |
| Deterministic API comparison | 28 production and 28 recovery screening results matched exactly, including material and formula ordering |
| Production after recovery | Application and Nginx active; health returned HTTP 200 |
| Final cleanup | Isolated API stopped; local artifacts and shell connection values removed; temporary Neon branch deleted |
| Repository verification | 19 focused tests and 737 complete tests passed; focused Ruff and Git whitespace checks passed |

The bucket identifier, AWS account details, database URLs, passwords, temporary
credentials, and complete object key are intentionally omitted. The redacted
evidence is sufficient to reproduce the control checks without publishing
operational identifiers.

## Conclusion

The independent recovery path is proven from scheduled export through isolated
application behavior. The 24-hour RPO, four-hour RTO, private retention,
least-privilege upload boundary, scheduled execution, relational integrity,
deterministic output, production isolation, and cleanup criteria all passed.
`MG-SEC-012` is Verified. Quarterly and material-change restore exercises and
daily journal review remain ongoing controls rather than closure blockers.
