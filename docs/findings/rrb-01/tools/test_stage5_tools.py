"""Tests for normalize_formulas.py and compare_runs.py. Synthetic data only."""
import json

import pytest

openpyxl = pytest.importorskip("openpyxl")

import compare_runs as cr
import normalize_formulas as nf


@pytest.mark.parametrize("raw,expected", [
    ("AbX", None),                                   # unknown element
    ("LiNiO2", "Li1Ni1O2"),
    ("LiNi0.8Mn0.1Co0.1O2", "Co1Li10Mn1Ni8O20"),
    ("Na2/3Ni1/3Mn2/3O2", "Mn2Na2Ni1O6"),
    ("Na3V2(PO4)3", "Na3O12P3V2"),
    ("Li[Ni0.9Co0.1]O2", "Co1Li10Ni9O20"),
    ("LiFePO\u2084", "Fe1Li1O4P1"),                 # subscript digit
    ("0.5Li2MnO3\u00b70.5LiNiO2", "Li3Mn1Ni1O5"),
    ("Li2O2", "Li1O1"),                               # reduced by gcd
])
def test_normalize_values(raw, expected):
    if expected is None:
        with pytest.raises(nf.NormalizationError):
            nf.normalize(raw)
    else:
        assert nf.normalize(raw)[0] == expected


@pytest.mark.parametrize("raw", ["C-LiFePO4", "LiNi1-xMnxO2", "Li1+xMn2O4", "NaFePO4@C",
                                 "Li-rich", "Na2 FePO4F", "(LiO2", "LiO2)", ""])
def test_normalize_failures_are_not_guessed(raw):
    with pytest.raises(nf.NormalizationError):
        nf.normalize(raw)


def test_phase_label_removed_and_noted():
    canon, note = nf.normalize("P2-Na2/3Ni1/3Mn2/3O2")
    assert canon == "Mn2Na2Ni1O6" and "P2" in note
    assert nf.normalize("\u03b2-NaMnO2") == ("Mn1Na1O2", "phase label '\u03b2' removed")


def rec(rid, decision, parent, target, **kw):
    r = {"record_id": rid, "source": rid.split("-")[0], "decision": decision,
         "parent_as_published": parent, "target_as_published": target,
         "exclusion_reason": kw.get("reason"), "relationship_type": kw.get("rel"),
         "characterization": kw.get("char"), "composition_type": None,
         "confounders": [], "direction_basis": None, "evidence": "e"}
    return nf.normalize_record(r)


def test_include_matching_is_by_normalized_key_and_direction():
    a = [rec("NOE21-2-1", "include", "LiCoO2", "LiNiO2", rel="r1"),
         rec("NOE21-3-1", "include", "LiNiO2", "LiCoO2")]
    b = [rec("NOE21-9-4", "include", "LiCoO\u2082", "LiNiO2", rel="r2")]   # other page, same pair
    res = cr.compare(a, b)
    assert len(res["matched_includes"]) == 1
    ra, rb = res["matched_includes"][0]
    assert ra["record_id"] == "NOE21-2-1" and rb["record_id"] == "NOE21-9-4"
    assert cr.field_diffs(ra, rb) == ["relationship_type"]
    assert [r["record_id"] for r in res["unmatched_a"]] == ["NOE21-3-1"]  # reversed direction


def test_extra_occurrences_stay_unmatched():
    a = [rec("NOE21-2-1", "include", "LiCoO2", "LiNiO2"),
         rec("NOE21-4-1", "include", "LiCoO2", "LiNiO2")]
    b = [rec("NOE21-5-1", "include", "LiCoO2", "LiNiO2")]
    res = cr.compare(a, b)
    assert len(res["matched_includes"]) == 1
    assert [r["record_id"] for r in res["unmatched_a"]] == ["NOE21-4-1"]


def test_exclusions_match_on_page_and_published_strings_uniquely():
    a = [rec("HWA17-6-1", "exclude", None, "NaFeO2", reason="no_named_parent"),
         rec("HWA17-7-1", "exclude", "LiX", "NaX", reason="not_directed"),
         rec("HWA17-7-2", "exclude", "LiX", "NaX", reason="not_directed")]
    b = [rec("HWA17-6-3", "ambiguous", None, "NaFeO2"),
         rec("HWA17-7-1", "exclude", "LiX", "NaX", reason="not_directed")]
    res = cr.compare(a, b)
    assert len(res["decision_conflicts"]) == 1          # exclude vs ambiguous, same key
    assert res["joint_excluded"] == []                    # page-7 key not unique in A
    assert {r["record_id"] for r in res["unmatched_a"]} == {"HWA17-7-1", "HWA17-7-2"}


def test_published_string_difference_is_not_matched_for_exclusions():
    a = [rec("HWA17-6-1", "exclude", None, "NaFeO2", reason="no_named_parent")]
    b = [rec("HWA17-6-1", "exclude", None, "NaFeO\u2082", reason="no_named_parent")]
    res = cr.compare(a, b)
    assert res["joint_excluded"] == [] and len(res["unmatched_a"]) == 1


@pytest.mark.parametrize("n,expected", [
    (0, []), (3, [0, 1, 2]), (10, list(range(10))),
    (12, [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]),
    (30, [0, 1, 2, 3, 5, 10, 15, 20, 25, 4]),
    (60, list(range(0, 60, 5))),
])
def test_audit_sample_rule(n, expected):
    assert cr.audit_sample(n) == sorted(expected)


def test_normalization_failure_category_and_workbook(tmp_path):
    a = [rec("NOE21-2-1", "include", "LiNi1-xMnxO2", "LiNiO2"),
         rec("NOE21-3-1", "include", "LiCoO2", "LiNiO2")]
    b = [rec("NOE21-3-2", "include", "LiCoO2", "LiNiO2")]
    for r in a + b:
        pass
    pa, pb = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    pa.write_text("".join(json.dumps(r) + "\n" for r in a), encoding="utf-8")
    pb.write_text("".join(json.dumps(r) + "\n" for r in b), encoding="utf-8")
    cr.main([str(pa), str(pb), str(tmp_path / "out")])
    rep = json.loads((tmp_path / "out" / "comparison_report.json").read_text(encoding="utf-8"))
    assert rep["workbook_rows_by_category"] == {"audit_joint_include": 1,
                                                "normalization_failure": 1}
    wb = openpyxl.load_workbook(tmp_path / "out" / "adjudication.xlsx")
    ws = wb["adjudication"]
    assert [c.value for c in ws[1]] == cr.ADJ_COLUMNS
    assert ws.max_row == 3
    with pytest.raises(SystemExit):
        cr.main([str(pa), str(pb), str(tmp_path / "out")])   # never overwrites


def test_normalize_cli_never_overwrites_and_keeps_fields(tmp_path):
    src, dst = tmp_path / "r.jsonl", tmp_path / "r.n.jsonl"
    r = {"record_id": "NOE21-1-1", "source": "NOE21", "decision": "include",
         "parent_as_published": "LiCoO2", "target_as_published": "LiNiO2",
         "parent_normalized": None, "target_normalized": None, "evidence": " x "}
    src.write_text(json.dumps(r) + "\n", encoding="utf-8")
    before = src.read_bytes()
    nf.main([str(src), str(dst)])
    out = json.loads(dst.read_text(encoding="utf-8"))
    assert out["parent_normalized"] == "Co1Li1O2" and out["evidence"] == " x "
    assert src.read_bytes() == before
    with pytest.raises(SystemExit):
        nf.main([str(src), str(dst)])
