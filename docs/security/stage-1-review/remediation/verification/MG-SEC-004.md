# MG-SEC-004 Verification — Dedicated Runtime Identity

## Status

Pending production implementation and verification.

Baseline: `97aa170b3418afc38570a14bcc93523d6ce98392`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Dedicated `materialgraph` system user and group exist with a non-login shell and nonexistent home path | Pending |
| 2 | Runtime identity has no supplementary, sudo, or LXD membership | Pending |
| 3 | Effective systemd `User` and `Group` are `materialgraph` | Pending |
| 4 | Runtime environment is root-owned, group-readable only by `materialgraph`, mode `640`, and has one hard link | Pending |
| 5 | Runtime identity can read but cannot modify the environment file | Pending |
| 6 | Runtime identity cannot write the repository, application code, scripts, or virtual environment | Pending |
| 7 | Pre-start metadata validation succeeds for the protected runtime environment | Pending |
| 8 | Unsafe mode, owner, group, symlink, and hard-link fixtures fail closed | Pending |
| 9 | `NoNewPrivileges`, private temporary storage/devices, filesystem, kernel, and control-group protections are effective | Pending |
| 10 | Effective capability bounding and ambient capability sets are empty | Pending |
| 11 | Runtime identity cannot invoke passwordless sudo or access LXD | Pending |
| 12 | Application starts and restarts without permission or sandbox violations | Pending |
| 13 | Uvicorn remains bound only to `127.0.0.1:8000` and Nginx remains active | Pending |
| 14 | Health and database-backed endpoints return HTTP `200` | Pending |
| 15 | Representative material, screening, and discovery JSON responses match the pre-change baseline exactly | Pending |
| 16 | Backup timer and isolated migration path remain operational | Pending |
| 17 | Focused tests, complete suite, Ruff, diff check, and GitHub secret scan pass | Pending |
| 18 | Rollback artifacts and superseded runtime secret are removed only after successful verification | Pending |

The finding remains **In remediation** until every row is supported by recorded
production evidence.
