#!/usr/bin/env python3
"""RRB-01: make a committable copy of an AI Studio transcript.

Usage:
  python reduce_transcript.py <raw_transcript> <reduced_out.json>

AI Studio's saved prompt file embeds every uploaded file as base64 text, which makes
the transcript huge and trips secret scanners. This script copies the transcript
unchanged except that each embedded base64 value longer than 1000 characters is
replaced by a placeholder with the decoded size and SHA-256. Every other value,
including all prompts, model replies and thinking, is kept exactly.

The raw transcript is not modified; keep it outside the repository and record its
SHA-256. The printed attachment hashes can be checked against the frozen sources.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import json
import sys
from pathlib import Path

MIN_LEN = 1000


def reduce(obj, found):
    if isinstance(obj, dict):
        return {k: reduce(v, found) for k, v in obj.items()}
    if isinstance(obj, list):
        return [reduce(v, found) for v in obj]
    if isinstance(obj, str) and len(obj) > MIN_LEN:
        try:
            raw = base64.b64decode(obj, validate=True)
        except (binascii.Error, ValueError):
            return obj
        digest = hashlib.sha256(raw).hexdigest().upper()
        found.append((len(raw), digest, raw[:8]))
        return f"<embedded file omitted: {len(raw)} bytes, sha256={digest}>"
    return obj


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        sys.exit(__doc__)
    src, out = Path(argv[0]), Path(argv[1])
    if out.exists():
        sys.exit(f"Refusing to overwrite existing file: {out}")
    raw_bytes = src.read_bytes()
    data = json.loads(raw_bytes.decode("utf-8"))
    found = []
    reduced = reduce(data, found)
    out.write_text(json.dumps(reduced, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"raw transcript      {src.name}: {len(raw_bytes)} bytes, "
          f"sha256={hashlib.sha256(raw_bytes).hexdigest().upper()}")
    for size, digest, head in found:
        kind = "PDF" if head.startswith(b"%PDF") else "file"
        print(f"embedded {kind:<4}       {size} bytes, sha256={digest}")
    print(f"reduced transcript  {out.name}: sha256="
          f"{hashlib.sha256(out.read_bytes()).hexdigest().upper()}")


if __name__ == "__main__":
    main()
