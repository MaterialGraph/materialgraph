#!/usr/bin/env python3
"""RRB-01 Stage 4: load the AI's CSV into the standard entry workbook.

Usage:
  python csv_to_workbook.py <ai_extraction.csv> <ai_extraction.xlsx>

Then validate and convert exactly as for the founder extraction, with --extractor ai:
  python rrb01_extract.py validate ai_extraction.xlsx --extractor ai
  python rrb01_extract.py convert  ai_extraction.xlsx ai_extraction.jsonl --extractor ai

Strict by design: the header must match the template columns exactly, every value is
written as text unchanged (no trimming, no fixing), "" becomes an empty cell, and an
existing output file is never overwritten. Rows with the wrong number of fields stop
the conversion; nothing is repaired. The CSV itself is kept as the raw AI output.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import rrb01_extract as tool


def load_csv(path: Path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        sys.exit("CSV is empty.")
    header, body = rows[0], rows[1:]
    if header != tool.COLUMNS:
        sys.exit("CSV header does not match the template columns.\n"
                 f"Expected: {tool.COLUMNS}\nFound:    {header}")
    bad = [i for i, r in enumerate(body, start=2) if len(r) != len(tool.COLUMNS)]
    if bad:
        sys.exit(f"CSV line(s) {bad} do not have {len(tool.COLUMNS)} fields. "
                 "Nothing was written.")
    return body


def write_workbook(rows, out: Path):
    from openpyxl import load_workbook

    if out.exists():
        sys.exit(f"Refusing to overwrite existing file: {out}")
    tmp = out.with_name(out.stem + ".tmp-template.xlsx")
    if tmp.exists():
        tmp.unlink()
    tool.write_template(tmp)
    wb = load_workbook(tmp)
    ws = wb[tool.SHEET]
    for i, row in enumerate(rows, start=2):
        for j, value in enumerate(row, start=1):
            cell = ws.cell(row=i, column=j)
            cell.value = value if value != "" else None
            cell.data_type = "s" if value != "" else cell.data_type
    wb.save(out)
    tmp.unlink()
    print(f"{len(rows)} row(s) written to {out}")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        sys.exit(__doc__)
    write_workbook(load_csv(Path(argv[0])), Path(argv[1]))


if __name__ == "__main__":
    main()
