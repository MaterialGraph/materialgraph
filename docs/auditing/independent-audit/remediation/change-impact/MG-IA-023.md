# MG-IA-023 Change Impact — Graph-Job Capability Disclosure

## Status

Verified locally: seven focused configuration tests, 720 full-suite tests,
Ruff, and Git whitespace validation passed.

## Before

The README listed “PostgreSQL-backed graph-job routes and persistence” under
current knowledge-graph capabilities. The application deliberately did not
register the graph-job router, so those routes were absent from the public API
and OpenAPI schema even though persistence and lifecycle primitives existed.

## After

The README describes the implemented PostgreSQL-backed persistence and
lifecycle primitives without presenting graph-job routes as public. It also
states that public graph-job routes remain intentionally unregistered while
worker ownership, lifecycle, and API-contract requirements are incomplete.

A project-configuration regression test checks both sides of the contract: no
graph-job path is present in OpenAPI, and the README contains the explicit
non-public disclosure rather than the former capability claim.

## Impact

- Documentation accuracy: **Corrected** — current capabilities now match the
  registered API surface.
- Public API behavior: **Unchanged** — graph-job routes remain unregistered.
- Internal graph-job primitives: **Unchanged** — persistence, schemas, and
  service code remain available for future lifecycle work.
- Scientific computation and ranking: **No change**.
- Database schema and stored data: **No change**.
- Deployment configuration: **No change**.

## Scope decision

Activating the dormant router would require unresolved worker ownership,
authorization, lifecycle, and public-contract decisions. The remediation
therefore corrects the documentation contract and locks it to the actual API
surface rather than expanding runtime behavior.
