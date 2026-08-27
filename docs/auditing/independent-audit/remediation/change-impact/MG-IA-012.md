# MG-IA-012 Change Impact — Deterministic Bounded Neighborhoods

## Status

Verified locally: 716 full-suite tests, Ruff, and Git whitespace validation
passed.

## Before

Neighbor ranking sorted by score, shared-application count, and shared-element
count, all descending, but provided no final key for complete ties. Database
encounter order could therefore change neighbor order. Because bounded
neighborhood traversal admitted and expanded neighbors in that order, a tie
could change returned membership rather than presentation alone. Tied edges
were also ordered only by score.

## After

A shared neighbor-ranking policy now resolves complete ties using ascending
material ID. Both neighbor results and bounded-neighborhood traversal apply the
same policy. Neighborhood edges use descending score followed by ascending
source and target material IDs.

Permutation regressions prove that changing tied candidate encounter order does
not change neighbor output, bounded membership, expansion calls, or edge order.

## Impact

- Determinism: **Corrected** — identical persisted state and parameters produce
  stable neighbor and neighborhood results.
- Bounded membership: **Stabilized** — truncation selects the same tied material
  IDs regardless of database encounter order.
- Traversal: **Stabilized** — tied nodes are expanded in material-ID order.
- Edge presentation: **Stabilized** — complete score ties use endpoint keys.
- Similarity and recommendation ranking: **Unchanged** — their existing final
  material-ID policies remain authoritative downstream.
- Scientific scores and relationship counts: **Unchanged**.
- API schemas: **Unchanged**.
- Database schema and stored data: **No change**.

## Scope decision

The ordering key is shared between neighbor construction and neighborhood
consumption. This makes the producer contract explicit while also protecting
bounded traversal if a future provider returns candidates in a different
encounter order.

