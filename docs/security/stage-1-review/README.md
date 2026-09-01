# MaterialGraph Stage 1 Security Review

**Status:** Active — inspection and evidence collection
**Governing baseline:** [`../README.md`](../README.md)
**Review opened:** 2026-08-28

## Baselines

- Frozen application review commit:
  `32bc57cc78754e061f9a2f4294d81aa39e4f9955`.
- Current repository and deployment evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`.
- The intervening commit reconciles independent-audit documentation and its
  consistency test; it does not change security-relevant application behavior.
- Bundle SHA-256:
  `456591e419c41e8e377f4a718240bd234c3843c9e93b60e801b6e717d29b666b`.

## Review boundary

Stage 1 covers the current public deterministic scientific prototype:

- public route exposure and information disclosure;
- request and computation bounds;
- rate, connection, and concurrency limiting;
- request, proxy, and database timeouts;
- Nginx, systemd, EC2, and database boundaries;
- secrets, CI, dependencies, logging, backups, and recovery.

Authentication, tenancy, private workspaces, uploads, billing, and LLM risks
remain future scope unless current code exposes those capabilities.

## Evidence threshold

An `MG-SEC-*` identifier is assigned only when inspection confirms:

1. an affected current component;
2. a concrete threat scenario;
3. the safeguards already present; and
4. a material missing safeguard.

Code-backed facts and deployed-environment facts are recorded separately.
Unconfirmed propositions remain observations. A performance concern becomes a
security finding only when it creates an exploitable resource-exhaustion or
availability scenario.

## Current records

- [`STAGE_1_FINDINGS_REGISTER.md`](STAGE_1_FINDINGS_REGISTER.md) — canonical
  finding index.
- [`STAGE_1_EVIDENCE_REGISTER.md`](STAGE_1_EVIDENCE_REGISTER.md) — reviewed
  evidence and positive safeguards.
- [`STAGE_1_OBSERVATIONS.md`](STAGE_1_OBSERVATIONS.md) — propositions awaiting
  evidence or classification.
- [`findings/`](findings/) — complete finding records.

## Current phase

Eleven findings are confirmed. The database, request-boundary, dependency,
CI-integrity, and public operational-exposure and error-response evidence
groups are complete. Remaining request-model, dependency-advisory,
source-governance, and operational-hardening cases that did not meet the
security finding threshold are explicitly classified in the observation
register. Inspection remains active for backup and restore readiness.

No remediation record or implementation change is authorized by this review
checkpoint. Security changes must preserve deterministic scientific results
and ordering and must be verified in both tests and deployed behavior.

## Investigation sequence

1. Record the current application, proxy, host, and network evidence.
2. Inspect database TLS, role privileges, and timeout settings.
3. Test extreme-but-valid request fields and payload cardinality.
4. Inspect public documentation, health, and error responses.
5. Assess dependencies and CI supply-chain controls.
6. Verify backup retention, recovery targets, and restore testing.
7. Reconcile findings and observations into a final inspection report.
8. Begin remediation only after explicit approval.
