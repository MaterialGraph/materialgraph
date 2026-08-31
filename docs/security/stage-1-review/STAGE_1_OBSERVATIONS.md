# Stage 1 Security Observations

**Status:** Active — not confirmed findings
**Last updated:** 2026-08-28

Observations are propositions requiring additional evidence or classification.
They do not carry `MG-SEC-*` identifiers and are not counted as vulnerabilities.

| Area | Observation | Evidence required |
|---|---|---|
| Operational exposure | Swagger, ReDoc, OpenAPI, and health endpoints are public; root health returns version and environment. | Confirm intended consumers and capture public responses and error behavior. |
| Readiness | The service exposes liveness-style health responses but no demonstrated database readiness check. | Confirm monitoring requirements and failure behavior. |
| Nginx disclosure | `server_tokens` is not disabled in the effective configuration. | Capture public response headers and default error pages. |
| Host containment | systemd lacks additional sandboxing beyond the privilege issue recorded in `MG-SEC-004`. | Define required runtime writes and test a least-privilege unit design. |
| Network egress | EC2 outbound traffic is unrestricted. | Establish required destinations and determine whether egress restriction is practical for this prototype. |
| Source governance | No ruleset or classic branch protection applies to `main`. | Define the collaboration and release trust model before deciding whether pull-request, status-check, signed-commit, force-push, or deletion protections are required. |
| Logging | No global exception correlation or redacted deployed-error sample has been reviewed. | Inspect representative Nginx/Uvicorn failures without secrets or personal data. |
| Recovery | Backup retention, RPO/RTO, restore procedure, and restore-test evidence are not documented. | Inspect Neon settings and perform or document a restore test. |

## Classification rule

Promote an observation only after the current component, concrete threat,
existing safeguards, and material missing safeguard are confirmed. Close or
retain an observation explicitly when new evidence does not support a finding.

## Resolved dependency classifications

| Area | Evidence-based disposition |
|---|---|
| Installation and vulnerability governance | Promoted to `MG-SEC-010` after deployed-version drift and the absence of a vulnerability gate were confirmed. |
| Pillow advisories | A vulnerable version is installed transitively, but current code exposes no Pillow, image-processing, or upload path. Retained as remediation-relevant dependency evidence, not a separately reachable finding. |
| pydantic-settings advisory | The vulnerable version is installed, but MaterialGraph does not use `NestedSecretsSettingsSource` or a secrets directory affected by the advisory. Not separately reachable in the current configuration. |
| Starlette URL-authority advisory | The vulnerable version is installed, but no current caller trusts `request.url.hostname` or `request.url.netloc`. Not separately reachable in current application tracing. |
| Starlette form-parsing advisory | The vulnerable version is installed, but no current route calls `request.form()`; mounted POST routes use JSON models. Not separately reachable in current application tracing. |
| Development tooling in production | Production installs from `pyproject.toml`, whose runtime dependency list does not directly include the development extra. The earlier proposition was not confirmed as a separate issue. |

## Resolved CI-integrity classifications

| Area | Evidence-based disposition |
|---|---|
| Mutable automation references | Promoted to `MG-SEC-011` after repository policy and the local read-write container mount were confirmed. |
| Workflow token | Read-only contents and packages permission and disabled pull-request creation materially constrain CI impact; recorded as positive safeguards. |
| Fork workflows | First-time contributors require approval. Requiring approval for every external contributor remains optional hardening under the current read-only, public-repository workflow. |
| Self-hosted execution | No self-hosted runner is configured, so the current workflow does not expose EC2 or another persistent runner host. |
| OIDC | The immutable default subject claim is enabled, but no current workflow requests `id-token` or uses cloud federation. No current OIDC finding is confirmed. |
| Branch and commit governance | Missing branch protection and unsigned commits remain source-governance observations, not separate current vulnerabilities for the solo-maintainer public prototype. |

## Resolved request-boundary classifications

| Area | Evidence-based disposition |
|---|---|
| Research-objective collections | Promoted to `MG-SEC-008` after measured single-request CPU amplification. |
| Screening request collections | Verbatim logging is promoted to `MG-SEC-009`; set construction itself did not establish a separate computation finding. |
| Comparison request collections | Comparison evaluates exactly two materials. Collection bounds remain API hardening, but no separate security finding was confirmed. |
| Substitution `top_n` | Negative, zero, and extreme values are accepted, but the complete finite candidate pool is evaluated before slicing. This is an API-contract defect, not a separate current resource-exhaustion finding. |
| Subgraph and objective strings | Explicit length bounds remain desirable, but bounded downstream comparisons did not establish material resource amplification in the current prototype. |
