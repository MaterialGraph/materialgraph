# RRB-01 AI adjudication: batch 2 (ADJ-026 to ADJ-050)

Under AMD-002 (tag `rrb-01-amd-002`).

| Item | Value |
| --- | --- |
| Adjudicator | Claude Code, model `claude-opus-5-5` |
| Rows | ADJ-026 to ADJ-050 (workbook rows 27–51) |
| Output | `adjudication_ai.xlsx`, SHA-256 after batch 2: `4D171E0B03B5F8FDA5FADDA5DE8B4412EEC0FEC4852F0905BF8B0672CCF93EA8` |
| Counts | include 2, exclude 13, ambiguous 10; confirmed 0, error 0 (no audit rows in this batch) |

## Claude Code report (verbatim)

Model identifier: claude-opus-5-5

Batch 2 (ADJ-026 to ADJ-050) counts. ADJ-026 to 028 are HWA17 rows and ADJ-029 to 050 are NOE21 rows; all are unmatched_a.

- Include: 2. ADJ-032 and ADJ-033: "NMC111 was replaced by NMC622 LiNi0.6Mn0.2Co0.2O2 and NMC811 LiNi0.8Mn0.1Co0.1O2". NMC111 is defined on the same page as LiNi1/3Mn1/3Co1/3O2, so both sides are fixed compositions. Run A had excluded these two as family_no_composition.
- Exclude: 13.
  - not_directed: ADJ-026, 027, 036, 043
  - unresolved_variable: ADJ-035, 041, 047, 048
  - spatially_heterogeneous: ADJ-044, 045, 046 (core–shell materials)
  - no_named_parent: ADJ-029
  - family_no_composition: ADJ-031
- Ambiguous: 10. ADJ-028, 030, 034, 037, 038, 039, 040, 042, 049, 050.
- Confirmed / error: 0 / 0. This batch has no audit_joint_include rows.

Quote not found on the cited page:

- ADJ-034 (cited p.3): the quote is on p.5 of NOE21. It's a volume-change comparison between NMC811 and NMC111 with no substitution wording.

Rows where the passage doesn't contain the recorded composition:

- ADJ-028: Bi0.57Sb0.43 appears only in the Fig. 40 caption, as "Bi0.57–Sb0.43–C".
- ADJ-031: LixCo1-yNiyO2 isn't printed anywhere; the text only says Co was added to LNO.

Why these rows are ambiguous:

- ADJ-037 to ADJ-039: the quote only compares the Mg, Mn and Al dopants with each other. They are linked to cobalt only through the general phrase "cobalt replacement cations in LiNi1−xMxO2".
- ADJ-049 and ADJ-050: the Table 1 rows say "Tungsten-doped" but don't name LiNiO2 as the doped parent.

I compared every cell with the batch-1 version and with adjudication.xlsx. The only changes are in the allowed columns for rows ADJ-026 to ADJ-050; batch 1 rows are untouched.

SHA-256 of adjudication_ai.xlsx: 4d171e0b03b5f8fda5fadda5de8b4412eec0fec4852f0905bf8b0672ccf93ea8

Stopping here; batch 3 is not started.

## Founder notes

- **Generated workbook rewritten during batch 2:** the local `adjudication.xlsx` was found rewritten after batch 2 (SHA-256 `A945FB48581D5E6CEF993A1D2A26A0D3BED3E6109F850ABDE628AB4546B4557C`; copy kept at `C:\mg-validation\rrb01-adjudication\adjudication_local_modified_batch2.xlsx`). It was restored to the committed version (`1B7777690497093BDDF48848B6430A79183D00DAB3C80E8E2E3632541B9DC444`).
- **Integrity check after restoring:** the cell comparison against the committed file showed 0 differing generated cells; yellow columns are filled in rows 2–51 only (batches 1 and 2).
- **Safeguard:** `adjudication.xlsx` was set to read-only before batch 3.
- **Open issue for Stage 6:** included records whose recorded composition is a label rather than a formula (e.g. "NMC111", ADJ-032 and ADJ-033) cannot be normalized. A handling rule is to be fixed before cohort construction and before any benchmark request.
