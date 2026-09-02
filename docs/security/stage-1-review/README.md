# MaterialGraph Stage 1 Security Review

**Status:** Inspection complete — remediation approval pending
**Governing baseline:** [`../README.md`](../README.md)
**Review opened:** 2026-08-28

## Baselines

- Frozen application review commit:
  `32bc57cc78754e061f9a2f4294d81aa39e4f9955`.
- Initial repository and deployment evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`.
- Final inspection and evidence checkpoint:
  `870e9861abbb607b1dc0b51ee20be5c19d9de222`.
- Final bundle SHA-256:
  `7db00cf30e716b3cb1cbdcc78cb9bd32c515ac2340c7dc03bf7a9b7a8d290ec5`.
- Commits after the frozen application baseline record audit reconciliation,
  architecture and product documentation, and Stage 1 evidence; they do not
  change the inspected application behavior.

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
- [`STAGE_1_FINAL_INSPECTION.md`](STAGE_1_FINAL_INSPECTION.md) — reconciled
  inspection result and scope conclusion.
- [`STAGE_1_REMEDIATION_PLAN.md`](STAGE_1_REMEDIATION_PLAN.md) — proposed
  prerequisite-aware remediation and verification sequence.
- [`findings/`](findings/) — complete finding records.

## Current phase

Twelve findings are confirmed. The database, request-boundary, dependency,
CI-integrity, public operational-exposure and error-response, and backup and
recovery evidence groups are complete. Remaining request-model,
dependency-advisory, source-governance, and operational-hardening cases that
did not meet the security finding threshold are explicitly classified in the
observation register. Final evidence reconciliation is complete and the
proposed remediation sequence is ready for review.

No remediation record or implementation change is authorized by this review
closure. Security changes must preserve deterministic scientific results and
ordering and must be verified in both tests and deployed behavior.

## Investigation sequence

1. Record the current application, proxy, host, and network evidence.
2. Inspect database TLS, role privileges, and timeout settings.
3. Test extreme-but-valid request fields and payload cardinality.
4. Inspect public documentation, health, and error responses.
5. Assess dependencies and CI supply-chain controls.
6. Verify backup retention, recovery targets, and restore testing.
7. Reconcile findings and observations into a final inspection report.
8. Begin remediation only after explicit approval.
