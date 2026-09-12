# MG-SEC-004 Verification — Dedicated Runtime Identity

## Status

Verified on 2026-09-12. All nineteen acceptance criteria passed.

Baseline: `97aa170b3418afc38570a14bcc93523d6ce98392`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Dedicated `materialgraph` system user and group exist with a non-login shell and nonexistent home path | Pass |
| 2 | Runtime identity has no supplementary, sudo, or LXD membership | Pass |
| 3 | Effective systemd `User` and `Group` are `materialgraph` | Pass |
| 4 | Runtime environment is root-owned, group-readable only by `materialgraph`, mode `640`, and has one hard link | Pass |
| 5 | Runtime identity can read but cannot modify the environment file | Pass |
| 6 | Runtime identity cannot write the repository, application code, scripts, or virtual environment | Pass |
| 7 | Pre-start metadata validation succeeds for the protected runtime environment | Pass |
| 8 | Production disables the second Pydantic dotenv read while local development retains its `.env` default | Pass |
| 9 | Unsafe mode, owner, group, symlink, and hard-link fixtures fail closed | Pass |
| 10 | `NoNewPrivileges`, private temporary storage/devices, filesystem, kernel, and control-group protections are effective | Pass |
| 11 | Effective capability bounding and ambient capability sets are empty | Pass |
| 12 | Runtime identity cannot invoke passwordless sudo or access LXD | Pass |
| 13 | Application starts and restarts without permission or sandbox violations | Pass |
| 14 | Uvicorn remains bound only to `127.0.0.1:8000` and Nginx remains active | Pass |
| 15 | Health and database-backed endpoints return HTTP `200` | Pass |
| 16 | Representative material, screening, and discovery JSON responses match the pre-change baseline exactly | Pass |
| 17 | Backup timer and isolated migration path remain operational | Pass |
| 18 | Focused tests, complete suite, Ruff, diff check, and GitHub secret scan pass | Pass |
| 19 | Rollback artifacts and superseded runtime secret are removed only after successful verification | Pass |

## Repository evidence

- Implementation checkpoint:
  `b2747f67fcdf78568891525e66814b5de2adfb83`.
- 29 focused tests passed with one expected Windows-only POSIX integration
  skip; 756 complete tests passed with the same skip.
- Focused Ruff and Git whitespace checks passed.
- GitHub Secret Scan run 69 completed successfully.
- The tracked unit uses the dedicated identity, protected environment path,
  empty capability sets, restricted address families, and the approved systemd
  protections.
- Pydantic retains `.env` as its local-development default and accepts an
  explicit empty `MATERIALGRAPH_ENV_FILE` to disable the duplicate production
  dotenv read after systemd loads the protected file.

## Production evidence

- Baseline checks confirmed the previous `ubuntu` process had passwordless
  sudo, LXD membership, writable code and configuration, and no evaluated
  systemd isolation controls.
- The created `materialgraph` identity has UID 999, primary GID 988, nologin
  shell, nonexistent home path, no supplementary groups, no sudo access, and no
  LXD membership.
- `/etc/materialgraph/runtime.env` is a regular single-link file owned by
  `root:materialgraph`, mode `640`; the runtime identity can read but cannot
  modify it.
- The pre-start checker completed with `0/SUCCESS`. The running Uvicorn process
  uses UID 999 and GID 988, has `NoNewPrivs: 1`, and has zero inheritable,
  permitted, effective, bounding, and ambient capability sets.
- Effective systemd properties confirm private temporary storage and devices,
  strict system protection, protected home, kernel tunables, kernel modules,
  control groups, SUID/SGID restrictions, and only Unix/IPv4/IPv6 address
  families.
- The runtime identity cannot write the repository root, application code,
  scripts, virtual environment, or runtime environment.
- Uvicorn remains loopback-bound, Nginx and MaterialGraph remain active, health
  and a database-backed material read returned HTTP `200`, and the backup timer
  remains active.
- The isolated migration path and a fresh verified backup completed
  successfully after the identity change.
- Parsed material, screening, and discovery JSON responses matched the
  pre-change captures exactly.

## Rollout correction and recovery evidence

The first restart failed closed because Pydantic independently attempted to
read the old checkout `.env`. The prior unit was restored from the protected
rollback copy, and application health plus database access returned to HTTP
`200`. Commit `b2747f6` added the explicit production dotenv-disable boundary.

A subsequent preflight exposed one unreadable tracked source file created while
the operator shell retained `umask 077`. The public source file was restored to
mode `644`, the deployment mask was returned to `022`, and the dedicated
identity then imported the application successfully. Neither correction
weakened the secret boundary or added the runtime identity to another group.

After the hardened restart passed, the superseded checkout `.env` was removed.
MaterialGraph restarted again without it and returned HTTP `200` for health and
database-backed access. Rollback files and all response captures were then
removed; the Git worktree remained clean.

## Conclusion

The Internet-facing application no longer runs as the passwordless sudo- and
LXD-capable deployment account. Runtime, deployment, migration, backup, and
administrative boundaries are separated, and the deployed sandbox preserves
required application behavior. `MG-SEC-004` is Verified.
