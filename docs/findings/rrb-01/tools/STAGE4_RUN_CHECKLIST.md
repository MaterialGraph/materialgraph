# RRB-01 Stage 4: AI extraction run checklist

The rule-reproducibility check: a second, automated application of the locked rules.
It is not independent scientific verification.

## Before the run

- [ ] Founder extraction frozen and verified (Stage 3, commit 57f5af8).
- [ ] Page convention confirmed: the convention used in the founder extraction's
      `record_id` / `location` (`pdf_index` = PDF page counting the file's first page as 1;
      `printed` = journal page number). The AI must use the same one, or comparison keys
      will not match.
- [ ] Package built from the LOCKED protocol file in the repo:
      `python build_ai_package.py docs/findings/rrb-01/rrb-01-protocol-v0.3.md <out_dir> --page-convention <pdf_index|printed>`
- [ ] `ai_extraction_rules.md` read once by you to confirm it contains only rule text
      (no design rationale, no expectations, nothing about the founder extraction's content).
- [ ] Package directory committed (or its manifest hashes recorded) before the run.
- [ ] Both PDFs are the frozen snapshots from `docs/findings/rrb-01/sources/`
      (SHA-256 6832B1BC… Hwang, 8D8991D4… Noerochim).
- [ ] File size checked against the chosen interface's upload limit. If a PDF is too
      large, stop and decide the handling before running (see "Open procedure points").

## Session isolation

- [ ] New chat OUTSIDE the MaterialGraph Project (or the API), with memory off or an
      incognito/temporary chat, and no connectors or web access.
- [ ] Nothing else uploaded: only `ai_extraction_prompt.md` (pasted as the message or
      attached), `ai_extraction_rules.md` and the two PDFs.
- [ ] No follow-up messages except "continue" (for long output) and the format-only
      correction step below.

## Record (run log)

- [ ] Interface and model name/version, settings (e.g. extended thinking on/off).
- [ ] Date and time of the run.
- [ ] SHA-256 of the prompt, rules and both PDFs as uploaded.
- [ ] Full transcript exported or saved unchanged.

## After the run

- [ ] Save the AI's CSV exactly as produced: `ai_extraction.csv`. If it came in several
      replies, join the rows in order without editing them and note this in the log.
- [ ] `python csv_to_workbook.py ai_extraction.csv ai_extraction.xlsx`
- [ ] `python rrb01_extract.py validate ai_extraction.xlsx --extractor ai`
- [ ] If valid: `python rrb01_extract.py convert ai_extraction.xlsx ai_extraction.jsonl --extractor ai`
- [ ] Never edit the AI's records by hand. Commit CSV, workbook, JSONL, report, run log
      and transcript before any comparison (Stage 5).

## Open procedure points (decide and record BEFORE the run)

1. Format errors in the AI output: proposed rule — return the validator's error lines
   verbatim to the same session for a format-only correction, at most twice; preserve
   every version; whatever the AI returns is its output; the founder never edits it.
2. Upload size limit for the Hwang PDF (about 41 MB): handling to be decided before the
   run if the chosen interface rejects it.
