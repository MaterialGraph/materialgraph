# MG-IA-017 Remediation Verification

## Title

Pathway quality summaries preserve unknown-risk semantics

## Status

Verified in the local project environment on Windows with Python 3.14.5.

## Acceptance criteria

1. Highest-risk selection considers only records whose risk is explicitly
   known and whose score is a finite numeric value.
2. Unknown, missing, NaN, infinite, and boolean risk values cannot be labelled
   as the highest-risk material.
3. Mixed known/unknown evidence selects from the known subset and reports
   partial coverage.
4. All-unknown and empty inputs return `highest_risk_material: null` and an
   unavailable summary rather than failing or fabricating a ranking.
5. All-known inputs retain numeric highest-risk selection and report complete
   coverage.
6. Existing average-quality, lowest-quality, confidence, comparison, and
   endpoint behavior remain operational.

## Implemented changes

- Filtered highest-risk candidates through an explicit known-and-finite risk
  predicate.
- Preserved `None` when no scientifically eligible risk record exists.
- Added bounded summary metadata:
  `known_risk_material_count`, `total_risk_material_count`, `risk_coverage`,
  and `risk_summary_status`.
- Added schema constraints for non-negative counts and `0.0–1.0` coverage.
- Added regressions for all-known, mixed, all-unknown, non-finite, and empty
  evidence states.

## Verification results

Commands:

```powershell
pytest tests/services/research/test_scientific_pathway_analysis_service.py -v
pytest tests/services/research/test_research_objective_exploration_contracts.py tests/services/research/test_research_evidence_intelligence_service.py tests/services/research/test_comparative_research_intelligence_service.py tests/api/test_research_routes.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused scientific-pathway tests: **26 passed in 1.08 seconds**;
- adjacent contract, evidence, comparison, and API tests:
  **55 passed in 1.42 seconds**;
- complete test suite: **646 passed in 16.43 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

The suite increased from 641 to 646 tests because this remediation added five
regressions.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-017` is verified as remediated.
