# MG-IA-013 Change Impact — Canonical Scenario Element Validation

## Status

Verified locally: 188 focused and adjacent validation tests passed during
implementation, followed by 711 full-suite tests, Ruff, and Git whitespace
validation after the final deprecation cleanup.

## Before

The scenario-recommendation endpoint validated `element`, `avoid_element`, and
`prefer_element` with a regular-expression shape check. Values such as `Q` and
`Xx` therefore passed even though they are absent from the authoritative
118-element set. Discovery endpoints already rejected the same values through
the canonical periodic-table normalizer.

## After

All scenario element parameters now use the same canonical normalization and
structured error mapping as discovery filters. Valid lowercase or supported
whitespace-padded inputs are normalized before service execution. Unknown
one- and two-letter symbols return HTTP 422 with the parameter name, submitted
value, stable error code, and explanatory message.

The legacy `is_valid_element_symbol` utility now checks authoritative periodic-
table membership rather than only capitalization shape.

## Impact

- Scientific-input integrity: **Corrected** — nonexistent symbols cannot
  produce apparently meaningful scenario results.
- Cross-route consistency: **Improved** — scenario and discovery endpoints use
  one normalization and error contract.
- Valid callers: **Compatible** — canonical symbols remain accepted; lowercase
  and permitted surrounding whitespace are normalized.
- Invalid callers: **Intentional behavior change** — well-shaped nonexistent
  symbols now return structured HTTP 422 responses.
- Scenario scoring: **Unchanged for valid inputs**.
- Recommendation ranking: **Unchanged for valid inputs**.
- Database schema and stored data: **No change**.

## Scope decision

Validation is centralized at the API boundary so services receive canonical
symbols. The utility predicate is also corrected to prevent future callers from
reintroducing regex-only validation. Formula extraction behavior is unchanged.

