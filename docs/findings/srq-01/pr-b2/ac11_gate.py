"""SRQ-01 AC11 gate: representative sensitivity for the NaFePO4 formula group.

Runs objective-aware Objective Explore requests against the production-equivalent
local database once with the default representative and once with each NaFePO4
record forced as representative, then records every difference.

Read-only: requests only; nothing is written to the database.

Usage (from the repository root, PR-B2 checked out, local `db` running):
    python ac11_gate.py C:\\mg-validation\\ac11
"""

import json
import os
import sys
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/materialgraph_test_mg_de_007",
)
sys.path.insert(0, os.getcwd())

from fastapi.testclient import TestClient  # noqa: E402

from app.domain import ordering  # noqa: E402
from app.main import app  # noqa: E402

NAFEPO4_RECORDS = ["mp-19226", "mp-746030", "mp-753672", "mp-1192859"]
SOURCE = 5  # LiFePO4 (mp-19017); same local ID in the production-equivalent database
BASE = {"avoid_elements": [], "prefer_elements": [], "preserve_elements": [], "target_family": None,
        "max_hops": 2, "limit": 10, "prefer_lower_criticality": True, "require_stable_materials": False}
REQUESTS = {
    "cs01_l5": {"objective": {**BASE, "avoid_elements": ["Li", "Co"], "prefer_elements": ["Na", "K"],
                              "preserve_elements": ["Fe", "P", "O"], "target_family": "phosphate", "limit": 5},
                "mode": "balanced", "limit": 5},
    "cs01_l10": {"objective": {**BASE, "avoid_elements": ["Li", "Co"], "prefer_elements": ["Na", "K"],
                               "preserve_elements": ["Fe", "P", "O"], "target_family": "phosphate"},
                 "mode": "balanced", "limit": 10},
    "strict_l10": {"objective": {**BASE, "avoid_elements": ["Li"]}, "mode": "strict", "limit": 10},
}
DEFAULT_CHOOSE = ordering.choose_representative


def forcing(target_mp_id):
    def choose(members):
        for member in members:
            if member.get("mp_id") == target_mp_id:
                return member
        return DEFAULT_CHOOSE(members)
    return choose


def summary(data):
    ranked = [(c.get("mp_id"), c["score"]) for c in data["ranked_candidates"]]
    chains = [(tuple(m.get("mp_id") for m in ch["materials"]), ch.get("scientific_usefulness_score"))
              for ch in data["chains"]]
    report = data.get("formula_correspondence") or {}
    analogs = [(e["candidate_rank"], e["material_id"],
                [(m["mp_id"], m["energy_above_hull"], m["traversed"]) for m in e["formula_group"]])
               for e in report.get("source_correspondence", [])]
    return {"ranked": ranked, "chains": chains, "source_analogs": analogs,
            "eligible_total": data["search_metadata"].get("candidates_eligible_total"),
            "admitted_total": data["search_metadata"].get("candidates_admitted_total")}


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    client = TestClient(app)
    lines = ["# AC11 representative sensitivity (NaFePO4)", ""]
    for name, body in REQUESTS.items():
        runs = {}
        for label, choose in [("default", DEFAULT_CHOOSE)] + [(mp, forcing(mp)) for mp in NAFEPO4_RECORDS]:
            ordering.choose_representative = choose
            try:
                response = client.post(f"/api/v1/materials/{SOURCE}/discovery/objective/explore", json=body)
            finally:
                ordering.choose_representative = DEFAULT_CHOOSE
            assert response.status_code == 200, response.text
            data = response.json()
            (out / f"{name}__{label}.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
            runs[label] = summary(data)
        base = runs["default"]
        lines += [f"## {name}", "", f"Default: ranked {base['ranked']}", "",
                  f"Default source analogs and groups: {base['source_analogs']}", ""]
        for mp in NAFEPO4_RECORDS:
            run = runs[mp]
            diffs = [key for key in ("ranked", "chains", "source_analogs", "eligible_total", "admitted_total")
                     if run[key] != base[key]]
            lines.append(f"- forced {mp}: {'identical to default' if not diffs else 'differs in ' + ', '.join(diffs)}")
            for key in diffs:
                lines.append(f"  - {key}: {run[key]}")
        lines.append("")
    report_path = out / "ac11-summary.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nWritten: {report_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ac11")
