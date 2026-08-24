# Detailed Finding Crosswalk

## Purpose and evidence state

This crosswalk compares the 21 frozen, independently confirmed `MG-IA-*`
findings with the complete detailed records for `MG-AUD-001`–`MG-AUD-094`.
It uses:

- the completed `AUDIT_REGISTER.md` as authoritative for current old-audit
  status;
- the four detailed range files as authoritative for original scope, expected
  behavior, and any embedded resolution narrative;
- the frozen independent finding records as evidence of current behavior at
  commit `a1605e61f72035890692ab4df63ebd2f7b859069`.

Resolution and change-impact ledgers have not yet been reviewed. Therefore,
labels such as “candidate regression,” “candidate incomplete remediation,” and
“candidate new finding” are provisional. No final remediation-effectiveness
decision is made here.

## Status-source consistency

The four detailed files correctly state that the completed register is the
authority for status. This matters because:

- `MG-AUD-010` and `MG-AUD-026` appear as resolved in their detailed records
  but are `Accepted behavior` in the authoritative register;
- `MG-AUD-072`, `073`, `081`–`083`, `085`, and `094` retain original
  `Confirmed` text without embedded resolution narratives, while the register
  marks them `Remediated`.

These are not treated as audit defects because the documents explicitly assign
status authority to the register. They mean the resolution ledgers are
essential before evaluating those remediations.

## Crosswalk

| Independent finding | Earlier finding relationship | Scope comparison | Provisional disposition before resolution-ledger review |
|---|---|---|---|
| `MG-IA-003` — populated-predecessor migration failure | No matching `MG-AUD-*` scope found | Earlier graph-job lifecycle text mentions a separate enum-downgrade follow-up, but no old finding covers adding a non-null material column to populated predecessor data | Candidate genuinely new finding |
| `MG-IA-004` — tied criticality-element ordering | Related to `MG-AUD-032`, `053`, and `062`, but not the same component or decision | Earlier work corrected family/discovery ordering and unknown-criticality preference; it did not specify ordering inside the public criticality element list | Candidate genuinely new deterministic-output finding |
| `MG-IA-007` — selected risk-profile source omitted | Related to `MG-AUD-021`–`024` and `029` | Earlier work disclosed shared evidence dimensions, aggregation, and coverage, but the detailed records do not require the selected persisted profile's `source` to travel with computed outputs | Candidate genuinely new provenance gap |
| `MG-IA-008` — failed import leaves pending session changes | No matching `MG-AUD-*` scope found | Earlier import findings address fractions, normalized duplicate membership, dependency setup, and seed data; none defines failure transaction ownership or rollback | Candidate genuinely new transaction-integrity finding |
| `MG-IA-009` — unknown composition becomes equal composition | Directly related to `MG-AUD-001` and `MG-AUD-059` | `MG-AUD-001` corrected universal `fraction=1.0` import behavior for structured composition. `MG-AUD-059` explicitly says the legacy unknown-weight fallback was preserved. The independent finding isolates that preserved fallback and its undisclosed quantitative use | Candidate incomplete remediation / narrower residual of `MG-AUD-001`; ledger required |
| `MG-IA-010` — sensitivity deltas bypass canonical aggregation | Related to `MG-AUD-067` and `069`, but mathematically distinct | Earlier remediation made unknown values safe and separated supply/geopolitical component baselines. The independent finding shows the perturbation delta still does not flow through the canonical per-element and per-material means used by screening | Candidate new post-remediation mathematical defect or incomplete sensitivity-model remediation |
| `MG-IA-011` — neighborhood limit does not bound expansion | Exact correspondence with `MG-AUD-072` | Same service, response limit, traversal work, and small-response/broad-computation behavior | Candidate regression or ineffective remediation; resolution ledger decisive |
| `MG-IA-012` — tied neighbor order changes bounded membership | Related to `MG-AUD-031`, `032`, and `053`, but distinct component | Earlier deterministic tie fixes cover family and discovery candidate ordering. The neighbor-ranking and neighborhood-edge keys remain outside those stated scopes | Candidate genuinely new bounded-membership determinism finding |
| `MG-IA-013` — multiple APIs accept nonexistent symbols | Expanded correspondence with `MG-AUD-093` | `MG-AUD-093` remediation explicitly covers shared validation on seven discovery GET routes. Those routes remain favorable. Scenario recommendation plus list-valued screening, comparison, and research-objective contracts were not included and still accept invalid symbols | Earlier remediation effective in stated discovery scope but incomplete at the cross-API domain-contract level |
| `MG-IA-014` — downstream stability policy bypass | Expanded correspondence with `MG-AUD-027` | `MG-AUD-027` centralized energy-primary stability semantics for quality, similarity, and recommendation and prevented repeated recommendation credit. Discovery adds another raw-flag bonus and substitution independently uses the raw flag | Candidate incomplete cross-service remediation of `MG-AUD-027` |
| `MG-IA-015` — weighted shortest path remains one-hop | Exact correspondence with `MG-AUD-084` | Both describe a hop-accepting discovery path lookup that searches only direct connectivity. The present cause is the production graph builder's effective-depth clamp, which the old controlled search tests may not have exercised | Candidate regression or incomplete integration remediation; ledger/test diff required |
| `MG-IA-016` — preferred elements are a hidden hard prefilter | Direct semantic conflict with `MG-AUD-016` and `017`; also related to `MG-AUD-030` | Earlier resolution declares preferred elements soft bonuses in all exploration modes and strict rejection only for avoided elements. Current chain expansion excludes every intermediate lacking a preferred element before ranking | Candidate regression or incomplete search-pool remediation with high correspondence |
| `MG-IA-017` — unknown risk breaks pathway quality summary | Related to `MG-AUD-025`, `029`, `067`, and `088`, but a distinct downstream failure | Earlier work preserves nullable risk, propagates coverage, and prevents favorable readiness. Scientific pathway summary still applies numeric `max` to nullable risk and can fail or mislabel unknown as highest risk | Candidate genuinely new downstream unknown-evidence defect |
| `MG-IA-018` — objective stability/criticality controls ignored | Partial correspondence with `MG-AUD-045`; related to `MG-AUD-027` and `034` | `MG-AUD-045` identifies objective-contract semantics and open validation, but its recorded resolution focuses on response typing. Current public objective fields remain accepted and returned without execution. Earlier lower-criticality policy says research objectives retain explicit policy, which current caller trace does not support | Candidate incomplete semantic remediation / unresolved contract scope from `MG-AUD-045` |
| `MG-IA-019` — scenario `top_n` negative/unbounded | Exact subset of `MG-AUD-094` | Same unconstrained analytical limit, negative slicing, and unbounded response behavior at scenario ranking | Candidate regression or endpoint omitted from remediation; resolution ledger decisive |
| `MG-IA-020` — missing material yields successful empty research result | Related generally to `MG-AUD-044` and `045`, but no same scope | Earlier comparison distinguishes missing versus filtered candidates and strengthens response types. No old finding defines missing-root semantics for chain/objective/pathway routes | Candidate genuinely new cross-endpoint resource-semantics finding |
| `MG-IA-021` — `MP_API_URL` silently ignored | No correspondence with `MG-AUD-057` beyond setup/configuration area | `MG-AUD-057` aligns the API-key name. It does not advertise, type, or consume a configurable Materials Project base URL | Candidate genuinely new configuration-contract finding |
| `MG-IA-023` — README advertises disabled graph-job routes | Consequential relationship to `MG-AUD-092` | `MG-AUD-092` intentionally removes graph-job routes from the public API. Current tests and router preserve that remediation, but README current-capability text still advertises the routes | Runtime remediation appears effective; candidate new/stale documentation collateral |
| `MG-IA-024` — root Quick Start omits required configuration | Related to `MG-AUD-056` and `057`, but distinct setup path | Earlier work corrects checkout installation and API-key naming. The dedicated getting-started guide is correct, but the root Quick Start still runs migration/import/startup without required database and API-key setup | Candidate new or incomplete documentation remediation localized to root README |
| `MG-IA-025` — vision document reports old first-element limitation | Exact historical correspondence with `MG-AUD-009` | Current runtime passes full avoid/prefer collections, consistent with the old remediation. Only the vision/current-state document still describes the pre-remediation limitation | Earlier runtime remediation appears effective; confirmed stale documentation, not runtime regression |
| `MG-IA-026` — deployment guide omits systemd unit creation | No matching `MG-AUD-*` scope found | Earlier setup findings cover checkout selection, API-key naming, and version authority; none supplies the missing service-unit installation workflow | Candidate genuinely new deployment-documentation finding |

## Preliminary category counts

These counts describe the 21 independent findings before ledger review; they
are not final reconciliation outcomes.

| Preliminary category | Count | Independent IDs |
|---|---:|---|
| Exact or direct high-overlap recurrence/conflict | 5 | `011`, `015`, `016`, `019`, `025` |
| Expanded or residual earlier scope | 4 | `009`, `013`, `014`, `018` |
| Related subject, materially distinct defect | 4 | `010`, `017`, `023`, `024` |
| No matching earlier scope found / candidate genuinely new | 8 | `003`, `004`, `007`, `008`, `012`, `020`, `021`, `026` |

`MG-IA-025` is included in direct correspondence even though current runtime
evidence supports the earlier fix; its independent defect is stale
documentation. `MG-IA-023` is categorized as related/distinct because route
removal appears preserved while capability documentation is stale.

## Confirmed favorable persistence of earlier work from current code

The detailed old scopes allow several favorable judgments without relying on a
status label alone:

- Full multi-element objective collections are propagated at runtime, preserving
  the core `MG-AUD-009` remediation; only documentation is stale (`MG-IA-025`).
- Discovery GET routes use the canonical 118-symbol validation introduced for
  `MG-AUD-093`; the independent defect lies in other public inputs
  (`MG-IA-013`).
- Graph-job public routes remain disabled as required by `MG-AUD-092`; the
  independent issue is the README capability claim (`MG-IA-023`).
- Atomic graph-job claiming and guarded terminal transitions described by
  `MG-AUD-060` and `061` are present and were independently recorded as
  positive checks.
- Explicit-empty structured composition membership remains authoritative in the
  reviewed pathway/family logic, consistent with `MG-AUD-086` and `087`.
- K-best transition validation, graph node/edge closure, and internal search
  budgets described by `MG-AUD-077`, `078`, `080`, and `082` were independently
  observed as favorable behavior in their reviewed scopes.
- Research evidence/readiness preserves the external-evidence boundary and caps
  current readiness at `moderate`, consistent with `MG-AUD-028` and `088`.

These favorable checks will be tied to exact remediation records after the
resolution ledgers are supplied.

## Old findings not reopened by the independent pass

Absence of a new independent defect is not proof for every old remediation.
However, the independent pass recorded favorable behavior corresponding to
many earlier areas, including composition normalization, nullable risk,
criticality direction, evidence coverage, family taxonomy/qualification,
scenario explanation arithmetic, deterministic candidate ordering, graph
closure, bounded K-best enumeration, endpoint/path-event separation, tie-aware
comparison, and evidence-readiness qualification.

Final resolution-by-resolution effectiveness requires the linked July/August
ledger entries and regression evidence. This crosswalk must not convert silence
into a “verified effective” conclusion.

## Next evidence required

Provide:

1. `resolutions/2026-07.md`;
2. `resolutions/2026-08.md`;
3. the corresponding July/August change-impact records.

The next pass will assign, for each mapped independent finding:

- correspondence status;
- earlier remediation mechanism;
- current effectiveness result;
- regression versus incomplete original scope;
- genuinely new versus previously covered status;
- missing regression coverage and next remediation boundary.
