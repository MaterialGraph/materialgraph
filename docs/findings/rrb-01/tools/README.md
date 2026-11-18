# RRB-01 extraction toolkit

Format tooling for the founder extraction (and later the AI extraction) under the
locked protocol `rrb-01-protocol-v0.3.md` (tag `rrb-01-protocol-lock`). It enforces
the schema's format only. It makes no chemistry judgments and never decides whether
a passage qualifies.

## Files

| File | Purpose |
| --- | --- |
| `rrb01_extract.py` | `template`, `validate` and `convert` commands |
| `test_rrb01_extract.py` | Tests, synthetic data only |
| `rrb01_extraction_entry.xlsx` | Blank entry workbook (sheet `records`; sheet `legend` explains fields) |

Requires Python 3.9+, `openpyxl`; tests need `pytest`.

## Use

```
python rrb01_extract.py validate founder_extraction.xlsx
python rrb01_extract.py convert  founder_extraction.xlsx founder_extraction.jsonl
python -m pytest test_rrb01_extract.py
```

`convert` writes nothing unless every row passes, never overwrites an existing file,
and writes `<out>.jsonl.report.json` with the SHA-256 of both the workbook and the JSONL
plus record counts.

## What the converter guarantees

- Text is copied exactly as typed: no trimming, case change or formula normalization.
  Leading or trailing spaces produce a warning and are kept.
- Every row is exported, including `exclude` and `ambiguous`.
- Decisions, parents and reasons are never inferred or changed.
- `parent_normalized` and `target_normalized` are always `null`; normalization is a
  separate step after the extraction is preserved.
- Deterministic output: fixed key order, records sorted by source, page, record number;
  UTF-8; LF line endings.

## Implementation notes (format decisions within the locked schema)

These interpret the locked schema's wording; none changes what qualifies as a pair.

1. `composition_type` ("for parent and target separately") is entered as two columns and
   exported as `{"parent": ..., "target": ...}`. The parent value is `null` when no parent
   is named.
2. `direction_basis`, `relationship_type` and `characterization` are required for
   `include` records and optional otherwise.
3. An empty parent is accepted only with `exclude` / `no_named_parent`, as the record
   trigger requires. A parent entered with `no_named_parent` is a warning, not an error.
4. `confounders` is an open list of snake_case tokens separated by `;`.
5. Cells must be text. A number, date or formula cell is an error, so the spreadsheet
   cannot silently convert values.

## Relationship between the two files

The workbook is the entry interface; the JSONL is the scientific record. Both are
preserved and committed unchanged, and the report file links them by SHA-256.
