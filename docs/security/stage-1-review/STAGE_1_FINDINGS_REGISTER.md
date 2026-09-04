# Stage 1 Security Findings Register

**Status:** Inspection complete — Wave 0 remediation active
**Last reconciled:** 2026-09-02

## Status definitions

- `Open`: confirmed and not remediated.
- `In remediation`: an approved remediation is being implemented.
- `Implemented`: implementation is complete; verification is pending.
- `Verified`: acceptance and deployment verification passed.
- `Closed`: verified remediation and closure evidence are recorded.

## Confirmed findings

| ID | Title | Severity | Confidence | Boundary | Status |
|---|---|---|---|---|---|
| [`MG-SEC-001`](findings/MG-SEC-001.md) | Public expensive endpoints lack rate and concurrency limiting | High | High | Application and Nginx | Open |
| [`MG-SEC-002`](findings/MG-SEC-002.md) | Scientific requests lack an enforced deadline and timeout hierarchy | Medium | High | Application, Nginx, and database client | Open |
| [`MG-SEC-003`](findings/MG-SEC-003.md) | Production environment file is world-readable | Medium | High | EC2 filesystem | Open |
| [`MG-SEC-004`](findings/MG-SEC-004.md) | Internet-facing service runs with passwordless root authority | High | High | systemd and EC2 account boundary | Open |
| [`MG-SEC-005`](findings/MG-SEC-005.md) | Public API traffic is served over unencrypted HTTP | Medium | High | Nginx and EC2 network boundary | Open |
| [`MG-SEC-006`](findings/MG-SEC-006.md) | Production database connection is unencrypted | High | High | EC2-to-Neon database transport | Open |
| [`MG-SEC-007`](findings/MG-SEC-007.md) | Application database role has administrative capabilities | High | High | Neon role and application credential boundary | Open |
| [`MG-SEC-008`](findings/MG-SEC-008.md) | Unbounded research-objective collections permit CPU amplification | High | High | Public research and objective-exploration requests | Open |
| [`MG-SEC-009`](findings/MG-SEC-009.md) | Screening logs unbounded request collections verbatim | Medium | High | Screening service and system journal | Open |
| [`MG-SEC-010`](findings/MG-SEC-010.md) | Production dependencies are neither reproducibly installed nor vulnerability-gated | Medium | High | Packaging, deployment, and dependency maintenance | Open |
| [`MG-SEC-011`](findings/MG-SEC-011.md) | Mutable third-party automation references permit unreviewed code execution | Medium | High | Local pre-commit hook and GitHub Actions | Open |
| [`MG-SEC-012`](findings/MG-SEC-012.md) | Production recovery is limited to an untested six-hour history window | Medium | High | Neon database and recovery process | In remediation |

## Review rule

This register is an index. Exact evidence, threat scenario, current safeguards,
missing safeguards, remediation recommendation, and verification requirements
are maintained in the linked finding record. Observations are not counted as
findings and remain in [`STAGE_1_OBSERVATIONS.md`](STAGE_1_OBSERVATIONS.md).
Current remediation status and evidence are maintained separately under
[`remediation/`](remediation/README.md).
