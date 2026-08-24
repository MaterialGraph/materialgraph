# MG-IA-016 Change Impact — Soft Preferred-Element Chain Semantics

## Status

Prepared; local verification pending.

## Before

Requesting preferred elements removed every chain candidate lacking all
preferred elements before transition validation or ranking. A valid endpoint
could be unreachable when an intermediate did not already contain a preferred
element, even though the API declared the preference a soft bonus.

## After

Preferred elements no longer determine chain eligibility. Bounded family
candidates proceed through normal transition validation and search. Preference
alignment remains a deterministic ranking contribution downstream. Strict
hard rejection remains limited to avoided elements in non-root chain materials.

## Impact

- Scientific result: **Yes** — previously hidden valid pathways may appear.
- Ranking: **Potentially** — newly eligible paths enter the bounded evaluated
  pool and are ranked by the existing score policy.
- API structure: **No change**.
- Declared API semantics: **Now enforced consistently**.
- Search bounds: **Unchanged** — six candidates per material and 200 expanded
  states.
- Database migration: **No**.
- Data mutation: **No**.
