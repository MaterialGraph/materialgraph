# MG-IA-018 Change Impact — Effective Research Objective Controls

## Status

Verified locally: targeted policy regressions, 675 full-suite tests, Ruff, and
Git whitespace validation passed.

## Before

The public research objective exposed `require_stable_materials` and
`prefer_lower_criticality`, but the controls were not applied consistently
through objective chain generation, exploration ranking, path ranking, and
scientific pathway analysis. Responses also did not consistently disclose the
effective policy. A caller could therefore request strict stability or disable
criticality preference without receiving behavior that reliably matched the
request.

## After

Research objective processing now treats both controls as executable policy:

- `require_stable_materials=true` rejects a chain when any non-root material
  lacks canonical evidence classifying it as stable;
- unknown or non-stable evidence does not pass a required-stability filter;
- `prefer_lower_criticality=true` includes the canonical criticality quality
  contribution in objective-specific ranking;
- `prefer_lower_criticality=false` excludes that contribution and avoids the
  corresponding evidence lookup;
- objective generation, exploration, and scientific pathway responses disclose
  the effective objective policy.

Quality scoring exposes stability, criticality, and risk contributions
separately. The implementation reuses canonical material-quality evidence and
does not introduce a second criticality formula.

## Impact

- Objective semantics: **Corrected** — both advertised controls now change
  behavior as stated.
- Stability filtering: **Stricter when requested** — missing evidence is not
  treated as proof of stability.
- Criticality ranking: **Conditional** — criticality affects objective ranking
  only when the preference is enabled.
- Explainability: **Improved** — research responses disclose the effective
  objective policy and component quality contributions.
- Scientific honesty: **Improved** — unknown stability is preserved as unknown
  and rejected under an explicit stability requirement.
- Existing non-objective ranking: **Preserved** — legacy callers retain their
  existing behavior unless they opt into objective-specific controls.
- Determinism: **Preserved** — stable ordering and tie behavior are unchanged.
- Database schema and stored data: **No change**.

## Compatibility boundary

The response contract gains typed objective-policy disclosure and component
quality contributions. Existing tests using lightweight objective or service
test doubles were updated to represent the current public contract explicitly;
production code was not weakened to accommodate incomplete fixtures.
