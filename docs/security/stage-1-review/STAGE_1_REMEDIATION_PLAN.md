# MaterialGraph Stage 1 Security Review — Proposed Remediation Plan

## Status and authority

**Status:** Approved; Wave 0 remediation active

This plan orders the twelve confirmed Stage 1 findings by current exploit
impact, safe prerequisites, shared implementation boundaries, and verification
cost. Wave 0 remediation for `MG-SEC-012` is authorized. The coordinated
database sequence in `MG-SEC-006` and `MG-SEC-007` is approved to follow only
after recovery verification. Other findings require their scope to be opened
in the remediation register before implementation.

Each approved finding must receive separate change-impact and verification
records. A finding remains Open until its implementation and deployed behavior
satisfy every finding-specific verification requirement.

## Governing rules

1. Preserve deterministic scientific results, scores, explanations, and
   ordering unless a separately approved scientific change requires otherwise.
2. Establish a tested recovery path before database, role, dependency, or host
   changes that could impair production.
3. Separate runtime, deployment, migration, and administrative identities.
4. Coordinate proxy, application, and database controls rather than relying on
   one layer.
5. Test controls locally or in an isolated target before production rollout.
6. Never print credentials, database URLs, environment contents, or recovery
   secrets in evidence.
7. Roll out reversible changes in small groups with explicit rollback and
   post-deployment checks.
8. Do not mix future authentication, tenancy, upload, billing, or LLM security
   into current Stage 1 remediation.

## Remediation sequence

### Wave 0 — Establish recovery safety

| Order | Finding | Objective | Why first |
|---:|---|---|---|
| 1 | `MG-SEC-012` | Define RPO/RTO, create an independent backup path, write a runbook, and complete an isolated restore test | Provides rollback confidence before database, identity, dependency, and deployment changes |

The first restore test must target an isolated Neon branch or separate
database. Production must not be the first restore-test target.

### Wave 1 — Protect credentials, transport, and privilege boundaries

| Order | Finding | Objective | Coordination |
|---:|---|---|---|
| 2 | `MG-SEC-003` | Restrict environment-file ownership and mode | Design ownership with the dedicated service identity in `MG-SEC-004` |
| 3 | `MG-SEC-006` | Require validated TLS for runtime and Alembic database sessions | Verify encryption before rotating or separating database credentials |
| 4 | `MG-SEC-007` | Create separate least-privilege runtime and migration roles | Rotate credentials only after TLS and grant requirements are established |
| 5 | `MG-SEC-004` | Run under a dedicated non-administrative systemd identity with tested hardening | Coordinate file ownership, code writability, logging, and deployment authority |
| 6 | `MG-SEC-005` | Serve public routes through HTTPS and redirect HTTP | Independent transport hardening; verify responses remain byte-for-byte equivalent where appropriate |

`MG-SEC-003` may receive an immediate owner-only mode correction after
approval, but its final ownership verification belongs with `MG-SEC-004`.
`MG-SEC-006` and `MG-SEC-007` should share one database rollback plan while
remaining separate findings and verification records.

### Wave 2 — Bound public work and overload behavior

| Order | Finding | Objective | Coordination |
|---:|---|---|---|
| 7 | `MG-SEC-008` | Canonicalize, deduplicate, validate, and bound research-objective collections | Establishes the maximum valid request contract used by proxy and performance controls |
| 8 | `MG-SEC-009` | Replace verbatim user collections in logs with bounded metadata | Reuse the normalized boundary and define journal retention and monitoring |
| 9 | `MG-SEC-001` | Add trusted-client request limits, connection limits, and expensive-route admission control | Tune against the maximum valid workloads established by `MG-SEC-008` |
| 10 | `MG-SEC-002` | Add coordinated proxy, application, pool, lock, and statement deadlines | Tune after valid workload cost and concurrency budgets are measurable |

Proxy body size, rate limits, concurrency gates, and timeouts must not truncate
or silently reinterpret successful scientific results. Rejections and timeouts
must be explicit and must never present partial results as complete.

### Wave 3 — Make automation and dependencies reproducible

| Order | Finding | Objective | Coordination |
|---:|---|---|---|
| 11 | `MG-SEC-011` | Pin Actions and containers immutably and constrain the local scanner | Stabilizes the automation executing later dependency checks |
| 12 | `MG-SEC-010` | Define the production lock/constraints contract, enforce integrity, and add vulnerability scanning | Use reviewed immutable automation and complete scientific regression testing for upgrades |

Immutable pins must be recorded with human-readable release annotations and a
repeatable update process. Scanner findings must be evaluated for version,
reachability, severity, and available fixes rather than treated as automatic
proof of exploitability.

## Dependency map

| Prerequisite | Dependent work | Reason |
|---|---|---|
| `MG-SEC-012` recovery capability | Waves 1–3 production changes | Enables tested recovery if a security change damages deployment or data |
| `MG-SEC-004` service identity design | Final `MG-SEC-003` ownership | The secret file must be readable only by the intended runtime boundary |
| `MG-SEC-006` database TLS | `MG-SEC-007` credential separation and rotation | New credentials must not first travel over an unencrypted session |
| `MG-SEC-008` maximum valid request contract | `MG-SEC-001`, `MG-SEC-002`, and `MG-SEC-009` tuning | Limits, deadlines, and logs require a defined valid workload |
| `MG-SEC-011` immutable automation | `MG-SEC-010` CI vulnerability gate | The security scanner must not add a mutable execution path |

The groups permit practical parallel work after Wave 0: HTTPS design,
application request validation, service-user design, and dependency-contract
design can be prepared independently, but production changes should follow the
verified prerequisite order.

## Required records per finding

Before implementation:

- approved scope and owner;
- exact starting commit and deployed checkpoint;
- affected files, configuration, roles, or external settings;
- rollback plan;
- expected user-visible and scientific impact;
- explicit non-goals.

Before status becomes Verified:

- focused security-control tests;
- adjacent API, service, deployment, or migration tests;
- complete project test suite and Ruff result where code is changed;
- `git diff --check` and secret scan;
- redacted deployment evidence;
- deterministic scientific output comparison where relevant;
- finding-specific verification checklist;
- resolution commit and deployed version.

## Cross-wave verification gate

After each production wave:

1. Confirm the deployed commit and clean worktree.
2. Confirm Nginx and systemd configuration validity.
3. Confirm application and database connectivity without printing secrets.
4. Exercise health and representative simple and expensive scientific routes.
5. Compare deterministic outputs and ordering with approved fixtures.
6. Review bounded logs and rejection/error behavior.
7. Confirm the recovery mechanism remains usable.
8. Record rollback readiness and monitoring results.

## Completion criteria

Stage 1 remediation is complete only when:

- all twelve register rows are Verified or Closed with linked evidence;
- no finding-specific verification step remains pending;
- production configuration matches the reviewed repository documentation;
- deterministic scientific regression checks pass;
- an isolated recovery test remains current;
- retained observations are explicitly accepted, deferred, promoted, or
  resolved without being silently counted as findings; and
- a separate final remediation closure record reconciles statuses, commits,
  deployed evidence, and residual risk.
