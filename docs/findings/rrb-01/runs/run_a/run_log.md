# RRB-01 Run A (AMD-001)

Note: this log was written after the run, on 11/11/2026, from the interface, the saved
transcript and the files below. It was not filled in during the run.

- Interface: Google AI Studio
- Model: Gemini 3.8 Flash (model ID shown: gemini-3.8-flash)
- Settings: thinking level Medium; all tools off (structured outputs, code execution,
  function calling, Google Search grounding, Google Maps grounding, URL context);
  system instructions empty; temperature [value shown under Advanced settings, or "default, not checked"]
- Date: [date]; coverage question answered 3:32 PM; extraction reply took about 2m38s
- Files uploaded: ai_extraction_rules.md (56BCD216…), Hwang PDF (6832B1BC…),
  Noerochim PDF (8D8991D4…); prompt = full text of ai_extraction_prompt.md (F78AA952…)
  pasted as the first message
- Follow-up messages, in order:
  1. [number] x "continue" [or "none"]
  2. "List every page of each PDF that you did not fully process, or reply 'none'."
  3. Format correction 1: the 16 ERROR lines from the validator, sent verbatim
- Coverage answer: "none"
- Outputs:
  - ai_extraction.csv: v1, 77 rows, 16 errors
  - ai_extraction_v2.csv: v2, 75 rows (two fewer than v1), 0 errors; final
  - ai_extraction_v2.xlsx: SHA-256 9D946958B2E9DD0B1368F79748D9FD6FD6817B0A19D4E1C4B7B24C9D42CD3E39
  - run_a.jsonl: SHA-256 4BD46AA7BC7F5E9C9785CE95B52DF1899813B1656094D3C427672FED8A86C05C
    (75 records: include 53, exclude 22, ambiguous 0; HWA17 48, NOE21 27)
- Transcript: AI Studio prompt file downloaded from Google Drive, saved as `transcript`,
  SHA-256 [new hash after re-downloading]. Print-to-PDF captured only the page frame,
  so the Drive file was used. Share link (pointer only): [URL]
- Page diagnostic (pages with at least one record; a page without records is not
  proof the page was skipped):
  - HWA17: 21 of 86 pages: 3, 6, 7, 9, 10, 11, 12, 14, 15, 16, 24, 25, 27, 28, 29, 31, 41, 60, 61, 62, 70
  - NOE21: 10 of 16 pages: 1–7, 9, 10, 11
- Manual steps: [e.g. "removed ``` fence lines from the copied CSV", or "none"]
- Problems: [any, or "none"]
- Raw transcript: C:\mg-validation\rrb01-runs\run_a\transcript_raw.json, 61,506,354 bytes, SHA-256 12DBFA67A1444DB8903D54E3CECB3FC044F2EEBD7977FCD0B63E68CA24B40970, backed up off the laptop.
- Committed transcript: transcript_reduced.json, SHA-256 0C8C5FBE038D30171533C6C63FC8EB6565B660CA508DF912293042B1786A6DCE, made with tools/reduce_transcript.py, which replaces embedded files with size and SHA-256 placeholders.
- Embedded sources verified: both PDF hashes equal the frozen sources.
- Gitleaks: the raw transcript tripped five AWS-key pattern matches inside the embedded Hwang PDF data, which were false positives. The reduced transcript passes.
- Rules file: the result of the check above.