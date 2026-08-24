# MG-IA-007 — Computed risk and criticality outputs omit selected profile source attribution

- Classification: explainability and provenance defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Evidence

`ElementRiskProfile` persists `year` and `source`; the raw risk-profile schema exposes source. Computed material-risk output exposes neither selected profile year nor source. Criticality exposes year but not source. `EVIDENCE_BASIS="latest_element_risk_profile"` describes selection methodology, not row attribution. Quality and downstream services propagate generic evidence labels without selected sources.

Affected files/components: `app/models/element_risk_profile.py`, `app/schemas/risk.py`, `app/schemas/material_risk.py`, `app/schemas/material_criticality.py`, `app/services/material/risk_service.py`, `criticality_service.py`, `quality_service.py`, candidate screening, sensitivity, and substitution.

## Expected versus actual

Numeric evidence should identify the stored dataset that supplied it. Consumers receive scores without knowing whether selected rows came from the canonical profile, a legacy default, or another dataset.

## Impact

Results are not fully attributable or independently reproducible, and mixed-source or legacy profiles cannot be identified from computed output.

## Tests

No supplied computed-output test asserts persisted source propagation or multi-source behavior.

## Reproduction and caller trace

Persist profiles with distinguishable `source` values, compute material risk/criticality, and inspect serialized element evidence. `MaterialRiskService` feeds the public material-risk route plus screening, sensitivity, substitution, and quality; `MaterialCriticalityService` feeds quality and its response schema.

## Remediation scope

Expose selected source, year, and preferably profile identity per element; propagate an aggregate source summary where appropriate; test persisted-to-response attribution.
