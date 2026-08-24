# Stack 04 Evidence — Discovery Candidates, Graphs, and Paths

## Scope

Reviewed discovery candidate generation, scoring, explanations, warnings, substitution-path hypotheses, transition validation, edge intelligence, graph construction, traversal, graph algorithms, graph analytics, K-best paths, path ranking, discovery schemas/routes, chemical-formula and periodic-table utilities, and supplied tests.

## Vertical traces

### Candidate generation and scoring

Candidate merges are deterministic, score breakdowns reconcile, unknown composition membership gains no absence benefit, and soft constraints are disclosed. Recommendation stability is already embedded through similarity, but discovery adds a raw-flag bonus again; substitution analysis also bypasses the energy-primary policy (`MG-IA-014`). Correlated source-diversity semantics remain `OBS-015`.

### Formula and symbol validation

Formula membership uses token extraction and tests protect symbol-prefix cases. The authoritative periodic-table normalizer contains all 118 symbols and rejects unknowns. The separate scenario validator checks only lexical shape and accepts nonexistent elements (`MG-IA-013`).

### Transition and edge semantics

Transitions require a strong composition relationship, prevent newly introduced avoided elements, and deliberately permit retained avoided elements. Metadata and reasons disclaim structural and mechanistic validation. Edge plausibility is labelled as an internal composition heuristic. Differing edge/path plausibility constants remain `OBS-013` pending calibration evidence.

### Graph construction and algorithms

Graph nodes and edges are admitted only after transition validation and sorted by stable keys. Branching is capped at six. Normal `build_graph` clamps depth to one while `build_adjacency` honors the requested depth. Weighted shortest path uses the former and silently loses multi-hop reachability, unlike unweighted and K-best algorithms (`MG-IA-015`). Whole-table composition loading and post-build result limiting remain `OBS-014`.

### Analytics and K-best paths

Analytics intentionally builds an undirected graph and permits depth two. Canonical structured node elements feed community summaries. Explicit tied-result secondary keys are absent (`OBS-012`). K-best path enumeration prevents cycles, enforces 100-path and 1000-state internal budgets, and exposes truncation. Path ranking separates path-wide element events from endpoint state and gives unknown endpoint composition no objective credit.

## Test-quality assessment

Graph-builder tests protect validated admission, canonical elements, quality metadata, and edge intelligence. Transition tests establish retained-versus-newly-introduced avoid semantics. K-best tests strongly cover metadata lineage and internal budgets. Analytics tests are mainly shape checks and do not permute ties. The two-hop weighted test mocks out the production graph builder and therefore misses the real depth clamp. No supplied path-ranking test file was available.

## Negative findings

No defect was confirmed merely because graph analytics uses an undirected representation, normal graph depth is operationally capped, or K-best search is incomplete under disclosed budgets. Transition explanations and schemas consistently qualify their heuristic scientific basis.

## Execution limitation

Uploaded modules were inspected directly; the complete checkout and database-backed test environment remain unavailable. Direct helper behavior was reproduced locally where dependencies were unnecessary. Full caller-wide searches and pytest execution were not possible.
