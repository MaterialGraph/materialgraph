# RRB-01 AI adjudication: batch 4 (ADJ-076 to ADJ-093)

Under AMD-002 (tag `rrb-01-amd-002`). Final batch; all 93 rows now have a decision.

| Item | Value |
| --- | --- |
| Adjudicator | Claude Code, model `claude-opus-5-5` |
| Rows | ADJ-076 to ADJ-093 (workbook rows 77–94) |
| Output | `adjudication_ai.xlsx`, SHA-256 after batch 4: `505A65E382BC12CBF4BD5AC2389EF68F16DE8719E8F7044F8758B0FE2B04198D` |
| Counts | include 5, exclude 3, ambiguous 10; confirmed 1, error 14 (15 audit rows) |

## Claude Code report (verbatim)

Model identifier: claude-opus-5-5

Batch 4 (ADJ-076 to ADJ-093) counts. The batch has 3 normalization_failure rows and 15 audit_joint_include rows. No writes were refused.

- Include: 5. ADJ-079, 080, 083, 086, 088.
- Exclude: 3. ADJ-078 (family_no_composition); ADJ-092 and ADJ-093 (not_directed, because they only say "comparable capacity").
- Ambiguous: 10. ADJ-076, 077, 081, 082, 084, 085, 087, 089, 090, 091.
- Confirmed: 1. ADJ-079.
- Error: 14.
  - evidence_not_found: ADJ-080, 083, 084, 085, 086, 087, 088, 089
  - composition_mismatch: ADJ-081, 090
  - no_explicit_direction: ADJ-091, 092, 093
  - variable_or_family: ADJ-082
- ADJ-080, 083, 086 and 088 are marked error only because Run B's quote drops words. Run A's quote supports the pair in each case, so founder_decision stays include.

Quotes not found on the cited page, applying the new rule that omitted words make check1 = no:

- ADJ-077 (A): the sentence is on p.70, but the reference "630" attached to the quote belongs to an earlier sentence, so the quote is altered.
- ADJ-080 (B), 081 (B), 083 (B), 086 (B), 088 (B), 092 (B), 093 (B): words are omitted.
- ADJ-084 (B): the record page is 13; the quote is on p.18.
- ADJ-085 (A): the quote runs from p.15 onto p.16. Run B's quote also omits words.
- ADJ-087 (A and B): both quotes omit words.
- ADJ-089 (A): the quote runs from p.24 onto p.25. Run B's quote is only on p.24.
- ADJ-090 (A): the source prints Na4Co2.4Mn0.3Ni0.32P2O7, not Na4Co2.4Mn0.3Ni0.32P2O7.
- ADJ-090 (B): adds "in Na4Co3(PO4)2P2O7", which isn't on p.29.
- ADJ-076 quotes with "..." marking the cuts. Each piece is verbatim, so I counted check1 = yes.

Rows in ADJ-001 to ADJ-075 whose reason mentions an abridged quote (not changed):

- ADJ-057, 058, 059, 060, 063, 065, 066, 068, 070. In batch 3 these got check1 = yes on the old reading, so under the new rule their check1 would be no and their decisions would be ambiguous.
- ADJ-052 and ADJ-064 also mention an abridged quote, but they were already ambiguous because the quote is on a different page.

I compared every cell with the batch-3 version and with adjudication.xlsx. The only changes are in the allowed columns for rows ADJ-076 to ADJ-093, and all 93 rows now have a founder_decision.

SHA-256 of adjudication_ai.xlsx: 505a65e382bc12cbf4bd5ac2389ef68f16de8719e8f7044f8758b0fe2b04198d

## Founder notes

- **OneDrive sync conflict after batch 4:** the main `adjudication_ai.xlsx` was found holding an older version (SHA-256 `DCCBB2A459093887B17285DDB2999CC587CF11DBBAFC2C2E80C3B00B50629763`, batches 1–3 only; copy kept at `C:\mg-validation\rrb01-adjudication\adjudication_ai_found_DCCBB2A4.xlsx`). Claude Code's batch 4 save survived as the OneDrive conflict copy `adjudication_ai-JithinHP.xlsx` (`505A65E3…`, matching Claude Code's report). The batch 4 version was restored as `adjudication_ai.xlsx` (backup at `C:\mg-validation\rrb01-adjudication\adjudication_ai_batch4_505A65E3.xlsx`) and the conflict copy removed from the repository folder.
- **Integrity check after restoring:** generated cells differing from the committed `adjudication.xlsx`: 0; rows with yellow columns filled: 2–94, count 93; rows without a decision: none. `adjudication.xlsx` unchanged at `1B7777690497093BDDF48848B6430A79183D00DAB3C80E8E2E3632541B9DC444`; `adjudication_ai.xlsx` at `505A65E382BC12CBF4BD5AC2389EF68F16DE8719E8F7044F8758B0FE2B04198D`.
- **Ellipsis quote (ADJ-076):** Claude Code counted a quote with "..." cuts as passing check 1. Under the strict reading stated in the batch 4 brief, cuts are omitted words, so check 1 is no. ADJ-076 is already `ambiguous`, so neither the decision nor the cohort changes. Recorded as a deviation.
- **Audit rows marked error but kept as include (ADJ-080, 083, 086, 088):** the error is in Run B's quote (omitted words); Run A's quote for the same pair passes all checks. The pair itself is supported, so the decision remains include. The error counts against Run B's record, not against the pair.
- **ADJ-090:** the report's two formula strings print identically here; the distinction (probably subscript or bracket formatting) was lost in the report text. The row is `ambiguous`, so the cohort is unaffected.
- **Strict check 1 applied to earlier rows:** confirmed list ADJ-057, 058, 059, 060, 063, 065, 066, 068, 070 (see batch 3 report). ADJ-052 and ADJ-064 were already ambiguous.
