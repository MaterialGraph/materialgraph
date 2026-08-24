# Resolution Effectiveness Assessment

## Evidence reviewed

- Complete July 2026 append-only resolution ledger.
- Complete August 2026 append-only resolution ledger.
- Authoritative completed `AUDIT_REGISTER.md`.
- Four detailed `MG-AUD-001`–`MG-AUD-094` range files.
- Frozen independent implementation evidence at commit
  `a1605e61f72035890692ab4df63ebd2f7b859069`.

The ledgers establish the intended remediation mechanism, affected components,
test claims, scope qualifications, and deployment checks. Test-count and
production-verification statements are historical evidence from the ledgers;
they were not independently rerun in this workspace.

## Classification vocabulary

- **Effective in reviewed scope:** current code independently retains the old
  remediation behavior.
- **Partially effective / incomplete scope:** the old change remains effective
  where implemented, but the same contract is still violated in omitted
  callers, routes, or downstream consumers.
- **Not effective at reviewed baseline:** current code exhibits the same
  behavior the resolution says was removed. Commit history is needed to
  distinguish later regression from an ineffective original application.
- **Related but distinct:** the current issue resembles an older defect family
  but occurs in a different component, model, or contract not covered by the
  old remediation.
- **Genuinely new candidate:** no old finding or resolution scope covers the
  current issue.

## Finding-by-finding assessment

| Independent finding | Resolution evidence | Effectiveness assessment | Reconciliation classification |
|---|---|---|---|
| `MG-IA-003` | No resolution covers the non-null `materials.source` upgrade on populated predecessor data. `MG-AUD-060/061` mention a different enum-downgrade follow-up only. | Not applicable | Genuinely new candidate |
| `MG-IA-004` | `MG-AUD-032/053/062` add tie/evidence ordering in family, discovery, and similarity. None addresses element ordering inside criticality responses. | Old fixes may be effective in their own components; no coverage here | Genuinely new deterministic-output candidate |
| `MG-IA-007` | `MG-AUD-021–025` adds evidence basis, dimensions, aggregation, and coverage; `MG-AUD-028/029` propagates origin and coverage. The ledger does not propagate each selected persisted profile's `source`. | Existing evidence metadata is effective but does not provide row/dataset attribution | Genuinely new provenance candidate |
| `MG-IA-008` | Import remediations cover structured fractions and normalized membership, not exception rollback or transaction ownership. | Not applicable | Genuinely new transaction-integrity candidate |
| `MG-IA-009` | `MG-AUD-001` fixes Materials Project structured composition and backfills records. `MG-AUD-059` explicitly preserves the legacy `1.0` fallback when weights are unavailable. | Structured-import remediation is effective; the independent defect concerns a deliberately preserved, undisclosed quantitative fallback | Related residual behavior; new scientific-evidence policy defect rather than regression |
| `MG-IA-010` | `MG-AUD-067` makes unknown sensitivity nullable. `MG-AUD-069` separates component baselines by averaging available element-level component values. It does not recompute canonical element-risk and material-risk aggregation after perturbation. | Old null-safety and dimension separation are effective; quantitative parity with screening remains outside their mechanism | Related but distinct post-remediation mathematical defect |
| `MG-IA-011` | `MG-AUD-072` claims the response limit is applied during node selection/expansion and cites tests that bound descendant work. Current code queues and expands nodes rejected by the limit; supplied tests state the same bounded-expansion contract and should fail. | **Not effective at reviewed baseline** | Exact recurrence; regression-versus-failed-application chronology pending |
| `MG-IA-012` | Family/discovery tie-breaker resolutions do not change `MaterialNeighborService` or neighborhood edge ordering. `MG-AUD-072` says deterministic ordering is preserved but does not add the missing neighbor/edge final keys. | No applicable remediation | Genuinely new bounded-membership determinism candidate |
| `MG-IA-013` | `MG-AUD-093` explicitly applies canonical 118-symbol validation to seven discovery GET routes and both scalar filter parameters. Current discovery routes retain that behavior. Scenario recommendation and list-valued screening/comparison/objective fields are outside the recorded scope. | Effective for the seven discovery routes; incomplete across equivalent public scientific inputs | Partially effective / incomplete cross-API scope |
| `MG-IA-014` | `MG-AUD-027` centralizes energy-primary stability for quality, similarity, and recommendation, and prevents recommendation from reapplying inherited stability. Discovery and substitution are absent from affected components and still use raw `is_stable`; discovery re-adds stability after recommendation. | Effective through recommendation, incomplete in downstream consumers | Partially effective / incomplete dependency scope |
| `MG-IA-015` | `MG-AUD-084` changes `DiscoveryTraversalService.get_path()` from hard-coded one-hop/direct-edge lookup to bounded BFS. The independent defect is `DiscoveryGraphAlgorithmsService.weighted_shortest_path()` using a graph builder that clamps effective depth to one. | The old public traversal fix is a different path and is not contradicted by this finding | Related but distinct weighted-algorithm defect; not a recurrence of `MG-AUD-084` |
| `MG-IA-016` | `MG-AUD-016/017` declares preferences `soft_bonus` in all modes and says preferred elements remain soft. Current `DiscoveryChainService` removes every candidate/intermediate lacking a preferred element before scoring. | **Not effective across the complete chain-generation pipeline** | Direct semantic recurrence caused by incomplete dependency/search-pool scope; chronology pending |
| `MG-IA-017` | `MG-AUD-025` makes risk nullable; `MG-AUD-028/029` propagates risk completeness into quality and lists pathway-analysis tests. Current pathway quality summary applies numeric `max` to nullable risk and can fail or mislabel it. | Nullable evidence remains effective upstream; downstream summary is not null-safe | Partially effective / incomplete downstream-consumer remediation |
| `MG-IA-018` | Original `MG-AUD-045` explicitly lists objective contract/validation concerns, but its resolution is limited to typed scientific-pathway response structures and finite output states. It does not implement or remove `prefer_lower_criticality` or `require_stable_materials`. `MG-AUD-034` merely says research objectives retain an independently explicit policy. | Response typing is effective; accepted objective controls remain semantically unimplemented | Partially effective / unresolved original contract scope |
| `MG-IA-019` | `MG-AUD-094` resolution explicitly bounds **discovery analytical routes**. It does not list scenario ranking or `ScenarioRankingRequest.top_n`. Current discovery bounds remain favorable, while scenario `top_n` is unconstrained. | Effective for recorded discovery routes; old broad title overstates implemented endpoint coverage | Partially effective / endpoint omitted from remediation scope, not evidence of regression |
| `MG-IA-020` | `MG-AUD-044` distinguishes missing versus filtered comparison candidates; `MG-AUD-045` types pathway responses. Neither defines missing-root behavior for chain, objective, or scientific-pathway routes. | Not applicable | Genuinely new resource-semantics candidate |
| `MG-IA-021` | `MG-AUD-057` standardizes `MATERIALS_PROJECT_API_KEY`. No resolution introduces or removes the separately advertised `MP_API_URL`. | API-key remediation is effective but unrelated to endpoint URL configuration | Genuinely new configuration-contract candidate |
| `MG-IA-023` | `MG-AUD-092` removes graph-job routes and requires 404/OpenAPI absence. Current router and tests preserve this exactly. README nevertheless advertises graph-job routes as current. | Runtime/security-surface remediation effective; documentation not synchronized | New stale-documentation collateral, not runtime regression |
| `MG-IA-024` | `MG-AUD-056–058` fixes checkout installation, API-key naming, version authority, and dedicated getting-started/deployment guides. The root README Quick Start is not listed and still omits required configuration. | Earlier listed setup paths are effective; root Quick Start remains outside scope | Related but distinct/incomplete documentation coverage |
| `MG-IA-025` | `MG-AUD-009` propagates complete avoid/prefer collections and verifies multi-element behavior. Current code preserves that runtime change. The vision document still says only first elements execute. | Runtime remediation effective | Stale documentation only; no runtime regression |
| `MG-IA-026` | No setup/deployment resolution supplies installation of the named systemd unit. | Not applicable | Genuinely new deployment-documentation candidate |

## Refined reconciliation counts

These counts cover all 21 independently confirmed findings after resolution
ledger review. Change-impact and commit chronology are still pending.

| Classification | Count | Independent IDs |
|---|---:|---|
| Genuinely new candidate | 8 | `003`, `004`, `007`, `008`, `012`, `020`, `021`, `026` |
| Partially effective / incomplete earlier scope | 7 | `011`, `013`, `014`, `016`, `017`, `018`, `019` |
| Related but distinct post-remediation issue | 4 | `009`, `010`, `015`, `024` |
| Earlier runtime remediation effective; stale documentation only | 2 | `023`, `025` |

Within the seven incomplete-scope items, `MG-IA-011` is the clearest exact
same-behavior recurrence. `MG-IA-016` directly contradicts the declared
soft-preference policy. The others establish omitted routes, callers, or
semantic fields rather than necessarily reintroducing code that was once
correct in the same location.

## Resolution claims independently supported by current code

The current review supplies affirmative evidence that the following earlier
remediations remain effective within their documented implementation scope:

- `MG-AUD-001`: structured composition fractions are normalized and persisted;
- `MG-AUD-002/003/008/021–025/028–029/062/064–070`: unknown and partial risk
  and criticality are generally nullable, coverage-aware, directionally
  correct, and not favorably ranked in the reviewed primary consumers;
- `MG-AUD-009`: full multi-element objective collections propagate at runtime;
- `MG-AUD-014/015/050`: path continuity, path events, and endpoint state are
  distinguished;
- `MG-AUD-018–020`: family and substitution semantics are qualified as
  composition heuristics and Mg is not an alkali metal;
- `MG-AUD-027`: energy-primary stability is effective through quality,
  similarity, and recommendation;
- `MG-AUD-030–035/040–044/046–048/053`: bounded-pool disclosure, deterministic
  family/candidate ordering, complete-pool recommendation evaluation,
  causal-prefix attribution, comparison availability, and bulk-loading changes
  remain visible in their reviewed scopes;
- `MG-AUD-060/061/063/071/073/078/080–083/085`: graph-job atomicity, graph
  closure/truncation, bulk loading, rejected-node exclusion, K-best budgets,
  subgraph filtering, and tie semantics remain present where independently
  inspected;
- `MG-AUD-086–093`: endpoint family/structured membership, evidence readiness,
  explanation provenance, route validation, community response models,
  graph-job route removal, and discovery symbol validation remain present.

This list does not claim independent execution of the historical test suites or
production probes. It records static current-code agreement with their stated
mechanisms.

## Resolution-ledger quality observations

- The ledgers consistently separate scientific validation from engineering
  verification and frequently qualify fixture versus endpoint evidence.
- Scope qualifications under `MG-AUD-002`, `003`, `015`, `051`, `060`, and
  `061` are useful and prevent overclaiming.
- Several grouped August resolutions are much narrower than their register
  titles. `MG-AUD-094` is the clearest example: the title says analytical
  endpoints generally, while the resolution explicitly covers discovery
  analytical routes only. This scope difference allowed scenario ranking to
  remain unbounded.
- Historical full-suite pass counts are not proof that the current snapshot
  passes. `MG-IA-011` demonstrates why implementation inspection remains
  necessary: its current code contradicts both the claimed `MG-AUD-072`
  mechanism and the supplied bounded-expansion test expectations.

## Remaining evidence before final reconciliation

The July and August change-impact histories are still needed to:

- confirm which remediations were intended to change public behavior;
- identify whether current contradictory behavior was introduced after the
  recorded fix;
- distinguish regression from an original remediation that never covered the
  complete caller path;
- verify whether documentation was expected to be updated with route removal,
  setup changes, and multi-element objective behavior.

Commit-level chronology would be required for a definitive “regressed after
fix” label for `MG-IA-011` and `MG-IA-016`. Without it, the evidence supports
“not effective at the reviewed baseline” and “incomplete complete-pipeline
scope,” respectively.
