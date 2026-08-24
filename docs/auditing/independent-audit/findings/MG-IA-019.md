# MG-IA-019 — Scenario ranking accepts negative and unbounded result limits

- Classification: API validation and bounded-response defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/schemas/scenario_ranking.py`
- `app/services/scenario_ranking_service.py`
- `app/api/v1/routes/scenario_ranking.py`
- scenario-ranking tests

## Exact evidence

`ScenarioRankingRequest.top_n` is declared as an unconstrained `int` with default 10. `ScenarioRankingService.rank_for_scenario` applies it directly as `results[: request.top_n]`. The route catches only unknown-scenario `ValueError`; it does not validate or normalize the result limit.

Python negative slicing is valid: `results[:-1]` returns every result except the last, rather than rejecting the request. `top_n=0` silently returns an empty successful response. Arbitrarily large positive values allow the response to grow with every eligible material returned by screening.

## Expected versus actual

A parameter named `top_n` should be a positive, explicitly capped result limit and invalid values should fail request validation. It currently accepts zero, negative, and unbounded positive values with successful but misleading or potentially large responses.

## Impact

Negative inputs have unintended semantics unrelated to “top N.” Unbounded positive inputs defeat route-level response bounding and can increase serialization, transfer, and downstream processing as the materials table grows. This also conflicts with the explicit bounds used by other list/ranking endpoints.

## Reproduction

Submit a valid preset such as `lithium_supply_shock` with `top_n=-1`. Pydantic accepts it, and the service returns `results[:-1]` with ranks starting at one. Submit a very large positive integer to request every eligible screened material.

## Caller trace

The `/api/v1/scenarios/rank` route passes the request directly to `ScenarioRankingService`. The service first computes the full screening result and then slices it using the unchecked value. No downstream layer restores the intended limit semantics.

## Tests

Supplied tests cover `top_n=1` and `top_n=5`, unknown scenario names, and unknown-risk explanations. They do not cover zero, negative, maximum, or over-maximum values, nor API validation for those boundaries.

## Recommended remediation scope

Declare `top_n` with an explicit positive bound using Pydantic `Field`, align the maximum with documented product needs, and add schema/API tests at zero, one, maximum, and maximum-plus-one. Consider threading the validated limit into candidate selection if full-pool screening becomes materially expensive; response bounding alone does not bound upstream computation.
