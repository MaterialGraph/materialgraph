# MG-IA-016 — Preferred elements are a hidden hard chain prefilter

- Classification: objective-semantics and hidden-preselection defect
- Priority: P1
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/schemas/discovery.py`
- `app/schemas/research_objective_exploration.py`
- `app/services/research/objective_exploration_service.py`
- `app/services/research/objective_service.py`
- `app/services/discovery/chain_service.py`
- research-objective exploration and scientific-pathway endpoints

## Exact evidence

The exploration response contract declares `prefer_elements` to be `soft_bonus` in balanced, exploratory, and strict modes. `ResearchObjectiveService.generate_chains_for_objective` passes `objective.prefer_elements` into `DiscoveryChainService.get_discovery_chains`.

For every expanded node, `DiscoveryChainService._get_next_candidates` rejects a candidate when preferred elements are requested and the candidate has no intersection with them. This rejection occurs before transition validation, path ranking, and exploration scoring. Because it is applied at every hop, an intermediate without a preferred element cannot lead to a later endpoint that contains it.

## Expected versus actual

A soft preferred-element objective should affect ranking without removing otherwise eligible candidates. The implementation instead makes presence of at least one preferred element a hard per-hop eligibility condition while reporting it as a soft bonus.

## Impact

Scientifically plausible pathways and candidates can be absent without an exclusion reason. Multi-hop searches are especially affected because every intermediate must prematurely satisfy the endpoint preference. Balanced and exploratory modes therefore search a narrower chemistry space than their public policy and explanations state.

## Reproduction

Create a valid two-hop route `A -> B -> C` where `B` lacks preferred element `Na` and `C` contains `Na`. Request `prefer_elements=["Na"]`. `_get_next_candidates` excludes `B`, so `C` is never reached. With no preferred element requested, the same route remains eligible.

## Caller trace

Research-objective exploration calls `ResearchObjectiveService`, and scientific-pathway analysis calls the same service. Both inherit the prefilter through chain generation. The later path-ranking soft score cannot recover candidates removed from the search pool.

## Tests

The relevant tests have not yet been supplied. Missing regression coverage should prove that soft preferences do not change eligibility, including a two-hop route whose preference is satisfied only at the endpoint, and should separately verify strict avoidance behavior.

## Recommended remediation scope

Remove preferred-element filtering from chain eligibility and retain it in deterministic ranking, or explicitly introduce and disclose a separate hard-preference constraint. Add search-metadata counts/reasons for every intentional preselection and end-to-end tests across all exploration modes.
