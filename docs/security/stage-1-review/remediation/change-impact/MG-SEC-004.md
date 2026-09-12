# MG-SEC-004 Change Impact — Dedicated Runtime Identity

## Status

Approved and in progress on 2026-09-12.

Repository and deployed baseline:
`97aa170b3418afc38570a14bcc93523d6ce98392`.

## Confirmed production baseline

- `materialgraph.service` runs as `ubuntu:ubuntu`.
- `ubuntu` has passwordless sudo and belongs to `lxd`.
- `/opt/materialgraph`, its application code, scripts, virtual environment, and
  runtime environment file are writable by `ubuntu`.
- `NoNewPrivileges`, private temporary storage and devices, filesystem
  protection, kernel protection, control-group protection, and SUID/SGID
  restrictions are disabled.
- The application and database-backed health checks returned HTTP `200` before
  remediation.

## Approved scope

1. Create a dedicated system user and primary group named `materialgraph` with
   no interactive shell, home directory, sudo access, LXD membership, or other
   supplementary groups.
2. Run only the public MaterialGraph application as that identity. Deployment,
   migration, backup, SSH, and administrative work remain separate.
3. Move the runtime environment boundary to
   `/etc/materialgraph/runtime.env`, owned by `root:materialgraph`, mode `640`,
   with one hard link. The service can read but cannot modify it.
4. Keep the repository and virtual environment owned by the deployment account
   and unwritable by the runtime identity.
5. Extend the existing metadata checker to verify an explicit owner, the
   runtime group, exact mode, regular-file type, and one-hard-link boundary
   without reading contents.
6. Enable systemd protections that preserve only Unix, IPv4, and IPv6 network
   access and do not require a writable application checkout.

## Expected impact

- Application compromise no longer directly yields the passwordless sudo or
  LXD-capable deployment identity.
- The runtime process cannot modify application code, its virtual environment,
  deployment configuration, or runtime credentials.
- Uvicorn continues to bind only to `127.0.0.1:8000`, connect outbound to Neon,
  write temporary files only in its private temporary namespace, and log to the
  journal.
- Database privileges remain restricted by MG-SEC-007.
- Scientific responses and deterministic ordering remain unchanged.
- No paid service or additional infrastructure is introduced.

## Rollout

1. Pass focused tests, the complete suite, lint, diff checks, and secret scan.
2. Create the locked `materialgraph` system identity and verify its exact group
   and sudo boundaries.
3. Install a root-owned runtime environment file without printing its contents.
4. Install and validate the reviewed unit, then reload systemd.
5. Restart the application and verify the pre-start check, process identity,
   listener, database access, health, and deterministic scientific responses.
6. Verify the runtime identity cannot write protected paths, invoke sudo, or
   access LXD.
7. Remove the superseded `/opt/materialgraph/.env` only after the new service is
   stable and recovery evidence is retained securely for the rollout window.

## Rollback

- Before mutation, preserve root-readable copies of the deployed unit and
  environment file outside the repository with mode `600`.
- If the dedicated identity cannot run the reviewed application, restore the
  prior unit and environment path, reload systemd, restart, and require health
  plus database-backed HTTP `200` before investigating further.
- Do not weaken file permissions, add the runtime user to `ubuntu`, `sudo`, or
  `lxd`, or grant capabilities as an expedient rollback.

## Non-goals

- This change does not alter SSH access or remove administrative privileges
  from the separate deployment account; host administration remains in scope
  for operators and outside the public runtime identity.
- It does not change Nginx, TLS, request limiting, database roles, migrations,
  backups, or scientific algorithms.
- It does not claim container-level or virtual-machine isolation.
