# MaterialGraph Stage 1 Security Remediation

## Status

Wave 0 verified. `MG-SEC-012` established recovery readiness.
`MG-SEC-006` is retired after exact deployment revalidation and completed
certificate-validation hardening. `MG-SEC-007` is verified with deployed
least-privilege runtime and backup roles and an isolated migration path.
`MG-SEC-003` is verified with an owner-only environment-file boundary and
deployed fail-closed pre-start enforcement.
`MG-SEC-004` is verified with a dedicated non-login public runtime identity,
root-owned configuration, non-writable code, and tested systemd isolation.
`MG-SEC-005` is verified with trusted HTTPS for both public hostnames,
plaintext redirects, modern TLS, exercised renewal, and unchanged scientific
responses.

The governing inspection remains frozen. Finding records retain their original
evidence and severity; remediation status, change impact, implementation, and
verification are recorded separately in this directory.

## Baseline and authority

- Frozen application review commit:
  `32bc57cc78754e061f9a2f4294d81aa39e4f9955`.
- Final Stage 1 inspection commit:
  `bb888b54280fa5084fb9217335602527533be45a`.
- Verified remediation: `MG-SEC-012` recovery readiness.
- Retired after revalidation: `MG-SEC-006` database transport.
- Verified database finding: `MG-SEC-007` runtime, backup, and migration
  privilege separation.
- Verified filesystem finding: `MG-SEC-003` production environment-file access.
- Verified host-boundary remediation: `MG-SEC-004` dedicated runtime identity.
- Verified public-transport remediation: `MG-SEC-005` trusted HTTPS and HTTP
  redirection.
- Other findings remain outside the active implementation scope.

## Cost and reliability boundary

Wave 0 uses a proportionate prototype design:

- recovery-point objective: **24 hours**;
- recovery-time objective: **4 hours**;
- one compressed logical backup per day;
- 30-day rolling retention;
- private Amazon S3 storage with S3-managed encryption;
- EC2 systemd timer rather than a paid orchestration service;
- initial isolated restore test, then quarterly and after material backup or
  schema-process changes;
- no paid Neon upgrade, read replica, RDS database, AWS Backup plan,
  customer-managed KMS key, or multi-region replication at this stage.

The design must be revisited before MaterialGraph stores private research data
or when the cost of reconstructing production data materially increases.

## Workflow

1. Record the exact remediation baseline and approved scope.
2. Define rollback, secret-handling, cost, and scientific-integrity boundaries.
3. Prepare repository-controlled scripts and deployment configuration.
4. Verify scripts without production mutation.
5. Configure private off-host storage and least-privilege AWS access.
6. Create and verify the first production logical backup.
7. Restore only into an isolated target.
8. Verify schema, relationships, representative records, and deterministic API
   behavior.
9. Record timing, limitations, cleanup, and ongoing schedule evidence.
10. Mark `MG-SEC-012` Verified only when every acceptance criterion passes.

## Records

- [`REMEDIATION_REGISTER.md`](REMEDIATION_REGISTER.md) — authoritative current
  status.
- [`change-impact/MG-SEC-012.md`](change-impact/MG-SEC-012.md) — expected and
  observed operational impact.
- [`verification/MG-SEC-012.md`](verification/MG-SEC-012.md) — acceptance
  criteria and evidence checklist.
- [`verification/MG-SEC-006.md`](verification/MG-SEC-006.md) — corrected
  database-transport classification and deployed hardening evidence.
- [`change-impact/MG-SEC-007.md`](change-impact/MG-SEC-007.md) — approved role,
  credential, rollback, and scientific-impact boundaries.
- [`verification/MG-SEC-007.md`](verification/MG-SEC-007.md) — required
  privilege, deployment, backup, migration, and deterministic checks.
- [`change-impact/MG-SEC-003.md`](change-impact/MG-SEC-003.md) — approved
  environment-file metadata and rollback boundary.
- [`verification/MG-SEC-003.md`](verification/MG-SEC-003.md) — permission,
  pre-start enforcement, restart, and secret-safe evidence checklist.
- [`change-impact/MG-SEC-004.md`](change-impact/MG-SEC-004.md) — approved
  runtime-identity, filesystem, sandbox, rollout, and rollback boundary.
- [`verification/MG-SEC-004.md`](verification/MG-SEC-004.md) — required
  identity, privilege, systemd, endpoint, and scientific-integrity checks.
- [`change-impact/MG-SEC-005.md`](change-impact/MG-SEC-005.md) — approved DNS,
  certificate, proxy, rollback, and scientific-impact boundaries.
- [`verification/MG-SEC-005.md`](verification/MG-SEC-005.md) — public TLS,
  redirect, renewal, header, endpoint, and scientific-integrity checks.
- [`runbooks/database_backup_restore.md`](runbooks/database_backup_restore.md) —
  cost-conscious backup and isolated restore procedure.

## Safety boundary

- Never use production as the first restore-test target.
- Never print or commit database URLs, passwords, AWS credentials, account
  numbers, bucket names, object keys that expose sensitive context, or secret
  file contents.
- Do not treat backup creation as proof of recoverability.
- Do not delete the source backup or isolated target until verification
  evidence is recorded.
- Do not close the finding solely because a timer or bucket exists.
