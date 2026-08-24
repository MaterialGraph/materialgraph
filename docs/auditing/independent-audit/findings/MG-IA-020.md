# MG-IA-020 — Chain-derived APIs return success for nonexistent materials

- Classification: cross-endpoint resource-semantics defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/services/discovery/chain_service.py`
- `app/services/research/objective_service.py`
- `app/services/research/objective_exploration_service.py`
- `app/services/research/scientific_pathway_analysis_service.py`
- discovery objective-chain, objective-exploration, and scientific-pathway routes
- missing-material API tests

## Exact evidence

`DiscoveryChainService.get_discovery_chains` returns an empty response with `mp_id=None`, `base_formula=None`, and `chains=[]` when the root material does not exist. The basic chain route returns that response directly. Objective-chain generation consumes it and returns an empty objective result without checking `mp_id`; objective exploration and scientific-pathway analysis consume the same result and also return successful empty analyses.

In contrast, supplied API tests require 404 for nonexistent materials on material-family, material-neighbor, material-risk, and candidate-comparison endpoints. Family/neighbor routes use the shared `ensure_material_found` helper. Candidate and other reviewed material routes likewise apply explicit not-found handling.

The scientific-pathway service test explicitly characterizes missing ID `999999` as an empty result, confirming that this is reachable behavior rather than hypothetical dead code.

## Expected versus actual

A material-scoped API should distinguish a nonexistent root resource from an existing material with no related chains or research opportunities. Most reviewed material endpoints return 404; chain-derived endpoints instead return HTTP 200 with empty data for both states.

## Impact

Clients cannot distinguish invalid/stale material identifiers from scientifically valid searches that found no opportunity. This can produce misleading “no candidates/pathways” conclusions, inconsistent UI behavior, and unreliable workflow state.

## Reproduction

Request chain-derived analysis for a missing ID such as `999999`. Chain generation returns its empty sentinel; objective and research services propagate it without raising. Compare with `/materials/999999/families`, `/materials/999999/neighbors`, or `/material-risks/999999`, which return 404 under supplied tests.

## Caller trace

The empty sentinel originates in `DiscoveryChainService._empty_response`. It reaches the discovery-chain route directly and flows through `ResearchObjectiveService` into objective exploration and `ScientificPathwayAnalysisService`. None of those callers invokes the shared material-found helper.

## Tests

Existing service tests assert that missing chain and scientific-pathway roots are safe empty results. Supplied family, neighbor, risk, and comparison API tests assert 404. Missing regression coverage should establish one uniform API policy and separately test existing materials with genuinely empty results.

## Recommended remediation scope

Define the API-wide resource policy and enforce it at route boundaries using a shared typed result or `ensure_material_found`-equivalent check. Preserve safe empty service results if useful internally, but map missing roots to 404 before response serialization. Add parity tests across chain, objective-chain, objective-exploration, scientific-pathway, family, neighbor, risk, and graph endpoints.
