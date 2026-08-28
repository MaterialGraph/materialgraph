# Stage 1 Security Observations

**Status:** Active — not confirmed findings
**Last updated:** 2026-08-28

Observations are propositions requiring additional evidence or classification.
They do not carry `MG-SEC-*` identifiers and are not counted as vulnerabilities.

| Area | Observation | Evidence required |
|---|---|---|
| Request validation | Some request models accept unbounded element lists or strings. | Exercise extreme valid payloads, confirm body-size controls, and measure downstream work. |
| Substitutions | `SubstitutionRequest.top_n` lacks an explicit lower and upper bound. | Test negative and extreme positive values and trace database work. |
| Operational exposure | Swagger, ReDoc, OpenAPI, and health endpoints are public; root health returns version and environment. | Confirm intended consumers and capture public responses and error behavior. |
| Readiness | The service exposes liveness-style health responses but no demonstrated database readiness check. | Confirm monitoring requirements and failure behavior. |
| Nginx disclosure | `server_tokens` is not disabled in the effective configuration. | Capture public response headers and default error pages. |
| Host containment | systemd lacks additional sandboxing beyond the privilege issue recorded in `MG-SEC-004`. | Define required runtime writes and test a least-privilege unit design. |
| Network egress | EC2 outbound traffic is unrestricted. | Establish required destinations and determine whether egress restriction is practical for this prototype. |
| Database grants | Role attributes are confirmed as overprivileged, but detailed schema/table/sequence grants and application/migration role separation remain unverified. | Inspect redacted grants and determine whether migrations use the runtime credential. |
| Dependencies | No repository dependency-vulnerability workflow has been confirmed. | Run a scanner against frozen dependency files and inspect update policy. |
| CI supply chain | CI actions and containers may use mutable version tags. | Inspect exact workflow references and accepted trust policy. |
| Runtime dependencies | Production dependency inputs may include development tooling. | Reconcile deployment installation commands and dependency files. |
| Logging | No global exception correlation or redacted deployed-error sample has been reviewed. | Inspect representative Nginx/Uvicorn failures without secrets or personal data. |
| Recovery | Backup retention, RPO/RTO, restore procedure, and restore-test evidence are not documented. | Inspect Neon settings and perform or document a restore test. |

## Classification rule

Promote an observation only after the current component, concrete threat,
existing safeguards, and material missing safeguard are confirmed. Close or
retain an observation explicitly when new evidence does not support a finding.
