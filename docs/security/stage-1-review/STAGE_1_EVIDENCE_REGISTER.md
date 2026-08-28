# Stage 1 Security Evidence Register

**Status:** Active — evidence collection in progress
**Last updated:** 2026-08-28

## Evidence-handling rules

- Record only the facts needed to support a conclusion.
- Do not commit secret values, environment contents, database URLs, access
  tokens, AWS account numbers, public IP addresses, or unnecessary resource
  identifiers.
- Distinguish repository evidence from deployed-environment evidence.
- Preserve unresolved propositions in the observation register.

## Repository baseline

| Evidence | Result |
|---|---|
| Frozen application review commit | `32bc57cc78754e061f9a2f4294d81aa39e4f9955` |
| Current evidence checkpoint | `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d` |
| Bundle history | Complete |
| Bundle SHA-256 | `456591e419c41e8e377f4a718240bd234c3843c9e93b60e801b6e717d29b666b` |
| Review worktree | Clean at inspection start |

## Application evidence

- Active project routes and FastAPI documentation/schema routes are public and
  have no authentication dependency. This is consistent with the public-data
  prototype and is not itself classified as a vulnerability.
- Graph-job routes exist in source but are not mounted.
- Several scientific routes perform complete-table screening, bounded graph
  construction, multi-stage ranking, or NetworkX analytics.
- Per-request safeguards include bounded discovery hops, branching, search
  states, result counts, graph depth, and K-best enumeration.
- `app/main.py` installs no rate-limiting, concurrency, admission-control, or
  request-deadline middleware.
- Active routes install no rate-limit dependency or expensive-route concurrency
  gate.
- `app/core/database.py` configures `pool_pre_ping=True` but no project-defined
  statement, lock, or pool-acquisition timeout.

## Deployed process and proxy evidence

- Deployed Git checkout was clean at `60c0665` when inspected.
- Uvicorn binds to `127.0.0.1:8000`; it is not directly Internet-facing.
- Nginx listens publicly on port 80 and proxies all paths to Uvicorn.
- No process listens on port 443 at the evidence checkpoint.
- Effective Nginx configuration passed `nginx -t`.
- Effective Nginx configuration defines no `limit_req`, `limit_conn`, explicit
  request-body policy, or explicit proxy connect/read/send timeout.
- UFW is inactive; EC2 security-group rules provide the inspected network
  boundary.
- The systemd service runs as `ubuntu:ubuntu` with `NoNewPrivileges=no`,
  `PrivateTmp=no`, `ProtectSystem=no`, and `ProtectHome=no`.

## Filesystem and account evidence

- `/opt/materialgraph/.env` is owned by `ubuntu:ubuntu` with mode `664`.
- The application directory is owned by `ubuntu:ubuntu`.
- The runtime account belongs to administrative groups including `sudo` and
  `lxd`.
- Sudo policy grants the runtime account passwordless execution as any user,
  including root.

## EC2 network evidence

- SSH ingress is restricted to one IPv4 `/32` source.
- HTTP port 80 is permitted from all IPv4 addresses.
- HTTPS port 443 is permitted from all IPv4 addresses, but no deployed service
  listens on that port.
- Port 8000 has no inbound security-group rule.
- No other inbound ports were present in the inspected group.
- Outbound traffic is permitted to all IPv4 destinations.

## Database session evidence

The following values were queried through MaterialGraph's deployed SQLAlchemy
engine without printing the connection URL, database name, role name, or secret
values:

- `pg_stat_ssl` reports `ssl=false`; TLS version and cipher are null.
- The application role is not a PostgreSQL superuser, but has role creation,
  database creation, login, replication, and row-level-security bypass
  attributes.
- Runtime and Alembic have different configured URLs, but both authenticate as
  the same database role. The distinction is connection-path configuration,
  not privilege separation.
- The Alembic session also reports `ssl=false`; TLS version and cipher are null.
- The runtime role can create databases, connect, and create temporary objects.
- Across all nine inspected `public` tables, the runtime role has `SELECT`,
  `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, and `TRIGGER`.
- No explicit usage grants were returned for the runtime role.
- `statement_timeout` is `0` and `lock_timeout` is `0`.
- `idle_in_transaction_session_timeout` is `5min`.

The same results were observed independently in the Neon SQL Editor, but the
application-engine query is the authoritative evidence for the deployed
MaterialGraph session.

## Confirmed positive safeguards

- Production credentials are external to the tracked repository.
- Gitleaks scans repository history in CI and staged changes locally.
- Uvicorn has both a loopback bind and no EC2 inbound rule for port 8000.
- SSH ingress is source-restricted.
- Graph and search operations have multiple per-request complexity bounds.
- Graph-job routes are unmounted.
- Nginx configuration is syntactically valid.
- PostgreSQL terminates idle-in-transaction sessions after five minutes.

## Evidence still required

- Extreme-but-valid request and payload measurements.
- Public health, documentation, and error-response behavior.
- Dependency vulnerability scan and CI dependency-update policy.
- Backup/PITR retention, recovery targets, restore runbook, and restore test.
- Redacted production log samples for representative failures.
