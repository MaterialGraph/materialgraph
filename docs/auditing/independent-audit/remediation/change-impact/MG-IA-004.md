# MG-IA-004 Change Impact — Deterministic Criticality Element Ordering

## Status

Verified locally: 717 full-suite tests, Ruff, and Git whitespace validation
passed.

## Before

Criticality responses ordered elements only by whether a calculated score was
available and by the score itself. Equal known scores and multiple unknown
scores retained the material-element query's unspecified row order. Identical
data could therefore produce different serialized `elements` sequences.

## After

Criticality responses use one explicit total ordering:

1. known criticality before unknown criticality;
2. known scores descending;
3. element symbol ascending;
4. element ID ascending as the final stable key.

Permutation evidence reverses tied known and unknown input rows and requires
identical serialized output.

## Impact

- Determinism: **Corrected** — tied element output no longer depends on query
  or physical row order.
- Scientific scoring: **Unchanged** — weights, aggregation, rounding, evidence
  coverage, and legitimate ties are preserved.
- Scalar and bulk criticality: **Consistent** — both use the shared response
  builder and ordering policy.
- Public criticality API: **Stabilized** — ordered element lists are
  reproducible for snapshots and comparisons.
- Material quality consumers: **No scoring change**.
- API schema: **Unchanged**.
- Database schema and stored data: **No change**.

## Scope decision

The remediation sorts the constructed response rather than relying on database
row order. Symbol provides the human-readable stable tie-breaker requested by
the finding, and element ID protects total ordering if malformed or legacy data
ever duplicates a symbol.

