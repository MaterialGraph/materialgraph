# MG-IA-016 Remediation Verification

## Title

Preferred elements remain soft throughout discovery-chain generation

## Status

Implementation and regression tests prepared; local project verification
pending.

## Acceptance criteria

1. Supplying one or more preferred elements does not remove an otherwise
   eligible family candidate from `_get_next_candidates`.
2. Unknown candidate element membership is not a hard rejection solely because
   a preference was requested.
3. A valid two-hop path remains reachable when its intermediate lacks the
   preferred element and its endpoint contains it.
4. The six-candidate per-material expansion bound, 200-state search budget,
   cycle prevention, transition validation, and deterministic family order are
   unchanged.
5. Strict-mode hard rejection remains limited to avoided elements in non-root
   chain materials.
6. Later objective/path ranking remains responsible for preferred-element
   bonuses.

## Prepared changes

- Removed preferred-element membership rejection from
  `DiscoveryChainService._get_next_candidates`.
- Updated two tests that previously encoded the incorrect hard-filter
  behavior.
- Added a two-hop reachability regression with a non-Na intermediate and Na
  endpoint.

## Static verification

```text
python -m compileall -q \
  app/services/discovery/chain_service.py \
  tests/services/discovery/test_discovery_chain_service.py \
  tests/services/discovery/test_discovery_chain_element_membership.py
```

Result: passed in the remediation workspace.

`git diff --check` also passed. The workspace Python runtime does not include
`pytest` or Ruff.

## Required local verification

Run from the activated project virtual environment:

```powershell
pytest tests/services/discovery/test_discovery_chain_element_membership.py tests/services/discovery/test_discovery_chain_service.py -v
pytest tests/services/research/test_research_objective_service.py tests/services/research/test_research_objective_exploration_service.py tests/api/test_discovery_chains_api.py tests/api/test_research_objective_exploration_api.py -v
pytest -v
ruff check .
```

Record test counts, failures if any, and Ruff output before changing the status
to `Verified`.
