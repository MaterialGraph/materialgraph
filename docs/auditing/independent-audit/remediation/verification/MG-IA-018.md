# MG-IA-018 Remediation Verification

## Title

Research objective controls are executed and disclosed consistently

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. Required stability applies to every non-root material in a chain.
2. Unknown and non-stable evidence fail the required-stability policy.
3. Disabling required stability avoids stability-policy filtering.
4. Lower-criticality preference includes the canonical criticality quality
   contribution only when enabled.
5. Disabling lower-criticality preference excludes that contribution and its
   evidence lookup.
6. Objective generation, exploration, and scientific pathway results disclose
   the effective policy.
7. Quality results disclose stability, criticality, and risk contributions,
   including zero contributions for missing material evidence.
8. Exact chemical element membership remains correct (`N` does not match
   `Na`).
9. Scientific tie and competition ranking remain unchanged.
10. The complete test suite and lint checks pass.

## Current-baseline confirmation

The finding was re-evaluated against committed baseline `060744cf0dd34347ab6ed2021c042616caaaddd3`.
The two public objective controls remained present, but their behavior and
response disclosure were incomplete across the research orchestration chain.
The remediation was rebuilt from a bundle containing that exact baseline after
an older working reconstruction was rejected.

## Implemented changes

- Added typed objective-policy disclosure to discovery and exploration schemas.
- Enforced required stability through canonical material-quality evidence.
- Rejected unknown stability when stable materials are required.
- Added separately disclosed criticality and risk quality contributions.
- Made objective path ranking include criticality contribution conditionally.
- Propagated policy through objective generation, exploration, and scientific
  pathway analysis.
- Added paired enabled/disabled policy regressions.
- Updated exact-dictionary and lightweight fake-objective fixtures to represent
  the expanded contract.
- Preserved scientific competition ranking and exact element-membership
  behavior.

## Verification results

Commands included:

```powershell
pytest tests/services/research/test_research_objective_controls.py tests/services/research/test_research_objective_service.py tests/services/research/test_research_objective_exploration_service.py tests/services/discovery/test_discovery_path_ranking_service.py tests/services/material/test_material_quality_service.py -v
pytest tests/services/research/test_research_objective_exploration_element_membership.py tests/services/research/test_scientific_scoring.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused policy and adjacent service run initially identified two stale test
  expectations while 54 tests passed;
- the subsequent full run identified four additional incomplete legacy test
  doubles;
- corrected exact-membership and scientific-ranking regressions: **7 passed in
  0.20 seconds**;
- complete test suite after all corrections: **675 passed in 22.33 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; reported LF-to-CRLF informational
  notices only.

## Change boundary

The verified implementation boundary contains 15 files: seven production
files, seven modified test files, and one new objective-control test file.
Remediation documentation and the register update are added separately after
verification.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-018` is verified as remediated.
