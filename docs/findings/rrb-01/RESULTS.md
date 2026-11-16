# RRB-01 results

Date: 2026-11-16
Status: **final for the locked protocol; provisional because the adjudication is AI-made
(AMD-002).**

## Summary

RRB-01 set out to measure how well frozen release-4 of MaterialGraph (main 50dd3ed; dataset
of 1,727 materials, Materials Project release 2026.04.13) retrieves a substitute composition
documented in the literature, given its parent and an explicit substitution objective.

The two pre-registered review articles yielded **10 unique qualifying directed pairs**.
**None of them has both the parent and the target in the dataset**, so the primary cohort
is empty. Under the protocol's pre-registered rule for an empty cohort, the retrieval
questions (Q1, Q1b, Q2, Q3) and the response diagnostics (Q5, Q6) are **not estimable**.
No benchmark request was sent to release-4. The only reportable result is **coverage (Q4)**.

This result says nothing about whether release-4 retrieves substitutes well or badly. It
shows that, for these sources, the literature's substitution pairs are almost entirely
compositions the frozen dataset does not contain.

## Registration trail

| Step | Record |
| --- | --- |
| Protocol lock | tag `rrb-01-protocol-lock` (PR #111, merge 4bb60f1c), `rrb-01-protocol-v0.3.md` |
| Sources | Hwang, Myung & Sun 2017 (HWA17, SHA-256 6832B1BC…); Noerochim et al. 2021 (NOE21, SHA-256 8D8991D4…) |
| Founder extraction | Invalid: AI-generated in a non-isolated session (DEV-001) |
| Two isolated AI extractions | AMD-001 (tag `rrb-01-amd-001`). Run A: Gemini 3.8 Flash, 75 records. Run B: DeepSeek web chat, 33 records, coverage self-reported as incomplete |
| Comparison | 15 jointly included pairs, 60 unmatched in A, 18 unmatched in B, 0 jointly excluded; 93 adjudication rows (`comparison/`) |
| Adjudication | AI adjudication under AMD-002 (tag `rrb-01-amd-002`); founder spot-check of 11 fixed rows: 11 of 11 agree (`comparison/spotcheck_founder.md`) |
| Label rule | AMD-003 (tag `rrb-01-amd-003`); no label resolution needed (see `cohort/COHORT.md`) |
| Dataset export | `dataset/materials_50dd3ed.csv`, 1,727 rows, SHA-256 CF49CAC2… (PR #128) |
| Cohort | `cohort/` (PR #130); `cohort.json` SHA-256 C334ECFA… |
| Evaluation lock | tag `rrb-01-evaluation-lock` on 2164b09 (DEV-002, PR #131) |

## Denominators

| Count | Value |
| --- | --- |
| Source records | 108 (Run A 75, Run B 33) |
| After adjudication | include 17, exclude 35, ambiguous 56 |
| P records by reason | ambiguous 56; unresolved_variable 11; not_directed 9; family_no_composition 5; no_named_parent 5; spatially_heterogeneous 3; label_unresolved 2; morphology_or_surface_only 2 |
| Ambiguous by source | HWA17 39, NOE21 17 |
| Unique qualifying directed pairs | 10 (8 from HWA17 only, 2 from NOE21 only; none in both) |
| Development pairs found | 0 |

## Classification

| Layer | Pairs |
| --- | --- |
| N (same element set, not objective-expressible) | 2 |
| X (objective-expressible, parent or target absent from dataset) | 8 |
| E (both present, at least 3 shared elements) | 0 |
| I (both present, fewer than 3 shared elements) | 0 |

The ten pairs, with dataset presence, are listed in `cohort/COHORT.md`.

## Q4: coverage

Coverage over the 10 unique qualifying pairs. The 95% Wilson intervals are descriptive:
the pairs are a complete enumeration of two sources, not a random sample.

| Measure | Pairs | Fraction | 95% Wilson interval |
| --- | --- | --- | --- |
| Objective-expressible (not N) | 8 | 0.80 | 0.49–0.94 |
| Parent in dataset | 3 | 0.30 | 0.11–0.60 |
| Target in dataset | 1 | 0.10 | 0.02–0.40 |
| Both in dataset | 0 | 0.00 | 0.00–0.28 |
| Both in dataset and objective-expressible (E + I) | 0 | 0.00 | 0.00–0.28 |

Why the pairs are absent. Seven of the eight X pairs have a doped or mixed-site composition
(for example NaFe0.5Co0.5O2, Na0.67[Ni0.2Mg0.1Mn0.7]O2) on the missing side. 15 of the 16
absent sides have no dataset formula with the same element set at any stoichiometry. The
exception is the parent Na4Fe3(PO4)2P2O7 of RRB01-007: the dataset holds 15 other Na–Fe–P–O
formulas, but not this one. This check is diagnostic only and changes no classification.

## Not estimable

| Question | Reason |
| --- | --- |
| Q1 (primary: informed-arm positional Formula Hit@5 on E) | E has 0 cases |
| Q1b (same metric on E + I) | E + I has 0 cases |
| Q2 (paired difference vs baselines B1–B3) | E has 0 cases |
| Q3 (balanced avoid-only arm) | E has 0 cases |
| Q5 (miss attribution, duplicate rate) | no benchmark responses |
| Q6 (strict avoid-only, exploratory) | no benchmark responses |

## Deviations

- **DEV-001.** The Stage 3 "founder extraction" was AI-generated in a non-isolated
  session. It is preserved but not used; AMD-001 replaced it with two isolated AI runs.
- **DEV-002.** The request generator, baselines and analysis script were not built, and
  no benchmark requests were sent, because every scored cohort is empty. DEV-002 also
  records the strict reading of AMD-002 check 1 (ADJ-057, 058, 059, 060, 063, 065, 066,
  068, 070 and 076 read as ambiguous). This changed 7 records from exclude to ambiguous
  and affected no included record.
- **Evaluation lock tag moved.** The tag was first placed at 12:20 IST on 2026-11-16 on
  80f1c4c (the PR #130 merge), because a local `git pull` had failed. It was deleted and
  re-created at 12:31 IST on 2164b09 (the PR #131 merge), as DEV-002 specifies. The tag
  message records this. `cohort/cohort.json` is identical in both commits.

## Limitations

- **AI extraction and AI adjudication.** Both extractions and the adjudication were done
  by AI models; the founder checked only textual matches (spot-check 11/11) and made no
  chemistry judgement. 56 of 108 records ended ambiguous. A domain adjudication made
  before any benchmark request would replace the AI adjudication (AMD-002), and could
  change the counts above.
- **Incomplete extraction coverage.** Run B self-reported incomplete coverage. Run A
  reported none. The union of the two runs is still not proof that every pair in the
  sources was found.
- **Two sources.** The cohort comes from two review articles. Coverage figures describe
  these sources against this dataset, not the literature in general.
- **Formula-level matching.** Presence in the dataset means an exact match of the reduced
  formula. Near compositions (different stoichiometry or dopant level) never count.

## What this result does and does not show

It shows that the frozen 1,727-material dataset does not contain the compositions that
these two reviews describe as substitutions. That is mainly because the reviews discuss
doped and mixed-site compositions, while the dataset holds ordered stoichiometric
compounds. Under these conditions, a retrieval benchmark built from these sources cannot
score release-4 at all.

It does not show anything about release-4's ranking or retrieval quality, in either
direction.

Any study that changes the sources, the dataset or the matching rule in response to this
result is a new study (for example RRB-02) with its own pre-registration. It is not a
continuation of RRB-01.
