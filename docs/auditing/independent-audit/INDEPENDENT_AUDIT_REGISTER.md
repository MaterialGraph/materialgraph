# MaterialGraph Independent Audit Register

## Baseline

Reviewed commit: `a1605e61f72035890692ab4df63ebd2f7b859069`

## Status summary

| Category | Count |
|---|---:|
| Confirmed defects or material risks | 6 |
| Improvements | 2 |
| Open observations | 9 |
| Retired finding identifiers | 4 |
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

## Retired finding identifiers

These identifiers were assigned too early, re-evaluated under the stricter evidence threshold, and retired without reuse.

| Retired ID | Former proposition | Current disposition | Evidence still required |
|---|---|---|---|
| `MG-IA-001` | Package/runtime version conflicts with documented `v1.9.6` | Observation `OBS-001` | Explicit distinction or equivalence between package, API, release, and capability versions |
| `MG-IA-002` | Root and versioned health contracts improperly diverge | Observation `OBS-002` | Deployment probe contract and intended liveness/readiness semantics |
| `MG-IA-005` | First-page Materials Project selection is improperly hidden or nondeterministic | Observation `OBS-004` | Import-selection policy and upstream ordering/reproducibility evidence |
| `MG-IA-006` | Existing Materials Project rows must be refreshed rather than skipped | Observation `OBS-005` | Immutable-snapshot versus refresh/upsert policy and provenance contract |

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

## Improvements

| ID | Title | Priority | Status |
|---|---|---|---|
| `MG-IA-IMP-001` | Repair corrupted multiplication symbols in criticality-test comments | P3 | Proposed |
| `MG-IA-IMP-002` | Document or expose screening decision-ordering semantics | P2 | Proposed |

## Confirmed positive checks

- Model modules compile and are completely imported into Alembic metadata.
- Primary keys, foreign keys, cascade declarations, core uniqueness constraints, and association uniqueness are present.
- Structured composition is validated, normalized, and membership-checked.
- Canonical risk seeding is range-validated, deterministic, idempotent, source-labelled, and rollback-aware.
- Unknown and all-null risk evidence remain numerically unknown.
- Risk and criticality coverage distinguish known, partial, complete, and missing evidence.
- Bulk risk and criticality paths avoid per-material query amplification in the reviewed services.
- Risk-profile latest-year selection is deterministic under `(element_id, year)` uniqueness.
- Candidate screening and substitution use stable material-ID tie-breakers.
- Substitution gives unknown risk no low-risk benefit and explains missing evidence.
- Stability evidence uses energy above hull as primary evidence and the imported flag only as an explicitly incomplete fallback.
- Quality grants no favorable risk bonus unless risk evidence is known and complete.

## Finding record requirements

Every confirmed finding records its affected components, exact evidence, expected and actual behavior, impact, reproducibility, existing and missing tests, recommended remediation scope, caller trace, confidence, priority, and disposition.

## Priority guide

- `P0`: credible catastrophic corruption or invalid system-wide conclusions requiring containment
- `P1`: high-impact correctness, scientific-honesty, determinism, contract, or severe boundedness failure
- `P2`: material but narrower defect or risk with practical impact
- `P3`: limited-impact defect or material risk for normal remediation
