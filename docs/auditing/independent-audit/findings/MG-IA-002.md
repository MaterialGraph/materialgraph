# MG-IA-002 — Public health endpoints expose divergent, untyped contracts

- Classification: confirmed API-contract defect
- Priority: P3
- Confidence: high
- Disposition: confirmed
- Baseline: `a1605e61f72035890692ab4df63ebd2f7b859069`

## Affected files and components

- `app/main.py` — root `GET /health`
- `app/api/v1/api.py` — versioned router assembly
- `app/api/v1/routes/health.py` — `GET /api/v1/health`
- `tests/test_health.py` — partial contract coverage
- `app/core/config.py` and `app/version.py` — values exposed only by the root route

## Exact evidence

- Root `GET /health` returns `status`, `service`, `version`, and `environment`; `service` comes from `settings.project_name`.
- Versioned `GET /api/v1/health` returns only `status` and a hard-coded `service` value, `MaterialGraph API`.
- Both routes are registered by `app.main` through direct declaration and `api_router` inclusion.
- Neither handler declares a Pydantic response model.
- `tests/test_health.py` tests only `/api/v1/health` and does not cover the root route or parity between the contracts.

## Expected behavior

Two public endpoints representing the health of the same deployed API should either share one defined response contract or be explicitly named and documented as different probe types with independently typed contracts.

## Actual behavior

The endpoints share the health name but return different fields and derive service identity differently. Configuration can therefore change the root service name while the versioned endpoint remains fixed.

## Impact

Monitoring, deployment checks, clients, and documentation can observe inconsistent service metadata depending on the chosen URL. Untyped response bodies permit further accidental divergence without schema-level detection.

## Reproducibility

Static reproduction:

1. Inspect both `health_check` handlers.
2. Trace inclusion of the versioned handler through `app/api/v1/api.py` and `app.main.py`.
3. Compare returned keys and service-value sources.

Runtime confirmation when a checkout is available: request `/health` and `/api/v1/health` from the same process and compare their JSON bodies and OpenAPI schemas.

## Existing tests

`tests/test_health.py` asserts a 200 response, `status == "ok"`, and the hard-coded service value only for `/api/v1/health`.

## Missing regression coverage

- Root health-route contract test.
- Explicit parity test if both routes are aliases.
- Response-model/OpenAPI contract test.
- Configuration-override test for service identity.

## Recommended remediation scope

Decide whether the routes are aliases or distinct liveness/readiness/version endpoints. Reuse one typed response contract for aliases; otherwise give distinct probes explicit semantics and schemas. Consolidate service identity to one configured source. Database readiness itself remains outside this finding until deployment requirements are established.

## Caller/cross-service trace

Both routes are publicly registered by the same FastAPI application. The reviewed test suite directly consumes only the versioned route. Deployment configuration and external probe callers require checkout/document follow-up.
