# MG-IA-019 Remediation Verification

## Title

Scenario ranking validates a positive, capped result limit

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. The default scenario-ranking result limit remains 10.
2. The minimum value 1 is accepted.
3. The maximum value 20 is accepted.
4. Negative values are rejected during request validation.
5. Zero is rejected during request validation.
6. Maximum-plus-one is rejected during request validation.
7. Invalid API requests return HTTP 422 before screening executes.
8. A maximum-boundary API request returns no more than 20 results.
9. Existing scenario ranking, unknown scenario, unknown risk, screening,
   deterministic ordering, and bulk-loading behavior remain regression-safe.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `8bb1c17`.
`ScenarioRankingRequest.top_n` remained an unconstrained `int`, and
`ScenarioRankingService` still applied it as `results[: request.top_n]`.
The route provided no independent limit validation. The frozen finding
therefore remained fully applicable.

## Implemented changes

- Imported Pydantic `Field` in `app/schemas/scenario_ranking.py`.
- Declared `top_n` as `Field(default=10, ge=1, le=20)`.
- Added schema tests for the default, both valid boundaries, negative, zero,
  and maximum-plus-one values.
- Added API tests for maximum acceptance and HTTP 422 rejection of invalid
  limits.
- Preserved the existing service and route implementations because validated
  request construction already establishes the boundary centrally.

## Verification results

Commands:

```powershell
pytest tests/services/test_scenario_ranking_service.py tests/api/test_scenario_ranking_api.py -v
pytest tests/services/test_candidate_screening_service.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused scenario schema, service, and API tests: **15 passed in 0.26
  seconds**;
- adjacent candidate-screening service tests: **6 passed in 0.09 seconds**;
- complete test suite: **685 passed in 14.49 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

## Change boundary

The verified implementation boundary contains three files: one request schema,
one scenario-ranking API test file, and one scenario-ranking service test file.
No route, service, database, or migration change is required.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-019` is verified as remediated.
