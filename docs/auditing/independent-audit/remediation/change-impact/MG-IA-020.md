# MG-IA-020 Change Impact — Uniform Chain-Derived Resource Semantics

## Status

Verified locally: focused, internal-sentinel, adjacent resource-semantics, and
689 full-suite tests passed; Ruff and Git whitespace validation passed.

## Before

Chain-derived material APIs returned HTTP 200 with empty results when the root
material did not exist. The same empty service sentinel represented both a
missing resource and a valid material with no chains or research opportunities.
Clients therefore could not distinguish a stale identifier from a scientifically
valid search with no result.

## After

A shared route utility now performs an exact material primary-key lookup.
Discovery chains, objective chains, objective exploration, and scientific
pathway analysis invoke it before their analysis services. A nonexistent root
returns HTTP 404 with `Material not found`; an existing root continues into the
same service pipeline and may still return an empty valid result.

## Impact

- Resource semantics: **Corrected** — missing material identifiers are distinct
  from valid empty scientific results.
- Cross-endpoint consistency: **Improved** — chain-derived APIs now match
  families, neighbors, risks, candidates, and other material-scoped endpoints.
- Service reuse: **Preserved** — internal services retain safe empty sentinels.
- Existing materials: **Unchanged** — all existing-material requests continue
  through the same deterministic analysis.
- Error contract: **Consistent** — affected routes return HTTP 404 with the
  established `Material not found` detail.
- Performance: **Bounded overhead** — one indexed primary-key lookup occurs
  before potentially expensive analysis.
- Database schema and stored data: **No change**.

## API boundary

Existence is checked from the database rather than inferred from response
fields such as `mp_id` or `base_formula`. This avoids coupling resource identity
to individual response schemas and prevents false 404 responses for typed
objective results that do not expose `mp_id`.
