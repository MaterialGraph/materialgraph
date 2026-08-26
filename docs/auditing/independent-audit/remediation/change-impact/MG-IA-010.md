# MG-IA-010 Change Impact — Canonical Sensitivity Recalculation

## Status

Verified locally: 35 focused tests, 35 adjacent tests, 659 full-suite tests,
Ruff, and Git whitespace validation passed.

## Before

Baseline screening penalized the material-risk aggregate produced by averaging
available dimensions within each element and then averaging calculable
elements. Sensitivity instead changed a material-level component mean and
multiplied that raw change by the full screening penalty weight. The two paths
therefore represented different mathematical models.

## After

Sensitivity perturbs the selected component on each element that has that
evidence, retains missing dimensions as missing, caps adjusted inputs at the
canonical maximum of 10, and recomputes element and material risk through the
same shared aggregation functions used by the baseline risk service. The
screening service reapplies its canonical risk penalty to the disclosed
pre-risk score and enforces the same score bounds.

## Impact

- Scientific mathematics: **Corrected** — sensitivity and baseline screening
  now use the same aggregation model.
- Partial evidence: **Preserved honestly** — each element continues to use only
  its available dimensions.
- Unknown evidence: **Preserved** — a wholly unavailable selected component
  yields unknown scenario results rather than a numeric assumption.
- Scenario bounds: **Explicit** — perturbed risk inputs cannot exceed the
  canonical 1–10 evidence scale.
- Screening scores: **Corrected** — scenarios recompute from the pre-risk score,
  including when the baseline output was clipped.
- Sensitivity classifications: **May change intentionally** — `LOW`, `MEDIUM`,
  and `HIGH` now reflect canonical recomputed score deltas.
- Screening API contract: **Additive** — results now expose
  `score_before_risk_penalty`.
- Sensitivity API contract: **Additive** — scenarios now expose
  `adjusted_material_risk_score` and `material_risk_delta`.
- Candidate ordering: **Semantics preserved and made exact** — the decision key
  now consumes the explicit pre-risk score instead of reconstructing it from a
  potentially clipped result.
- Database schema and stored data: **No change**.
- Performance: **Bounded** — each of four fixed scenarios performs linear work
  over the selected material's element-risk summaries.

## Unrelated file exclusion

The owner's periodic update to `docs/exploration/external_insights.md` is not
part of this remediation and must not be staged with MG-IA-010.
