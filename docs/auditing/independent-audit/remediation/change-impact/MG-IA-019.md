# MG-IA-019 Change Impact — Bounded Scenario Ranking Results

## Status

Verified locally: 15 focused tests, 6 adjacent screening tests, 685
full-suite tests, Ruff, and Git whitespace validation passed.

## Before

`ScenarioRankingRequest.top_n` was an unconstrained integer with default 10.
The service applied it directly through Python slicing. Zero returned an empty
successful response, negative values used unintended slice semantics, and
arbitrarily large positive values allowed the response to grow with the entire
eligible candidate set.

## After

`top_n` is validated by Pydantic as an integer from 1 through 20, inclusive,
while retaining the default of 10. The maximum matches MaterialGraph's existing
public result-limit boundary for discovery chains and research objectives.
FastAPI rejects invalid requests with HTTP 422 before scenario screening runs.

## Impact

- Negative and zero limits: **Rejected** instead of producing misleading
  successful slices.
- Excessive limits: **Rejected** above 20.
- Valid boundary: **Explicit** — 1 and 20 are accepted.
- Default behavior: **Unchanged** — omitted `top_n` remains 10.
- Response boundedness: **Corrected** — at most 20 ranked results can be
  serialized by the endpoint.
- Unknown-scenario behavior: **Unchanged** — valid requests with unknown
  scenario names still return the established HTTP 400 response.
- Screening and ranking logic: **Unchanged**.
- Database schema and stored data: **No change**.

## Performance boundary

The remediation bounds returned results and downstream serialization. It does
not change the candidate-screening pool or introduce premature limiting before
scientific screening and deterministic ordering are complete.
