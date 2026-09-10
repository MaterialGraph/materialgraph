# MG-SEC-003 Verification — Production Environment File Boundary

## Status

In progress. The deployed mode correction is confirmed; repository-controlled
pre-start enforcement still requires deployment verification.

## Acceptance criteria

| Check | Required result | Status |
|---|---|---|
| Runtime environment path | Regular file, not a symlink | Pending |
| Runtime environment owner | Effective service user | Pending |
| Runtime environment mode | Exactly `600` | Pending |
| Runtime environment hard links | Exactly one | Pending |
| Extended ACL indicator | Absent | Pending |
| Unauthorized local read | Rejected | Pending |
| Unsafe metadata unit tests | Rejected | Pending |
| systemd pre-start enforcement | Installed and successful | Pending |
| MaterialGraph restart | Active without traceback | Pending |
| Health endpoint | HTTP `200` | Pending |
| Database-backed material read | HTTP `200` | Pending |
| Secrets absent from output, logs, tests, and Git | Pass | Pending |
| Full tests, Ruff, diff check, and Gitleaks | Pass | Pending |

## Pre-implementation deployment evidence

Redacted checks at deployed baseline `28d205d` established:

- the Git worktree was clean;
- `/opt/materialgraph/.env` was a single-link regular file owned by
  `ubuntu:ubuntu` with symbolic mode `-rw-------` and numeric mode `600`;
- no extended-ACL marker was present;
- a read attempt as the unprivileged `nobody` identity was rejected;
- systemd loaded the exact environment path as `ubuntu:ubuntu`;
- MaterialGraph restarted cleanly without a traceback; and
- health and a database-backed material endpoint both returned HTTP `200`.

The environment contents, connection URLs, credentials, external identifiers,
and secret values were neither inspected nor recorded.

## Required deployment verification

- Install the reviewed unit and reload systemd.
- Run the metadata checker directly as the service user.
- Confirm the effective unit contains the exact `ExecStartPre` check.
- Restart and repeat active, health, and database-backed endpoint checks.
- Confirm unsafe temporary fixtures fail without modifying the production
  environment file.
- Reconfirm the repository/deployment commit and clean worktree.

## Closure rule

MG-SEC-003 remains In remediation until every acceptance row is Pass and the
enforcement commit is deployed. MG-SEC-004 remains independently open even
after this file-read exposure is verified.
