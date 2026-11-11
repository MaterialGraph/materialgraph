# RRB-01 AI adjudication: batch 1 (ADJ-001 to ADJ-025)

Under AMD-002 (tag `rrb-01-amd-002`, tag commit dated 2026-11-11 07:43:25 -0800).

| Item | Value |
| --- | --- |
| Adjudicator | Claude Code, model `claude-opus-5-5` |
| Rows | ADJ-001 to ADJ-025 (workbook rows 2–26) |
| Output | `adjudication_ai.xlsx`, SHA-256 after batch 1: `2B039BD49889DD8C9C8C245861AE15A97657FE103292703975612E0608C13AA8` |
| Counts | include 3, exclude 11, ambiguous 11; confirmed 0, error 0 (no audit rows in this batch) |

## Claude Code report (verbatim)

The brief had no batch number, and adjudication_ai.xlsx didn't exist yet, so I treated this as batch 1 (ADJ-001 to ADJ-025).

Model identifier: claude-opus-5-5

Batch 1 counts (all 25 rows are unmatched_a, all from HWA17):

- Include: 3. ADJ-016 (NaFePO4 → Na[Fe0.5Mn0.5]PO4, "an extension of"), ADJ-021 (Na4Fe3 → Na4Co3(PO4)2P2O7, "instead of"), ADJ-022 (LiFePO4F → LiFeSO4F, "substitution of (SO4) for (PO4)").
- Exclude: 11.
  - unresolved_variable: ADJ-001, 002, 006, 008, 010, 014
  - no_named_parent: ADJ-012, 017, 023
  - not_directed: ADJ-007
  - family_no_composition: ADJ-011
- Ambiguous: 11. ADJ-003, 004, 005, 009, 013, 015, 018, 019, 020, 024, 025.
- Confirmed / error: 0 / 0. This batch has no audit_joint_include rows, so audit_result and error_type are blank.

Quote not found on the cited page:

- ADJ-025 (cited p.41): the quote runs across two pages. It starts on p.41 and continues from "(Fig. 24e). A reversible capacity…" on p.42. The target Na4Ti5O12 isn't on p.41 at all; it appears only on p.45, with no stated link to Li4Ti5O12.

These rows did match once rendering differences were ignored, as the brief allows:

- ADJ-002: "°C" is extracted as "1C".
- ADJ-005: the "ff" ligature in "cutoff" is dropped.
- ADJ-009: "≤" is extracted as "r".

Three rows cite a composition that isn't printed on the cited page:

- ADJ-019: NaV0.96Cr0.04PO4F appears only in the table on p.72.
- ADJ-024: KMnFe[CN]6 appears only in the table on p.72. The text on p.31 says KMFe[CN]6 / Na1.72MFe[CN]6.
- ADJ-012 and ADJ-023: the recorded parents, Na[Ni0.75Mn0.25]O2 and NaMPO4F, aren't printed anywhere in the passage.

A cell-by-cell comparison with adjudication.xlsx shows changes only in the allowed columns for rows 2–26. adjudication.xlsx already showed as modified in git before I started, and I didn't touch it. To read the PDFs I installed the openpyxl, pypdf and pymupdf Python packages.

SHA-256 of adjudication_ai.xlsx: 2b039bd49889dd8c9c8c245861ae15a97657fe103292703975612e0608c13aa8

Stopping here as the brief says; batch 2 is not started.

## Founder notes

- **Brief:** sent without the batch line filled in; Claude Code treated it as batch 1, which was correct.
- **Generated workbook re-saved before batch 1:** the local `adjudication.xlsx` had been re-saved (SHA-256 `0E1829B0DD32FC2003FA5ADAE8AE2643680AAFB5CDFC0C57AAC2BF54B3FB6992`; copy kept at `C:\mg-validation\rrb01-adjudication\adjudication_local_modified.xlsx`). It was restored to the committed version (`1B7777690497093BDDF48848B6430A79183D00DAB3C80E8E2E3632541B9DC444`).
- **Integrity check after restoring:** the cell comparison of `adjudication_ai.xlsx` against the committed `adjudication.xlsx` showed 0 differing generated cells; yellow columns are filled in rows 2–26 only.
- **Software:** Claude Code installed openpyxl, pypdf and pymupdf to read the files.
- **Order:** batch 1 was sent after AMD-002 was tagged. [Confirm, or replace with the actual time if it was earlier.]
