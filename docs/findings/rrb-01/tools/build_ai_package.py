#!/usr/bin/env python3
"""RRB-01 Stage 4: build the AI extraction package from the LOCKED protocol.

Usage:
  python build_ai_package.py <locked-protocol.md> <out_dir> --page-convention pdf_index|printed

Writes to <out_dir> (which must not exist yet):
  ai_extraction_rules.md   extraction rule blocks copied verbatim from the locked file
  ai_extraction_prompt.md  the neutral task statement + output format (no other guidance)
  package_manifest.json    SHA-256 of the locked protocol and of both outputs

Rule blocks are selected by their labels in the locked protocol. Each block is copied
byte-for-byte, together with the unlabeled lists/tables/paragraphs that directly follow
it. If any label is missing, nothing is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import rrb01_extract as tool

# Labels of the extraction-rule blocks, in output order. Matched at the start of a
# block after the opening '**' (bold labels) or '### ' (headings).
RULE_LABELS = [
    "Order of operations.",
    "Explicit-pair requirement.",
    "Relationship characterization.",
    "Qualifying relationship types",
    "Composition rules",
    "Spatially heterogeneous materials.",
    "Morphology and surface modifications.",
    "Directed pairs only.",
    "Evidence-source record.",
    "Extraction output schema",
    "Frozen source snapshots.",
    "What creates a record.",
    "Duplicates.",
]

PAGE_CONVENTIONS = {
    "pdf_index": "the page number of the PDF file itself, counting the first page of the "
                 "file as 1 (not the journal's printed page numbers)",
    "printed": "the journal's printed page number shown on the page",
}

PROMPT = """\
# Task

Two review articles are attached as PDF files:

- HWA17: Hwang, Myung & Sun (2017), "Sodium-ion batteries: present and future", Chem. Soc. Rev. 46, 3529–3614.
- NOE21: Noerochim, Suwarno, Idris & Dipojono (2021), "Recent Development of Nickel-Rich and Cobalt-Free Cathode Materials for Lithium-Ion Batteries", Batteries 7, 84.

The attached file "ai_extraction_rules.md" contains a fixed set of extraction rules.
Apply those rules exactly as written to every page of both PDFs. Use only the two PDFs
and the rules; do not use other knowledge, other sources or the internet.

# Output format

Produce one CSV file (UTF-8, comma-separated, every value enclosed in double quotes,
first row = header). The header row must be exactly:

{header}

One row per record, covering both sources. Formatting conventions for this CSV:

- An empty value means null: write "".
- `parent_composition_type` and `target_composition_type` are the two parts of the
  rules' `composition_type` field.
- `confounders`: tokens separated by ";" with no spaces, or "" if none.
- Page numbers in `record_id` and `location` use {page_convention}.
- Do not add the fields schema_version, extractor, parent_normalized or target_normalized;
  they are filled in later by software.
- Allowed values:
{enums}

If the full CSV does not fit in one reply, stop at the end of a complete row and
continue from the next row when asked to continue, without repeating the header or
any row.
"""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()


def split_blocks(text: str):
    """Split markdown into blocks separated by blank lines, keeping exact text."""
    return [b for b in re.split(r"\n[ \t]*\n", text.replace("\r\n", "\n")) if b.strip()]


def block_label(block: str):
    s = block.lstrip()
    if s.startswith("**"):
        return s[2:]
    if s.startswith("#"):
        return s.lstrip("#").lstrip()
    return None


def is_labeled(block: str) -> bool:
    s = block.lstrip()
    return s.startswith("**") or s.startswith("#")


def select_rules(text: str):
    blocks = split_blocks(text)
    picked, missing = [], []
    for label in RULE_LABELS:
        idx = [i for i, b in enumerate(blocks)
               if (block_label(b) or "").startswith(label)]
        if len(idx) != 1:
            missing.append(f"{label!r} found {len(idx)} times (need exactly 1)")
            continue
        i = idx[0]
        group = [blocks[i]]
        j = i + 1
        while j < len(blocks) and not is_labeled(blocks[j]):
            group.append(blocks[j])
            j += 1
        picked.append("\n\n".join(group))
    return picked, missing


def build(protocol: Path, out_dir: Path, page_convention: str):
    if out_dir.exists():
        sys.exit(f"Refusing to write into existing directory: {out_dir}")
    raw = protocol.read_bytes()
    picked, missing = select_rules(raw.decode("utf-8"))
    if missing:
        sys.exit("Locked protocol does not contain the expected rule blocks:\n  "
                 + "\n  ".join(missing) + "\nNothing was written.")
    proto_hash = sha256_bytes(raw)
    rules = (f"<!-- Copied verbatim from {protocol.name} (SHA-256 {proto_hash}); "
             f"blocks: {', '.join(RULE_LABELS)} -->\n\n" + "\n\n".join(picked) + "\n")
    enums = "\n".join(f"  - {name}: " + ", ".join(sorted(vals)) for name, vals in [
        ("source", tool.SOURCES),
        ("parent_composition_type / target_composition_type", tool.COMPOSITION_TYPES),
        ("relationship_type", tool.RELATIONSHIP_TYPES),
        ("characterization", tool.CHARACTERIZATIONS),
        ("decision", tool.DECISIONS),
        ("exclusion_reason", tool.EXCLUSION_REASONS),
    ])
    prompt = PROMPT.format(header=",".join(f'"{c}"' for c in tool.COLUMNS),
                           page_convention=PAGE_CONVENTIONS[page_convention],
                           enums=enums)
    out_dir.mkdir(parents=True)
    files = {"ai_extraction_rules.md": rules, "ai_extraction_prompt.md": prompt}
    manifest = {"locked_protocol": protocol.name, "locked_protocol_sha256": proto_hash,
                "page_convention": page_convention, "rule_labels": RULE_LABELS, "files": {}}
    for name, content in files.items():
        data = content.encode("utf-8")
        (out_dir / name).write_bytes(data)
        manifest["files"][name] = sha256_bytes(data)
    (out_dir / "package_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(manifest, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("protocol", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--page-convention", choices=sorted(PAGE_CONVENTIONS), required=True)
    a = ap.parse_args(argv)
    build(a.protocol, a.out_dir, a.page_convention)


if __name__ == "__main__":
    main()
