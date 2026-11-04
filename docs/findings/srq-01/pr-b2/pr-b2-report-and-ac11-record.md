# SRQ-01 PR-B2 report and AC11 gate record

| Field | Value |
|---|---|
| Date | 2026-11-04 |
| Branch | `srq-01-pr-b2` (commits `634c837`, `36cc456`, `9798b6f`, `15d98a7`) |
| Spec | SRQ-01 S2 rev 3.11 (R3, R7.1, D11, D12, AC11) |
| Status | Implementation complete; AC11 gate **passed** (all differences explained); merge pending review. Not deployed: production remains on `release-3` until PR-B1–B3 are qualified together |

## 1. What PR-B2 changes (objective-aware requests only)

- **Request-scoped composition load (D11).** `DiscoveryChainService.request_compositions()` loads every stored composition once per request, normalised with `normalise_stored_composition`, plus `energy_above_hull`. The report, the per-step reason labels and the PR-B1 source-analog tie key reuse it; the report path no longer runs its own query on objective-aware requests (tested).
- **Formula groups at admission (R3).** For each expansion, eligible candidates that are exact alkali formula analogs of the expanding material are grouped by normalised composition (not formula string). One record per group stays eligible: the representative from `app.domain.ordering.choose_representative` (lowest numeric MP ID, a reproducibility convention).
- **Representative slot (AC11 finding 1).** The representative takes the admission position of the group's earliest member, so which record represents a group never decides whether the group gets a slot.
- **Admitted groups only (AC11 finding 2, D12).** Groups are formed before the expansion cap; only groups whose representative actually won a slot are kept and reported.
- **Report.** `formula_group` lists the members of the admission group a source analog came from (representative `traversed: true`, each member with its own MP ID and energy above hull); empty when the material was not reached through an admission group. `formula_grouping_available: true`; `admission_reporting_available` stays `false`; `expansions` stays `[]`. New limitations state the empty-group meaning and that the representative is a convention, not a scientific preference.
- PR-B1 review nits: `chain_tie_key` typed; `is_objective_aware` docstring cites rev 3.11.

Unchanged: frozen requests (all `srq01_pr0` golden tests pass without regeneration), scores, score formulas and weights, shared Discovery schemas, `family_service`, the legacy path. No `alkali_substitution` in `objective_exploration_service.py` (S-3); new text passes the S-5 scan.

## 2. Verification (local, CI-equivalent database)

- Backend suite: **1,466 passed, 1 skipped**; ruff and gitleaks pass.
- New tests (`tests/services/discovery/test_formula_groups.py`, 9): lowest-MP-ID representative; grouping by composition (a NaFePO₄ record stored as `Na4Fe4P4O16` joins the group); one slot per group with order kept; members recorded with their own records; non-analogs never grouped; unusable composition groups nothing; AC11 substitution mechanism; forced representative keeps the earliest slot; groups whose representative missed the cap are not reported; empty-group meaning.
- Updated report tests: grouping flag `true`, new limitations, normalisation spy extended to the chain service (same strictness), Case Study 01 expects NaFePO₄'s group, new test that the report never runs its own composition query.
- `srq01_pra` snapshots regenerated deliberately; a structural comparison confirms **only `formula_correspondence` changed** in all three (no candidate, chain, score or metadata change on the reference data, which holds one NaFePO₄ record).

## 3. AC11 gate — representative sensitivity

Method: `ac11_gate.py` (read-only) against the production-equivalent local database `materialgraph_test_mg_de_007` (1,727 materials, four NaFePO₄ records: mp-19226 E_hull 0, mp-746030 0.0049, mp-753672 0.0058, mp-1192859 0.0404). Case Study 01 (limits 5 and 10) and Strict Avoid Li (limit 10) were run with the default representative and with each NaFePO₄ record forced through a substitute `choose_representative`. Responses and summaries are kept with this record.

### Run 1 (initial code) — finding 1
Forcing a non-default record moved the whole group to that record's later admission position, past the 6-slot cap: in Strict the direct LiFePO₄ → NaFePO₄ chain disappeared and NaFePO₄'s group came back empty. Representative choice was deciding whether the group was admitted. **Fixed** (`9798b6f`): the representative takes the earliest member's slot.

### Run 2 — finding 2
Case Study 01 still differed only in an empty group. Cause: groups were recorded before the cap. In Balanced Case Study 01, LiFePO₄'s six slots go to Li–Fe–P–O compounds sharing four elements plus the reserved Na slot (mp-18493, lowest MP ID among Na compounds), so NaFePO₄ is **not admitted directly**; it is reached in two steps. The default run nevertheless showed a group for it, contradicting D12. **Fixed** (`15d98a7`): only admitted groups are kept.

### Run 3 (final) — gate result
| Request | Result |
|---|---|
| Case Study 01, limit 5 | All five runs identical. NaFePO₄ (mp-19226) rank 1 at 117.25; `formula_group` empty (not reached through an admission group) |
| Case Study 01, limit 10 | All five runs identical, as above |
| Strict Avoid Li, limit 10 | Default: NaFePO₄ group admitted directly from LiFePO₄ with all four members. Forced runs differ as explained below |

Strict differences with a forced representative, each explained:
1. **The forced record is the admitted, traversed analog** (direct chain `mp-19017 → forced record`), with the group listing all four records and that record marked traversed. Intended.
2. **Chain usefulness 83.0 for mp-1192859 versus 84.5 for the other three.** mp-1192859 has energy above hull 0.0404, well above the others (0–0.006), so the stability component of the chain usefulness score is lower. Scores use the traversed record's own data (R3). Legitimate.
3. **mp-19226 also appears (rank 1), reached in two steps through mp-18774**, with an empty group. At that step NaFePO₄ is not an exact analog of the expanding material, so it is not grouped there. Consequence: with a non-default representative, two NaFePO₄ records can appear among ranked candidates. With the default representative this does not occur (the representative is mp-19226). Known limitation of per-step grouping (R3), recorded below.

No difference remained unexplained. **AC11 passes.** D2 (lowest MP ID as representative) is retained.

## 4. Observations for PR-B3 and the specification

- With PR-B1 and PR-B2, Case Study 01 on the production-equivalent data ranks NaFePO₄ **first at limit 5** (tie order: source analog first), but the direct LiFePO₄ → NaFePO₄ step is **not admitted** in Balanced mode, because four-element Li–Fe–P–O neighbours fill the slots before three-element Na compounds. PR-B3's admission sequence (preferred exact analogs first) is what admits it directly.
- Spec rev 3.12 should record: the representative takes the earliest member's slot; only admitted groups are reported; grouping is per step, so the same formula can reach the ranked list through a non-grouped path (most visible with a non-default representative).
- Local data differs from production in candidate scores (here all leading candidates tie at 117.25; production shows NaFe₃P₃O₁₃ higher). Final qualification (S4) must run on production.
