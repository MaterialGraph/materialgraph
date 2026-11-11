#!/usr/bin/env python3
"""RRB-01 Stage 5: normalize published formulas with exact rational arithmetic.

Usage:
  python normalize_formulas.py <run.jsonl> <run.normalized.jsonl>

Reads a frozen run JSONL and writes a NEW file in which parent_normalized and
target_normalized are filled, plus a "normalization" object per record with the
status of each side. The input file is never modified. Every field other than these
is copied unchanged. A formula that cannot be parsed unambiguously is never guessed:
its normalized value stays null and the failure reason is recorded.

Canonical form: elements in alphabetical order, each with an explicit integer count,
after scaling all amounts to integers and dividing by their greatest common divisor.
Example: "LiNi0.8Mn0.1Co0.1O2" -> "Co1Li10Mn1Ni8O20".

Parsing rules (mechanical, no chemistry judgment):
  * Element symbols must be real elements; amounts may be integers, decimals (0.5)
    or fractions (2/3); groups use (), [] or {} with an optional multiplier.
  * Unicode subscript digits are read as digits.
  * A middle dot (·) joins additive parts; each part may start with a multiplier.
  * A leading phase label followed by a hyphen is removed and reported in the note.
    Only these labels: one Greek letter (α-, β-, ...), O1-O9, P1-P9, T-, M-, H-.
    Any other prefix (e.g. "C-" for carbon-coated) makes the formula a failure.
  * Anything else (spaces, variables such as x or δ, charges, "@", "/", words,
    unknown symbols) is a failure.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from fractions import Fraction
from functools import reduce
from math import gcd
from pathlib import Path

ELEMENTS = set("""H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni
Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr
Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th
Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og""".split())

SUBSCRIPTS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
PHASE_PREFIX = re.compile(r"^([α-ωΑ-Ω]|[OP][1-9]|[TMH])[-–‑](?=[A-Z(\[{])")
NUMBER = re.compile(r"(\d+\.\d+|\d+/\d+|\d+)")
OPEN, CLOSE = "([{", ")]}"


class NormalizationError(ValueError):
    pass


def _number(s, i):
    m = NUMBER.match(s, i)
    if not m:
        return Fraction(1), i
    text = m.group(1)
    if "/" in text:
        a, b = text.split("/")
        if int(b) == 0:
            raise NormalizationError("division by zero in amount")
        return Fraction(int(a), int(b)), m.end()
    return Fraction(text), m.end()


def _parse_group(s, i, closer):
    counts = {}
    while i < len(s):
        ch = s[i]
        if ch in CLOSE:
            if ch != closer:
                raise NormalizationError(f"unbalanced bracket at position {i}")
            return counts, i + 1
        if ch in OPEN:
            inner, i = _parse_group(s, i + 1, CLOSE[OPEN.index(ch)])
            mult, i = _number(s, i)
            for el, n in inner.items():
                counts[el] = counts.get(el, 0) + n * mult
            continue
        m = re.match(r"[A-Z][a-z]?", s[i:])
        if not m:
            raise NormalizationError(f"unexpected character {ch!r} at position {i}")
        sym = m.group(0)
        if sym not in ELEMENTS:
            raise NormalizationError(f"unknown element symbol {sym!r}")
        i += len(sym)
        amount, i = _number(s, i)
        counts[sym] = counts.get(sym, 0) + amount
    if closer:
        raise NormalizationError("unclosed bracket")
    return counts, i


def normalize(formula):
    """Return (canonical, note). Raise NormalizationError on failure."""
    if formula is None:
        return None, None
    s = formula.translate(SUBSCRIPTS)
    note = None
    m = PHASE_PREFIX.match(s)
    if m:
        note = f"phase label {m.group(1)!r} removed"
        s = s[m.end():]
    if s == "" or any(c.isspace() for c in s):
        raise NormalizationError("empty or contains whitespace")
    total = {}
    for part in s.split("·"):
        if part == "":
            raise NormalizationError("empty part around '·'")
        mult, i = _number(part, 0)
        counts, end = _parse_group(part, i, "")
        if end != len(part):
            raise NormalizationError("trailing characters")
        for el, n in counts.items():
            total[el] = total.get(el, 0) + n * mult
    if not total or any(v <= 0 for v in total.values()):
        raise NormalizationError("no positive element amounts")
    lcm = reduce(lambda a, b: a * b // gcd(a, b), (v.denominator for v in total.values()), 1)
    ints = {el: int(v * lcm) for el, v in total.items()}
    g = reduce(gcd, ints.values())
    canon = "".join(f"{el}{ints[el] // g}" for el in sorted(ints))
    return canon, note


def normalize_record(rec):
    out = dict(rec)
    status = {}
    for side in ("parent", "target"):
        raw = rec.get(f"{side}_as_published")
        try:
            canon, note = normalize(raw)
            out[f"{side}_normalized"] = canon
            status[side] = {"status": "null" if raw is None else "ok", "note": note}
        except NormalizationError as e:
            out[f"{side}_normalized"] = None
            status[side] = {"status": "failed", "note": str(e)}
    out["normalization"] = status
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        sys.exit(__doc__)
    src, dst = Path(argv[0]), Path(argv[1])
    if dst.exists():
        sys.exit(f"Refusing to overwrite existing file: {dst}")
    lines = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = [normalize_record(r) for r in lines]
    data = "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in out)
    dst.write_bytes(data.encode("utf-8"))
    failed = sum(r["normalization"][s]["status"] == "failed" for r in out for s in ("parent", "target"))
    noted = sum(bool(r["normalization"][s]["note"]) and r["normalization"][s]["status"] == "ok"
                for r in out for s in ("parent", "target"))
    print(json.dumps({
        "input": src.name, "input_sha256": hashlib.sha256(src.read_bytes()).hexdigest().upper(),
        "output": dst.name, "output_sha256": hashlib.sha256(dst.read_bytes()).hexdigest().upper(),
        "records": len(out), "formulas_failed": failed, "phase_labels_removed": noted,
    }, indent=2))


if __name__ == "__main__":
    main()
