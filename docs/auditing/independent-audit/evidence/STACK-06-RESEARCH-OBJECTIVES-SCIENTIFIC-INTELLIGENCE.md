# Stack 06 Evidence — Research Objectives and Scientific Intelligence

## Scope

Reviewed research-objective exploration, objective-chain orchestration, scientific-pathway analysis, edge intelligence, candidate comparison, chain generation, research-objective schemas, and the scientific-pathways route supplied for the baseline commit.

All eight supplied Python files compiled successfully. Tests and three directly imported research-intelligence collaborators have not yet been supplied, so their internal behavior remains outside this bounded record.

## Vertical traces

### Objective exploration and chains

The objective schema describes preferred elements as an objective input, and exploration declares `prefer_elements: soft_bonus` in every mode. `ResearchObjectiveService` nevertheless passes preferred elements into `DiscoveryChainService`; `_get_next_candidates` rejects each candidate that does not already contain one of them before transition validation or ranking. This converts a stated soft preference into hidden hard preselection at every hop and can remove routes whose later endpoint satisfies the preference (`MG-IA-016`).

Chain exploration is bounded by a three-hop maximum, six candidates per expansion, and a 200-state budget. Search metadata discloses both truncation and the absence of a scientific-completeness guarantee. Strict avoidance explicitly excludes avoided elements from every non-root chain material. Pathway reporting separately exposes path-event and endpoint-state objective satisfaction.

### Scientific pathway analysis

Material quality is bulk-prefetched and reused. Pathway IDs are deterministic material-ID sequences, tied usefulness scores receive shared competition ranks, and structural continuity is explicitly limited to element overlap rather than claimed structural validation.

`_quality_summary` calls `max` over all quality records using nullable `risk_score` values. Unknown risk is intentionally represented by `risk_score = None`; pathways contain at least the root and one candidate. Any unknown score can therefore raise a Python comparison `TypeError`, and a single unknown record would be labelled as the highest-risk material despite lacking numeric evidence (`MG-IA-017`).

### Candidate comparison and edge intelligence

Candidate comparison delegates eligibility and decision semantics to screening, preserves true decision-key ties, orders tied IDs deterministically, and gives unknown risk no favorable numeric explanation. Edge intelligence labels its plausibility as an internal composition heuristic and explicitly reports that the substitution mechanism is unvalidated. The differing plausibility constants across edge and path services remain `OBS-013` pending calibration intent.

## Negative findings

No defect was confirmed merely because exploration and pathway ranking use different scores: they serve different response contracts. Repeated preserve-element credit in exploratory candidate scoring and score-only tie ordering require tests, consumer expectations, and permutation evidence before classification. Formula-based strict-mode checks are consistent with the reviewed parser, although structured element membership would reduce dependence on fallback parsing.

## Evidence still required

- research-objective exploration, objective-service, chain-service, pathway-analysis, edge-intelligence, and candidate-comparison tests;
- `research_evidence_intelligence_service.py`;
- `comparative_research_intelligence_service.py`;
- `endpoint_sensitive_research_ranking_service.py`;
- the route exposing `ResearchObjectiveExplorationService`, if registered;
- router registration and API-contract tests for the research routes.

## Execution limitation

Source compilation and direct semantic traces were completed. Database-backed tests were not executed because the repository checkout and configured test database are unavailable in this workspace.
