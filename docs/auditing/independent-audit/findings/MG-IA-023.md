# MG-IA-023 — README presents disabled graph-job routes as a current capability

- Classification: documentation-to-implementation contract defect
- Priority: P3
- Confidence: high
- Disposition: confirmed

## Affected files and components

- root `README.md`, “Current Capabilities — v1.9.6”
- `app/api/v1/api.py`
- graph-job route, schema, model, and service stack

## Exact evidence

The README lists “PostgreSQL-backed graph-job routes and persistence” under current Knowledge-Graph Intelligence capabilities. The reviewed versioned API router deliberately does not include the graph-job router, and route/OpenAPI tests confirm that graph-job endpoints are absent from the public application. The persistence model and service primitives exist, but the routes are not an accessible current API capability.

## Expected versus actual

The current-capability list should distinguish implemented internal/dormant components from publicly registered capabilities. It currently groups disabled routes with active capabilities.

## Impact

Users, evaluators, and deployment operators can expect graph-job endpoints that the running API does not expose. This weakens documentation trust and obscures the intentionally incomplete worker/lifecycle state recorded in `OBS-016`.

## Reproduction and callers

Inspect the versioned router or generated OpenAPI schema: no graph-job paths are mounted. Compare this with the README current-capability statement.

## Tests

Supplied graph-job API tests positively assert that these paths are absent. No documentation-contract test checks the README capability list against router registration.

## Recommended remediation scope

Describe graph-job persistence and lifecycle primitives as dormant/internal or planned, and state that routes are intentionally not registered until lifecycle and public-contract requirements are complete.
