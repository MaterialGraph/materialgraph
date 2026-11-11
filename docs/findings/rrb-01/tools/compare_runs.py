#!/usr/bin/env python3
"""RRB-01 Stage 5: compare Run A and Run B (AMD-001) and build the adjudication workbook.

Usage:
  python compare_runs.py <run_a.normalized.jsonl> <run_b.normalized.jsonl> <out_dir>

Matching (locked comparison keys):
  * Included pairs match on (source, normalized parent, normalized target), direction-
    sensitive. Several occurrences with the same key are paired in record order; extra
    occurrences stay unmatched.
  * Non-included records (exclude or ambiguous) match on (source, page, published parent,
    published target). The page comes from record_id; free-text paragraph positions are
    not compared mechanically. If a key matches more than one record on either side,
    none of those records is matched (reported as unmatched, never forced).

Categories written to the workbook:
  unmatched_a / unmatched_b      a record with no counterpart in the other run
  decision_conflict              matched non-included records whose decisions differ
  jointly_ambiguous              both runs marked the record ambiguous
  normalization_failure          an include whose formulas could not be normalized
                                 (cannot be matched by the include key)
  audit_joint_include            every pair both runs include (AMD-001: audit all)
  audit_joint_exclude_sample     the AMD-001 sample of jointly excluded records
Records only listed (not adjudicated): jointly excluded records outside the sample.

Nothing in the run files is modified. "possible_counterparts" lists other-run records on
the same source and page, as a reading aid only; it is never treated as a match.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ADJ_COLUMNS = [
    "item_id", "category", "a_record_id", "b_record_id", "source", "page",
    "a_decision", "b_decision", "a_parent", "a_target", "b_parent", "b_target",
    "a_exclusion_reason", "b_exclusion_reason", "a_relationship_type",
    "b_relationship_type", "a_characterization", "b_characterization",
    "a_evidence", "b_evidence", "field_differences", "possible_counterparts",
    # founder fills these:
    "founder_decision", "founder_exclusion_reason", "audit_result", "error_type",
    "rule_applied", "reason", "assistance_used",
]
FOUNDER_COLUMNS = ADJ_COLUMNS[ADJ_COLUMNS.index("founder_decision"):]
# Categorical fields only: free-text fields (evidence, direction_basis, location) are
# worded differently by every extractor and would flag nearly every pair.
COMPARED_FIELDS = ["relationship_type", "characterization", "composition_type",
                   "exclusion_reason", "confounders"]


def load(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def order_key(r):
    s, p, n = r["record_id"].split("-")
    return (s, int(p), int(n))


def page(r):
    return int(r["record_id"].split("-")[1])


def include_key(r):
    if r["decision"] != "include":
        return None
    if r["target_normalized"] is None or (r["parent_as_published"] is not None
                                          and r["parent_normalized"] is None):
        return None
    return (r["source"], r["parent_normalized"], r["target_normalized"])


def other_key(r):
    if r["decision"] == "include":
        return None
    return (r["source"], page(r), r["parent_as_published"], r["target_as_published"])


def field_diffs(a, b):
    return [f for f in COMPARED_FIELDS if a.get(f) != b.get(f)]


def audit_sample(n):
    """AMD-001: positions 1, 6, 11, ... then earliest unselected until min(10, n)."""
    chosen = list(range(0, n, 5))
    target = min(10, n)
    i = 0
    while len(chosen) < target:
        if i not in chosen:
            chosen.append(i)
        i += 1
    return sorted(chosen)


def compare(a_recs, b_recs):
    a_recs = sorted(a_recs, key=order_key)
    b_recs = sorted(b_recs, key=order_key)
    matched_inc, matched_other = [], []
    used_a, used_b = set(), set()

    # includes: pair occurrences in record order per key
    ka, kb = defaultdict(list), defaultdict(list)
    for r in a_recs:
        if include_key(r):
            ka[include_key(r)].append(r)
    for r in b_recs:
        if include_key(r):
            kb[include_key(r)].append(r)
    for k in sorted(set(ka) & set(kb)):
        for ra, rb in zip(ka[k], kb[k]):
            matched_inc.append((ra, rb))
            used_a.add(ra["record_id"]); used_b.add(rb["record_id"])

    # non-includes: unique keys only
    oa, ob = defaultdict(list), defaultdict(list)
    for r in a_recs:
        if other_key(r):
            oa[other_key(r)].append(r)
    for r in b_recs:
        if other_key(r):
            ob[other_key(r)].append(r)
    for k in sorted(set(oa) & set(ob), key=str):
        if len(oa[k]) == 1 and len(ob[k]) == 1:
            matched_other.append((oa[k][0], ob[k][0]))
            used_a.add(oa[k][0]["record_id"]); used_b.add(ob[k][0]["record_id"])

    unmatched_a = [r for r in a_recs if r["record_id"] not in used_a]
    unmatched_b = [r for r in b_recs if r["record_id"] not in used_b]
    joint_excl = [(x, y) for x, y in matched_other
                  if x["decision"] == "exclude" and y["decision"] == "exclude"]
    joint_amb = [(x, y) for x, y in matched_other
                 if x["decision"] == "ambiguous" and y["decision"] == "ambiguous"]
    conflicts = [(x, y) for x, y in matched_other if x["decision"] != y["decision"]]
    joint_excl.sort(key=lambda p: order_key(p[0]))
    sample_idx = audit_sample(len(joint_excl))
    return {
        "matched_includes": matched_inc, "joint_excluded": joint_excl,
        "joint_ambiguous": joint_amb, "decision_conflicts": conflicts,
        "unmatched_a": unmatched_a, "unmatched_b": unmatched_b,
        "sample_idx": sample_idx, "a_recs": a_recs, "b_recs": b_recs,
    }


def counterparts(r, others):
    return "; ".join(o["record_id"] for o in others
                     if o["source"] == r["source"] and page(o) == page(r))


def row(category, a, b, others_a, others_b):
    get = lambda r, f: (r or {}).get(f)
    rec = a or b
    cp = ""
    if a and not b:
        cp = counterparts(a, others_b)
    elif b and not a:
        cp = counterparts(b, others_a)
    return {
        "category": category,
        "a_record_id": get(a, "record_id"), "b_record_id": get(b, "record_id"),
        "source": rec["source"], "page": page(rec),
        "a_decision": get(a, "decision"), "b_decision": get(b, "decision"),
        "a_parent": get(a, "parent_as_published"), "a_target": get(a, "target_as_published"),
        "b_parent": get(b, "parent_as_published"), "b_target": get(b, "target_as_published"),
        "a_exclusion_reason": get(a, "exclusion_reason"),
        "b_exclusion_reason": get(b, "exclusion_reason"),
        "a_relationship_type": get(a, "relationship_type"),
        "b_relationship_type": get(b, "relationship_type"),
        "a_characterization": get(a, "characterization"),
        "b_characterization": get(b, "characterization"),
        "a_evidence": get(a, "evidence"), "b_evidence": get(b, "evidence"),
        "field_differences": ", ".join(field_diffs(a, b)) if a and b else None,
        "possible_counterparts": cp or None,
    }


def build_rows(res):
    A, B = res["a_recs"], res["b_recs"]
    rows = []
    for r in res["unmatched_a"]:
        failed = r["decision"] == "include" and include_key(r) is None
        rows.append(row("normalization_failure" if failed else "unmatched_a", r, None, A, B))
    for r in res["unmatched_b"]:
        failed = r["decision"] == "include" and include_key(r) is None
        rows.append(row("normalization_failure" if failed else "unmatched_b", None, r, A, B))
    for a, b in res["decision_conflicts"]:
        rows.append(row("decision_conflict", a, b, A, B))
    for a, b in res["joint_ambiguous"]:
        rows.append(row("jointly_ambiguous", a, b, A, B))
    for a, b in res["matched_includes"]:
        rows.append(row("audit_joint_include", a, b, A, B))
    for i in res["sample_idx"]:
        a, b = res["joint_excluded"][i]
        rows.append(row("audit_joint_exclude_sample", a, b, A, B))
    order = ["unmatched_a", "unmatched_b", "normalization_failure", "decision_conflict",
             "jointly_ambiguous", "audit_joint_include", "audit_joint_exclude_sample"]
    rows.sort(key=lambda r: (order.index(r["category"]), r["source"], r["page"],
                             r["a_record_id"] or "", r["b_record_id"] or ""))
    for n, r in enumerate(rows, start=1):
        r["item_id"] = f"ADJ-{n:03d}"
    return rows


def write_workbook(rows, path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "adjudication"
    ws.append(ADJ_COLUMNS)
    head = Font(name="Arial", size=10, bold=True)
    body = Font(name="Arial", size=10)
    for c in ws[1]:
        c.font = head
        c.fill = PatternFill("solid", start_color="D9E1F2")
    for r in rows:
        ws.append([r.get(c) for c in ADJ_COLUMNS])
    yellow = PatternFill("solid", start_color="FFF2CC")
    for i, col in enumerate(ADJ_COLUMNS, start=1):
        letter = ws.cell(row=1, column=i).column_letter
        ws.column_dimensions[letter].width = 48 if "evidence" in col or col == "reason" else 20
        for rr in range(2, len(rows) + 2):
            cell = ws.cell(row=rr, column=i)
            cell.font = body
            cell.number_format = "@"
            cell.alignment = Alignment(wrap_text="evidence" in col or col == "reason",
                                       vertical="top")
            if col in FOUNDER_COLUMNS:
                cell.fill = yellow
    ws.freeze_panes = "C2"

    def dropdown(col, values):
        letter = ws.cell(row=1, column=ADJ_COLUMNS.index(col) + 1).column_letter
        dv = DataValidation(type="list", formula1='"' + ",".join(values) + '"',
                            allow_blank=True, showErrorMessage=True)
        ws.add_data_validation(dv)
        dv.add(f"{letter}2:{letter}{max(len(rows) + 1, 2)}")

    dropdown("founder_decision", ["include", "exclude", "ambiguous"])
    dropdown("audit_result", ["confirmed", "error"])
    wb.save(path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3:
        sys.exit(__doc__)
    pa, pb, out = Path(argv[0]), Path(argv[1]), Path(argv[2])
    if out.exists():
        sys.exit(f"Refusing to write into existing directory: {out}")
    res = compare(load(pa), load(pb))
    rows = build_rows(res)
    out.mkdir(parents=True)
    write_workbook(rows, out / "adjudication.xlsx")
    listing = [{"a_record_id": a["record_id"], "b_record_id": b["record_id"],
                "in_audit_sample": i in res["sample_idx"]}
               for i, (a, b) in enumerate(res["joint_excluded"])]
    (out / "jointly_excluded.json").write_text(json.dumps(listing, indent=2) + "\n",
                                               encoding="utf-8", newline="\n")
    counts = defaultdict(int)
    for r in rows:
        counts[r["category"]] += 1
    report = {
        "run_a": pa.name, "run_a_sha256": sha(pa), "run_b": pb.name, "run_b_sha256": sha(pb),
        "run_a_records": len(res["a_recs"]), "run_b_records": len(res["b_recs"]),
        "matched_includes": len(res["matched_includes"]),
        "matched_includes_with_field_differences":
            sum(bool(field_diffs(a, b)) for a, b in res["matched_includes"]),
        "jointly_excluded": len(res["joint_excluded"]),
        "jointly_excluded_audit_sample": len(res["sample_idx"]),
        "jointly_ambiguous": len(res["joint_ambiguous"]),
        "decision_conflicts": len(res["decision_conflicts"]),
        "unmatched_a": len(res["unmatched_a"]), "unmatched_b": len(res["unmatched_b"]),
        "workbook_rows_by_category": dict(sorted(counts.items())),
        "adjudication_xlsx_sha256": sha(out / "adjudication.xlsx"),
    }
    (out / "comparison_report.json").write_text(json.dumps(report, indent=2) + "\n",
                                                encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
