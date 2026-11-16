# RRB-01 founder spot-check of the AI adjudication (AMD-002 section 4)

Checked by: Jithin Mathews
Date: 2026-11-16
Workbook checked: `comparison/adjudication_ai.xlsx` (SHA-256 505A65E382BC12CBF4BD5AC2389EF68F16DE8719E8F7044F8758B0FE2B04198D)
Rows: fixed in AMD-002 before any AI decision existed (every 9th row from ADJ-001).

Method, for each row: read the page and evidence quote in the workbook (a_evidence or
b_evidence), open the PDF at that page (HWA17 = Hwang, NOE21 = Noerochim; PDF page
count), search with Ctrl+F for 4–5 distinctive words of the quote, and compare with the
AI's check 1 (the start of its reason). No chemistry judgment is made.

| Row | Source | Page | Words searched | Found on that page? | AI check 1 | Agree? | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADJ-001 | HWA17 | 3 | Despite the remarkable cyclability over 300 | yes | yes | yes | |
| ADJ-010 | HWA17 | 11 | Yang et al.77 successfully stabilized the | yes | yes | yes | |
| ADJ-019 | HWA17 | 25 | Cr-doping into the V site of | yes | yes | yes | |
| ADJ-028 | HWA17 | 61 | Zhao et al. proposed bismuth (Bi) | yes | yes | yes | |
| ADJ-037 | NOE21 | 4 | LiNi0.95Mg0.05O2 yielded a lower initial discharge | yes | yes | yes | |
| ADJ-046 | NOE21 | 9 | It is reported that the LiNiO2 | yes | yes | yes | |
| ADJ-055 | HWA17 | 16 | Zn-substituted P2-Na2/3[Ni1/3-xZnxMn2/3]O2 induces | yes | yes | yes | Formula spans a line break |
| ADJ-064 | NOE21 | 4 | cobalt substitution LiNi0.95Co0.05O2 does not improve | no | no | yes | Not on p.4. A near match is on p.5: "cobalt substitution (LiNi0.95Co0.05O2) does not improve…"; the quote drops the brackets, so it is not verbatim. |
| ADJ-073 | HWA17 | 25 | NaVPO4F has tetragonal symmetry with a | yes | yes | yes | Quote spans the column break |
| ADJ-082 | HWA17 | 12 | Recently, Matsui et al. explored the | yes | yes | yes | |
| ADJ-091 | NOE21 | 1 | Cobalt is the main element of | yes | yes | yes | |

For rows with both a Run A and a Run B quote, check the one the AI's reason refers to, or
both, and say which in the note.

Summary: 11 of 11 agree. Disagreements: none. Note: ADJ-064's quote is cited to p.4 but a near match (brackets dropped) is on p.5; the AI's check 1 correctly reported "not found on the cited page".

A blank copy of this template was merged in #126 by mistake before the check was done; this version, completed 2026-11-16, contains the actual check.
