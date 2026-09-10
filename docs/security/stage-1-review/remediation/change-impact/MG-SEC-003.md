# MG-SEC-003 Change Impact — Production Environment File Boundary

## Status

Completed and verified on 2026-09-10.

Implementation and deployed checkpoint:
`cb8e3b711b74ec0f7fe1158e7b2f6f18d03309f3`.

## Baseline

- Repository and deployed baseline:
  `28d205db60467a949a74f6e38135c20825b55502`.
- The original inspection recorded `/opt/materialgraph/.env` as
  `ubuntu:ubuntu` mode `664`.
- The approved MG-SEC-007 rollout corrected the deployed mode to `600`; this
  remediation independently verifies that boundary and prevents regression.

## Approved scope

1. Require the runtime environment path to be a regular file.
2. Require ownership by the effective MaterialGraph service user.
3. Require mode exactly `600` and exactly one hard link.
4. Check metadata before every service start without reading file contents.
5. Fail service startup when the boundary is unsafe.
6. Preserve the current `ubuntu` service identity until MG-SEC-004 separately
   establishes a dedicated non-administrative account.

## Expected impact

- Other local identities cannot read the runtime environment file through
  ordinary filesystem permissions.
- Accidental permission, ownership, symlink, or hard-link regression prevents
  MaterialGraph startup instead of silently exposing credentials.
- Valid production startup, database access, and scientific behavior are
  unchanged.
- No paid service or additional infrastructure is introduced.

## Rollout and rollback

1. Run focused and complete repository tests before deployment.
2. Copy the reviewed `materialgraph.service` into `/etc/systemd/system` and run
   `systemctl daemon-reload`.
3. Execute the checker directly against the deployed environment file.
4. Restart MaterialGraph and require active state plus HTTP `200` health and a
   database-backed material read.
5. On failure, inspect metadata without printing contents. Restore owner
   `ubuntu:ubuntu` and mode `600` if drift is confirmed.
6. Roll back only the unit-file pre-start line if the checker itself is proven
   defective; do not weaken the environment-file permissions.

## Non-goals and coordination

- MG-SEC-003 does not remove `ubuntu` from `sudo` or `lxd`, make the application
  checkout read-only, or create a dedicated service identity. Those controls
  remain MG-SEC-004.
- It does not move migration or backup credentials back into the runtime file.
- It does not rotate credentials without separate evidence of exposure.
- It does not print or inspect environment-file contents.
