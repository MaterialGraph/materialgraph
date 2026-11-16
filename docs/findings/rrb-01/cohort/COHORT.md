# RRB-01 Stage 6: cohort

Built: 2026-11-16, by `tools/build_cohort.py` (tests: `tools/test_stage6_tools.py`, synthetic
data only). Output files in this folder are the script's output, copied unchanged; their
SHA-256 values are in `cohort_report.json` (`outputs_sha256`).

Inputs (SHA-256):

| File | SHA-256 |
| --- | --- |
| `comparison/adjudication_ai.xlsx` | 505A65E382BC12CBF4BD5AC2389EF68F16DE8719E8F7044F8758B0FE2B04198D |
| `runs/run_a/run_a.normalized.jsonl` | E866BB2A5A67086498AC32DB07E4F4D093127BA9483462C3802259F148A6CDCA |
| `runs/run_b/run_b.normalized.jsonl` | 07E4C4DA4A78C934C1CAC7C4A3C40CD9050CD9FA8A4B609847D702921E95A651 |
| `dataset/materials_50dd3ed.csv` | CF49CAC2F6673BBF47C7425904458EA346743480424446C2F2B6892F3A0E4B51 |

No `label_resolutions.csv` was used (see "Labels").

## Rules applied

- Decisions come from `founder_decision` in the AI adjudication (AMD-002). These rows are read as `ambiguous` under the strict reading of check 1 (omitted words are not an allowed difference): ADJ-057, 058, 059, 060, 063, 065, 066, 068, 070, 076. This changed 7 records from exclude to ambiguous (a different P reason). No include was affected.
- Non-included records get status P. Included records whose composition does not normalize, and has no AMD-003 resolution, get P `label_unresolved`.
- Occurrences of one normalized directed pair collapse into one case. Cases are classified N > X > E > I against the frozen dataset export (protocol v0.3, "Classification layers").

## Result

| Count | Value |
| --- | --- |
| Source records | Run A 75 (HWA17 48, NOE21 27); Run B 33 (HWA17 21, NOE21 12) |
| Decisions after strict check 1 | include 17, exclude 35, ambiguous 56 |
| P records by reason | ambiguous 56 (HWA17 39, NOE21 17); unresolved_variable 11; not_directed 9; family_no_composition 5; no_named_parent 5; spatially_heterogeneous 3; label_unresolved 2; morphology_or_surface_only 2 |
| Unique qualifying directed pairs | 10 |
| N / X / E / I | 2 / 8 / 0 / 0 |
| Development cases found | 0 |
| Primary cohort (E minus development exclusions) | **0 cases** |
| Dataset coverage (of 10 pairs) | parent present 3, target present 1, both present 0 |

| Case | Class | Parent → target (as published) | Parent in dataset | Target in dataset |
| --- | --- | --- | --- | --- |
| RRB01-001 | X | NaFeO2 → NaFe0.5Co0.5O2 | yes | no |
| RRB01-002 | X | NaFeO2 → NaFe0.3Ni0.7O2 | yes | no |
| RRB01-003 | X | Li[Ni0.5Mn0.5]O2 → Na[Ni0.5Mn0.5]O2 | no | no |
| RRB01-004 | X | Na2/3[Ni1/3Mn2/3]O2 → Na0.67[Ni0.2Mg0.1Mn0.7]O2 | no | no |
| RRB01-005 | X | Na2/3[Ni1/3Mn2/3]O2 → Na2/3[Ni1/3Mn1/2Ti1/6]O2 | no | no |
| RRB01-006 | X | NaFePO4 → Na[Fe0.5Mn0.5]PO4 | yes | no |
| RRB01-007 | X | Na4Fe3(PO4)2P2O7 → Na4Co3(PO4)2P2O7 | no | yes |
| RRB01-008 | X | LiFePO4F → LiFeSO4F | no | no |
| RRB01-009 | N | LiNi1/3Mn1/3Co1/3O2 → LiNi0.6Mn0.2Co0.2O2 | no | no |
| RRB01-010 | N | LiNi1/3Mn1/3Co1/3O2 → LiNi0.8Mn0.1Co0.1O2 | no | no |

Under the protocol's "Small or empty cohort" rule, E has zero cases, so Q1 and Q2 are
not estimable. The cohorts for Q1b (E + I) and Q3 (avoid-only arm on E) are also empty,
so these are not estimable either. Q4 (coverage) is reported. No benchmark requests are
needed. All results are provisional because the adjudication is AI-made (AMD-002).

## Labels (AMD-003)

Two included Run A records have label compositions: ADJ-032 (`a:NOE21-3-2`, NMC111 →
"NMC622 LiNi0.6Mn0.2Co0.2O2") and ADJ-033 (`a:NOE21-3-3`, NMC111 →
"NMC811 LiNi0.8Mn0.1Co0.1O2"). NOE21 p.3 prints "LiNi1/3Mn1/3Co1/3O2 (NMC111)". Resolved,
these records would only add second occurrences to the existing cases RRB01-009 and
RRB01-010; no case, class or coverage figure would change. They were not resolved: they
remain P `label_unresolved`, and no `label_resolutions.csv` was committed. This avoids a
judgement on AMD-003 condition 1 (each target was recorded as a label together with its
formula, not as a bare label).

## Absence check (diagnostic only)

For every dataset-absent side, the dataset formulas with the same element set (any
stoichiometry) were listed (normalizer from `tools/normalize_formulas.py`, dataset
`formula` column). All 1,727 dataset formulas normalize (`dataset_normalization.json`).
15 of the 16 absent sides have no dataset formula with the same element set.
The exception is the RRB01-007 parent (Fe3Na4O15P4): the dataset holds 15 other Na–Fe–P–O
formulas, none of which is that composition (Na2Fe3(PO4)3, Na2Fe7(PO4)6, Na2FePO5,
Na3Fe(PO4)2, Na3Fe2(PO4)3, Na3Fe3(PO4)4, Na4Fe2(PO4)3, Na7Fe4(PO4)6, Na7Fe4P9O32,
Na9Fe3P8O29, NaFe(PO3)3, NaFe3P3O13, NaFe7(PO4)6, NaFeP2O7, NaFePO4). These are not matches
and do not change any classification; they are listed as context for the coverage report.
