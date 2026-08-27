# MG-IA-007 Remediation Verification

## Title

Computed risk and criticality evidence identifies selected persisted profiles

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. Each calculable material-risk element exposes selected profile ID, year,
   and source.
2. Each criticality element with a selected profile exposes its ID, year, and
   source, including selected profiles whose dimensions are incomplete.
3. Material-risk and criticality responses expose deterministic aggregate
   selected-profile IDs, years, and sources.
4. Risk signals preserve aggregate attribution across scalar and bulk paths.
5. Quality, screening, sensitivity, substitution, and research-quality
   contracts expose the relevant aggregate attribution.
6. Unknown evidence exposes empty attribution lists rather than fabricated or
   default sources.
7. Distinct persisted sources survive selection and serialization without
   collapsing into a generic methodology label.
8. Scores, rankings, evidence coverage, and existing API fields remain
   regression-safe.
9. The complete test suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `6fdc991`.
`ElementRiskProfile` still persisted `id`, `year`, and `source`, but computed
material-risk element summaries exposed none of them. Criticality elements
exposed `risk_year` but omitted profile ID and source. Risk signals and
downstream quality, screening, sensitivity, and substitution contracts carried
only generic methodology and coverage metadata. The frozen finding remained
fully applicable.

## Implemented changes

- Added profile ID, year, and source to computed material-risk element details.
- Added profile ID and source alongside the existing year in criticality
  element details.
- Added sorted aggregate selected-profile ID, year, and source lists to risk
  and criticality results.
- Propagated aggregate attribution through scalar/bulk risk signals.
- Exposed selected risk-profile attribution in screening, sensitivity, and
  substitution results, including source-material attribution.
- Exposed risk and criticality profile summaries in material-quality and typed
  research-quality evidence.
- Added empty-list attribution to unknown and missing-material responses.
- Added persisted multi-source regression evidence and API/schema propagation
  assertions.

## Verification results

Commands included focused material risk, criticality, quality, downstream
decision-service, typed-contract, and API suites, followed by:

```powershell
pytest -q
ruff check .
git diff --check
```

Results:

- focused and downstream verification: **37 passed in 0.71 seconds**;
- complete test suite: **719 passed in 30.36 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

## Change boundary

The verified implementation boundary contains 23 files: six schemas, six
services, seven service/contract test files, and four API test files. It makes
no model, migration, seed-data, or deployment change.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-007` is verified as remediated.

