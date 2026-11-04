# SRQ-01 PR-B1 — change attribution

| Field | Value |
|---|---|
| Branch | `srq-01-pr-b1` |
| Code under test | PR-B1 ordering (`6a6e138`), with `mp_id_sort_key` moved to `app/domain/ordering.py` (`f12c925`, no behaviour change) |
| Pre-PR-B1 reference | `f792826` snapshots under `tests/fixtures/golden/srq01_pra/full/` |
| Dataset | CI reference dataset (28 curated materials) |
| Harness | `tests/support/srq01_attribution.py` (test-side monkeypatching only) |
| Machine-readable diffs | `docs/findings/srq-01/pr-b1-attribution/*.json` |

## 1. Method

Each objective-aware request is run through `ResearchObjectiveExplorationService.explore` under five configurations of the three PR-B1 ordering points. The points are switched by test-side monkeypatching only; no application code is changed:

| Configuration | Admission ordering (R5a) | Ranked-candidate tie key (R5b/R6) | Chain tie key (R5b) |
|---|---|---|---|
| 0 baseline | off | off | off |
| 1 admission | **on** | off | off |
| 2 ranked tie | off | **on** | off |
| 3 chain tie | off | off | **on** |
| 4 all (current branch) | **on** | **on** | **on** |
| 5 = 1+3 (supplementary) | **on** | off | **on** |

- *Admission* is switched by overriding `objective_aware_ordering` on `generate_chains_for_objective`; *chain tie* by overriding `chain_tie_key` there; *ranked tie* by passing `source_material_id=None` to `_rank_candidates_from_chains`. The eligible chain pool (chains after the mode filter, before truncation) is captured at the same call.
- **Validation before attribution.** Configuration 0 reproduces the pre-PR-B1 snapshots exactly, and configuration 4 the current snapshots (ranked candidates with scores and reasons; returned chains with scores), for all three requests.
- **Attribution rule.** A change in configuration 4 relative to 0 is attributed to every single configuration (1, 2 or 3) that produces the same change on its own. A change no single configuration produces is flagged and examined; configuration 5 (1 and 3 together) is run only to test those explanations.
- **Chain changes** are classified as *crossed the limit boundary* (the chain is in both eligible pools, so only selection at limit 10 changed) or *generation changed* (the chain is in one pool only, so admission changed which chains exist).
- **Reasons.** A candidate's reasons are built from every eligible chain that contains it, in pool order. A changed reason string is classified as following from eligible chains gained or lost for that candidate; a change with no such chain would be flagged.

## 2. Case Study 01 (source #5 LiFePO₄; Avoid Li, Co; Prefer Na, K; preserve Fe, P, O; phosphate; Balanced; limit 10)

Validation: configuration 0 = pre-PR-B1 snapshot **True**; configuration 4 = current snapshot **True**. Eligible pool size 34 in every configuration.

### Ranked candidates (MP ID, score) per configuration

| Rank | 0 baseline | 1 admission | 2 ranked tie | 3 chain tie | 4 all |
|---|---|---|---|---|---|
| 1 | mp-19028 (117.25) | mp-19028 (117.25) | mp-19226 (117.25) | mp-19028 (117.25) | mp-19226 (117.25) |
| 2 | mp-556540 (117.25) | mp-19226 (117.25) | mp-19028 (117.25) | mp-556540 (117.25) | mp-19028 (117.25) |
| 3 | mp-761065 (117.25) | mp-556540 (117.25) | mp-556540 (117.25) | mp-19226 (117.25) | mp-556540 (117.25) |
| 4 | mp-752506 (117.25) | mp-752506 (117.25) | mp-752506 (117.25) | mp-752506 (117.25) | mp-752506 (117.25) |
| 5 | mp-19226 (117.25) | mp-761065 (117.25) | mp-761065 (117.25) | mp-761065 (117.25) | mp-761065 (117.25) |
| 6 | mp-26003 (77.25) | mp-19294 (77.25) | mp-19294 (77.25) | mp-19294 (77.25) | mp-19294 (77.25) |
| 7 | mp-25977 (77.25) | mp-25977 (77.25) | mp-25977 (77.25) | mp-25977 (77.25) | mp-25977 (77.25) |
| 8 | mp-27007 (77.25) | mp-26003 (77.25) | mp-26003 (77.25) | mp-26003 (77.25) | mp-26003 (77.25) |
| 9 | mp-19294 (77.25) | mp-27007 (77.25) | mp-27007 (77.25) | mp-27007 (77.25) | mp-27007 (77.25) |

### Returned chains per configuration (MP IDs without the `mp-` prefix; score)

| Position | 0 baseline | 1 admission | 2 ranked tie | 3 chain tie | 4 all |
|---|---|---|---|---|---|
| 1 | 19017/19028 (90.75) | 19017/19028 (90.75) | 19017/19028 (90.75) | 19017/19028 (90.75) | 19017/19028 (90.75) |
| 2 | 19017/556540 (90.75) | 19017/19226 (90.75) | 19017/556540 (90.75) | 19017/556540 (90.75) | 19017/19226 (90.75) |
| 3 | 19017/26003/19028 (88.25) | 19017/19294/19028 (88.25) | 19017/26003/19028 (88.25) | 19017/19028/19226 (88.25) | 19017/19028/19226 (88.25) |
| 4 | 19017/26003/556540 (88.25) | 19017/19294/19226 (88.25) | 19017/26003/556540 (88.25) | 19017/19028/556540 (88.25) | 19017/19028/556540 (88.25) |
| 5 | 19017/25977/19028 (88.25) | 19017/25977/19028 (88.25) | 19017/25977/19028 (88.25) | 19017/19028/752506 (88.25) | 19017/19028/752506 (88.25) |
| 6 | 19017/25977/556540 (88.25) | 19017/25977/19226 (88.25) | 19017/25977/556540 (88.25) | 19017/19028/761065 (88.25) | 19017/19028/761065 (88.25) |
| 7 | 19017/27007/19028 (88.25) | 19017/26003/19028 (88.25) | 19017/27007/19028 (88.25) | 19017/19294/19028 (88.25) | 19017/19226/19028 (88.25) |
| 8 | 19017/27007/556540 (88.25) | 19017/26003/19226 (88.25) | 19017/27007/556540 (88.25) | 19017/19294/556540 (88.25) | 19017/19226/556540 (88.25) |
| 9 | 19017/19294/19028 (88.25) | 19017/27007/19028 (88.25) | 19017/19294/19028 (88.25) | 19017/25977/19028 (88.25) | 19017/19226/752506 (88.25) |
| 10 | 19017/19294/556540 (88.25) | 19017/27007/19226 (88.25) | 19017/19294/556540 (88.25) | 19017/25977/556540 (88.25) | 19017/19226/761065 (88.25) |

### Attribution

**Ranked positions changed (0 → 4):**

| Rank | Before | After | Score | Produced alone by |
|---|---|---|---|---|
| 1 | mp-19028 | mp-19226 | 117.25 | 2 ranked tie |
| 2 | mp-556540 | mp-19028 | 117.25 | 2 ranked tie |
| 3 | mp-761065 | mp-556540 | 117.25 | 1 admission, 2 ranked tie |
| 5 | mp-19226 | mp-761065 | 117.25 | 1 admission, 2 ranked tie, 3 chain tie |
| 6 | mp-26003 | mp-19294 | 77.25 | 1 admission, 2 ranked tie, 3 chain tie |
| 8 | mp-27007 | mp-26003 | 77.25 | 1 admission, 2 ranked tie, 3 chain tie |
| 9 | mp-19294 | mp-27007 | 77.25 | 1 admission, 2 ranked tie, 3 chain tie |

**Chains added to or dropped from the returned ten (0 → 4):**

| Chain | Change | Kind | Produced alone by | In eligible pool of | Returned in |
|---|---|---|---|---|---|
| 19017/19028/19226 | added | crossed the limit boundary | 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 19017/19028/556540 | added | crossed the limit boundary | 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 19017/19028/752506 | added | crossed the limit boundary | 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 19017/19028/761065 | added | crossed the limit boundary | 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 19017/19226 | added | generation changed (eligible pool) | 1 admission | 1 admission, 4 all, 5 = 1+3 (supplementary) | 1 admission, 4 all, 5 = 1+3 (supplementary) |
| 19017/19226/19028 | added | generation changed (eligible pool) | **none** | 1 admission, 4 all, 5 = 1+3 (supplementary) | 4 all, 5 = 1+3 (supplementary) |
| 19017/19226/556540 | added | generation changed (eligible pool) | **none** | 1 admission, 4 all, 5 = 1+3 (supplementary) | 4 all, 5 = 1+3 (supplementary) |
| 19017/19226/752506 | added | generation changed (eligible pool) | **none** | 1 admission, 4 all, 5 = 1+3 (supplementary) | 4 all, 5 = 1+3 (supplementary) |
| 19017/19226/761065 | added | generation changed (eligible pool) | **none** | 1 admission, 4 all, 5 = 1+3 (supplementary) | 4 all, 5 = 1+3 (supplementary) |
| 19017/19294/19028 | dropped | crossed the limit boundary | **none** | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie |
| 19017/19294/556540 | dropped | generation changed (eligible pool) | 1 admission | 0 baseline, 2 ranked tie, 3 chain tie | 0 baseline, 2 ranked tie, 3 chain tie |
| 19017/25977/19028 | dropped | crossed the limit boundary | **none** | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie |
| 19017/25977/556540 | dropped | generation changed (eligible pool) | 1 admission | 0 baseline, 2 ranked tie, 3 chain tie | 0 baseline, 2 ranked tie, 3 chain tie |
| 19017/26003/19028 | dropped | crossed the limit boundary | 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 1 admission, 2 ranked tie |
| 19017/26003/556540 | dropped | generation changed (eligible pool) | 1 admission, 3 chain tie | 0 baseline, 2 ranked tie, 3 chain tie | 0 baseline, 2 ranked tie |
| 19017/27007/19028 | dropped | crossed the limit boundary | 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 1 admission, 2 ranked tie |
| 19017/27007/556540 | dropped | generation changed (eligible pool) | 1 admission, 3 chain tie | 0 baseline, 2 ranked tie, 3 chain tie | 0 baseline, 2 ranked tie |
| 19017/556540 | dropped | generation changed (eligible pool) | 1 admission | 0 baseline, 2 ranked tie, 3 chain tie | 0 baseline, 2 ranked tie, 3 chain tie |

**Flagged: 6 change(s) no single configuration produces.** All are chain-set changes, and all depend on combining admission ordering (1) with the chain tie key (3):

- `19017/19226/19028` added (generation changed (eligible pool)); in the eligible pool of 1 admission, 4 all, 5 = 1+3 (supplementary); returned in 4 all, 5 = 1+3 (supplementary).
- `19017/19226/556540` added (generation changed (eligible pool)); in the eligible pool of 1 admission, 4 all, 5 = 1+3 (supplementary); returned in 4 all, 5 = 1+3 (supplementary).
- `19017/19226/752506` added (generation changed (eligible pool)); in the eligible pool of 1 admission, 4 all, 5 = 1+3 (supplementary); returned in 4 all, 5 = 1+3 (supplementary).
- `19017/19226/761065` added (generation changed (eligible pool)); in the eligible pool of 1 admission, 4 all, 5 = 1+3 (supplementary); returned in 4 all, 5 = 1+3 (supplementary).
- `19017/19294/19028` dropped (crossed the limit boundary); in the eligible pool of 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary); returned in 0 baseline, 1 admission, 2 ranked tie, 3 chain tie.
- `19017/25977/19028` dropped (crossed the limit boundary); in the eligible pool of 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary); returned in 0 baseline, 1 admission, 2 ranked tie, 3 chain tie.

Mechanism: admission ordering makes NaFePO₄ (mp-19226) an expanded material, which *generates* the four `19017/19226/*` chains (they exist only in pools with admission ordering on). They score 88.25, tied with the Li-phosphate two-hop chains; only the chain tie key orders them by MP ID ahead of those chains, so only with both on are they *selected* at limit 10. Selecting them pushes `19017/19294/19028` and `19017/25977/19028`, present in every pool, past position 10. The supplementary run 5 (1 and 3 together, ranked tie off) returns exactly configuration 4's chains: **True**. No change is left unexplained.

### Changed reason strings (0 → 4)

**mp-19226** — follows from eligible-chain changes.

- Eligible chains containing it gained: `19017/19226`, `19017/19226/19028`, `19017/19226/556540`, `19017/19226/752506`, `19017/19226/761065`, `19017/19294/19226`, `19017/25977/19226`, `19017/26003/19226`, `19017/27007/19226`; lost: `19017/556540/19226`.
- Added: "Appears in an eligible composition chain containing a step classified as exact formula analog (alkali metal Li → Na; all other element ratios unchanged)."
- Added: "Shares elements across the composition relationship: Fe, Li, O, P. Structural preservation is not validated."

**mp-19028** — follows from eligible-chain changes.

- Eligible chains containing it gained: `19017/19226/19028`; lost: `19017/556540/19028`.
- Added: "Appears in an eligible composition chain containing a step classified as exact formula analog (alkali metal Li → Na; all other element ratios unchanged)."

**mp-556540** — follows from eligible-chain changes.

- Eligible chains containing it gained: `19017/19226/556540`; lost: `19017/19294/556540`, `19017/25977/556540`, `19017/26003/556540`, `19017/27007/556540`, `19017/556540`, `19017/556540/19028`, `19017/556540/19226`, `19017/556540/752506`, `19017/556540/761065`.
- Added: "Appears in an eligible composition chain containing a step classified as exact formula analog (alkali metal Li → Na; all other element ratios unchanged)."
- Removed: "Shares elements across the composition relationship: Fe, Li, O, P. Structural preservation is not validated."

**mp-752506** — follows from eligible-chain changes.

- Eligible chains containing it gained: `19017/19226/752506`; lost: `19017/556540/752506`.
- Added: "Appears in an eligible composition chain containing a step classified as exact formula analog (alkali metal Li → Na; all other element ratios unchanged)."

**mp-761065** — follows from eligible-chain changes.

- Eligible chains containing it gained: `19017/19226/761065`; lost: `19017/556540/761065`.
- Added: "Appears in an eligible composition chain containing a step classified as exact formula analog (alkali metal Li → Na; all other element ratios unchanged)."

### AC8b score check

| Configuration | Ranked materials with a different score | Returned chains with a different score or breakdown | Eligible-pool chains with a different score or breakdown |
|---|---|---|---|
| 1 admission | 0 | 0 | 0 |
| 2 ranked tie | 0 | 0 | 0 |
| 3 chain tie | 0 | 0 | 0 |
| 4 all | 0 | 0 | 0 |
| 5 = 1+3 (supplementary) | 0 | 0 | 0 |

## 3. Q6-style (source #28 LiMnO₂; Avoid Li; Prefer Na; Balanced; limit 10)

Validation: configuration 0 = pre-PR-B1 snapshot **True**; configuration 4 = current snapshot **True**. Eligible pool size 16 in every configuration.

### Ranked candidates (MP ID, score) per configuration

| Rank | 0 baseline | 1 admission | 2 ranked tie | 3 chain tie | 4 all |
|---|---|---|---|---|---|
| 1 | mp-18988 (27.25) | mp-18988 (27.25) | mp-18988 (27.25) | mp-18988 (27.25) | mp-18988 (27.25) |
| 2 | mp-691115 (27.25) | mp-530177 (27.25) | mp-530177 (27.25) | mp-530177 (27.25) | mp-530177 (27.25) |
| 3 | mp-530177 (27.25) | mp-691115 (27.25) | mp-691115 (27.25) | mp-691115 (27.25) | mp-691115 (27.25) |
| 4 | mp-1272804 (27.25) | mp-1272804 (27.25) | mp-1272804 (27.25) | mp-1272804 (27.25) | mp-1272804 (27.25) |

### Returned chains per configuration (MP IDs without the `mp-` prefix; score)

| Position | 0 baseline | 1 admission | 2 ranked tie | 3 chain tie | 4 all |
|---|---|---|---|---|---|
| 1 | 754656/18988 (61.95) | 754656/18988 (61.95) | 754656/18988 (61.95) | 754656/18988 (61.95) | 754656/18988 (61.95) |
| 2 | 754656/691115 (61.95) | 754656/530177 (61.95) | 754656/691115 (61.95) | 754656/530177 (61.95) | 754656/530177 (61.95) |
| 3 | 754656/530177 (61.95) | 754656/691115 (61.95) | 754656/530177 (61.95) | 754656/691115 (61.95) | 754656/691115 (61.95) |
| 4 | 754656/1272804 (61.95) | 754656/1272804 (61.95) | 754656/1272804 (61.95) | 754656/1272804 (61.95) | 754656/1272804 (61.95) |
| 5 | 754656/18988/691115 (59.45) | 754656/18988/530177 (59.45) | 754656/18988/691115 (59.45) | 754656/18988/530177 (59.45) | 754656/18988/530177 (59.45) |
| 6 | 754656/18988/530177 (59.45) | 754656/18988/691115 (59.45) | 754656/18988/530177 (59.45) | 754656/18988/691115 (59.45) | 754656/18988/691115 (59.45) |
| 7 | 754656/18988/1272804 (59.45) | 754656/18988/1272804 (59.45) | 754656/18988/1272804 (59.45) | 754656/18988/1272804 (59.45) | 754656/18988/1272804 (59.45) |
| 8 | 754656/691115/18988 (59.45) | 754656/530177/18988 (59.45) | 754656/691115/18988 (59.45) | 754656/530177/18988 (59.45) | 754656/530177/18988 (59.45) |
| 9 | 754656/691115/530177 (59.45) | 754656/530177/691115 (59.45) | 754656/691115/530177 (59.45) | 754656/530177/691115 (59.45) | 754656/530177/691115 (59.45) |
| 10 | 754656/691115/1272804 (59.45) | 754656/530177/1272804 (59.45) | 754656/691115/1272804 (59.45) | 754656/530177/1272804 (59.45) | 754656/530177/1272804 (59.45) |

### Attribution

**Ranked positions changed (0 → 4):**

| Rank | Before | After | Score | Produced alone by |
|---|---|---|---|---|
| 2 | mp-691115 | mp-530177 | 27.25 | 1 admission, 2 ranked tie, 3 chain tie |
| 3 | mp-530177 | mp-691115 | 27.25 | 1 admission, 2 ranked tie, 3 chain tie |

**Chains added to or dropped from the returned ten (0 → 4):**

| Chain | Change | Kind | Produced alone by | In eligible pool of | Returned in |
|---|---|---|---|---|---|
| 754656/530177/1272804 | added | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 1 admission, 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 754656/530177/18988 | added | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 1 admission, 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 754656/530177/691115 | added | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 1 admission, 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 754656/691115/1272804 | dropped | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 2 ranked tie |
| 754656/691115/18988 | dropped | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 2 ranked tie |
| 754656/691115/530177 | dropped | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 2 ranked tie |

**Chains returned in both, at a different position:**

| Chain | Position before | Position after | Produced alone by |
|---|---|---|---|
| 754656/530177 | 3 | 2 | 1 admission, 3 chain tie |
| 754656/691115 | 2 | 3 | 1 admission, 3 chain tie |
| 754656/18988/530177 | 6 | 5 | 1 admission, 3 chain tie |
| 754656/18988/691115 | 5 | 6 | 1 admission, 3 chain tie |

Every change is produced by at least one single configuration; nothing depends on combining them.

### Changed reason strings (0 → 4)

None.

### AC8b score check

| Configuration | Ranked materials with a different score | Returned chains with a different score or breakdown | Eligible-pool chains with a different score or breakdown |
|---|---|---|---|
| 1 admission | 0 | 0 | 0 |
| 2 ranked tie | 0 | 0 | 0 |
| 3 chain tie | 0 | 0 | 0 |
| 4 all | 0 | 0 | 0 |
| 5 = 1+3 (supplementary) | 0 | 0 | 0 |

## 4. Strict Avoid Li (source #5 LiFePO₄; Strict; limit 10)

Validation: configuration 0 = pre-PR-B1 snapshot **True**; configuration 4 = current snapshot **True**. Eligible pool size 25 in every configuration.

### Ranked candidates (MP ID, score) per configuration

| Rank | 0 baseline | 1 admission | 2 ranked tie | 3 chain tie | 4 all |
|---|---|---|---|---|---|
| 1 | mp-19028 (52.25) | mp-19028 (52.25) | mp-19226 (52.25) | mp-19028 (52.25) | mp-19226 (52.25) |
| 2 | mp-556540 (52.25) | mp-19226 (52.25) | mp-19028 (52.25) | mp-19226 (52.25) | mp-19028 (52.25) |
| 3 | mp-761065 (52.25) | mp-556540 (52.25) | mp-556540 (52.25) | mp-556540 (52.25) | mp-556540 (52.25) |
| 4 | mp-752506 (52.25) | mp-752506 (52.25) | mp-752506 (52.25) | mp-752506 (52.25) | mp-752506 (52.25) |
| 5 | mp-19226 (52.25) | mp-761065 (52.25) | mp-761065 (52.25) | mp-761065 (52.25) | mp-761065 (52.25) |

### Returned chains per configuration (MP IDs without the `mp-` prefix; score)

| Position | 0 baseline | 1 admission | 2 ranked tie | 3 chain tie | 4 all |
|---|---|---|---|---|---|
| 1 | 19017/19028 (84.5) | 19017/19028 (84.5) | 19017/19028 (84.5) | 19017/19028 (84.5) | 19017/19028 (84.5) |
| 2 | 19017/556540 (84.5) | 19017/19226 (84.5) | 19017/556540 (84.5) | 19017/19226 (84.5) | 19017/19226 (84.5) |
| 3 | 19017/761065 (84.5) | 19017/556540 (84.5) | 19017/761065 (84.5) | 19017/556540 (84.5) | 19017/556540 (84.5) |
| 4 | 19017/752506 (84.5) | 19017/752506 (84.5) | 19017/752506 (84.5) | 19017/752506 (84.5) | 19017/752506 (84.5) |
| 5 | 19017/19226 (84.5) | 19017/761065 (84.5) | 19017/19226 (84.5) | 19017/761065 (84.5) | 19017/761065 (84.5) |
| 6 | 19017/19028/556540 (82.0) | 19017/19028/19226 (82.0) | 19017/19028/556540 (82.0) | 19017/19028/19226 (82.0) | 19017/19028/19226 (82.0) |
| 7 | 19017/19028/761065 (82.0) | 19017/19028/556540 (82.0) | 19017/19028/761065 (82.0) | 19017/19028/556540 (82.0) | 19017/19028/556540 (82.0) |
| 8 | 19017/19028/752506 (82.0) | 19017/19028/752506 (82.0) | 19017/19028/752506 (82.0) | 19017/19028/752506 (82.0) | 19017/19028/752506 (82.0) |
| 9 | 19017/19028/19226 (82.0) | 19017/19028/761065 (82.0) | 19017/19028/19226 (82.0) | 19017/19028/761065 (82.0) | 19017/19028/761065 (82.0) |
| 10 | 19017/556540/19028 (82.0) | 19017/19226/19028 (82.0) | 19017/556540/19028 (82.0) | 19017/19226/19028 (82.0) | 19017/19226/19028 (82.0) |

### Attribution

**Ranked positions changed (0 → 4):**

| Rank | Before | After | Score | Produced alone by |
|---|---|---|---|---|
| 1 | mp-19028 | mp-19226 | 52.25 | 2 ranked tie |
| 2 | mp-556540 | mp-19028 | 52.25 | 2 ranked tie |
| 3 | mp-761065 | mp-556540 | 52.25 | 1 admission, 2 ranked tie, 3 chain tie |
| 5 | mp-19226 | mp-761065 | 52.25 | 1 admission, 2 ranked tie, 3 chain tie |

**Chains added to or dropped from the returned ten (0 → 4):**

| Chain | Change | Kind | Produced alone by | In eligible pool of | Returned in |
|---|---|---|---|---|---|
| 19017/19226/19028 | added | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 1 admission, 3 chain tie, 4 all, 5 = 1+3 (supplementary) |
| 19017/556540/19028 | dropped | crossed the limit boundary | 1 admission, 3 chain tie | 0 baseline, 1 admission, 2 ranked tie, 3 chain tie, 4 all, 5 = 1+3 (supplementary) | 0 baseline, 2 ranked tie |

**Chains returned in both, at a different position:**

| Chain | Position before | Position after | Produced alone by |
|---|---|---|---|
| 19017/19226 | 5 | 2 | 1 admission, 3 chain tie |
| 19017/556540 | 2 | 3 | 1 admission, 3 chain tie |
| 19017/761065 | 3 | 5 | 1 admission, 3 chain tie |
| 19017/19028/19226 | 9 | 6 | 1 admission, 3 chain tie |
| 19017/19028/556540 | 6 | 7 | 1 admission, 3 chain tie |
| 19017/19028/761065 | 7 | 9 | 1 admission, 3 chain tie |

Every change is produced by at least one single configuration; nothing depends on combining them.

### Changed reason strings (0 → 4)

**mp-19028** — order only: reasons follow eligible-chain order, which changed.


### AC8b score check

| Configuration | Ranked materials with a different score | Returned chains with a different score or breakdown | Eligible-pool chains with a different score or breakdown |
|---|---|---|---|
| 1 admission | 0 | 0 | 0 |
| 2 ranked tie | 0 | 0 | 0 |
| 3 chain tie | 0 | 0 | 0 |
| 4 all | 0 | 0 | 0 |
| 5 = 1+3 (supplementary) | 0 | 0 | 0 |

## 5. Summary

| Request | Ranked positions changed | Chains added/dropped | Chains reordered | Candidates with changed reasons | Not explained by a single configuration |
|---|---|---|---|---|---|
| cs01_source5_balanced | 7 | 18 | 0 | 5 | 6 |
| q6_source28_balanced | 2 | 6 | 4 | 0 | 0 |
| strict_source5_avoid_li | 4 | 2 | 6 | 1 | 0 |

- **Q6 and Strict Avoid Li:** every change is produced by a single configuration. In Q6, admission ordering and the chain tie key each alone reproduce the full chain change; in Strict, the ranked tie key alone places NaFePO₄ first.
- **Case Study 01:** six chain-set changes depend on combining admission ordering with the chain tie key, as explained in section 2. They are expected under R5: admission decides which chains exist, the chain key decides which equally scored chains are returned at the limit.
- **Ranked order without the ranked tie key.** Configurations 1 and 3 alone also reorder tied ranked candidates, because candidates are collected in eligible-chain order and both change that order. With the ranked tie key on (2 and 4), tied candidates are ordered by source analog first, then MP ID, independently of chain order.
- **AC8b:** no ranked material, returned chain or eligible-pool chain present in two configurations has a different score or score breakdown, in any configuration.
- **Eligible pool membership** changes only when admission ordering is on, and only in Case Study 01 (configurations 1, 4 and 5). In Q6 and Strict every configuration has the same eligible chains; only their order and the limit-10 selection change.
- **Reasons:** every changed reason string follows from eligible chains gained or lost for that candidate, which in Case Study 01 come from admission ordering (configuration 1); in Strict the one change (mp-19028) is order-only, following eligible-chain order. None is unexplained.

Reproduce: with the CI reference dataset loaded, `python -m tests.support.srq01_attribution docs/findings/srq-01/pr-b1-attribution f792826`.
