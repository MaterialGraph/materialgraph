"""SRQ-01 S4 attribution: run the same requests at four commits and diff each step.

Run `capture` once inside each git worktree (release-3, after PR-B1, after
PR-B2, current main), then `compare` once. Read-only: requests only.

  python s4_attribution.py capture <label> <out_dir>   (cwd = a worktree)
  python s4_attribution.py compare <out_dir>

Labels, in order: r3, b1, b2, b3. Uses the production-equivalent local
database unless DATABASE_URL is already set.
"""

import json
import os
import sys
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/materialgraph_test_mg_de_007",
)

LABELS = ["r3", "b1", "b2", "b3"]
STEP_NAMES = {"b1": "PR-B1 ordering", "b2": "PR-B2 formula groups", "b3": "PR-B3 admission sequence"}
NAFEPO4 = {"mp-19226", "mp-746030", "mp-753672", "mp-1192859"}
BASE = {"avoid_elements": [], "prefer_elements": [], "preserve_elements": [], "target_family": None,
        "max_hops": 2, "limit": 10, "prefer_lower_criticality": True, "require_stable_materials": False}
CS01 = {**BASE, "avoid_elements": ["Li", "Co"], "prefer_elements": ["Na", "K"],
        "preserve_elements": ["Fe", "P", "O"], "target_family": "phosphate"}
REQUESTS = {
    "cs01_l5": (5, {"objective": {**CS01, "limit": 5}, "mode": "balanced", "limit": 5}),
    "cs01_l10": (5, {"objective": CS01, "mode": "balanced", "limit": 10}),
    "strict_l10": (5, {"objective": {**BASE, "avoid_elements": ["Li"]}, "mode": "strict", "limit": 10}),
    "q6_l10": (28, {"objective": {**BASE, "avoid_elements": ["Li"], "prefer_elements": ["Na"]},
                    "mode": "balanced", "limit": 10}),
    "frozen_avoid_only": (5, {"objective": {**BASE, "avoid_elements": ["Li"], "limit": 5},
                              "mode": "balanced", "limit": 5}),
}


def capture(label: str, out_dir: str) -> None:
    sys.path.insert(0, os.getcwd())
    from fastapi.testclient import TestClient
    from app.main import app

    out = Path(out_dir) / label
    out.mkdir(parents=True, exist_ok=True)
    client = TestClient(app)
    for name, (source, body) in REQUESTS.items():
        response = client.post(f"/api/v1/materials/{source}/discovery/objective/explore", json=body)
        if response.status_code != 200:
            raise SystemExit(f"{label} {name}: HTTP {response.status_code}: {response.text[:300]}")
        (out / f"{name}.json").write_bytes(response.content)
        print(f"{label} {name}: {len(response.content)} bytes")


def _summary(data: dict, source_mp: str) -> dict:
    ranked = [(c.get("mp_id"), c["score"]) for c in data["ranked_candidates"]]
    chains = {tuple(m.get("mp_id") for m in ch["materials"]): ch.get("scientific_usefulness_score")
              for ch in data["chains"]}
    nafepo4_ranks = [(i + 1, mp) for i, (mp, _) in enumerate(ranked) if mp in NAFEPO4]
    direct = sorted(k for k in chains if len(k) == 2 and k[0] == source_mp and k[1] in NAFEPO4)
    report = data.get("formula_correspondence") or {}
    groups = {e["material_id"]: [m["mp_id"] for m in e.get("formula_group", [])]
              for e in report.get("source_correspondence", [])}
    return {"ranked": ranked, "chains": chains, "nafepo4_ranks": nafepo4_ranks, "direct": direct,
            "groups": groups, "metadata": data.get("search_metadata", {})}


def compare(out_dir: str) -> None:
    root = Path(out_dir)
    lines = ["# S4 attribution (production-equivalent database)", ""]
    for name, (source, _) in REQUESTS.items():
        raw = {label: (root / label / f"{name}.json").read_bytes() for label in LABELS}
        data = {label: json.loads(raw[label]) for label in LABELS}
        source_mp = next(m.get("mp_id") for m in data["r3"]["chains"][0]["materials"][:1]) if data["r3"]["chains"] else None
        lines.append(f"## {name}")
        if name.startswith("frozen"):
            same = all(raw[label] == raw["r3"] for label in LABELS)
            lines += [f"Frozen request byte-identical at all four commits: **{same}**", ""]
            continue
        summaries = {label: _summary(data[label], source_mp) for label in LABELS}
        for label in LABELS:
            s = summaries[label]
            lines.append(f"- {label}: NaFePO4 ranks {s['nafepo4_ranks']}; direct chains {s['direct']}; "
                         f"groups {s['groups'] or '-'}")
        for before, after in zip(LABELS, LABELS[1:]):
            a, b = summaries[before], summaries[after]
            lines.append(f"### {before} → {after} ({STEP_NAMES[after]})")
            if a["ranked"] != b["ranked"]:
                lines.append(f"- ranked: {a['ranked']} → {b['ranked']}")
            added = [k for k in b["chains"] if k not in a["chains"]]
            dropped = [k for k in a["chains"] if k not in b["chains"]]
            if added or dropped:
                lines.append(f"- chains added {added}; dropped {dropped}")
            score_a = dict(a["ranked"])
            changed = [(mp, score_a[mp], s) for mp, s in b["ranked"] if mp in score_a and score_a[mp] != s]
            if changed:
                lines.append(f"- candidate score changes (material, before, after): {changed}")
            chain_changes = [(k, a["chains"][k], v) for k, v in b["chains"].items()
                             if k in a["chains"] and a["chains"][k] != v]
            if chain_changes:
                lines.append(f"- chain score changes: {chain_changes}")
            meta = {k: (a["metadata"].get(k), v) for k, v in b["metadata"].items() if a["metadata"].get(k) != v}
            if meta:
                lines.append(f"- search_metadata: {meta}")
            if len(lines) and lines[-1].startswith("###"):
                lines.append("- no change in ranked candidates, chains, scores or metadata")
        lines.append("")
    path = root / "s4-attribution.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWritten: {path}")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "capture":
        capture(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == "compare":
        compare(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(2)
