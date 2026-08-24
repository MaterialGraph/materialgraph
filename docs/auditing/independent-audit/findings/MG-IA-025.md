# MG-IA-025 — Vision document incorrectly says objectives execute only first avoid/prefer elements

- Classification: documentation-to-implementation semantic defect
- Priority: P3
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `docs/architecture/what_should_be_materialgraph.md`, objective-semantics section
- `app/services/research/objective_service.py`
- `app/services/research/objective_exploration_service.py`
- `app/services/discovery/chain_service.py`
- `app/services/discovery/path_ranking_service.py`

## Exact evidence

The document states that reviewed objective-chain execution “currently forwards only the first avoid element and first prefer element into chain generation and path ranking.” Current code passes `objective.avoid_elements` and `objective.prefer_elements` as complete collections into chain generation and path ranking. `DiscoveryChainService` normalizes them into sets and uses collection membership; objective exploration iterates every prefer and avoid element. No `[0]` selection exists on this path.

## Expected versus actual

A current-state architecture/vision document should accurately separate implemented limitations from future work. It currently describes a remediated or obsolete limitation as active and proposes future choices around it.

## Impact

The stale statement can trigger unnecessary schema contraction or duplicate remediation, mislead researchers about multi-element objective behavior, and corrupt roadmap prioritization.

## Reproduction and callers

Trace `ResearchObjectiveService.generate_chains_for_objective`: complete lists are passed to `DiscoveryChainService.get_discovery_chains` and `DiscoveryPathRankingService.rank_path`. Trace exploration scoring: loops cover each element. Compare those calls with the document's first-element statement.

## Tests

Existing element-membership/objective tests exercise list-shaped fields but do not include a focused two-avoid/two-prefer end-to-end regression proving every requested element contributes. That regression remains worthwhile even though the direct caller trace disproves the documentation statement.

## Recommended remediation scope

Update the section to describe full collection propagation and retain only evidence-backed remaining limitations, including hidden preferred-element preselection (`MG-IA-016`) and ignored stability/criticality controls (`MG-IA-018`). Add an end-to-end multi-element objective test.
