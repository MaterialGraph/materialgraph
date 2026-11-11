# RRB-01 AI adjudication: batch 3 (ADJ-051 to ADJ-075)

Under AMD-002 (tag `rrb-01-amd-002`).

| Item | Value |
| --- | --- |
| Adjudicator | Claude Code, model `claude-opus-5-5` |
| Rows | ADJ-051 to ADJ-075 (workbook rows 52–76) |
| Output | `adjudication_ai.xlsx`, SHA-256 after batch 3: `FA9711B2EBDD286ECDCC88780B3ED029776A3F72C4D9317519B2E53C03709950` |
| Counts | include 2, exclude 13, ambiguous 10; confirmed 0, error 0 (no audit rows in this batch) |

## Claude Code report (verbatim)

Model identifier: claude-opus-5-5

Batch 3 (ADJ-051 to ADJ-075) counts. The batch has 1 unmatched_a row, 17 unmatched_b rows and 7 normalization_failure rows.

- Include: 2. ADJ-061 and ADJ-062: "NMC111 was replaced by NMC622 / NMC811". These match my decisions on Run A's versions of the same pair, ADJ-032 and ADJ-033.
- Exclude: 13.
  - family_no_composition: ADJ-058, 067, 068, 071
  - morphology_or_surface_only: ADJ-056 (Al2O3 coating), 065 (single crystal vs polycrystalline), 072 (olivine vs maricite polymorph)
  - not_directed: ADJ-057, 063
  - no_named_parent: ADJ-051, 060
  - unresolved_variable: ADJ-055
  - spatially_heterogeneous: ADJ-066
- Ambiguous: 10. ADJ-052, 053, 054, 059, 064, 069, 070, 073, 074, 075.
- Confirmed / error: 0 / 0. This batch has no audit_joint_include rows.

Quote not found on the cited page:

- ADJ-052 (cited p.8): found in abridged form on p.7 of HWA17.
- ADJ-053 (cited p.11): a close but altered form is on p.10 of HWA17. The source reads "Nax[Co2/3Mn1/3]O2", not "Na[…]".
- ADJ-064 (cited p.4): found in abridged form on p.5 of NOE21.

One judgement call you may want to review: many Run B quotes are abridged. They drop small words such as "a", "which is", "(M: metal)" or commas. Every word that remains appears, in order, in the cited sentence. The brief's tolerance list doesn't cover omitted words, but I counted these as check1 = yes and noted "Quote is abridged" in the reason.

- The rows affected are ADJ-057, 058, 059, 060, 063, 065, 066, 068 and 070.
- If you want check1 read strictly, those rows would all become ambiguous.

Other notes:

- ADJ-059, ADJ-070, ADJ-073: the source calls these pairs "isostructural with", "an isostructure of" or "similar to". That relation runs both ways and doesn't say which composition is the original, so I marked them ambiguous.
- ADJ-074 and ADJ-075: the source explicitly calls these terephthalate derivatives, but gives them only as abbreviations, with no formula or substituent position. That's why they couldn't be normalized, so I marked them ambiguous.
- ADJ-071 (Run A included it): I excluded it as family_no_composition, because Al-doped P2-Na2/3[Ni1/3Mn2/3]O2 has no stated composition.

I compared every cell with the batch-2 version and with adjudication.xlsx. The only changes are in the allowed columns for rows ADJ-051 to ADJ-075.

SHA-256 of adjudication_ai.xlsx: fa9711b2ebdd286ecdcc88780b3ed029776a3f72c4d9317519b2e53c03709950

Stopping here; batch 4 is not started.

## Founder notes

- **Integrity check:** the cell comparison against the committed `adjudication.xlsx` showed 0 differing generated cells; yellow columns are filled in rows 2–76 only. `adjudication.xlsx` was unchanged (`1B7777690497093BDDF48848B6430A79183D00DAB3C80E8E2E3632541B9DC444`) and read-only throughout batch 3.
- **Deviation: abridged quotes.** For ADJ-057, 058, 059, 060, 063, 065, 066, 068 and 070, Claude Code counted quotes with omitted words as passing check 1. AMD-002 section 3 does not list omitted words as an allowed difference. Under AMD-002 as written, these rows are reported as `ambiguous`. The AI's original decisions are preserved unchanged in `adjudication_ai.xlsx`; the strict reading is applied in reporting and cohort construction. No affected row is an include, so the cohort is unaffected.
- **Follow-up:** the batch 4 brief states the strict reading explicitly and asks Claude Code to list any earlier rows (ADJ-001 to ADJ-075) whose reasons mention an abridged quote.
