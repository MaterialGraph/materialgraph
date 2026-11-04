# SRQ-01 PR-B3 report and AC11 rerun

| Field | Value |
|---|---|
| Date | 2026-11-04 |
| Branch | `srq-01-pr-b3` |
| Spec | SRQ-01 S2 rev 3.12 (R2, R7.1, AC7, AC12, AC11) |
| Status | Implementation complete; AC11 rerun passed; merge pending review. Not deployed: production remains on `release-3` until PR-B1–B3 are qualified together (S4) |

## 1. What PR-B3 changes (objective-aware requests only)

- **R2 admission sequence** at each expansion, applied after eligibility, MP-ID ordering (B1) and grouping (B2):
  1. preferred exact analogs (one per preferred element, alphabetical, covered rule);
  2. existing reservation for still-uncovered preferred elements;
  3. remaining exact-analog groups, up to 4 per expansion in total;
  4. general fill.
- **Introduced-Avoid pre-check:** an exact analog that would introduce an avoided element gets no priority and stays an ordinary candidate.
- Admitted candidates are returned in admission order.
- **Reporting:** `expansions` lists every objective-aware expansion with groups found, groups admitted and excluded groups (`display_formula`, `member_mp_ids`, `reason` `cap` or `efa_budget`); `excluded` is typed (`ExcludedEfaGroup`) within contract version 1; `admission_reporting_available: true`; a limitation states that exact analogs are prioritised during exploration and no score changes.
- `reject_introduced_avoided` is threaded to admission and included in the admission cache key.

Unchanged: frozen requests (all `srq01_pr0` golden tests pass without regeneration), scores, score formulas and weights, `family_service`, the legacy path, shared Discovery schemas. S-3 holds (no `alkali_substitution` in `objective_exploration_service.py`); new text passes S-5.

## 2. Verification (local, CI-equivalent database built from the repository: migrations, seeds, reference data)

- Backend suite before snapshot regeneration: 5 expected failures (objective-aware snapshots for Case Study 01 and Q6, full snapshots for all three), 1,467 passed. All frozen golden, PR-B1 permutation and PR-B2 grouping tests passed.
- New tests (`tests/services/discovery/test_admission_sequence.py`, 6): preferred exact analog admitted first and covering its element (AC12 i); preferred element without an analog keeps its reservation (AC12 ii); groups beyond the budget reported as `efa_budget` (AC12 iii); cap reached during step 3 reported as `cap` (AC12 iv); analog introducing an avoided element gets no priority (AC7); without analogs, reservation then order.
- Report tests updated: admission flag `true`, per-expansion invariants, new limitations, S-5 scan including them.
- `srq01_pra` regeneration (`b3_snapshots.py`, self-checked derivation): on the reference data, ranked candidates and returned chains are **identical** in all three cases; AC8b PASS; `distinct_candidates_discarded_by_expansion_limit` +1 for Case Study 01 (6 → 7) and Q6 (11 → 12). Expansion reports show exact-analog groups admitted at LiFePO₄ (NaFePO₄), at LiFeP₂O₇ (its Na analog) and at LiMnO₂ (Q6).

## 3. Effect on the production-equivalent database (`materialgraph_test_mg_de_007`)

With B1–B3, Case Study 01 in Balanced mode now **admits NaFePO₄ directly from LiFePO₄** (its formula group is reported, with all four NaFePO₄ records), which PR-B2 alone did not (four-element Li–Fe–P–O neighbours took the slots). NaFePO₄ remains rank 1 at limits 5 and 10 (tie order: source analog first; scores unchanged).

## 4. AC11 rerun (admission changed, so representative sensitivity was re-checked)

Same method and script as the PR-B2 gate (`ac11_gate.py`, read-only, production-equivalent database, each NaFePO₄ record forced as representative).

| Request | Default | Forced representatives |
|---|---|---|
| Case Study 01, limit 5 | NaFePO₄ (mp-19226) rank 1, group of four, admitted directly | Forced record admitted directly (chain `mp-19017 → forced`, 90.75; 89.25 for mp-1192859); mp-19226 still ranked first via a two-step path through the forced record; downstream chains run through the forced record |
| Case Study 01, limit 10 | As above | As above, with more downstream chains through the forced record |
| Strict Avoid Li, limit 10 | As in the PR-B2 gate | As in the PR-B2 gate (direct chain 84.5; 83.0 for mp-1192859) |

All differences are explained by the same three causes recorded at the PR-B2 gate:
1. **The forced record is the traversed analog**, so chains run through it instead of mp-19226 (identical family neighbourhoods, since records with one formula share an element set).
2. **Chain usefulness reflects the traversed record's own stability:** mp-1192859 (energy above hull 0.0404) scores 1.5 lower on the direct step (89.25 vs 90.75; 83.0 vs 84.5 in Strict) and lower on chains where it is the weakest link (87.48 vs 88.25).
3. **Per-step grouping:** mp-19226 also reaches the results through a step where it is not an exact analog of the expanding material (rev 3.12 boundary). This does not occur with the default representative.

No unexplained difference. **AC11 passes under PR-B3.** D2 retained.

## 5. Notes for S4 and follow-ups

- Q6 (LiMnO₂): an exact-analog group is admitted at the source expansion on the reference data, yet no sodium compound reaches the results. Recorded as a clue for the separate Issue 3 diagnosis; not addressed here.
- S4 must run on production (local scores differ: production ranks NaFe₃P₃O₁₃ above the 115 group), with release-3 captures as the baseline and every change attributed to B1, B2 or B3 (rev 3.12, section 7 step 6).
