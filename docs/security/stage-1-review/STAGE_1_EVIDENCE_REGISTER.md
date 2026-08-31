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
- The local and deployed Python environments pass `pip check`.
- A fully version-pinned dependency snapshot exists in `requirements.txt`.
- Current application tracing found no mounted image-upload or Pillow-processing
  path, no `request.form()` call, no trust decision based on
  `request.url.hostname` or `request.url.netloc`, and no use of
  `NestedSecretsSettingsSource`.

## Dependency and supply-chain evidence

- `pyproject.toml` declares all direct runtime dependencies without version
  constraints.
- The production deployment guide runs `pip install -e .`; it does not install
  the pinned `requirements.txt` snapshot or enforce package hashes.
- `requirements.txt` pins 93 packages but does not include distribution hashes.
- The deployed environment is internally consistent according to `pip check`.
- Production contained Starlette `1.2.1` while `requirements.txt` pinned
  Starlette `1.2.0`, directly demonstrating resolution drift.
- Independent OSV and PyPI audits of the pinned snapshot both returned a
  nonzero vulnerability result for Pillow `12.2.0`, pydantic-settings `2.14.1`,
  and Starlette `1.2.0`. The deployed environment contained Pillow `12.2.0`,
  pydantic-settings `2.14.1`, and Starlette `1.2.1`.
- The scanner output contained duplicate aliases or records. Package presence,
  affected version ranges, applicability, and distinct advisory identity were
  evaluated separately from the scanner headline counts.
- Pillow is installed transitively through Matplotlib. Current MaterialGraph
  code does not import Pillow or expose image/file-upload processing.
- The pydantic-settings advisory affects `NestedSecretsSettingsSource` with a
  writable or attacker-influenced secrets directory. MaterialGraph uses
  `SettingsConfigDict` with ordinary `.env` loading and does not configure that
  source.
- One Starlette advisory requires application trust in reconstructed
  `request.url` hostname or authority. MaterialGraph contains no such caller.
- The other Starlette advisory requires `request.form()` processing of
  `application/x-www-form-urlencoded` data. MaterialGraph contains no such
  caller; mounted POST APIs use JSON request models.
- No Dependabot, Renovate, dependency-review, `pip-audit`, OSV, or equivalent
  dependency-vulnerability workflow is configured.
- Gitleaks CI uses read-only repository permission and scans complete history,
  but dependency vulnerability detection is outside its purpose.

## CI and automation-integrity evidence

- The secret-scan workflow references `actions/checkout@v4` and
  `ghcr.io/gitleaks/gitleaks:v8.18.4`; neither reference is pinned to an
  immutable commit SHA or container digest.
- The repository permits all actions and reusable workflows, and the setting
  requiring full-length commit-SHA pinning is disabled.
- The repository's default workflow token has read-only contents and packages
  permission. GitHub Actions cannot create or approve pull requests.
- The workflow separately declares `contents: read`.
- Workflow approval is required for first-time external contributors.
- No self-hosted runner or Actions policy is configured.
- The local Gitleaks pre-commit hook mounts the complete repository read-write
  into the tagged container. The mount can include ignored local configuration
  such as `.env`, and the container has no declared network restriction.
- Secret Scan run 49 completed successfully on the first attempt for commit
  `5bf859ae70444d223a147018c48f80bee1d90e21`.
- No repository ruleset or classic branch-protection rule applies to `main`.
- OIDC uses the default template with an immutable subject claim, but the
  current workflow does not request `id-token` permission or access a cloud
  trust relationship.

## Request-cardinality evidence

- Screening and comparison request models accept unbounded `scarce_elements`
  and `avoid_elements` collections.
- Research objectives accept unbounded `avoid_elements`, `prefer_elements`, and
  `preserve_elements` collections and an unbounded `target_family` string.
- `SubstitutionRequest.top_n` accepts negative, zero, and extreme positive
  values.
- A local, database-free model probe accepted 10,000-entry collections. The
  serialized research objective was 336,839 bytes with unique values.
- A second local, database-free benchmark used 10,000 repeated avoided and
  10,000 repeated preferred elements, serialized to 100,173 bytes, across 20
  candidate evaluations. It took 2.825286 seconds versus 0.000759 seconds for
  one avoided and one preferred element: a measured 3,722.38-times time
  amplification with a 937,943-byte measured peak allocation.
- The amplification occurs because exploration scoring, reason generation, and
  warning generation iterate the raw collections for each candidate and
  repeatedly parse the candidate formula. Duplicate values are not normalized
  before this work.
- These probes did not connect to a database or call the deployed API.

## Request logging and proxy-bound evidence

- `CandidateScreeningService` logs complete `scarce_elements` and
  `avoid_elements` collections at `INFO` after screening completes.
- MaterialGraph standard output is routed to the system journal; standard error
  inherits the service destination.
- Active and archived journals occupied 167.1 MB at the evidence checkpoint.
- No project-specific journal storage or rate setting was present in effective
  journald configuration.
- Effective Nginx configuration defines no explicit `client_max_body_size`,
  `client_body_buffer_size`, or `large_client_header_buffers` policy.
- A local process-isolated Loguru probe used the accepted 10,000-entry screening
  collections. A 157,871-byte serialized request produced a 177,850-byte log
  entry without printing the entry or calling the deployed API.

## Evidence still required

- Public health, documentation, and error-response behavior.
- Backup/PITR retention, recovery targets, restore runbook, and restore test.
- Redacted production log samples for representative failures.
