# MG-IA-010 Remediation Verification

## Title

Sensitivity scenarios reuse canonical risk aggregation and screening mathematics

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL `materialgraph_test` database.

## Acceptance criteria

1. A scenario perturbs the selected element-level evidence dimension rather
   than applying its component delta directly as a material-risk delta.
2. Element risk is recomputed as the mean of its available risk dimensions.
3. Material risk is recomputed as the equal mean of calculable element risks.
4. Partial profiles preserve their actual available-dimension denominators.
5. Multi-element scenarios preserve the canonical equal-element aggregation.
6. Entirely missing scenario-dimension evidence remains unknown.
7. Perturbed evidence stays within the canonical 1–10 score scale.
8. Adjusted screening scores use the same risk-penalty weight and 0–100 bounds
   as baseline screening.
9. Score recomputation starts from the pre-risk score, including when the
   baseline score was clipped at a boundary.
10. Responses disclose adjusted material risk and its delta from baseline.

## Current-baseline confirmation

The finding was re-evaluated against GitHub commit
`0e2fe6723ffb9c2acbba41dd9f896035e5efc89a` before implementation. The current
baseline still calculated material risk through dimension and element means,
but sensitivity multiplied a component-mean change directly by the complete
screening risk weight. The finding therefore remained applicable and had not
been invalidated by intervening remediations.

## Implemented changes

- Centralized element-risk and material-risk mean calculations in the shared
  risk evidence policy.
- Reused those calculations in both scalar and bulk material-risk service
  paths.
- Added the exact pre-risk screening score to the screening result contract.
- Centralized application of the screening risk penalty and score bounds.
- Updated sensitivity scenarios to perturb every available selected component
  at the element-evidence level and cap it at 10.
- Recomputed adjusted element risks, adjusted material risk, and adjusted
  screening score through the canonical calculation stages.
- Added `adjusted_material_risk_score` and `material_risk_delta` to every
  sensitivity scenario for numeric explainability.
- Preserved null scenarios when the selected evidence dimension is wholly
  unavailable.
- Updated comparison fixtures for the additive screening contract.

## Mathematical parity example

For one complete element with supply, geopolitical, and toxicity scores
`(6, 3, 3)`, baseline element and material risk are both `4`. A 50% supply-risk
scenario changes the evidence to `(9, 3, 3)`, producing adjusted risk `5`.
With screening weight `5`, the adjusted score changes by `-5`, not the former
`-15`. The focused regression verifies this exact case.

## Verification results

Commands:

```powershell
pytest tests/services/test_sensitivity_analysis_service.py tests/services/test_candidate_screening_service.py tests/services/test_candidate_comparison_service.py tests/services/material/test_material_risk_service.py tests/api/test_sensitivity_api.py -v
pytest tests/services/test_scenario_policy.py tests/services/test_scenario_ranking_service.py tests/services/test_substitution_analysis_service.py tests/services/material/test_recommendation_service.py tests/api/test_scenario_ranking_api.py tests/api/test_substitutions_api.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused sensitivity, screening, comparison, risk, and API tests:
  **35 passed in 0.78 seconds**;
- adjacent scenario, substitution, recommendation, and API tests:
  **35 passed in 0.59 seconds**;
- complete test suite: **659 passed in 61.18 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

Ruff emitted a non-fatal warning that its local cache file could not be written;
the lint analysis itself completed and reported all checks passed.

The suite increased from 655 to 659 tests through three sensitivity-mathematics
regressions and one canonical screening recomputation regression.

## Unrelated worktree change

`docs/exploration/external_insights.md` was independently maintained by the
repository owner during this remediation. It is outside MG-IA-010 scope and is
intentionally excluded from the remediation commit.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-010` is verified as remediated.
