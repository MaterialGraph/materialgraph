# MG-IA-017 Change Impact — Evidence-Aware Pathway Risk Summary

## Status

Verified locally: 26 focused tests, 55 adjacent tests, 646 full-suite tests,
Ruff, and Git whitespace validation passed.

## Before

Scientific-pathway quality summaries applied `max` directly to nullable risk
scores. Mixed or all-unknown evidence could raise `TypeError`, while a single
unknown record could be presented as the highest-risk material without numeric
support.

## After

Highest-risk selection uses only explicitly known, finite numeric risk scores.
When none are eligible, `highest_risk_material` is `null`. The summary reports
known and total material counts, risk coverage, and a `complete`, `partial`, or
`unavailable` status.

## Impact

- Scientific result: **Yes** — unsupported highest-risk labels are removed.
- Reliability: **Yes** — nullable risk no longer causes summary failure.
- Explainability: **Yes** — summary-level evidence coverage is explicit.
- Ranking: **No pathway score or ranking formula change**.
- API structure: **Additive fields only**.
- Existing nullable field: `highest_risk_material` now correctly returns
  `null` when risk comparison is unavailable.
- Database migration: **No**.
- Data mutation: **No**.
