#!/usr/bin/env python3
"""RRB-01 Stage 6: build the benchmark cohort from the adjudicated AI extractions.

Usage:
  python build_cohort.py <adjudication_ai.xlsx> <run_a.normalized.jsonl>
                         <run_b.normalized.jsonl> <materials.csv> <out_dir>
                         [--labels label_resolutions.csv]

What it does (protocol v0.3 "Classification layers", AMD-001, AMD-002, AMD-003):
  1. Takes each record's decision from founder_decision in the adjudication workbook
     (one row per record or per jointly included pair). Rows listed in
     STRICT_CHECK1_AMBIGUOUS are read as ambiguous (AMD-002 check 1 read strictly:
     omitted words are not an allowed difference; see batch 3 and 4 reports). The
     workbook is never modified.
  2. Non-included records get status P with their reason. Included records whose
     parent or target does not normalize are resolved through label_resolutions.csv
     (AMD-003) or get status P, reason label_unresolved. They are listed in
     label_resolutions_needed.csv.
  3. Occurrences of the same normalized directed pair (both sources, both runs) collapse
     into one case. Non-included occurrences with the same normalized pair are listed in
     the case's audit trail but never make it qualify.
  4. Each case is classified N > X > E > I against the frozen dataset export, gets
     Avoid/Prefer, its parent record (lowest numeric MP-ID, then MP-ID string, then
     local id) with the full ordered match list, and its family key.
  5. The two development pairs are reported separately and never enter the cohort.

Writes into <out_dir> (must not exist): cohort.json, development_cases.json,
p_records.json, label_resolutions_needed.csv, dataset_normalization.json,
cohort_report.json. No input file is modified. Nothing is guessed: any inconsistency
in the inputs stops the script before anything is written.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from normalize_formulas import NormalizationError, normalize

# AMD-002 check 1 read strictly (batch 3 founder notes; batch 4 report and notes).
STRICT_CHECK1_AMBIGUOUS = {"ADJ-057", "ADJ-058", "ADJ-059", "ADJ-060", "ADJ-063",
                           "ADJ-065", "ADJ-066", "ADJ-068", "ADJ-070", "ADJ-076"}
DEVELOPMENT_PAIRS = [("LiFePO4", "NaFePO4"), ("Li3Fe2(PO4)3", "Na3Fe2(PO4)3")]
LABEL_COLUMNS = ["label", "formula_as_printed", "source", "page", "defining_text",
                 "record_ids", "verified_by"]
NEEDED_COLUMNS = ["run", "record_id", "item_id", "side", "as_published", "source",
                  "page", "normalizer_note", "evidence"]
SOURCE_ORDER = {"HWA17": 0, "NOE21": 1}
RUNS = ("a", "b")


def fail(msg):
    sys.exit("STOPPED, nothing written: " + msg)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def load_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines()
            if l.strip()]


def rec_order(run, rec_id):
    s, p, n = rec_id.split("-")
    return (SOURCE_ORDER.get(s, 9), s, int(p), int(n), RUNS.index(run))


def page_of(rec_id):
    return int(rec_id.split("-")[1])


def elements(canon):
    return set(re.findall(r"[A-Z][a-z]?", canon))


def cell(v):
    if v is None:
        return None
    v = str(v).strip()
    return v or None


# ---------------------------------------------------------------- decisions

def read_adjudication(path):
    from openpyxl import load_workbook
    ws = load_workbook(path, read_only=True, data_only=True)["adjudication"]
    rows = ws.iter_rows(values_only=True)
    head = [cell(h) for h in next(rows)]
    need = ["item_id", "category", "a_record_id", "b_record_id", "founder_decision",
            "founder_exclusion_reason"]
    missing = [c for c in need if c not in head]
    if missing:
        fail(f"adjudication workbook lacks columns {missing}")
    out = []
    for r in rows:
        d = {c: cell(r[head.index(c)]) for c in need}
        if d["item_id"] is None:
            continue
        out.append(d)
    return out


def decisions(adj_rows, runs):
    """Return {(run, record_id): decision dict}. Stops on any gap or double mapping."""
    out = {}
    for row in adj_rows:
        dec = row["founder_decision"]
        if dec not in ("include", "exclude", "ambiguous"):
            fail(f"{row['item_id']}: founder_decision is {dec!r}")
        strict = row["item_id"] in STRICT_CHECK1_AMBIGUOUS
        final = "ambiguous" if strict else dec
        refs = [(run, row[f"{run}_record_id"]) for run in RUNS if row[f"{run}_record_id"]]
        if not refs:
            fail(f"{row['item_id']}: no record id")
        for key in refs:
            if key[1] not in runs[key[0]]:
                fail(f"{row['item_id']}: record {key[0]}:{key[1]} not in run file")
            if key in out:
                fail(f"record {key[0]}:{key[1]} appears in {out[key]['item_id']} "
                     f"and {row['item_id']}")
            out[key] = {"item_id": row["item_id"], "category": row["category"],
                        "ai_decision": dec, "decision": final,
                        "exclusion_reason": row["founder_exclusion_reason"],
                        "strict_check1": strict}
    gaps = [f"{run}:{rid}" for run in RUNS for rid in runs[run] if (run, rid) not in out]
    if gaps:
        fail(f"records without an adjudication row: {gaps}")
    return out


# ---------------------------------------------------------------- labels

def read_labels(path):
    if path is None:
        return {}, []
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != LABEL_COLUMNS:
            fail(f"label_resolutions.csv header must be exactly {LABEL_COLUMNS}, "
                 f"got {rd.fieldnames}")
        rows = list(rd)
    table, listing = {}, []
    for n, r in enumerate(rows, start=2):
        empty = [c for c in LABEL_COLUMNS if not (r[c] or "").strip()]
        if empty:
            fail(f"label_resolutions.csv line {n}: empty {empty}")
        try:
            canon, note = normalize(r["formula_as_printed"].strip())
            status = "ok"
        except NormalizationError as e:
            canon, note, status = None, str(e), "printed_formula_does_not_normalize"
        ids = [x.strip() for x in r["record_ids"].split(";") if x.strip()]
        for rid in ids:
            if not re.fullmatch(r"[ab]:[A-Z0-9]+-\d+-\d+", rid):
                fail(f"label_resolutions.csv line {n}: record id {rid!r} must look like "
                     "a:HWA17-12-3 or b:NOE21-4-1")
            key = (rid.split(":")[0], rid.split(":")[1], r["label"].strip())
            if key in table:
                fail(f"label_resolutions.csv: {rid} / {r['label']!r} listed twice")
            table[key] = {"line": n, "canon": canon, "status": status, "note": note,
                          "source": r["source"].strip(), "page": r["page"].strip()}
        listing.append({**{c: r[c].strip() for c in LABEL_COLUMNS},
                        "normalized": canon, "status": status, "note": note})
    return table, listing


# ---------------------------------------------------------------- dataset

def numeric_mp(mp_id):
    m = re.search(r"(\d+)", mp_id or "")
    return int(m.group(1)) if m else 10**12


def read_dataset(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for c in ("id", "mp_id", "formula", "pretty_formula"):
        if rows and c not in rows[0]:
            fail(f"dataset export lacks column {c!r}")
    index, failures, disagreements, used = defaultdict(list), [], [], Counter()
    for r in rows:
        got = {}
        for col in ("formula", "pretty_formula"):
            try:
                got[col] = normalize(r[col])[0] if r[col] else None
            except NormalizationError as e:
                got[col] = None
                got[col + "_error"] = str(e)
        canon = got["formula"] or got["pretty_formula"]
        if got["formula"] and got["pretty_formula"] and got["formula"] != got["pretty_formula"]:
            disagreements.append({"id": r["id"], "mp_id": r["mp_id"], "formula": r["formula"],
                                  "pretty_formula": r["pretty_formula"],
                                  "formula_normalized": got["formula"],
                                  "pretty_normalized": got["pretty_formula"]})
            canon = None
        if canon is None:
            if not (got["formula"] and got["pretty_formula"]):
                failures.append({"id": r["id"], "mp_id": r["mp_id"], "formula": r["formula"],
                                 "pretty_formula": r["pretty_formula"],
                                 "errors": {k: v for k, v in got.items() if k.endswith("_error")}})
            continue
        used["formula" if got["formula"] else "pretty_formula"] += 1
        index[canon].append({"id": int(r["id"]), "mp_id": r["mp_id"],
                             "formula": r["formula"], "pretty_formula": r["pretty_formula"]})
    for recs in index.values():
        recs.sort(key=lambda x: (numeric_mp(x["mp_id"]), x["mp_id"], x["id"]))
    info = {"rows": len(rows), "indexed": sum(len(v) for v in index.values()),
            "formula_groups": len(index), "column_used": dict(used),
            "failures": failures, "disagreements": disagreements}
    return index, info


# ---------------------------------------------------------------- cohort

def side_value(run, rec, side, labels, resolutions_used):
    """Return (canon, problem). problem is None when the side is usable."""
    raw = rec.get(f"{side}_as_published")
    canon = rec.get(f"{side}_normalized")
    if raw is None:
        return None, "include_without_" + side
    if canon is not None:
        return canon, None
    hit = labels.get((run, rec["record_id"], raw))
    if hit is None:
        return None, "label_unresolved"
    if hit["source"] != rec["source"] or hit["page"] != str(page_of(rec["record_id"])):
        fail(f"label_resolutions.csv line {hit['line']}: source/page "
             f"{hit['source']} p.{hit['page']} do not match {run}:{rec['record_id']}")
    resolutions_used.add((run, rec["record_id"], raw))
    if hit["canon"] is None:
        return None, "label_unresolved"
    return hit["canon"], None


def build(adj_path, a_path, b_path, data_path, labels_path=None):
    runs = {"a": {r["record_id"]: r for r in load_jsonl(a_path)},
            "b": {r["record_id"]: r for r in load_jsonl(b_path)}}
    dec = decisions(read_adjudication(adj_path), runs)
    labels, label_listing = read_labels(labels_path)
    for run, rid, _ in labels:
        if rid not in runs[run]:
            fail(f"label_resolutions.csv names {run}:{rid}, which is not in run {run}")
    index, data_info = read_dataset(data_path)
    dev = {}
    for p, t in DEVELOPMENT_PAIRS:
        dev[(normalize(p)[0], normalize(t)[0])] = f"{p} -> {t}"

    p_records, needed, used = [], [], set()
    occurrences = defaultdict(list)          # pair -> qualifying occurrences
    other_occ = []                           # non-included occurrences with a pair
    for run in RUNS:
        for rid, rec in runs[run].items():
            d = dec[(run, rid)]
            occ = {"run": run, "record_id": rid, "item_id": d["item_id"],
                   "source": rec["source"], "page": page_of(rid),
                   "parent_as_published": rec.get("parent_as_published"),
                   "target_as_published": rec.get("target_as_published"),
                   "ai_decision": d["ai_decision"], "decision": d["decision"],
                   "strict_check1": d["strict_check1"],
                   "cited_primary_study": rec.get("cited_primary_study"),
                   "evidence": rec.get("evidence")}
            if d["decision"] != "include":
                reason = ("ambiguous" if d["decision"] == "ambiguous"
                          else d["exclusion_reason"] or "exclude_no_reason_given")
                p_records.append({**occ, "p_reason": reason})
                pn, tn = rec.get("parent_normalized"), rec.get("target_normalized")
                if pn and tn:
                    other_occ.append(((pn, tn), occ))
                continue
            sides, problems = {}, []
            for side in ("parent", "target"):
                canon, prob = side_value(run, rec, side, labels, used)
                sides[side] = canon
                if prob:
                    problems.append(prob)
                    if prob == "label_unresolved":
                        needed.append({"run": run, "record_id": rid,
                                       "item_id": d["item_id"], "side": side,
                                       "as_published": rec.get(f"{side}_as_published"),
                                       "source": rec["source"], "page": page_of(rid),
                                       "normalizer_note": (rec.get("normalization") or {})
                                       .get(side, {}).get("note"),
                                       "evidence": rec.get("evidence")})
            if problems:
                p_records.append({**occ, "p_reason": ";".join(sorted(set(problems)))})
                continue
            occurrences[(sides["parent"], sides["target"])].append(occ)

    unused = sorted(f"{r}:{i} {l!r}" for r, i, l in set(labels) - used)
    if unused:
        fail("label_resolutions.csv rows that match no included unnormalized "
             f"composition: {unused}")

    cases = []
    for (pc, tc), occs in occurrences.items():
        occs.sort(key=lambda o: rec_order(o["run"], o["record_id"]))
        ep, et = elements(pc), elements(tc)
        avoid, prefer = sorted(ep - et), sorted(et - ep)
        pm, tm = index.get(pc, []), index.get(tc, [])
        if not avoid and not prefer:
            cls = "N"
        elif not pm or not tm:
            cls = "X"
        elif len(ep & et) >= 3:
            cls = "E"
        else:
            cls = "I"
        studies = sorted({o["cited_primary_study"] for o in occs if o["cited_primary_study"]})
        cases.append({
            "parent_normalized": pc, "target_normalized": tc,
            "parent_as_published": occs[0]["parent_as_published"],
            "target_as_published": occs[0]["target_as_published"],
            "classification": cls, "development": dev.get((pc, tc)),
            "avoid_elements": avoid, "prefer_elements": prefer,
            "avoid_only_eligible": bool(avoid),
            "shared_elements": len(ep & et), "family_key": "-".join(sorted(ep & et)),
            "parent_in_dataset": bool(pm), "target_in_dataset": bool(tm),
            "parent_record": pm[0] if pm else None, "parent_matches": pm,
            "target_matches": tm,
            "earliest_occurrence": f"{occs[0]['run']}:{occs[0]['record_id']}",
            "sources": sorted({o["source"] for o in occs}, key=SOURCE_ORDER.get),
            "cited_primary_studies": studies,
            "occurrences": occs,
            "non_qualifying_occurrences": [o for k, o in other_occ if k == (pc, tc)],
        })
    cases.sort(key=lambda c: rec_order(*c["earliest_occurrence"].split(":")))
    n_main = n_dev = 0
    for c in cases:
        if c["development"]:
            n_dev += 1
            c["case_id"] = f"DEV-{n_dev:02d}"
        else:
            n_main += 1
            c["case_id"] = f"RRB01-{n_main:03d}"
    main = [c for c in cases if not c["development"]]
    devs = [c for c in cases if c["development"]]

    def family_select(pool):
        seen, keep = set(), []
        for c in pool:
            if c["family_key"] not in seen:
                seen.add(c["family_key"])
                keep.append(c["case_id"])
        return keep

    primary = [c for c in main if c["classification"] == "E"]
    e_plus_i = [c for c in main if c["classification"] in ("E", "I")]
    study_counts = Counter(s for c in e_plus_i for s in c["cited_primary_studies"])
    report = {
        "source_records": {r: len(runs[r]) for r in RUNS},
        "source_records_by_source": {f"{r}:{s}": n for r in RUNS for s, n in
                                     sorted(Counter(x["source"] for x in runs[r].values()).items())},
        "decisions_after_strict_check1": dict(Counter(d["decision"] for d in dec.values())),
        "strict_check1_rows": sorted(STRICT_CHECK1_AMBIGUOUS),
        "strict_check1_changed_records": sorted(
            f"{k[0]}:{k[1]} ({v['item_id']}, AI {v['ai_decision']})"
            for k, v in dec.items() if v["strict_check1"] and v["ai_decision"] != "ambiguous"),
        "p_records_by_reason": dict(sorted(Counter(p["p_reason"] for p in p_records).items())),
        "ambiguous_by_source": dict(sorted(Counter(p["source"] for p in p_records
                                                   if p["p_reason"] == "ambiguous").items())),
        "label_unresolved": [f"{n['run']}:{n['record_id']} ({n['item_id']}) {n['side']} "
                             f"{n['as_published']!r}" for n in needed],
        "label_resolutions": label_listing,
        "unique_qualifying_pairs": len(cases),
        "classification_all_pairs": dict(sorted(Counter(c["classification"] for c in cases).items())),
        "classification_excluding_development": dict(sorted(
            Counter(c["classification"] for c in main).items())),
        "development_cases": [{"case_id": c["case_id"], "pair": c["development"],
                               "classification": c["classification"]} for c in devs],
        "primary_cohort_E": [c["case_id"] for c in primary],
        "primary_cohort_size": len(primary),
        "I_cases": [c["case_id"] for c in main if c["classification"] == "I"],
        "avoid_only_eligible": {
            "E": sum(c["avoid_only_eligible"] for c in primary),
            "E_plus_I": sum(c["avoid_only_eligible"] for c in e_plus_i)},
        "family_sensitivity": {"E": family_select(primary), "E_plus_I": family_select(e_plus_i)},
        "dataset_coverage": {
            "parent_present": sum(c["parent_in_dataset"] for c in cases),
            "target_present": sum(c["target_in_dataset"] for c in cases),
            "both_present": sum(c["parent_in_dataset"] and c["target_in_dataset"] for c in cases),
            "pairs": len(cases)},
        "evidence_sources_E_plus_I": {
            "distinct_primary_studies": len(study_counts),
            "most_frequent": study_counts.most_common(5),
            "cases_without_cited_study": sum(not c["cited_primary_studies"] for c in e_plus_i)},
        "dataset": {k: v for k, v in data_info.items() if k not in ("failures", "disagreements")}
        | {"normalization_failures": len(data_info["failures"]),
           "formula_pretty_disagreements": len(data_info["disagreements"])},
    }
    return {"cohort": main, "development": devs, "p_records": p_records,
            "needed": needed, "dataset_info": data_info, "report": report}


def write_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("adjudication", "run_a", "run_b", "materials", "out_dir"):
        ap.add_argument(name, type=Path)
    ap.add_argument("--labels", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.out_dir.exists():
        fail(f"output directory already exists: {a.out_dir}")
    res = build(a.adjudication, a.run_a, a.run_b, a.materials, a.labels)
    inputs = {p.name: sha(p) for p in (a.adjudication, a.run_a, a.run_b, a.materials)
              + ((a.labels,) if a.labels else ())}
    res["report"] = {"inputs_sha256": inputs, "labels_file_used": bool(a.labels),
                     **res["report"]}
    a.out_dir.mkdir(parents=True)
    write_json(a.out_dir / "cohort.json", res["cohort"])
    write_json(a.out_dir / "development_cases.json", res["development"])
    write_json(a.out_dir / "p_records.json", res["p_records"])
    write_json(a.out_dir / "dataset_normalization.json",
               {"failures": res["dataset_info"]["failures"],
                "disagreements": res["dataset_info"]["disagreements"]})
    with open(a.out_dir / "label_resolutions_needed.csv", "w", encoding="utf-8",
              newline="") as f:
        w = csv.DictWriter(f, fieldnames=NEEDED_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(res["needed"])
    outputs = {p.name: sha(p) for p in sorted(a.out_dir.iterdir())}
    res["report"]["outputs_sha256"] = outputs
    write_json(a.out_dir / "cohort_report.json", res["report"])
    print(json.dumps(res["report"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
