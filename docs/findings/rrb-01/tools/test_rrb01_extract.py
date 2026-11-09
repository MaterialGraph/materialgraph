"""Tests for rrb01_extract.py. All data is synthetic (not from either source)."""
import json
from pathlib import Path

import pytest
openpyxl = pytest.importorskip("openpyxl")
load_workbook = openpyxl.load_workbook

import rrb01_extract as tool

GOOD_INCLUDE = {
    "record_id": "NOE21-3-1", "source": "NOE21", "location": "p.3, s2, para 1",
    "evidence": "AbX2 was replaced by AbY2 \u2014 \u201cstable\u201d.",
    "cited_primary_study": "[9] 10.0000/x",
    "parent_as_published": "AbX0.9Q0.1O2", "target_as_published": "AbY2",
    "parent_composition_type": "fixed_fractional", "target_composition_type": "fixed_integer",
    "direction_basis": "was replaced by", "relationship_type": "within_family_substitution",
    "characterization": "proposed_replacement", "confounders": "morphology_change;coating",
    "decision": "include", "exclusion_reason": None, "ambiguity_note": None,
}
GOOD_NO_PARENT = {
    "record_id": "HWA17-10-2", "source": "HWA17", "location": "p.10, para 3",
    "evidence": "AbZ is an alternative to cobalt cathodes.", "cited_primary_study": "none",
    "parent_as_published": None, "target_as_published": "AbZ",
    "parent_composition_type": None, "target_composition_type": "fixed_integer",
    "direction_basis": None, "relationship_type": None, "characterization": None,
    "confounders": None, "decision": "exclude", "exclusion_reason": "no_named_parent",
    "ambiguity_note": None,
}
GOOD_AMBIGUOUS = {
    "record_id": "HWA17-2-1", "source": "HWA17", "location": "p.2, para 1",
    "evidence": "AbQ and AbR were compared.", "cited_primary_study": "[3] 10.0000/y",
    "parent_as_published": "AbQ", "target_as_published": "AbR",
    "parent_composition_type": "fixed_integer", "target_composition_type": "fixed_integer",
    "direction_basis": None, "relationship_type": None, "characterization": None,
    "confounders": None, "decision": "ambiguous", "exclusion_reason": None,
    "ambiguity_note": "direction unclear from wording",
}


_counter = [0]


def make_book(tmp_path, rows, name=None):
    _counter[0] += 1
    path = tmp_path / (name or f"in{_counter[0]}.xlsx")
    tool.write_template(path)
    wb = load_workbook(path)
    ws = wb[tool.SHEET]
    for i, row in enumerate(rows, start=2):
        for j, col in enumerate(tool.COLUMNS, start=1):
            ws.cell(row=i, column=j).value = row.get(col)
    wb.save(path)
    return path


def check(tmp_path, rows):
    path = make_book(tmp_path, rows)
    return tool.validate_rows(tool.read_rows(path), "founder")


def errors_of(problems):
    return [p for p in problems if p.error]


def test_valid_rows_pass_and_text_is_unchanged(tmp_path):
    problems, recs = check(tmp_path, [GOOD_INCLUDE, GOOD_NO_PARENT, GOOD_AMBIGUOUS])
    assert not errors_of(problems)
    by_id = {r["record_id"]: r for r in recs}
    r = by_id["NOE21-3-1"]
    assert r["evidence"] == GOOD_INCLUDE["evidence"]          # unicode kept exactly
    assert r["parent_as_published"] == "AbX0.9Q0.1O2"          # not normalized
    assert r["parent_normalized"] is None and r["target_normalized"] is None
    assert r["confounders"] == ["morphology_change", "coating"]
    assert r["composition_type"] == {"parent": "fixed_fractional", "target": "fixed_integer"}
    assert by_id["HWA17-10-2"]["decision"] == "exclude"       # every decision kept
    assert by_id["HWA17-2-1"]["decision"] == "ambiguous"


def test_whitespace_is_kept_and_only_warned(tmp_path):
    row = dict(GOOD_INCLUDE, evidence=" AbX2 was replaced by AbY2. ")
    problems, recs = check(tmp_path, [row])
    assert not errors_of(problems)
    assert any(not p.error and p.field == "evidence" for p in problems)
    assert recs[0]["evidence"] == " AbX2 was replaced by AbY2. "


@pytest.mark.parametrize("field,value", [
    ("decision", "maybe"), ("source", "XYZ99"), ("relationship_type", "analog"),
    ("exclusion_reason", "other"), ("target_composition_type", "fixed"),
])
def test_invalid_enum_rejected(tmp_path, field, value):
    row = dict(GOOD_NO_PARENT if field == "exclusion_reason" else GOOD_INCLUDE, **{field: value})
    problems, _ = check(tmp_path, [row])
    assert any(p.field == field for p in errors_of(problems))


@pytest.mark.parametrize("field", ["evidence", "location", "record_id", "decision",
                                   "target_as_published", "cited_primary_study"])
def test_missing_required_rejected(tmp_path, field):
    problems, _ = check(tmp_path, [dict(GOOD_INCLUDE, **{field: None})])
    assert errors_of(problems)


def test_duplicate_record_id_rejected(tmp_path):
    problems, _ = check(tmp_path, [GOOD_INCLUDE, dict(GOOD_INCLUDE)])
    assert any("duplicate" in p.message for p in errors_of(problems))


def test_record_id_prefix_must_match_source(tmp_path):
    problems, _ = check(tmp_path, [dict(GOOD_INCLUDE, source="HWA17")])
    assert any(p.field == "record_id" for p in errors_of(problems))


def test_empty_parent_requires_no_named_parent_exclusion(tmp_path):
    row = dict(GOOD_INCLUDE, parent_as_published=None, parent_composition_type=None)
    problems, _ = check(tmp_path, [row])
    assert any(p.field == "parent_as_published" for p in errors_of(problems))


def test_include_needs_direction_relationship_characterization(tmp_path):
    for f in ("direction_basis", "relationship_type", "characterization"):
        problems, _ = check(tmp_path, [dict(GOOD_INCLUDE, **{f: None})])
        assert any(p.field == f for p in errors_of(problems)), f


def test_reason_and_note_only_with_matching_decision(tmp_path):
    p1, _ = check(tmp_path, [dict(GOOD_INCLUDE, exclusion_reason="not_directed")])
    assert any(p.field == "exclusion_reason" for p in errors_of(p1))
    p2, _ = check(tmp_path, [dict(GOOD_INCLUDE, ambiguity_note="x")])
    assert any(p.field == "ambiguity_note" for p in errors_of(p2))


def test_evidence_word_limit(tmp_path):
    long = " ".join(["word"] * (tool.MAX_EVIDENCE_WORDS + 1))
    problems, _ = check(tmp_path, [dict(GOOD_INCLUDE, evidence=long)])
    assert any(p.field == "evidence" for p in errors_of(problems))


def test_non_text_cell_rejected(tmp_path):
    path = make_book(tmp_path, [GOOD_INCLUDE])
    wb = load_workbook(path)
    ws = wb[tool.SHEET]
    ws.cell(row=2, column=tool.COLUMNS.index("cited_primary_study") + 1).value = 12
    wb.save(path)
    problems, _ = tool.validate_rows(tool.read_rows(path), "founder")
    assert any(p.field == "cited_primary_study" for p in errors_of(problems))


def test_formula_text_rejected(tmp_path):
    problems, _ = check(tmp_path, [dict(GOOD_INCLUDE, target_as_published="=A1")])
    assert any(p.field == "target_as_published" for p in errors_of(problems))


def test_bad_confounder_token_rejected(tmp_path):
    problems, _ = check(tmp_path, [dict(GOOD_INCLUDE, confounders="morphology change")])
    assert any(p.field == "confounders" for p in errors_of(problems))


def test_convert_is_deterministic_and_complete(tmp_path):
    rows = [GOOD_INCLUDE, GOOD_NO_PARENT, GOOD_AMBIGUOUS]
    src = make_book(tmp_path, rows)
    out1, out2 = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    tool.run_convert(src, out1, "founder")
    tool.run_convert(src, out2, "founder")
    assert out1.read_bytes() == out2.read_bytes()
    lines = out1.read_bytes().decode("utf-8").splitlines()
    assert len(lines) == 3                                   # every record exported
    ids = [json.loads(x)["record_id"] for x in lines]
    assert ids == ["HWA17-2-1", "HWA17-10-2", "NOE21-3-1"]   # numeric page order
    assert list(json.loads(lines[0]).keys()) == tool.OUTPUT_KEYS
    assert b"\r\n" not in out1.read_bytes()
    rep = json.loads((tmp_path / "a.jsonl.report.json").read_text(encoding="utf-8"))
    assert rep["output_jsonl_sha256"] == tool.sha256_file(out1)
    assert rep["record_count"] == 3


def test_convert_refuses_errors_and_overwrite(tmp_path):
    src = make_book(tmp_path, [dict(GOOD_INCLUDE, decision="maybe")])
    out = tmp_path / "o.jsonl"
    with pytest.raises(SystemExit):
        tool.run_convert(src, out, "founder")
    assert not out.exists()                                  # nothing written
    good = make_book(tmp_path, [GOOD_INCLUDE], name="good.xlsx")
    tool.run_convert(good, out, "founder")
    with pytest.raises(SystemExit):
        tool.run_convert(good, out, "founder")               # never overwrites


def test_header_must_match(tmp_path):
    path = make_book(tmp_path, [GOOD_INCLUDE])
    wb = load_workbook(path)
    wb[tool.SHEET].cell(row=1, column=1).value = "id"
    wb.save(path)
    with pytest.raises(SystemExit):
        list(tool.read_rows(path))
