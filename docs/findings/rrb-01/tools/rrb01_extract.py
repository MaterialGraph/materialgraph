#!/usr/bin/env python3
"""RRB-01 extraction toolkit (format only; makes no chemistry judgments).

Commands
  template <out.xlsx>                      write a blank entry workbook
  validate <in.xlsx> [--extractor founder]  check every row, write nothing
  convert  <in.xlsx> <out.jsonl> [--extractor founder]
                                           validate, then write JSONL + report

Guarantees (RRB-01 protocol lock, extraction schema):
  * Text is copied exactly as entered: no trimming, case changes or
    formula normalization. Whitespace problems are reported, never fixed.
  * Every row is exported, including excludes and ambiguous records.
  * Decisions, parents and reasons are never inferred or altered.
  * parent_normalized / target_normalized are always null here; a separate
    normalization step fills them after the extraction is preserved.
  * Output is deterministic (fixed key order, record order, UTF-8, LF) and
    an existing output file is never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = "rrb01-extract-1"
SHEET = "records"

# Spreadsheet columns, in order. composition_type is entered as two columns
# and exported as {"parent": ..., "target": ...}.
COLUMNS = [
    "record_id", "source", "location", "evidence", "cited_primary_study",
    "parent_as_published", "target_as_published",
    "parent_composition_type", "target_composition_type",
    "direction_basis", "relationship_type", "characterization",
    "confounders", "decision", "exclusion_reason", "ambiguity_note",
]

SOURCES = {"HWA17", "NOE21"}
EXTRACTORS = {"founder", "ai"}
COMPOSITION_TYPES = {
    "fixed_integer", "fixed_fractional", "fixed_doped", "unresolved_variable",
    "variable_with_stated_value", "family_no_composition",
    "spatially_heterogeneous",
}
RELATIONSHIP_TYPES = {"cross_chemistry_analog", "within_family_substitution"}
CHARACTERIZATIONS = {
    "formula_or_structural_analog", "proposed_replacement",
    "experimentally_evaluated_substitute",
}
DECISIONS = {"include", "exclude", "ambiguous"}
EXCLUSION_REASONS = {
    "no_named_parent", "not_directed", "synthesis_route_only",
    "morphology_or_surface_only", "spatially_heterogeneous",
    "unresolved_variable", "family_no_composition",
}
RECORD_ID = re.compile(r"^(HWA17|NOE21)-([1-9][0-9]*)-([1-9][0-9]*)$")
CONFOUNDER_TOKEN = re.compile(r"^[a-z][a-z0-9_]*$")
MAX_EVIDENCE_WORDS = 40

# JSONL key order (locked schema order).
OUTPUT_KEYS = [
    "schema_version", "extractor", "record_id", "source", "location",
    "evidence", "cited_primary_study", "parent_as_published",
    "target_as_published", "composition_type", "direction_basis",
    "relationship_type", "characterization", "confounders", "decision",
    "exclusion_reason", "ambiguity_note", "parent_normalized",
    "target_normalized",
]


class Problem:
    def __init__(self, row, field, message, error=True):
        self.row, self.field, self.message, self.error = row, field, message, error

    def __str__(self):
        kind = "ERROR" if self.error else "WARNING"
        return f"{kind} row {self.row} [{self.field}]: {self.message}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


# ---------------------------------------------------------------- template
def write_template(out: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.worksheet.datavalidation import DataValidation

    if out.exists():
        sys.exit(f"Refusing to overwrite existing file: {out}")
    wb = Workbook()
    ws = wb.active
    ws.title = SHEET
    font = Font(name="Arial", size=10)
    head = Font(name="Arial", size=10, bold=True)
    fill = PatternFill("solid", start_color="FFF2CC")
    ws.append(COLUMNS)
    for c in ws[1]:
        c.font = head
        c.fill = PatternFill("solid", start_color="D9E1F2")
    widths = {"evidence": 60, "location": 28, "direction_basis": 40,
              "ambiguity_note": 40, "cited_primary_study": 24}
    for i, name in enumerate(COLUMNS, start=1):
        letter = ws.cell(row=1, column=i).column_letter
        ws.column_dimensions[letter].width = widths.get(name, 22)
        # Text format for every entry cell so Excel never converts values
        # (e.g. "1/3" to a date, "12" to a number).
        for r in range(2, 2001):
            cell = ws.cell(row=r, column=i)
            cell.number_format = "@"
            cell.font = font
            cell.fill = fill
            cell.alignment = Alignment(wrap_text=name in widths, vertical="top")
    ws.freeze_panes = "B2"

    def dropdown(col_name, values):
        col = ws.cell(row=1, column=COLUMNS.index(col_name) + 1).column_letter
        dv = DataValidation(type="list", formula1='"' + ",".join(sorted(values)) + '"',
                            allow_blank=True, showErrorMessage=True)
        ws.add_data_validation(dv)
        dv.add(f"{col}2:{col}2000")

    dropdown("source", SOURCES)
    dropdown("parent_composition_type", COMPOSITION_TYPES)
    dropdown("target_composition_type", COMPOSITION_TYPES)
    dropdown("relationship_type", RELATIONSHIP_TYPES)
    dropdown("characterization", CHARACTERIZATIONS)
    dropdown("decision", DECISIONS)
    dropdown("exclusion_reason", EXCLUSION_REASONS)

    leg = wb.create_sheet("legend")
    rows = [
        ("RRB-01 founder extraction entry workbook", ""),
        ("", ""),
        ("Where to type", "Sheet 'records', yellow cells only, one row per record. "
                          "Every cell is formatted as text; keep it that way."),
        ("Converter", "python rrb01_extract.py convert <this.xlsx> <out.jsonl>"),
        ("Rules", "The locked protocol (rrb-01-protocol-v0.3.md) defines what creates a "
                  "record and every field. This workbook only enforces format."),
        ("record_id", "<source>-<page>-<n>, n = record number on that page in reading order. "
                      "Example: NOE21-4-2"),
        ("parent_as_published", "Leave empty only when the source names no parent; such a "
                                "record must be exclude / no_named_parent."),
        ("composition types", "parent_composition_type is empty when the parent is empty."),
        ("include records", "need direction_basis, relationship_type and characterization."),
        ("exclude records", "need exclusion_reason; ambiguity_note stays empty."),
        ("ambiguous records", "need ambiguity_note; exclusion_reason stays empty."),
        ("confounders", "snake_case tokens separated by ';' e.g. morphology_change;coating"),
        ("cited_primary_study", "Reference number and DOI as printed, or the word none."),
        ("evidence", f"Quote exactly as printed, at most {MAX_EVIDENCE_WORDS} words."),
        ("", ""),
        ("Format example (synthetic, not from either source)", ""),
        ("record_id", "NOE21-99-1"),
        ("location", "p.99, section 9.9, paragraph 2"),
        ("evidence", "AbX2 was replaced by AbY2 to improve stability."),
        ("cited_primary_study", "[999] 10.0000/example"),
        ("parent / target", "AbX2 / AbY2   (types: fixed_integer / fixed_integer)"),
        ("direction_basis", "was replaced by"),
        ("relationship / characterization", "within_family_substitution / proposed_replacement"),
        ("decision", "include"),
    ]
    for a, b in rows:
        leg.append([a, b])
    for row in leg.iter_rows():
        for c in row:
            c.font = font
    leg["A1"].font = Font(name="Arial", size=12, bold=True)
    leg["A16"].font = head
    leg.column_dimensions["A"].width = 34
    leg.column_dimensions["B"].width = 100
    wb.save(out)
    print(f"Template written: {out}")


# ---------------------------------------------------------------- reading
def read_rows(path: Path):
    """Yield (excel_row_number, {column: raw value}) for non-empty rows."""
    from openpyxl import load_workbook

    wb = load_workbook(path, data_only=False, read_only=True)
    if SHEET not in wb.sheetnames:
        sys.exit(f"Workbook has no sheet named '{SHEET}'")
    ws = wb[SHEET]
    it = ws.iter_rows(values_only=True)
    header = list(next(it, []) or [])
    header = [h for h in header if h is not None]
    if header != COLUMNS:
        sys.exit("Header row does not match the locked column list.\n"
                 f"Expected: {COLUMNS}\nFound:    {header}")
    for n, values in enumerate(it, start=2):
        values = list(values[:len(COLUMNS)]) + [None] * (len(COLUMNS) - len(values))
        if all(v is None or v == "" for v in values):
            continue
        yield n, dict(zip(COLUMNS, values))


# ---------------------------------------------------------------- validation
def validate_rows(rows, extractor: str):
    problems, records, seen = [], [], {}

    for n, raw in rows:
        p = []

        def err(field, msg):
            p.append(Problem(n, field, msg))

        def warn(field, msg):
            p.append(Problem(n, field, msg, error=False))

        val = {}
        for k, v in raw.items():
            if v is None or v == "":
                val[k] = None
            elif isinstance(v, str):
                val[k] = v
                if v != v.strip():
                    warn(k, "leading or trailing whitespace (kept as entered)")
                if v.startswith("="):
                    err(k, "value starts with '=' (spreadsheet formula); enter text")
            else:
                err(k, f"cell is {type(v).__name__}, not text; format the cell as "
                       "text and retype it")
                val[k] = None

        def required(field):
            if val[field] is None:
                err(field, "required")

        def enum(field, allowed):
            if val[field] is not None and val[field] not in allowed:
                err(field, f"'{val[field]}' is not one of {sorted(allowed)}")

        for f in ("record_id", "source", "location", "evidence",
                  "cited_primary_study", "target_as_published",
                  "target_composition_type", "decision"):
            required(f)
        enum("source", SOURCES)
        enum("parent_composition_type", COMPOSITION_TYPES)
        enum("target_composition_type", COMPOSITION_TYPES)
        enum("relationship_type", RELATIONSHIP_TYPES)
        enum("characterization", CHARACTERIZATIONS)
        enum("decision", DECISIONS)
        enum("exclusion_reason", EXCLUSION_REASONS)

        rid = val["record_id"]
        if rid is not None:
            m = RECORD_ID.match(rid)
            if not m:
                err("record_id", f"'{rid}' does not match <HWA17|NOE21>-<page>-<n>")
            elif val["source"] is not None and m.group(1) != val["source"]:
                err("record_id", f"prefix {m.group(1)} does not match source {val['source']}")
            if rid in seen:
                err("record_id", f"duplicate of row {seen[rid]}")
            else:
                seen[rid] = n

        if val["evidence"] is not None:
            words = len(val["evidence"].split())
            if words > MAX_EVIDENCE_WORDS:
                err("evidence", f"{words} words; limit is {MAX_EVIDENCE_WORDS}")

        parent = val["parent_as_published"]
        if parent is None and val["parent_composition_type"] is not None:
            err("parent_composition_type", "must be empty when the parent is empty")
        if parent is not None and val["parent_composition_type"] is None:
            err("parent_composition_type", "required when a parent is entered")
        if parent is None and not (val["decision"] == "exclude"
                                   and val["exclusion_reason"] == "no_named_parent"):
            err("parent_as_published", "empty parent requires decision exclude "
                                       "with reason no_named_parent")
        if parent is not None and val["exclusion_reason"] == "no_named_parent":
            warn("exclusion_reason", "no_named_parent but a parent is entered; check")

        d = val["decision"]
        if d == "include":
            for f in ("direction_basis", "relationship_type", "characterization"):
                required(f)
        if d == "exclude":
            required("exclusion_reason")
        elif val["exclusion_reason"] is not None:
            err("exclusion_reason", "only allowed when decision is exclude")
        if d == "ambiguous":
            required("ambiguity_note")
        elif val["ambiguity_note"] is not None:
            err("ambiguity_note", "only allowed when decision is ambiguous")

        confounders = []
        if val["confounders"] is not None:
            confounders = val["confounders"].split(";")
            for t in confounders:
                if not CONFOUNDER_TOKEN.match(t):
                    err("confounders", f"'{t}' is not a snake_case token "
                                       "(separate tokens with ';', no spaces)")

        problems.extend(p)
        if not any(x.error for x in p):
            records.append({
                "schema_version": SCHEMA_VERSION,
                "extractor": extractor,
                "record_id": rid,
                "source": val["source"],
                "location": val["location"],
                "evidence": val["evidence"],
                "cited_primary_study": val["cited_primary_study"],
                "parent_as_published": parent,
                "target_as_published": val["target_as_published"],
                "composition_type": {"parent": val["parent_composition_type"],
                                     "target": val["target_composition_type"]},
                "direction_basis": val["direction_basis"],
                "relationship_type": val["relationship_type"],
                "characterization": val["characterization"],
                "confounders": confounders,
                "decision": d,
                "exclusion_reason": val["exclusion_reason"],
                "ambiguity_note": val["ambiguity_note"],
                "parent_normalized": None,
                "target_normalized": None,
            })
    return problems, records


def sort_key(rec):
    m = RECORD_ID.match(rec["record_id"])
    return (m.group(1), int(m.group(2)), int(m.group(3)))


def to_jsonl(records) -> bytes:
    lines = []
    for r in sorted(records, key=sort_key):
        ordered = {k: r[k] for k in OUTPUT_KEYS}
        lines.append(json.dumps(ordered, ensure_ascii=False, separators=(",", ":")))
    return ("\n".join(lines) + "\n").encode("utf-8") if lines else b""


# ---------------------------------------------------------------- commands
def run_validate(path: Path, extractor: str):
    problems, records = validate_rows(read_rows(path), extractor)
    for p in problems:
        print(p)
    errors = sum(p.error for p in problems)
    warnings = len(problems) - errors
    print(f"\n{len(records)} valid record(s); {errors} error(s); {warnings} warning(s)")
    return problems, records, errors


def run_convert(src: Path, out: Path, extractor: str):
    if out.exists():
        sys.exit(f"Refusing to overwrite existing file: {out}")
    _, records, errors = run_validate(src, extractor)
    if errors:
        sys.exit("Conversion stopped: fix every ERROR first. Nothing was written.")
    data = to_jsonl(records)
    out.write_bytes(data)
    counts = {d: sum(r["decision"] == d for r in records) for d in sorted(DECISIONS)}
    report = {
        "schema_version": SCHEMA_VERSION,
        "extractor": extractor,
        "input_xlsx": src.name,
        "input_xlsx_sha256": sha256_file(src),
        "output_jsonl": out.name,
        "output_jsonl_sha256": sha256_file(out),
        "record_count": len(records),
        "decision_counts": counts,
        "source_counts": {s: sum(r["source"] == s for r in records) for s in sorted(SOURCES)},
    }
    rep = out.with_suffix(out.suffix + ".report.json")
    if rep.exists():
        sys.exit(f"JSONL written, but report already exists and was not overwritten: {rep}")
    rep.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template"); t.add_argument("out", type=Path)
    v = sub.add_parser("validate"); v.add_argument("src", type=Path)
    v.add_argument("--extractor", choices=sorted(EXTRACTORS), default="founder")
    c = sub.add_parser("convert"); c.add_argument("src", type=Path); c.add_argument("out", type=Path)
    c.add_argument("--extractor", choices=sorted(EXTRACTORS), default="founder")
    a = ap.parse_args(argv)
    if a.cmd == "template":
        write_template(a.out)
    elif a.cmd == "validate":
        _, _, errors = run_validate(a.src, a.extractor)
        sys.exit(1 if errors else 0)
    else:
        run_convert(a.src, a.out, a.extractor)


if __name__ == "__main__":
    main()
