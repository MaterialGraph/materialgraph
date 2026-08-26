# MG-IA-015 Change Impact — Bounded Multi-Hop Path Construction

## Status

Verified locally: 36 focused tests, 56 adjacent tests, 667 full-suite tests,
Ruff, and Git whitespace validation passed.

## Before

Weighted shortest path accepted `max_depth` values greater than one but built
its search graph through the standard graph mode, whose deliberate production
cap is one hop. Its heap search then enforced the larger requested depth over a
graph that contained only direct edges. The public discovery-path service used
the same capped construction. Existing multi-hop tests substituted handcrafted
graphs and therefore bypassed the production builder behavior.

## After

Graph construction now has three explicit, mutually exclusive bounded modes:

- standard graph responses remain capped at one hop;
- analytics remain capped at two hops;
- path searches are capped at three hops, matching the existing public API
  validation boundary.

Weighted shortest path and the public discovery-path service select path-search
mode. Weighted responses disclose requested depth, effective depth, and whether
the request was truncated. A regression exercises the real builder through a
two-hop-only graph rather than replacing graph construction.

## Impact

- Weighted reachability: **Corrected** — targets reachable in two or three hops
  can be found within the requested bound.
- Public discovery path: **Corrected** — graph construction now matches the
  route's existing `max_hops` contract through three hops.
- Standard graph endpoint: **Unchanged** — its one-hop operational cap and
  requested/effective-depth disclosure remain intact.
- Graph analytics: **Unchanged** — the existing two-hop analytics cap remains.
- Boundedness: **Preserved** — path construction cannot exceed three hops and
  per-node expansion remains capped at six.
- Explainability: **Improved** — weighted results disclose requested/effective
  depth and truncation instead of silently searching a shallower graph.
- Determinism: **Preserved** — stable node, edge, heap, and path ordering are
  unchanged.
- API validation: **Unchanged** — the public path route already accepts only
  one through three hops.
- Weighted helper contract: **Additive** — three depth-metadata fields are
  added to success and failure responses.
- Database schema and stored data: **No change**.

## Performance boundary

The remediation does not raise the normal graph-response cap. Multi-hop work is
enabled only for bounded path lookup, where depth is at most three and candidate
expansion remains at most six per expanded material.
