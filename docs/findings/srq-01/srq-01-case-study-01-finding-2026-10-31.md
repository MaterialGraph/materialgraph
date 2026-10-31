# Scientific Relationship Qualification 01 — S1 Finding Record

**Case Study 01: direct sodium analog NaFePO₄ missed by Objective Investigation**

| Field | Value |
|---|---|
| Record date | 2026-10-31 |
| Status | S1 — finding frozen; no implementation change made or approved |
| Production code | `main` at `c8c6ed9` (tag `release-2`) |
| Dataset | 1,727 materials; values computed by Materials Project; most recent recorded import MP release 2026.04.13 (1,699 records with release provenance, 28 curated records predating provenance tracking) |
| Endpoint | `POST /api/v1/materials/5/discovery/objective/explore` |
| Source material | LiFePO₄, mp-19017, local ID 5 |

## 1. Purpose

This record documents a reproducible scientific weakness found by testing MaterialGraph against known chemistry. It is the before-correction baseline for SRQ-01. It does not propose or approve a code change; stages S2–S4 require separate review.

## 2. Request

Case Study 01 objective, as submitted by the production frontend (Balanced mode):

```json
{"objective":{"avoid_elements":["Li","Co"],"prefer_elements":["Na","K"],"preserve_elements":["Fe","P","O"],"target_family":"phosphate","max_hops":2,"limit":5,"prefer_lower_criticality":true,"require_stable_materials":false},"mode":"balanced","limit":5}
```

A second request was identical except `limit: 10` (both occurrences).

## 3. Evidence files

| File | Content | SHA-256 |
|---|---|---|
| `cs01-response.json` | Response, limit 5 | `2b5a7cf25947c29c1ad2f227549d46bbb54efda2fc6c76c618636592b6a87c1d` |
| `cs01-limit10-response.json` | Response, limit 10 | `8a51eb32c3f9542c883f9524e19f0478af6f2bed5a73622a10599ac53f237854` |
| `request.json`, `request-limit10.json` | Request bodies above | — |

Hashes were computed on the files as uploaded for analysis. Verify locally with `Get-FileHash <file> -Algorithm SHA256`.

## 4. Observations

### 4.1 Limit-5 result

Ranked materials:

| Rank | Material | MP ID | Local ID | Objective rule score |
|---|---|---|---|---|
| 1 | NaFe₃P₃O₁₃ | mp-1040459 | 70 | 117.25 |
| 2 | Na₃Fe(PO₄)₂ | mp-19028 | 6 | 115.0 |
| 3 | Na₃Fe₃(PO₄)₄ | mp-556540 | 7 | 115.0 |
| 4 | Na₉Fe₃P₈O₂₉ | mp-761065 | 8 | 115.0 |
| 5 | NaFeP₂O₇ | mp-752506 | 9 | 115.0 |

All five returned chains end at or pass through Na₃Fe(PO₄)₂ (local ID 6). Every Li→Na step in the response is an `alkali_substitution` transition to local ID 6, with `relationship_basis: composition_heuristic` and `preservation_basis: element_overlap`.

### 4.2 Dataset search

| Query | Result |
|---|---|
| `NaFePO4` | 4 exact formula matches. Visible: mp-19226 (local ID 10, E above hull 0.000 eV/atom), mp-1192859 (ID 384, 0.040), mp-746030 (ID 1094, 0.005). Fourth record not captured; identity unconfirmed. |
| `Na2FeP2O7` | 0 exact matches; 23 materials with the same elements in different proportions. |

### 4.3 Limit-10 result

NaFePO₄ (mp-19226, local ID 10) appears at **rank 6**, score **115.0**, tied with local IDs 6–9. Ranks 7–10 are Li-containing materials (local IDs 1–4) at 75.0.

The only returned path to NaFePO₄ is:

LiFePO₄ (ID 5) → `alkali_substitution` → Na₃Fe(PO₄)₂ (ID 6) → `family_expansion` → NaFePO₄ (ID 10)

No one-step LiFePO₄ → NaFePO₄ relationship was returned.

### 4.4 Search metadata (identical in both runs)

| Metric | Limit 5 | Limit 10 |
|---|---|---|
| Expanded states | 6 | 6 |
| Generated chains | 26 | 26 |
| Candidates considered | 5,034 | 5,034 |
| Candidates admitted | 36 | 36 |
| Cap discards (total / distinct) | 4,998 / 838 | 4,998 / 838 |
| Expansion limit per material | 6 | 6 |
| `search_truncated` / `result_truncated` | false / true | false / true |

The limit-5 response reports a ranked-material pool of 10, so the result limit affects presentation only, not exploration.

## 5. Findings

| ID | Finding |
|---|---|
| **SRQ-01** | The exact Li→Na formula analog NaFePO₄ is in the dataset and computationally stable (mp-19226, 0.000 eV/atom) but is absent from the Case Study 01 top five. |
| **SRQ-02** | The relationship model does not distinguish exact Li→Na formula replacement, preserving the Fe:P:O stoichiometric ratios, from broader composition changes. No structural framework preservation is inferred. NaFePO₄ receives the same score as materials with different stoichiometry and is reached only through a chemically different intermediate. |
| **SRQ-03** | Ordering effects appear to contribute to the miss. Two separate hypotheses are recorded: **(H1)** admission order determines which candidate occupies the reserved preferred-element slot (here the lowest-ID sodium material, local ID 6); **(H2)** tie-breaking determines the order of equally scored candidates (ranks 2–6 at 115.0 follow local ID order exactly). They may share one underlying ordering mechanism; that has not been demonstrated. Both require controlled ID-invariance tests. |
| **SRQ-04** | Search caps (838 distinct materials discarded) and formula-only data limit scientific completeness. The dataset holds no structure data, so the four NaFePO₄ records cannot be distinguished by polymorph. |

## 6. Analyst notes (manual, not computed by MaterialGraph)

- Under conventional ionic charge assignments (Li⁺/Na⁺, P⁵⁺, O²⁻), charge neutrality implies formal average Fe oxidation states of +2 for LiFePO₄ and NaFePO₄, +3 for Na₃Fe(PO₄)₂, Na₃Fe₃(PO₄)₄, Na₉Fe₃P₈O₂₉ and NaFeP₂O₇, and approximately +3.33 for NaFe₃P₃O₁₃. These are formula-derived estimates, not independently verified oxidation-state measurements. On this basis, the returned candidates are not formal oxidation-state analogs of the source.
- NaFePO₄ is known in more than one polymorph (maricite and olivine-type), with different electrochemical behavior reported in the literature. Which MP records correspond to which polymorph has not been verified here.
- Energy above hull is a computational stability indicator, not evidence of synthesizability or battery performance.

## 7. Limitations of this record

- One objective and one source material; not a general assessment of MaterialGraph.
- Chemistry notes in section 6 have not been reviewed by an independent materials scientist.
- Production version is taken from the `release-2` deployment record; it was not independently fingerprinted at request time.

## 8. Proposed next stages (not approved)

- **S2** — Specify a formula-level alkali-replacement relationship using normalized element counts, distinct from element-overlap relationships, without inferring structural equivalence.
- **S3** — Test H1 and H2 separately. Admit exact formula substitutions before generic relationships, independent of local IDs; use a documented stable identifier (MP ID) for tie-breaking; give classification and admission priority rather than an automatic score increase.
- **S4** — Rerun Case Study 01, Q6 and the other frozen objectives as an anti-overfitting set; verify relationship classification, ID invariance (compared on MP IDs, relationship classes and candidate sets), search behavior and unintended ranking changes.

Out of scope for this correction: structure import, oxidation-state prediction, ML models, and dataset expansion.
