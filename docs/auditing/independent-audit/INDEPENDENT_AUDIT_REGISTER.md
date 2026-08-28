# MaterialGraph Independent Audit Register

## Frozen-pass status

Complete. Counts below describe the independent pass before reconciliation or
remediation. Current status is recorded in
`remediation/REMEDIATION_REGISTER.md` and `FINAL_AUDIT_CLOSURE.md`.


## Baseline

Reviewed commit: `a1605e61f72035890692ab4df63ebd2f7b859069`

## Status summary

| Category | Count |
|---|---:|
| Confirmed defects or material risks | 21 |
| Improvements | 3 |
| Open observations | 16 |
| Retired finding identifiers | 5 |
| Remediated | 0 |
| Reconciled with `MG-AUD-*` | 0 |

## Confirmed findings

| ID | Title | Classification | Priority | Confidence | Disposition |
|---|---|---|---|---|---|
| `MG-IA-003` | Core-domain migration can fail on a populated predecessor database | Migration correctness and deployment risk | P2 | High | Confirmed |
| `MG-IA-004` | Criticality element ordering is nondeterministic for tied scores | Determinism and API-output risk | P2 | High | Confirmed |
| `MG-IA-007` | Computed risk and criticality outputs omit selected profile source attribution | Explainability and provenance defect | P2 | High | Confirmed |
| `MG-IA-008` | Failed material-import batch can leave partial pending session changes | Transaction-integrity risk | P2 | High | Confirmed |
| `MG-IA-009` | Unknown composition is persisted and computed as equal composition | Scientific correctness and evidence-honesty defect | P2 | High | Confirmed |
| `MG-IA-010` | Sensitivity deltas are inconsistent with baseline risk aggregation | Mathematical and scenario-semantics defect | P1 | High | Confirmed |
| `MG-IA-011` | Neighborhood limit does not bound graph expansion | Boundedness and query-amplification defect | P1 | High | Confirmed |
| `MG-IA-012` | Neighbor ties make bounded neighborhood membership nondeterministic | Determinism and graph-result defect | P2 | High | Confirmed |
| `MG-IA-013` | Multiple scientific APIs accept nonexistent element symbols | API validation and scientific-input defect | P2 | High | Confirmed |
| `MG-IA-014` | Downstream discovery and substitution bypass canonical stability evidence | Cross-service scientific-consistency and scoring defect | P2 | High | Confirmed |
| `MG-IA-015` | Weighted shortest path silently searches only one hop | Graph-algorithm contract and reachability defect | P2 | High | Confirmed |
| `MG-IA-016` | Preferred elements are a hidden hard chain prefilter | Objective-semantics and hidden-preselection defect | P1 | High | Confirmed |
| `MG-IA-017` | Pathway quality summary mishandles unknown risk | Missing-evidence correctness and runtime-reliability defect | P2 | High | Confirmed |
| `MG-IA-018` | Research-objective stability and criticality controls are ignored | API-contract and objective-semantics defect | P1 | High | Confirmed |
| `MG-IA-019` | Scenario ranking accepts negative and unbounded result limits | API validation and bounded-response defect | P2 | High | Confirmed |
| `MG-IA-020` | Chain-derived APIs return success for nonexistent materials | Cross-endpoint resource-semantics defect | P2 | High | Confirmed |
| `MG-IA-021` | Advertised Materials Project API URL setting is silently ignored | Configuration-contract defect | P3 | High | Confirmed |
| `MG-IA-023` | README presents disabled graph-job routes as a current capability | Documentation-to-implementation contract defect | P3 | High | Confirmed |
| `MG-IA-024` | Root README Quick Start omits configuration required by its commands | Setup documentation defect | P3 | High | Confirmed |
| `MG-IA-025` | Vision document incorrectly says objectives execute only first avoid/prefer elements | Documentation-to-implementation semantic defect | P3 | High | Confirmed |
| `MG-IA-026` | Deployment guide never creates the systemd service it operates | Deployment documentation defect | P3 | High | Confirmed |

## Retired finding identifiers

These identifiers were assigned too early, re-evaluated under the stricter evidence threshold, and retired without reuse.

| Retired ID | Former proposition | Current disposition | Evidence still required |
|---|---|---|---|
| `MG-IA-001` | Package/runtime version conflicts with documented `v1.9.6` | Observation `OBS-001` | Explicit distinction or equivalence between package, API, release, and capability versions |
| `MG-IA-002` | Root and versioned health contracts improperly diverge | Observation `OBS-002` | Deployment probe contract and intended liveness/readiness semantics |
| `MG-IA-005` | First-page Materials Project selection is improperly hidden or nondeterministic | Observation `OBS-004` | Import-selection policy and upstream ordering/reproducibility evidence |
| `MG-IA-006` | Existing Materials Project rows must be refreshed rather than skipped | Observation `OBS-005` | Immutable-snapshot versus refresh/upsert policy and provenance contract |
| `MG-IA-022` | Alembic silently falls back to a hard-coded local database target | Retired after import-order correction | `app.core.database` constructs required settings before Alembic URL selection, so missing `DATABASE_URL` fails before the alleged fallback is reachable |

## Open observations

| ID | Observation | Evidence needed |
|---|---|---|
| `OBS-001` | Package metadata reports `0.1.0` while current capabilities are documented as `v1.9.6`. | Canonical versioning and release policy |
| `OBS-002` | `/health` and `/api/v1/health` expose different fields and service-name sources. | Deployment and public API probe contract |
| `OBS-003` | Reviewed health handlers provide liveness only; database readiness expectations are unknown. | Deployment documentation and probe configuration |
| `OBS-004` | Materials Project import requests only one page of 25 stable records per chemical system without an explicit local ordering rule. | Intended curation policy, upstream ordering guarantee, import manifest requirements |
| `OBS-005` | Re-import skips existing `mp_id` rows rather than refreshing them. | Snapshot immutability or update policy |
| `OBS-006` | Computed material-risk API omits unknown-element identities and total counts although internal risk signals contain them. | Endpoint completeness contract and consumers |
| `OBS-007` | Internal risk-signal APIs represent nonexistent IDs and existing zero-element materials identically. | Complete caller trace and accepted input contract |
| `OBS-008` | Maximum-energy screening permits unknown `energy_above_hull` when other stability evidence passes. | Hard-constraint versus fallback-evidence policy |
| `OBS-009` | Partial criticality can improve quality without criticality coverage/completeness appearing in the quality response; sensitivity also omits component-coverage metadata. | Quality and sensitivity evidence policy plus public route contracts |
| `OBS-010` | Family, neighbor, similarity, recommendation, discovery, and substitution candidate pools can grow with all qualifying database materials; response limits are absent or applied only after full-pool work. | Repository-scale measurements, query plans, latency/resource evidence, and intended candidate-pool policy |
| `OBS-011` | Scenario supply-risk scoring uses formula membership and a fixed exposure weight rather than the selected element's stored risk evidence or composition fraction. | Scientific scenario policy establishing whether this endpoint is an explicitly heuristic stress test or a quantitative risk recomputation |
| `OBS-012` | Graph analytics omits explicit secondary keys for tied centralities, equal-size communities, tied hubs, and equal-frequency dominant labels. | Permutation tests and deterministic API-ordering contract |
| `OBS-013` | Edge intelligence and path ranking assign different hard-coded plausibility values to the same transition categories. | Intended distinction between edge plausibility and path-level transition contribution, calibration rationale, and path-ranking tests |
| `OBS-014` | Graph response limits are applied after construction, and each graph build loads the complete material-element association table. | Query plans and scaling measurements at intended dataset size |
| `OBS-015` | Discovery source-diversity bonuses treat family, recommendation, and scenario outputs as independent sources even though the pipelines share evidence and candidates. | Definition and scientific justification of source independence |
| `OBS-016` | Graph-job persistence has safe claim and terminal-transition primitives, but no supplied executor, lease, heartbeat, retry, cancellation, timeout, or stale-`RUNNING` recovery lifecycle; its routes are intentionally not registered publicly. | Worker/scheduler inventory and intended operational lifecycle before graph jobs are enabled |

## Closed observations

| ID | Proposition examined | Disposition | Closing evidence |
|---|---|---|---|
| `OBS-017` | The currently unreachable `strong` evidence-readiness state may indicate a defect. | Closed — intentional policy | Dedicated tests establish that present external-evidence gaps cap readiness at `moderate`, while direct no-gap input is allowed to produce `strong`; the contract reserves the state without falsely emitting it today. |
| `OBS-018` | Chain-derived endpoints may handle nonexistent materials inconsistently. | Closed — promoted to `MG-IA-020` | Family, neighbor, risk, and comparison API tests establish 404 behavior, while direct chain/research traces establish successful empty responses for missing roots. |

## Improvements

| ID | Title | Priority | Status |
|---|---|---|---|
| `MG-IA-IMP-001` | Repair corrupted multiplication symbols in criticality-test comments | P3 | Proposed |
| `MG-IA-IMP-002` | Document or expose screening decision-ordering semantics | P2 | Proposed |
| `MG-IA-IMP-003` | Add a stable tie-breaker to graph-job listing | P3 | Proposed |

## Confirmed positive checks

- Model modules compile and are completely imported into Alembic metadata.
- Primary keys, foreign keys, cascade declarations, core uniqueness constraints, and association uniqueness are present.
- Structured composition is validated, normalized, and membership-checked.
- The structured-composition backfill is dry-run by default, uses no formula inference, validates the complete selected batch before commit, and rolls back all pending corrections on any validation failure.
- Canonical risk seeding is range-validated, deterministic, idempotent, source-labelled, and rollback-aware.
- Unknown and all-null risk evidence remain numerically unknown.
- Risk and criticality coverage distinguish known, partial, complete, and missing evidence.
- Bulk risk and criticality paths avoid per-material query amplification in the reviewed services.
- Risk-profile latest-year selection is deterministic under `(element_id, year)` uniqueness.
- Candidate screening and substitution use stable material-ID tie-breakers.
- Substitution gives unknown risk no low-risk benefit and explains missing evidence.
- Stability evidence uses energy above hull as primary evidence and the imported flag only as an explicitly incomplete fallback.
- Quality grants no favorable risk bonus unless risk evidence is known and complete.
- Family outputs explicitly identify composition heuristics and disclaim validated structural-family or substitution-mechanism claims.
- Family, similarity, and recommendation result ordering includes stable material-ID tie-breakers.
- Similarity and recommendation disclose their full-pool-before-limit ranking policies and do not double-count stability.
- Scenario explanations reconcile exactly to the numeric scenario delta.
- Scenario preset ranking preserves unknown risk as unknown and explains the missing evidence.
- Graph nodes, edges, and adjacency use explicit deterministic construction order.
- Graph construction validates transitions before admitting nodes and preserves edge-node closure.
- K-best enumeration has explicit path/state budgets and discloses search truncation.
- Path explanations distinguish path-wide element events from endpoint composition state.
- Path ranking gives missing endpoint composition no objective credit and preserves weak intermediates as quality bottlenecks.
- Graph-job claiming uses deterministic FIFO ordering and PostgreSQL `FOR UPDATE SKIP LOCKED`.
- Graph-job terminal transitions are atomic, state-guarded, and protected against competing completion/failure.
- Graph-job routes are deliberately absent from the public router and OpenAPI schema.
- Research pathway reporting distinguishes path-wide element events from endpoint-state satisfaction.
- Research chain search is explicitly bounded and discloses truncation and incomplete scientific coverage.
- Candidate comparison preserves true decision-key ties and deterministically orders tied candidate IDs.
- Candidate comparison preserves unknown risk as `None` and distinguishes missing materials from constraint-filtered candidates at the API boundary.
- Scientific pathway claims limit preservation to element overlap and disclaim structural validation.
- Research evidence explicitly distinguishes internal deterministic support from unavailable external validation.
- Comparative intelligence preserves score ties and pathway identity rather than manufacturing a unique winner.
- Endpoint-sensitive ranking preserves original scores and admits risk-based differentiation only for known, complete evidence.
- Scientific-score comparisons consistently normalize producer values to two decimal places without mutating source opportunities.
- Current external-evidence gaps intentionally cap research readiness at `moderate`; weak internal support remains `limited`.
- Research and scientific-principles documentation clearly separates deterministic internal support from novelty, feasibility, physical validity, and external scientific validation.
- Planned knowledge, scientific-compute, orchestration, document-storage, and high-performance graph capabilities are labeled as future rather than current implementation.
- The dedicated getting-started guide configures required database and Materials Project credentials before commands that consume them, and its five example API paths match mounted routes.
- Technical notes accurately describe the supplied `httpx2`/`httpcore2` compatibility dependencies and PostgreSQL-plus-NetworkX graph implementation.

## Finding record requirements

Every confirmed finding records its affected components, exact evidence, expected and actual behavior, impact, reproducibility, existing and missing tests, recommended remediation scope, caller trace, confidence, priority, and disposition.

## Priority guide

- `P0`: credible catastrophic corruption or invalid system-wide conclusions requiring containment
- `P1`: high-impact correctness, scientific-honesty, determinism, contract, or severe boundedness failure
- `P2`: material but narrower defect or risk with practical impact
- `P3`: limited-impact defect or material risk for normal remediation
