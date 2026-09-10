# MG-SEC-003 Verification — Production Environment File Boundary

## Status

Verified on 2026-09-10. All thirteen acceptance criteria passed.

## Acceptance criteria

| Check | Required result | Status |
|---|---|---|
| Runtime environment path | Regular file, not a symlink | Pass |
| Runtime environment owner | Effective service user | Pass |
| Runtime environment mode | Exactly `600` | Pass |
| Runtime environment hard links | Exactly one | Pass |
| Extended ACL indicator | Absent | Pass |
| Unauthorized local read | Rejected | Pass |
| Unsafe metadata unit tests | Rejected | Pass |
| systemd pre-start enforcement | Installed and successful | Pass |
| MaterialGraph restart | Active without traceback | Pass |
| Health endpoint | HTTP `200` | Pass |
| Database-backed material read | HTTP `200` | Pass |
| Secrets absent from output, logs, tests, and Git | Pass | Pass |
| Full tests, Ruff, diff check, and Gitleaks | Pass | Pass |

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

## Implementation and deployment evidence

- Repository tests: 25 focused tests passed with one expected Windows-only
  POSIX integration skip; 752 complete tests passed with the same skip.
- Focused Ruff and Git whitespace checks passed.
- GitHub Secret Scan run 66 completed successfully for the implementation
  checkpoint.
- The deployed metadata checker accepted the production file and rejected
  unsafe-mode and symbolic-link temporary fixtures; all fixtures were removed.
- The reviewed unit was installed and systemd recognized the exact pre-start
  checker as `ubuntu:ubuntu` against `/opt/materialgraph/.env`.
- The pre-start process completed with status `0/SUCCESS`, MaterialGraph
  restarted without traceback, and both health and a database-backed material
  read returned HTTP `200`.
- The deployed unit matched the repository-controlled unit byte-for-byte.
- The deployed worktree was clean at
  `cb8e3b711b74ec0f7fe1158e7b2f6f18d03309f3`; the backup timer remained active.
- The rollback unit was removed after success. Final metadata remained
  `ubuntu:ubuntu`, mode `600`, one hard link; an unprivileged read remained
  rejected and final health remained HTTP `200`.

## Residual boundary

The current service and file owner remains the administratively capable
`ubuntu` account. MG-SEC-003 verifies that other local identities cannot read
the file and that unsafe metadata fails startup; it does not claim the service
identity itself is least-privileged. Dedicated account, checkout-writability,
and passwordless-root remediation remain independently open as MG-SEC-004.

## Conclusion

The original world-readable production environment-file exposure is removed
and protected by a deployed fail-closed regression guard. MG-SEC-003 is
Verified.
