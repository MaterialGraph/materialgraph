# MG-IA-014 Remediation Verification

## Title

Discovery and substitution reuse canonical stability-evidence semantics

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. Discovery does not reapply stability already included in recommendation and
   similarity scores.
2. Discovery does not create a raw-flag stability path or explanation.
3. Substitution evaluates stability through `StabilityEvidencePolicy`.
4. Energy above hull remains primary when energy and the imported flag differ.
5. A contradictory stable flag cannot earn a substitution stability benefit
   when energy evidence classifies the candidate as unstable.
6. Missing energy may use the imported flag only as incomplete fallback
   evidence with a smaller contribution.
7. Substitution exposes evidence basis, completeness, band, source consistency,
   and the exact numeric contribution.
8. Explanations describe the evidence actually used and disclose inconsistent
   stability sources.
9. The existing stable-energy substitution maximum remains bounded at 0.05.

## Current-baseline confirmation

The finding was re-evaluated against GitHub commit
`8e22ddbb5347c8c2110c1023f2ae981006ac288f` before implementation. Exact
current files confirmed that recommendation inherited the canonical similarity
contribution, discovery subsequently added `STABILITY_BONUS = 20.0` from raw
`is_stable`, and substitution independently added 0.05 and narrated “Stable
candidate” from that flag. The finding remained applicable.

## Implemented changes

- Removed the discovery `STABILITY_BONUS` constant and raw-flag scoring branch.
- Removed the corresponding `stable_material` discovery explanation.
- Retained recommendation score as the sole inherited stability-bearing score.
- Assessed every substitution candidate through `StabilityEvidencePolicy`.
- Scaled the canonical similarity contribution by 1/400 into substitution's
  existing rank-score range.
- Added stability band, basis, completeness, consistency, and rank contribution
  to `SubstituteCandidate`.
- Replaced the raw “Stable candidate” narrative with the canonical policy
  reason and an explicit inconsistency clause when applicable.
- Added regression coverage for inherited-score non-duplication,
  energy/flag contradiction, fallback scaling, and the additive API contract.

## Numeric verification examples

- A recommendation score of 120 that already contains a 20-point canonical
  stability contribution remains 120 in discovery, rather than becoming 140.
- A substitution candidate with `is_stable=True` and
  `energy_above_hull=0.2` is classified unstable, receives 0 stability rank
  contribution, and reports inconsistent sources.
- A candidate with `is_stable=True` and unavailable energy uses incomplete
  fallback evidence: canonical contribution 10 divided by 400 gives 0.025.

## Verification results

Commands:

```powershell
pytest tests/services/discovery/test_discovery_scoring_service.py tests/services/test_substitution_analysis_service.py tests/api/test_substitutions_api.py -v
pytest tests/services/discovery/test_candidate_service.py tests/services/material/test_stability_evidence_policy.py tests/services/material/test_similarity_service.py tests/services/material/test_recommendation_service.py tests/api/test_discovery_candidates.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused discovery scoring, substitution service, and substitution API tests:
  **20 passed in 0.29 seconds**;
- adjacent candidate, canonical policy, similarity, recommendation, and
  discovery API tests: **68 passed in 0.67 seconds**;
- complete test suite: **663 passed in 16.04 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; the reported LF-to-CRLF message is a
  non-failing Windows working-copy normalization warning.

The suite increased from 659 to 663 tests through two discovery regressions and
two substitution stability-evidence regressions. Existing substitution and API
tests were also extended for the additive evidence contract.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-014` is verified as remediated.
