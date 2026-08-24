# MG-IA-010 — Sensitivity deltas are inconsistent with baseline risk aggregation

- Classification: mathematical and scenario-semantics defect
- Priority: P1
- Confidence: high
- Disposition: confirmed

## Evidence

Baseline element risk is the mean of available supply, geopolitical, and toxicity dimensions; material risk is the equal mean of calculable elements; screening subtracts material risk multiplied by five. Sensitivity instead multiplies one component's raw change directly by five without recomputing either mean.

Affected files/functions: `risk_service.py:_calculate_element_risk` and `get_material_risk`; `candidate_screening_service.py:_screen_materials`; `sensitivity_analysis_service.py:_mean_component_score` and `_build_sensitivity_scenarios`; sensitivity schemas/tests.

For one complete element with dimensions `(6,3,3)`, baseline risk is `4`. Raising supply from `6` to `9` changes aggregate risk to `5`, so the screening penalty changes by `5`. Sensitivity reports `(9-6)*5=15`.

## Expected versus actual

A scenario purporting to adjust a screening input should reproduce the screening model with that input perturbed. Current deltas use a mathematically different model and can overstate or otherwise distort the change.

## Impact

Adjusted scores and `LOW`/`MEDIUM`/`HIGH` classifications can misstate sensitivity. Partial dimensions and multiple elements make the discrepancy data-dependent.

## Tests

Tests protect distinct component names and current arithmetic but do not recompute perturbed risk through `MaterialRiskService` and `CandidateScreeningService`.

## Caller trace and reproduction

`SensitivityAnalysisService.analyze` obtains the public screening baseline, independently derives component means from `MaterialRiskRead`, and returns scenario scores through `SensitivityAnalysisResult`. Reproduce with one complete `(6,3,3)` element as calculated above and compare the scenario delta with a full risk-and-screening recomputation.

## Remediation scope

Represent the scenario perturbation at the evidence-input level, recompute through the canonical aggregation and screening path, and add parity tests for complete, partial, multi-element, unknown, and threshold cases.
