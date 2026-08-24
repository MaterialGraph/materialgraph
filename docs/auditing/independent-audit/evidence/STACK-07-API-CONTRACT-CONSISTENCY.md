# Stack 07 Evidence — API Contract Consistency

## Scope

In progress. This first slice covers FastAPI application assembly, installed-package version resolution, shared element-filter dependency, application/element/health/comparison/material-family/material-risk/scenario routes, and application/element/comparison schemas.

All thirteen supplied Python files compiled successfully.

## Application and router assembly

`app.main` constructs one FastAPI application, uses the installed package version in OpenAPI and the root health response, installs a lifespan logger, and mounts the versioned API router under `/api/v1`. The supplied versioned router includes both discovery and research routers. Graph-job routing remains deliberately disabled as recorded in Stack 05.

Version resolution has one canonical package-metadata source and an explicit `0+unknown` source-checkout fallback. Root and versioned health routes remain intentionally unresolved observations because their payloads differ (`OBS-001`–`OBS-003`); this slice adds no contrary evidence.

## Element validation

Single-value discovery query filters normalize against the canonical 118-element table and return a structured 422 for nonexistent symbols. List-valued screening, comparison, and research-objective fields are unconstrained strings, while the scenario-recommendation validation reviewed earlier checks only symbol shape. `MG-IA-013` is therefore expanded from a scenario-only defect to a cross-API scientific-input defect; no additional finding ID is created.

## Resource and response semantics

Application and element collection routes are bounded to 100 rows, support nonnegative offset, and order by fields constrained unique in their corresponding models. Their item routes return 404 when absent. Material-family routes apply the shared material-found helper; material-risk routes return 404 when their service returns no result.

Candidate comparison maps missing candidates to 404 and constraint-filtered candidates to 422 while preserving typed unavailable details. Its success response is restricted to winner/tie results. Scenario ranking converts service `ValueError` to HTTP 400; validation and service tests are still required before judging that error taxonomy.

## Positive checks

- API assembly mounts the versioned router exactly once.
- Package/OpenAPI/root-health version values share one runtime source.
- Application and element list queries are bounded and deterministically ordered under model uniqueness.
- Application, element, family, risk, and comparison routes expose explicit missing-resource behavior.
- Comparison distinguishes nonexistent candidates from candidates excluded by declared constraints.

## Evidence still required

- scenario-ranking schemas, services, and tests;
- application, element, health, family, and material-risk API tests;
- remaining shared error/metadata schemas and route utilities;
- intended API-wide 404-versus-empty-result policy;
- current documentation for public error and health contracts.

## Execution limitation

Source compilation and static vertical traces were completed. Database-backed route tests were not executed because the exact checkout and configured test database are unavailable in this workspace.
