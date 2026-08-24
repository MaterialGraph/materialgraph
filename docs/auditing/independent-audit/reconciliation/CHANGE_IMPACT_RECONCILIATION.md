# Change-Impact Reconciliation

## Evidence reviewed

- Complete `docs/auditing/change-impact/2026-07.md` content supplied as
  `2026-07(1).md` (1,269 lines).
- Complete `docs/auditing/change-impact/2026-08.md` content supplied as
  `2026-08(20260824-115833).md` (669 lines).
- The completed audit register, detailed `MG-AUD-001`–`MG-AUD-094` records,
  July/August resolution ledgers, and frozen independent evidence at commit
  `a1605e61f72035890692ab4df63ebd2f7b859069`.

The change-impact histories are append-only descriptions of intended external
or system-level changes. Their `Production verified`, full-suite, focused-test,
and endpoint statements are historical claims; they were not rerun in this
workspace. They establish intended scope and public semantics, but they do not
by themselves establish that the reviewed commit implements those semantics.

## Scope conclusions affecting independent findings

| Independent finding | Change-impact evidence | Reconciliation consequence |
|---|---|---|
| `MG-IA-009` | The `MG-AUD-059` impact explicitly says missing composition fractions retain the legacy `1.0` fallback. | Confirms that the current fallback is preserved behavior, not a regression of the normalized-composition fix. Its undisclosed quantitative meaning remains a new scientific-evidence-policy defect. |
| `MG-IA-011` | The August reconciliation says neighborhood response limits “bound expansion and preserve graph closure.” | Strengthens the exact contradiction with current code, which can enqueue and expand nodes rejected by the response limit. The impact record has no implementation commit, so it cannot distinguish a later regression from a fix that was never effective in the reviewed code line. |
| `MG-IA-013` | `MG-AUD-093` explicitly covers `avoid_element` and `prefer_element` on all seven discovery GET routes. | Confirms the old fix was deliberately route- and scalar-filter-specific. Scenario recommendations and list-valued scientific inputs were omitted; this is incomplete cross-API scope, not evidence that the seven-route fix regressed. |
| `MG-IA-014` | The single-source stability impact names quality, similarity, and recommendation as consumers; screening constraints are separately described as request filters. | Confirms the policy did not claim discovery or substitution integration. The current downstream bypass is incomplete dependency scope. |
| `MG-IA-015` | The July `MG-AUD-084` impact is specifically the public `DiscoveryTraversalService` bounded path lookup. | Confirms that the weighted graph-algorithm defect is distinct from that remediation. |
| `MG-IA-016` | The August `MG-AUD-016/017` impact expressly says preferred elements remain soft bonuses and strict rejection applies only to avoided elements in non-root chain materials. | Establishes a direct current-contract contradiction: hard prefiltering intermediates that lack a preferred element is not an intentional strict-mode rule. The histories still do not provide commit-level chronology. |
| `MG-IA-017` | The risk impacts establish nullable risk throughout public, scalar, and bulk APIs; endpoint evidence impacts claim coverage propagation. | Strengthens the requirement that downstream pathway summaries accept `None`. The current numeric aggregation remains an incomplete downstream-consumer fix. |
| `MG-IA-018` | The `MG-AUD-045` impact is limited to typed response models, finite output states, and confidence scope; it explicitly says no pathway-generation or scoring change. | Confirms that accepted but ignored research-objective controls were not implemented by this remediation. |
| `MG-IA-019` | The grouped August impact describes “analytical result limits,” but its related resolution is expressly limited to discovery analytical routes. | The general wording does not expand implemented scope. Scenario `top_n` remains an omitted endpoint, not a demonstrated regression. |
| `MG-IA-023` | The graph-job impact explicitly removes public routes and OpenAPI paths while retaining the internal model/service. | Confirms current runtime behavior and makes the root README advertisement stale. No change-impact entry claims that README was updated. |
| `MG-IA-024` | Installation/configuration impact names requirements, setup instructions, the canonical repository, API-key naming, and runtime version authority. | Confirms the remediation's documented setup scope, but does not claim correction of the root README Quick Start. |
| `MG-IA-025` | The multi-element objective impact says every requested avoided and preferred element contributes and responses expose full coverage metadata. | Confirms current runtime behavior and establishes that the project-direction statement describing first-element-only execution is stale. |

For `MG-IA-003`, `004`, `007`, `008`, `010`, `012`, `020`, `021`, and
`026`, the histories add no earlier remediation scope that changes the detailed
crosswalk classification. `MG-IA-021` remains distinct from the API-key naming
fix: no impact entry introduces or removes the advertised `MP_API_URL`.

## Chronology assessment

The histories provide dates and release labels for claimed changes, including:

- `MG-AUD-072` included in the August 18 reconciliation of previously
  remediated impacts;
- `MG-AUD-016/017` recorded on August 19 with preferred elements expressly
  remaining soft; and
- the reviewed repository commit dated August 21.

Those dates show that both claimed behaviors were intended before the reviewed
baseline. They do **not** prove when the contradictory source lines entered the
branch, because the histories do not identify the implementing commit hashes or
show a before/after source diff. Therefore:

- `MG-IA-011` is confirmed as not effective at the reviewed baseline, with
  regression-versus-ineffective-application chronology unresolved; and
- `MG-IA-016` is confirmed as an incomplete complete-pipeline remediation and
  direct semantic recurrence, with the same chronology limitation.

A definitive regression label requires Git history for the relevant
`NeighborhoodService` and `DiscoveryChainService` lines and their tests.

## Documentation synchronization assessment

The histories are specific about additive fields, changed enums, route removal,
configuration names, and setup guides when those artifacts were in scope. They
do not claim updates to:

- the root README graph-job route inventory (`MG-IA-023`);
- the root README Quick Start (`MG-IA-024`); or
- the project-direction document's first-element-only statement
  (`MG-IA-025`).

This is affirmative evidence of remediation-scope omission, not proof that the
runtime fixes failed. The three documentation findings retain their current
classifications.

## Final reconciliation classification

All 21 frozen independent findings now have completed prior-audit mapping,
resolution-effectiveness, and change-impact assessments.

| Classification | Count | Independent IDs |
|---|---:|---|
| Genuinely new | 8 | `003`, `004`, `007`, `008`, `012`, `020`, `021`, `026` |
| Partially effective / incomplete earlier scope | 7 | `011`, `013`, `014`, `016`, `017`, `018`, `019` |
| Related but distinct post-remediation issue | 4 | `009`, `010`, `015`, `024` |
| Earlier runtime remediation effective; stale documentation only | 2 | `023`, `025` |

No independent finding was dismissed solely because an earlier ledger claimed
successful tests or production verification. Conversely, no earlier finding
was reopened where current code retains its remediation and the independent
issue is confined to stale documentation or a distinct caller.

## Remaining reconciliation limitation

Classification is complete. Only the narrower historical question of whether
`MG-IA-011` and `MG-IA-016` are later regressions or ineffective/incomplete
original applications remains unresolved. This does not change their confirmed
current-baseline defect status or remediation priority.
