"""Tests for build_cohort.py. Synthetic data only."""
import csv
import json

import pytest

openpyxl = pytest.importorskip("openpyxl")

import build_cohort as bc
from normalize_formulas import normalize_record

HEAD = ["item_id", "category", "a_record_id", "b_record_id", "source", "page",
        "founder_decision", "founder_exclusion_reason", "audit_result", "reason"]


def rec(rid, parent, target, decision="include", study="12", reason=None):
    r = {"record_id": rid, "source": rid.split("-")[0], "parent_as_published": parent,
         "target_as_published": target, "decision": decision, "exclusion_reason": reason,
         "cited_primary_study": study, "evidence": f"{parent} replaced by {target}"}
    return normalize_record(r)


def write_inputs(tmp_path, a_recs, b_recs, adj_rows, materials, labels=None):
    pa, pb = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    pa.write_text("".join(json.dumps(r) + "\n" for r in a_recs), encoding="utf-8")
    pb.write_text("".join(json.dumps(r) + "\n" for r in b_recs), encoding="utf-8")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "adjudication"
    ws.append(HEAD)
    for r in adj_rows:
        ws.append([r.get(c) for c in HEAD])
    px = tmp_path / "adj.xlsx"
    wb.save(px)
    pm = tmp_path / "materials.csv"
    with open(pm, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "mp_id", "formula", "pretty_formula", "energy_above_hull"])
        for row in materials:
            w.writerow(row)
    pl = None
    if labels is not None:
        pl = tmp_path / "labels.csv"
        with open(pl, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(bc.LABEL_COLUMNS)
            for row in labels:
                w.writerow(row)
    return px, pa, pb, pm, pl


def adj(item, a=None, b=None, dec="include", reason=None):
    return {"item_id": item, "category": "x", "a_record_id": a, "b_record_id": b,
            "founder_decision": dec, "founder_exclusion_reason": reason}


MATERIALS = [
    (1, "mp-20", "LiCoO2", "LiCoO2", 0),
    (2, "mp-3", "LiCoO2", "LiCoO2", 0),          # lower numeric MP-ID -> parent
    (3, "mp-7", "LiNiO2", "LiNiO2", 0),
    (4, "mp-8", "NaCoO2", "NaCoO2", 0),
    (5, "mp-9", "LiFePO4", "LiFePO4", 0),
    (6, "mp-10", "NaFePO4", "NaFePO4", 0),
    (7, "mp-11", "NaMnPO4", "NaMnPO4", 0),
    (8, "mp-12", "Li2CoO3", "Li2CoO3", 0),
]


def run(tmp_path, a_recs, b_recs, adj_rows, labels=None, materials=MATERIALS):
    return bc.build(*write_inputs(tmp_path, a_recs, b_recs, adj_rows, materials, labels))


def test_classification_layers_and_parent_record(tmp_path):
    a = [rec("HWA17-3-1", "LiCoO2", "LiNiO2"),        # I (2 shared)
         rec("HWA17-4-1", "LiFePO4", "NaMnPO4"),      # E? shared Fe? no: P,O -> I
         rec("HWA17-5-1", "LiCoO2", "Li2CoO3"),       # N (same element set)
         rec("HWA17-6-1", "LiCoO2", "KCoO2"),         # X (target absent)
         rec("HWA17-7-1", "NaFePO4", "NaMnPO4")]      # E (Na,P,O shared)
    rows = [adj(f"ADJ-00{i}", a=r["record_id"]) for i, r in enumerate(a, 1)]
    res = run(tmp_path, a, [], rows)
    cls = {(c["parent_normalized"], c["target_normalized"]): c for c in res["cohort"]}
    c = cls[("Co1Li1O2", "Li1Ni1O2")]
    assert c["classification"] == "I" and c["avoid_elements"] == ["Co"]
    assert c["prefer_elements"] == ["Ni"] and c["family_key"] == "Li-O"
    assert c["parent_record"]["mp_id"] == "mp-3"
    assert [m["mp_id"] for m in c["parent_matches"]] == ["mp-3", "mp-20"]
    assert cls[("Fe1Li1O4P1", "Mn1Na1O4P1")]["classification"] == "I"
    assert cls[("Co1Li1O2", "Co1Li2O3")]["classification"] == "N"
    assert cls[("Co1Li1O2", "Co1K1O2")]["classification"] == "X"
    e = cls[("Fe1Na1O4P1", "Mn1Na1O4P1")]
    assert e["classification"] == "E" and e["shared_elements"] == 3
    assert res["report"]["primary_cohort_E"] == [e["case_id"]]


def test_duplicates_collapse_and_non_qualifying_listed(tmp_path):
    a = [rec("NOE21-9-1", "LiCoO2", "LiNiO2"), rec("HWA17-2-1", "LiCoO2", "LiNiO2")]
    b = [rec("HWA17-2-1", "LiCoO2", "LiNiO2", decision="exclude", reason="not_directed")]
    rows = [adj("ADJ-001", a="NOE21-9-1"), adj("ADJ-002", a="HWA17-2-1"),
            adj("ADJ-003", b="HWA17-2-1", dec="exclude", reason="not_directed")]
    res = run(tmp_path, a, b, rows)
    assert len(res["cohort"]) == 1
    c = res["cohort"][0]
    assert c["earliest_occurrence"] == "a:HWA17-2-1"       # Hwang before Noerochim
    assert len(c["occurrences"]) == 2 and c["sources"] == ["HWA17", "NOE21"]
    assert [o["record_id"] for o in c["non_qualifying_occurrences"]] == ["HWA17-2-1"]
    assert res["report"]["p_records_by_reason"] == {"not_directed": 1}


def test_only_exclusions_never_create_a_case(tmp_path):
    a = [rec("HWA17-2-1", "LiCoO2", "LiNiO2", decision="exclude", reason="not_directed")]
    res = run(tmp_path, a, [], [adj("ADJ-001", a="HWA17-2-1", dec="exclude",
                                    reason="not_directed")])
    assert res["cohort"] == [] and len(res["p_records"]) == 1


def test_founder_decision_overrides_run_decision(tmp_path):
    a = [rec("HWA17-2-1", "LiCoO2", "LiNiO2", decision="exclude", reason="not_directed")]
    res = run(tmp_path, a, [], [adj("ADJ-001", a="HWA17-2-1", dec="include")])
    assert len(res["cohort"]) == 1


def test_strict_check1_rows_become_ambiguous(tmp_path):
    a = [rec("HWA17-2-1", "LiCoO2", "LiNiO2")]
    res = run(tmp_path, a, [], [adj("ADJ-057", a="HWA17-2-1", dec="include")])
    assert res["cohort"] == []
    assert res["p_records"][0]["p_reason"] == "ambiguous"
    assert res["report"]["strict_check1_changed_records"] == [
        "a:HWA17-2-1 (ADJ-057, AI include)"]


def test_joint_row_maps_both_runs(tmp_path):
    a = [rec("HWA17-2-1", "LiCoO2", "LiNiO2")]
    b = [rec("HWA17-2-4", "LiCoO2", "LiNiO2")]
    res = run(tmp_path, a, b, [adj("ADJ-001", a="HWA17-2-1", b="HWA17-2-4")])
    assert len(res["cohort"]) == 1 and len(res["cohort"][0]["occurrences"]) == 2


def test_development_pairs_reported_separately(tmp_path):
    a = [rec("HWA17-2-1", "LiFePO4", "NaFePO4"), rec("HWA17-3-1", "NaFePO4", "NaMnPO4")]
    rows = [adj("ADJ-001", a="HWA17-2-1"), adj("ADJ-002", a="HWA17-3-1")]
    res = run(tmp_path, a, [], rows)
    assert [c["case_id"] for c in res["development"]] == ["DEV-01"]
    assert [c["case_id"] for c in res["cohort"]] == ["RRB01-001"]
    assert res["report"]["primary_cohort_E"] == ["RRB01-001"]


def test_missing_decision_or_row_stops(tmp_path):
    a = [rec("HWA17-2-1", "LiCoO2", "LiNiO2"), rec("HWA17-3-1", "LiCoO2", "LiNiO2")]
    with pytest.raises(SystemExit):
        run(tmp_path, a, [], [adj("ADJ-001", a="HWA17-2-1")])          # 3-1 has no row
    with pytest.raises(SystemExit):
        run(tmp_path, a[:1], [], [adj("ADJ-001", a="HWA17-2-1", dec=None)])
    with pytest.raises(SystemExit):
        run(tmp_path, a[:1], [], [adj("ADJ-001", a="HWA17-9-9")])      # unknown record


def test_label_unresolved_then_resolved(tmp_path):
    a = [rec("NOE21-3-1", "NMC111", "LiNiO2")]
    rows = [adj("ADJ-001", a="NOE21-3-1")]
    res = run(tmp_path, a, [], rows)
    assert res["cohort"] == []
    assert res["p_records"][0]["p_reason"] == "label_unresolved"
    assert res["needed"][0]["as_published"] == "NMC111"
    good = [["NMC111", "LiNi1/3Mn1/3Co1/3O2", "NOE21", "3",
             "LiNi1/3Mn1/3Co1/3O2 (NMC111)", "a:NOE21-3-1", "Jithin Mathews"]]
    res = run(tmp_path, a, [], rows, labels=good)
    c = res["cohort"][0]
    assert c["parent_normalized"] == "Co1Li3Mn1Ni1O6"
    assert c["avoid_elements"] == ["Co", "Mn"] and c["classification"] == "X"


def test_label_rows_must_match_page_and_be_used(tmp_path):
    a = [rec("NOE21-3-1", "NMC111", "LiNiO2")]
    rows = [adj("ADJ-001", a="NOE21-3-1")]
    wrong_page = [["NMC111", "LiNi1/3Mn1/3Co1/3O2", "NOE21", "4", "x", "a:NOE21-3-1", "J"]]
    with pytest.raises(SystemExit):
        run(tmp_path, a, [], rows, labels=wrong_page)
    unused = [["NMC532", "LiNi0.5Mn0.3Co0.2O2", "NOE21", "3", "x", "a:NOE21-3-1", "J"]]
    with pytest.raises(SystemExit):
        run(tmp_path, a, [], rows, labels=unused)
    blank = [["NMC111", "LiNi1/3Mn1/3Co1/3O2", "NOE21", "3", "x", "a:NOE21-3-1", ""]]
    with pytest.raises(SystemExit):
        run(tmp_path, a, [], rows, labels=blank)


def test_printed_formula_that_fails_stays_p(tmp_path):
    a = [rec("NOE21-3-1", "NMCx", "LiNiO2")]
    labels = [["NMCx", "LiNixMn1-xO2", "NOE21", "3", "x", "a:NOE21-3-1", "J"]]
    res = run(tmp_path, a, [], [adj("ADJ-001", a="NOE21-3-1")], labels=labels)
    assert res["cohort"] == [] and res["p_records"][0]["p_reason"] == "label_unresolved"


def test_include_without_parent_is_p(tmp_path):
    a = [rec("HWA17-2-1", None, "LiNiO2")]
    res = run(tmp_path, a, [], [adj("ADJ-001", a="HWA17-2-1")])
    assert res["p_records"][0]["p_reason"] == "include_without_parent"


def test_family_sensitivity_selected_per_cohort(tmp_path):
    a = [rec("HWA17-2-1", "LiCoO2", "LiNiO2"),        # I, family Li-O (first)
         rec("HWA17-3-1", "NaFePO4", "NaMnPO4"),      # E, family Na-O-P
         rec("HWA17-4-1", "NaFePO4", "NaCoO2")]       # I, family Na-O (no P in target)
    rows = [adj(f"ADJ-00{i}", a=r["record_id"]) for i, r in enumerate(a, 1)]
    res = run(tmp_path, a, [], rows)
    fam = res["report"]["family_sensitivity"]
    assert fam["E"] == ["RRB01-002"]
    assert fam["E_plus_I"] == ["RRB01-001", "RRB01-002", "RRB01-003"]


def test_dataset_fallback_and_failures(tmp_path):
    mats = [(1, "mp-1", "Li1 Co1 O2", "LiCoO2", 0), (2, "mp-2", "Li Ni O2 x", "bad pretty", 0)]
    a = [rec("HWA17-2-1", "LiCoO2", "LiNiO2")]
    res = run(tmp_path, a, [], [adj("ADJ-001", a="HWA17-2-1")], materials=mats)
    info = res["dataset_info"]
    assert info["column_used"] == {"pretty_formula": 1} and len(info["failures"]) == 1
    assert res["cohort"][0]["parent_in_dataset"] and not res["cohort"][0]["target_in_dataset"]


def test_main_writes_outputs_and_refuses_overwrite(tmp_path):
    a = [rec("HWA17-2-1", "NaFePO4", "NaMnPO4")]
    px, pa, pb, pm, _ = write_inputs(tmp_path, a, [], [adj("ADJ-001", a="HWA17-2-1")],
                                     MATERIALS)
    out = tmp_path / "out"
    bc.main([str(px), str(pa), str(pb), str(pm), str(out)])
    names = sorted(p.name for p in out.iterdir())
    assert names == ["cohort.json", "cohort_report.json", "dataset_normalization.json",
                     "development_cases.json", "label_resolutions_needed.csv",
                     "p_records.json"]
    rep = json.loads((out / "cohort_report.json").read_text(encoding="utf-8"))
    assert rep["primary_cohort_size"] == 1 and "a.jsonl" in rep["inputs_sha256"]
    with pytest.raises(SystemExit):
        bc.main([str(px), str(pa), str(pb), str(pm), str(out)])
