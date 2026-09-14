# MG-SA Control Matrix

**Initial assessment checkpoint:** `5e794292eb7e712d1840095254cd72217d553cb5`
**Deployed remediation checkpoint:** `9a7fb1115e00d4e3a1864bf86e1423f522af2af1`
**Assessment status:** Both confirmed assurance defects verified and closed

| MG-SEC control | Threat and implementation | Test quality | Deployment evidence | Bypass analysis | Assurance result |
|---|---|---|---|---|---|
| `MG-SEC-001` | Aggregate exhaustion; Nginx per-IP rate/connection limits plus application concurrency gate | Every mounted route has an independent ordinary/expensive policy; tests enforce application/Nginx parity and behavioral `503` rejection for newly covered paths | Corrected commit deployed cleanly; effective distinct client/site zones and directive counts confirmed; bounded invalid-ID burst produced five `422` and three `429`; health remained `200` | Repository and deployed classifier cover all identified expensive routes; distinct `$binary_remote_addr` and `$server_name` zones implement per-client and aggregate limits, including explicit dual directives in expensive locations | **Implementation defect remediated and verified** through `MG-SA-001` |
| `MG-SEC-002` | Long scientific work; 3 s connection/pool, 3 s lock, 15 s statement, 20 s app, 25 s expensive-proxy hierarchy | Behavioral tests cover timeout response, recovery, retained slot, DB event configuration, rollback, exception mapping, and `504` behavior for newly covered paths | Corrected application restarted and route classifier verified directly; Nginx syntax/reload and 25-second location policy passed; six complete responses were unchanged | All policy-expensive material-intelligence routes receive the application deadline and expensive proxy timeout; individual DB statements remain bounded | **Implementation defect remediated and verified** through `MG-SA-001` |
| `MG-SEC-003` | Local secret disclosure; pre-start metadata validator and protected environment file | Behavioral metadata tests cover mode, owner/group, file type, hard links, and fail-closed startup configuration | Historical mode/read-denial/effective-unit evidence; not live-reproduced | Symlink and hard-link paths are checked; contents are not exposed; systemd loads the root-controlled file | **No issue** in repository; live state pending |
| `MG-SEC-004` | Host takeover after runtime compromise; dedicated identity and systemd sandbox | Mostly structural configuration assertions plus behavioral secret-file tests | Detailed historical effective-property and negative privilege evidence; not live-reproduced | Empty capabilities, no supplementary groups, protected filesystem, loopback bind; unrestricted egress remains accepted | **No issue** in repository; live state pending |
| `MG-SEC-005` | HTTP observation/modification; TLS, redirect, HSTS, protocol policy, renewal | Mostly structural assertions; TLS behavior requires deployed testing | Detailed historical certificate, protocol, redirect, renewal, and client evidence; not live-reproduced | Port-80 default host uses `$host` in redirect; retained as future hardening because no credentials/private state exist | **No issue** for current TLS control; live state pending |
| `MG-SEC-006` (Retired) | Original plaintext conclusion was disproved; both DB paths hardened to `verify-full` with channel binding | Repository checks establish configured requirements, not negotiated sessions | Historical direct client TLS/plaintext/hostname probes; not live-reproduced | `pg_stat_ssl` proxy-backend view is correctly excluded as client-leg proof | **No issue**; retirement reasoning is sound, live state pending |
| `MG-SEC-007` | Excessive DB blast radius; separate restricted runtime, backup, and migration roles | Repository tests mainly assert docs/config; role behavior is production evidence | Historical role attributes, grants, rejected mutation/DDL, migration and backup evidence; not live-reproduced | Runtime remains read-only; backup scoped read; default `TEMP` retained | **Accepted residual risk** for `TEMP`; otherwise no repository issue |
| `MG-SEC-008` | Single-request CPU amplification; max 32 canonical, deduplicated element symbols plus 32 KiB proxy body | Strong schema behavior tests; historical endpoint tests cover 422/no-service-entry and maximum valid request | Historical 413/422/200, timing, migration, health, and full-JSON evidence; not live-reproduced | Raw list size is bounded before normalization; downstream graph bounds remain in place | **No issue** in repository; live state pending |
| `MG-SEC-009` | Log/storage amplification; bounded input and count-only log plus journald/disk controls | Behavioral schema and log-capture tests; journald/systemd checks are structural | Historical journal allocation, monitor timer/run, and service evidence; not live-reproduced | Submitted collections are excluded; counts/booleans are bounded; logging and storage have separate limits | **No issue** in repository; live state pending |
| `MG-SEC-010` | Dependency drift and vulnerable packages; exact hashed lock, clean install, reconciliation, `pip-audit` workflow | Validators parse hashes/inputs and reject malformed locks; accepted remediation suite passed `841 passed, 1 skipped`; exact-commit hosted audit executed every substantive step | Remediation SHA dependency and secret jobs independently passed; fresh settings evidence confirmed no ruleset or branch protection, matching the documented manual boundary | Workflow is not required on `main` and can be skipped; corrected guidance requires exact-SHA Dependency Security and Secret Scan evidence as a manual production precondition | **Verification defect remediated and verified** through `MG-SA-002`; lack of protected-branch enforcement is an explicit accepted residual risk |
| `MG-SEC-011` | Mutable automation execution; full Action SHA, container digest, read-only/no-network scanner | Strong static validator plus behavioral local-hook evidence in historical record | Current SHA secret-scan job independently passed and used pinned references; hosted SHA-pin policy could not be read | No branch rule requires secret scan; nevertheless immutable references and scanner containment themselves are sound | **No issue** for implementation; hosted policy evidence remains unconfirmed |
| `MG-SEC-012` | Irrecoverable/prolonged data loss; daily consistent dump, manifest/checksum, S3 retention, isolated restore runbook | Backup helpers are behavior-tested; real PostgreSQL/S3/restore behavior is historical production evidence | Detailed scheduled backup and isolated restore/reconciliation evidence; not live-reproduced | Manifest records Git `HEAD` but does not fail on a dirty checkout; retained as future hardening, not a current recovery failure | **No issue** in repository; live schedule/retention pending |

## Cross-control conclusions

- The timeout ordering is internally consistent for all policy-expensive routes:
  database statement timeout < application deadline < expensive proxy read
  timeout.
- A timed-out synchronous task retains its admission slot until it exits, which
  prevents silent overcommit; the focused test exercises this behavior.
- Trusted forwarding headers are overwritten with Nginx `$remote_addr`, so the
  per-client key is not derived from caller-supplied `X-Forwarded-For` in the
  committed topology.
- Nginx uses a client-address zone for per-client controls and a separate
  `$server_name` zone for the aggregate cap. Expensive locations repeat the
  aggregate directive because their client directive prevents server-level
  `limit_conn` inheritance.
- Proxy body bounds and Pydantic collection bounds are complementary and do not
  rely on one another.
- systemd identity, environment-file checks, and read-only database privilege
  reduce distinct compromise paths and are mutually consistent.
- Backup/recovery evidence is materially stronger than a file-existence check,
  but current timer, object retention, and restore readiness require live
  evidence to assure against drift.
