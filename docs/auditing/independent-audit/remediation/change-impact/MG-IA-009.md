# MG-IA-009 Change Impact — Explicit Composition Evidence

## Status

Verified locally: 55 focused tests, 63 adjacent tests, 655 full-suite tests,
Ruff, Git whitespace validation, migration execution, backfill application,
and idempotency verification passed.

## Before

When structured composition was absent, membership-only imports stored `1.0`
for every element. Those fallback values were indistinguishable from measured
or structured quantitative fractions. Criticality treated them as equal
composition weights, the API labelled them fractions, and quality could consume
the resulting unsupported material criticality score.

## After

Every material-element link records whether its fraction is supported by
structured composition evidence. Membership-only links retain their legacy
numeric compatibility value internally but are explicitly unknown. Unknown
fractions are public `null` values, do not participate in weighted material
criticality, and cannot improve quality through an unsupported criticality
aggregate. Validated imports and backfill operations mark composition known.

## Impact

- Scientific honesty: **Improved** — membership and quantitative composition
  are no longer conflated.
- Existing membership semantics: **Preserved** — element membership remains
  available even when fractions are unknown.
- Criticality: **Changed intentionally** — material-level weighted criticality
  is unavailable unless composition evidence is complete; element-level risk
  details remain available.
- Quality: **Changed intentionally** — unknown-composition criticality provides
  no quality contribution, and evidence status is disclosed.
- API contract: **Additive and nullable** — composition evidence fields are
  added and unknown element fractions are returned as `null`.
- Database schema: **Changed** — `material_elements.fraction_known` is a
  non-null boolean with a conservative `false` default.
- Historical data: **Conservatively classified** — migration does not infer
  evidence from ambiguous predecessor values.
- Structured imports: **Evidence-aware** — validated fractions are marked
  known; membership-only imports are marked unknown.
- Backfill: **Evidence-only and idempotent** — validated source composition can
  promote rows without altering correct normalized numeric fractions.
- Ranking consumers: **Safer unknown propagation** — downstream similarity and
  recommendation behavior continues to handle unavailable criticality.

## Operational requirement

Deployments must apply Alembic revision `7a4c2e91b6d8` before running code that
expects `fraction_known`. Production backfill must be preceded by target
database confirmation and a restorable backup or database branch, first run as
a dry run, and followed by a second dry run after application to prove
idempotency.
