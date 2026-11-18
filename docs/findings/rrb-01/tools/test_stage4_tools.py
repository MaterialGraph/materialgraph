"""Tests for build_ai_package.py and csv_to_workbook.py. Synthetic data only."""
import csv
import json

import pytest

openpyxl = pytest.importorskip("openpyxl")

import build_ai_package as pkg
import csv_to_workbook as c2w
import rrb01_extract as tool

SYNTH = """# Title

## Case cohort

Intro paragraph that must not be copied.

**Source (selected).** Expectations that must not be copied.

**Order of operations.** First enumerate.

**Explicit-pair requirement.** A pair is extracted only when X.

**Relationship characterization.** Labels A, B, C.

**Source identity.** Not a rule block.

**Qualifying relationship types (provisional).** Two types qualify:

1. Type one.
2. Type two.

A synthesis route alone does not qualify.

**Composition rules (provisional).**

| Composition type | Rule |
| --- | --- |
| Fixed integer formula | Include |

**Stoichiometry-only substitutions.** Not copied.

**Spatially heterogeneous materials.** Excluded as endpoints.

**Morphology and surface modifications.** Not pairs.

**Directed pairs only.** Direction required.

**Evidence-source record.** Cite the primary study.

### Extraction output schema (draft, to be fixed at protocol lock)

Both extractions write JSONL.

**Raw preservation.** Not copied.

**Frozen source snapshots.** Use the PDFs.

| Source | File | SHA-256 |
| --- | --- | --- |
| Hwang 2017 | a.pdf | AAA |

**What creates a record.** A record is created for (a) or (b).

| Field | Content | Filled by |
| --- | --- | --- |
| record_id | id | Extractor |

**Comparison keys.** Not copied.

**Duplicates.** Each occurrence keeps its own record.

**Ambiguous after adjudication.** Not copied.
"""


def test_rules_are_verbatim_and_complete(tmp_path):
    proto = tmp_path / "proto.md"
    proto.write_text(SYNTH, encoding="utf-8")
    out = tmp_path / "pkg"
    pkg.build(proto, out, "pdf_index")
    rules = (out / "ai_extraction_rules.md").read_text(encoding="utf-8")
    for must in ["**Explicit-pair requirement.** A pair is extracted only when X.",
                 "1. Type one.\n2. Type two.", "A synthesis route alone does not qualify.",
                 "| Fixed integer formula | Include |", "Both extractions write JSONL.",
                 "| record_id | id | Extractor |", "**Duplicates.** Each occurrence"]:
        assert must in rules, must
    for never in ["Intro paragraph", "Expectations", "Source identity", "Stoichiometry",
                  "Raw preservation", "Comparison keys", "Ambiguous after adjudication"]:
        assert never not in rules, never
    prompt = (out / "ai_extraction_prompt.md").read_text(encoding="utf-8")
    assert ",".join(f'"{c}"' for c in tool.COLUMNS) in prompt
    assert "first page of the file as 1" in prompt
    man = json.loads((out / "package_manifest.json").read_text(encoding="utf-8"))
    assert man["locked_protocol_sha256"] == pkg.sha256_bytes(proto.read_bytes())


def test_missing_label_writes_nothing(tmp_path):
    proto = tmp_path / "proto.md"
    proto.write_text(SYNTH.replace("**Directed pairs only.**", "**Directed.**"), encoding="utf-8")
    out = tmp_path / "pkg"
    with pytest.raises(SystemExit):
        pkg.build(proto, out, "printed")
    assert not out.exists()


ROW = {
    "record_id": "NOE21-3-1", "source": "NOE21", "location": "p.3, para 1",
    "evidence": " AbX2 was replaced by AbY2 ", "cited_primary_study": "12",
    "parent_as_published": "AbX2", "target_as_published": "AbY2",
    "parent_composition_type": "fixed_integer", "target_composition_type": "fixed_integer",
    "direction_basis": "was replaced by", "relationship_type": "within_family_substitution",
    "characterization": "proposed_replacement", "confounders": "",
    "decision": "include", "exclusion_reason": "", "ambiguity_note": "",
}


def write_csv(path, rows, header=None):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(header or tool.COLUMNS)
        for r in rows:
            w.writerow([r[c] for c in tool.COLUMNS])


def test_csv_round_trip_keeps_text_exactly(tmp_path):
    src, xlsx = tmp_path / "ai.csv", tmp_path / "ai.xlsx"
    write_csv(src, [ROW])
    c2w.write_workbook(c2w.load_csv(src), xlsx)
    problems, recs = tool.validate_rows(tool.read_rows(xlsx), "ai")
    assert not [p for p in problems if p.error]
    r = recs[0]
    assert r["evidence"] == " AbX2 was replaced by AbY2 "   # untouched
    assert r["cited_primary_study"] == "12"                 # stays text
    assert r["extractor"] == "ai" and r["exclusion_reason"] is None


def test_csv_bad_header_or_field_count_stops(tmp_path):
    src = tmp_path / "ai.csv"
    write_csv(src, [ROW], header=list(reversed(tool.COLUMNS)))
    with pytest.raises(SystemExit):
        c2w.load_csv(src)
    src.write_text(",".join(tool.COLUMNS) + "\n\"a\",\"b\"\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        c2w.load_csv(src)


def test_csv_formula_like_value_is_text_and_flagged(tmp_path):
    src, xlsx = tmp_path / "ai.csv", tmp_path / "ai.xlsx"
    write_csv(src, [dict(ROW, target_as_published="=A1")])
    c2w.write_workbook(c2w.load_csv(src), xlsx)
    problems, _ = tool.validate_rows(tool.read_rows(xlsx), "ai")
    assert any(p.field == "target_as_published" for p in problems if p.error)


def test_csv_never_overwrites(tmp_path):
    src, xlsx = tmp_path / "ai.csv", tmp_path / "ai.xlsx"
    write_csv(src, [ROW])
    c2w.write_workbook(c2w.load_csv(src), xlsx)
    with pytest.raises(SystemExit):
        c2w.write_workbook(c2w.load_csv(src), xlsx)
