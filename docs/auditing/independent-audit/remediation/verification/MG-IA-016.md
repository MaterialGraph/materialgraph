# MG-IA-016 Remediation Verification

## Title

Preferred elements remain soft throughout discovery-chain generation

## Status

Verified.

Local project verification completed against clean commit
`32bc57cc78754e061f9a2f4294d81aa39e4f9955` on Windows with Python 3.14.5,
pytest 9.0.3, and Ruff.

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

## Local project verification

The required commands were run from the activated project virtual environment.

```powershell
pytest tests/services/discovery/test_discovery_chain_element_membership.py tests/services/discovery/test_discovery_chain_service.py -v
pytest tests/services/research/test_research_objective_service.py tests/services/research/test_research_objective_exploration_service.py tests/api/test_discovery_chains_api.py tests/api/test_research_objective_exploration_api.py -v
pytest -q
ruff check .
```

Results:

- Focused discovery-chain verification: **13 passed in 0.59s**.
- Adjacent research-service and API regression verification: **29 passed in
  1.48s**.
- Complete project suite: **729 passed in 31.01s**.
- Ruff: **All checks passed**.

The complete-suite command used quiet rather than verbose output; this changed
reporting verbosity only, not test selection or execution.

## Verification conclusion

All acceptance criteria are supported by focused and adjacent regression tests,
the complete project suite passes, and Ruff reports no violations. Preferred
elements remain soft during chain generation while strict avoided-element
handling, search bounds, transition validation, deterministic ordering, and
downstream preference ranking remain covered. No regression was observed.
