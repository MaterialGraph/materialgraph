# MG-IA-018 — Research-objective stability and criticality controls are ignored

- Classification: API-contract and objective-semantics defect
- Priority: P1
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/schemas/discovery.py`
- `app/services/research/objective_service.py`
- `app/services/research/objective_exploration_service.py`
- `app/services/research/scientific_pathway_analysis_service.py`
- `app/services/discovery/chain_service.py`
- `app/services/discovery/path_ranking_service.py`
- objective-chain, objective-exploration, and scientific-pathways endpoints

## Exact evidence

`ResearchObjective` publicly accepts `prefer_lower_criticality: bool = True` and `require_stable_materials: bool = False`. The objective, exploration, and scientific-pathway routes accept and return this object.

`ResearchObjectiveService.generate_chains_for_objective` passes only avoid elements, preferred elements, maximum hops, and limit into chain generation. Its filtering uses only preserved elements and target family. Path ranking receives only avoid and preferred elements. Exploration scoring and mode constraints likewise never read either stability/criticality field.

`DiscoveryPathRankingService` always includes the generic `MaterialQualityService.quality_score`; it has no parameters for either objective field. Consequently, criticality-related quality can affect every path regardless of `prefer_lower_criticality`, while `require_stable_materials=True` performs no stability rejection.

A caller-wide search of all supplied files finds these field names in the research stack only in schemas, request payloads, and tests that construct objectives. No research-pipeline consumer implements them.

## Expected versus actual

Setting `require_stable_materials=True` should enforce the disclosed stability constraint using the canonical evidence policy, or the API should not offer the field. Changing `prefer_lower_criticality` should change the documented ranking policy, or the API should identify it as unsupported. Both values currently have no effect on research results.

## Impact

Researchers can believe that unstable candidates were excluded or that lower criticality was intentionally preferred when neither requested behavior occurred. This is a material explainability and scientific-intent failure across all three research-objective endpoints.

## Reproduction

Run the same objective twice while toggling only `require_stable_materials`, including an otherwise eligible unstable material; the service call graph and result remain unchanged. Repeat while toggling only `prefer_lower_criticality`; ranking inputs remain identical and generic quality is applied in both cases.

## Caller trace

The discovery objective-chain and objective-exploration routes call `ResearchObjectiveService`; scientific-pathway analysis calls the same service. All therefore share the ignored controls. The recommendation service implements a separate `prefer_lower_criticality` parameter, but it is not called by this research-objective pipeline.

## Tests

Supplied API and service tests repeatedly construct objectives with `prefer_lower_criticality=True` and `require_stable_materials=False`, but do not compare toggled values or assert stable-only membership. Missing regression coverage should vary each field independently and verify eligibility, ranking, policy metadata, and explanation changes.

## Recommended remediation scope

Define the precise evidence policy for stable-only filtering and lower-criticality preference, thread both controls through every objective pipeline, and expose effective policy metadata. Use canonical stability evidence rather than the imported flag alone, ensure unknown evidence is handled explicitly, and add paired true/false end-to-end tests. If either feature is not supported, reject or remove the field instead of silently accepting it.
