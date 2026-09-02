# MaterialGraph Stage 1 Security Review — Final Inspection

## Inspection conclusion

The Stage 1 inspection of the current public deterministic prototype is
complete. Twelve security findings are confirmed and remain open: five High
and seven Medium. Every finding has High confidence and includes exact
evidence, a concrete current threat scenario, existing and missing safeguards,
a remediation recommendation, verification requirements, and an unresolved
resolution field.

No Critical finding was confirmed. No finding is remediated or closed by this
inspection record. Implementation remains prohibited until the inspection
result and proposed remediation plan are explicitly approved.

## Frozen baselines

| Attribute | Verified value |
|---|---|
| Governing baseline | `docs/security/README.md` |
| Frozen application review commit | `32bc57cc78754e061f9a2f4294d81aa39e4f9955` |
| Final inspection and evidence commit | `870e9861abbb607b1dc0b51ee20be5c19d9de222` |
| Final bundle history | Complete |
| Final bundle SHA-256 | `7db00cf30e716b3cb1cbdcc78cb9bd32c515ac2340c7dc03bf7a9b7a8d290ec5` |
| Final review worktree | Clean |
| Review mode | Repository and redacted deployment inspection; no remediation |

The application behavior was frozen at `32bc57c`. Later commits through
`870e986` record audit reconciliation, architecture and product documentation,
and Stage 1 evidence; they do not silently redefine the inspected application
behavior.

## Evidence chronology

| Commit | Evidence milestone |
|---|---|
| `32bc57c` | Independent implementation audit closed; application review baseline frozen |
| `60c0665` | Independent-audit evidence reconciled without application behavior change |
| `950b960` | Stage 1 records initialized and first five findings recorded |
| `516abec` | Database transport, privileges, and timeout evidence completed |
| `b2df9b0` | Request-cardinality evidence and `MG-SEC-008` recorded |
| `407a109` | Request logging and proxy-boundary evidence completed |
| `5bf859a` | Dependency installation and vulnerability-governance evidence recorded |
| `3bcd828` | CI and local automation-integrity evidence recorded |
| `24223ef` | Public operational exposure and error-response evidence completed |
| `870e986` | Backup and recovery evidence and `MG-SEC-012` recorded |

## Scope reconciliation

| Stage 1 area | Final disposition |
|---|---|
| Public API exposure | Public routes and documentation enumerated; unauthenticated public-data design is not itself a finding |
| Request validation and payload bounds | `MG-SEC-008` and `MG-SEC-009`; remaining bounded-impact contract cases classified as observations |
| Graph and search resource limits | Multiple positive per-request bounds confirmed; aggregate abuse remains in `MG-SEC-001` |
| Execution and upstream timeouts | `MG-SEC-002` |
| Rate and connection limiting | `MG-SEC-001` |
| Nginx configuration | `MG-SEC-001`, `MG-SEC-002`, `MG-SEC-005`, and operational-hardening observations |
| systemd and process privileges | `MG-SEC-003` and `MG-SEC-004` |
| EC2 network exposure | Public ports and loopback application boundary confirmed; evidence contributes to `MG-SEC-004` and `MG-SEC-005` |
| Database connectivity, TLS, and privileges | `MG-SEC-002`, `MG-SEC-006`, and `MG-SEC-007` |
| Secrets and CI controls | Existing secret safeguards confirmed; `MG-SEC-003` and `MG-SEC-011` |
| Logging, exceptions, and disclosure | `MG-SEC-009`; safe observed `404` and `422` behavior and retained correlation observation |
| Dependencies and supply chain | `MG-SEC-010` and `MG-SEC-011`; advisory reachability classified separately |
| Backup, restore, and recovery | `MG-SEC-012` |
| Health, OpenAPI, and operational endpoints | Public behavior confirmed and explicitly retained as hardening rather than promoted without a material threat scenario |

All requested Stage 1 areas therefore have an evidence-backed finding,
positive safeguard, retained observation, or explicit non-finding disposition.

## Confirmed findings

| ID | Severity | Finding | Primary risk |
|---|---|---|---|
| `MG-SEC-001` | High | Public expensive endpoints lack rate and concurrency limiting | Aggregate service exhaustion |
| `MG-SEC-002` | Medium | Scientific requests lack an enforced deadline and timeout hierarchy | Capacity loss from long-running work |
| `MG-SEC-003` | Medium | Production environment file is world-readable | Local credential disclosure |
| `MG-SEC-004` | High | Internet-facing service runs with passwordless root authority | Immediate host takeover after runtime compromise |
| `MG-SEC-005` | Medium | Public API traffic is served over unencrypted HTTP | Network observation or modification of scientific traffic |
| `MG-SEC-006` | High | Production database connection is unencrypted | Database credential and data interception or tampering |
| `MG-SEC-007` | High | Application database role has administrative capabilities | Excessive database compromise blast radius |
| `MG-SEC-008` | High | Unbounded research-objective collections permit CPU amplification | Single-request computational amplification |
| `MG-SEC-009` | Medium | Screening logs unbounded request collections verbatim | Journal storage and I/O amplification |
| `MG-SEC-010` | Medium | Production dependencies are neither reproducibly installed nor vulnerability-gated | Unreviewed dependency drift and persistent vulnerabilities |
| `MG-SEC-011` | Medium | Mutable third-party automation references permit unreviewed code execution | Supply-chain code execution without repository change |
| `MG-SEC-012` | Medium | Production recovery is limited to an untested six-hour history window | Irrecoverable or prolonged production data loss |

The canonical status and complete evidence remain in
[`STAGE_1_FINDINGS_REGISTER.md`](STAGE_1_FINDINGS_REGISTER.md) and the linked
finding records.

## Confirmed positive safeguards

- Production secrets are excluded from current source control and the exposed
  database credential was rotated and removed from current Git history.
- Gitleaks scans complete history in CI and staged changes through the local
  fail-closed hook.
- GitHub workflow permissions are read-only for repository contents and
  packages; Actions cannot create or approve pull requests.
- First-time external contributors require workflow approval, and no
  self-hosted runner is configured.
- Uvicorn binds to loopback, and EC2 has no inbound rule for port 8000.
- SSH ingress is restricted to one IPv4 source.
- Graph traversal, search state, branching, path enumeration, depth, and result
  counts have multiple per-request limits.
- Graph-job routes are deliberately unmounted.
- PostgreSQL terminates idle-in-transaction sessions after five minutes.
- The local and deployed dependency environments passed `pip check`, and a
  fully pinned dependency snapshot exists for review.
- Current application tracing found no mounted upload or Pillow-processing
  path, form parser, affected URL-authority trust decision, or affected nested
  secrets source.
- Unknown routes and malformed JSON returned bounded responses without stack
  traces, source paths, credentials, or internal exceptions.
- Nginx rejected `TRACE` before forwarding it to Uvicorn.
- Neon provides point-in-time recovery within the configured six-hour window.

These controls reduce current exposure but do not close any linked finding
unless its finding-specific verification requirements are satisfied.

## Retained observations and improvements

The following propositions remain outside the confirmed-finding count:

- additional systemd sandboxing beyond the privilege boundary in
  `MG-SEC-004`;
- unrestricted EC2 egress pending a defined destination model;
- branch protection, signed commits, and broader source-governance policy for
  the current solo-maintainer repository;
- global exception correlation and safe unexpected-exception behavior;
- public Swagger, ReDoc, OpenAPI, version, environment, and Nginx banner
  exposure as production-hardening choices;
- comparison-list and string bounds and substitution `top_n` validation where
  current tracing did not establish a distinct security impact;
- installed dependency advisories whose required application path was not
  reachable in the inspected implementation.

These items must not be represented as resolved vulnerabilities. They may be
reassessed if architecture, deployment, collaboration, or threat boundaries
change.

## Review limitations

- No destructive, sustained load, credential-theft, or first-time production
  restore test was performed.
- Extreme request amplification was measured locally without targeting the
  deployed service.
- Error-response evidence covered deployed routing and validation failures, not
  an intentionally triggered production `500`.
- Dependency advisory applicability was based on installed versions and current
  caller tracing, not exploit attempts.
- Deployment evidence represents the inspected EC2, Nginx, systemd, Neon, and
  GitHub configuration checkpoints and can drift after inspection.
- Future authentication, organizations, private workspaces, uploads, billing,
  and LLM capabilities remain outside current Stage 1 scope.

## Final decision

Stage 1 inspection is complete and evidence-consistent. The twelve findings are
appropriate for remediation planning; none is accepted as residual risk or
closed at this checkpoint. The next authorized action, if approved, is to open
finding-specific remediation and verification records following
[`STAGE_1_REMEDIATION_PLAN.md`](STAGE_1_REMEDIATION_PLAN.md).
