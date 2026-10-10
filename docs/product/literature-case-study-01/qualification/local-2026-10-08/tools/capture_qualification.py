"""Multi-objective qualification harness (pre-fix reproduction / post-fix capture).

Derived from capture_pre_fix_qualification.py with these deliberate differences:
  * Requests are read from the FROZEN baseline JSON (registered_request), so
    they cannot drift from what was captured on 2026-10-07.
  * Output is written ONLY to --out (must be outside the repo). The frozen
    evidence file is opened read-only and never written.
  * Each case runs twice in fresh sessions to check determinism, with timing.
  * Every case's projected result is compared to the frozen baseline.
  * Provenance: git HEAD, working-tree changes, app import path, masked DB target.

Same service, schemas, call path and projection (compact_result) as the original.

Run FROM the worktree whose code you want to exercise:
    python capture_qualification.py --label pre-fix-reproduction --baseline <frozen.json> --out <dir>
    python capture_qualification.py --label post-fix --baseline <frozen.json> --out <dir>

Exit code: 0 = all cases match baseline (pre) / capture completed (post);
           1 = reproduction mismatch or nondeterminism; 2 = setup error.
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    ).stdout.strip()


def masked_db_target(url: str) -> str:
    # Keep scheme/host/port/db; drop credentials.
    if "@" in url:
        scheme, rest = url.split("://", 1) if "://" in url else ("", url)
        return f"{scheme}://***@{rest.split('@', 1)[1]}"
    return url


def compact_result(case: dict, result: dict) -> dict:
    # Identical projection to the original capture script.
    return {
        "material_id": result["material_id"],
        "base_formula": result.get("base_formula"),
        "mode": result["mode"],
        "constraint_policy": result.get("constraint_policy"),
        "search_metadata": result["search_metadata"],
        "ranked_candidates": [
            {
                "material_id": c["material_id"],
                "formula": c.get("formula"),
                "score": c["score"],
                "reasons": c.get("reasons", []),
                "warnings": c.get("warnings", []),
            }
            for c in result["ranked_candidates"]
        ],
        "returned_chain_material_ids": [
            [m["material_id"] for m in chain["materials"]]
            for chain in result["chains"]
        ],
    }


def canon(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True)


def run_once(cases, SessionLocal, Service, Request, Objective):
    session = SessionLocal()
    try:
        service = Service(session)  # one service per run, same order as original
        out, timings = {}, {}
        for case in cases:
            req = case["registered_request"]
            request = Request(
                objective=Objective(**req["objective"]),
                mode=req["mode"],
                limit=req["limit"],
            )
            start = time.perf_counter()
            result = service.explore(material_id=case["source_id"], request=request)
            timings[case["case_id"]] = round(time.perf_counter() - start, 4)
            # Round-trip through JSON so types match the stored baseline.
            out[case["case_id"]] = json.loads(canon(compact_result(case, result)))
        return out, timings
    finally:
        session.close()


def summarize_change(before: dict, after: dict) -> dict:
    ids = lambda r: [c["material_id"] for c in r["ranked_candidates"]]
    return {
        "candidates_before": ids(before),
        "candidates_after": ids(after),
        "chains_before": before["returned_chain_material_ids"],
        "chains_after": after["returned_chain_material_ids"],
        "metadata_changed_keys": sorted(
            k
            for k in set(before["search_metadata"]) | set(after["search_metadata"])
            if before["search_metadata"].get(k) != after["search_metadata"].get(k)
        ),
        "warnings_after": sorted(
            {w for c in after["ranked_candidates"] for w in c["warnings"]}
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, choices=["pre-fix-reproduction", "post-fix"])
    ap.add_argument("--baseline", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    cwd = Path.cwd().resolve()
    out_dir = args.out.resolve()
    if cwd == out_dir or cwd in out_dir.parents:
        print("ABORT: --out must be outside the repository/worktree.")
        return 2

    sys.path.insert(0, str(cwd))
    import app
    from app.core.config import settings
    from app.core.database import SessionLocal
    from app.schemas.discovery import ResearchObjective
    from app.schemas.research_objective_exploration import (
        ResearchObjectiveExplorationRequest,
    )
    from app.services.research.objective_exploration_service import (
        ResearchObjectiveExplorationService,
    )

    app_path = Path(app.__file__).resolve()
    if cwd not in app_path.parents:
        print(f"ABORT: 'app' imported from {app_path}, not from {cwd}.")
        return 2

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))  # read-only
    cases = baseline["cases"]
    frozen = {c["case_id"]: c["result"] for c in cases}

    deps = (SessionLocal, ResearchObjectiveExplorationService,
            ResearchObjectiveExplorationRequest, ResearchObjective)
    run1, t1 = run_once(cases, *deps)
    run2, t2 = run_once(cases, *deps)

    per_case, all_match, deterministic = [], True, True
    for case in cases:
        cid = case["case_id"]
        same_as_frozen = canon(run1[cid]) == canon(frozen[cid])
        repeat_identical = canon(run1[cid]) == canon(run2[cid])
        all_match &= same_as_frozen
        deterministic &= repeat_identical
        entry = {
            "case_id": cid,
            "description": case["description"],
            "source_id": case["source_id"],
            "registered_request": case["registered_request"],
            "matches_frozen_baseline": same_as_frozen,
            "deterministic_across_two_runs": repeat_identical,
            "seconds_run1": t1[cid],
            "seconds_run2": t2[cid],
            "result": run1[cid],
        }
        if not same_as_frozen:
            entry["change_vs_frozen"] = summarize_change(frozen[cid], run1[cid])
        per_case.append(entry)

    status = git("status", "--porcelain")
    artifact = {
        "artifact_type": (
            "PRE_FIX_HARNESS_REPRODUCTION_CHECK"
            if args.label == "pre-fix-reproduction"
            else "POST_FIX_MULTI_OBJECTIVE_QUALIFICATION"
        ),
        "label": args.label,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "baseline_artifact": baseline["artifact_type"],
        "baseline_captured_at_utc": baseline["captured_at_utc"],
        "case_study_01_reexecution": False,
        "scientific_validation": False,
        "provenance": {
            "git_head": git("rev-parse", "HEAD"),
            "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "working_tree_changes": status.splitlines(),
            "app_import_path": str(app_path),
            "database_target": masked_db_target(str(settings.database_url)),
        },
        "summary": {
            "all_cases_match_frozen_baseline": all_match,
            "all_cases_deterministic": deterministic,
        },
        "cases": per_case,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"MG-LCS01-{args.label.upper()}-QUALIFICATION-{stamp}.json"
    path.write_text(canon(artifact), encoding="utf-8")

    print(f"WROTE {path}")
    print(f"database: {artifact['provenance']['database_target']}")
    print(f"head: {artifact['provenance']['git_head']}  changes: {len(status.splitlines())} file(s)")
    for e in per_case:
        flag = "MATCH " if e["matches_frozen_baseline"] else "CHANGED"
        det = "det" if e["deterministic_across_two_runs"] else "NONDETERMINISTIC"
        print(f"{e['case_id']}: {flag} {det} {e['seconds_run1']:.3f}s/{e['seconds_run2']:.3f}s")
        if "change_vs_frozen" in e:
            ch = e["change_vs_frozen"]
            print(f"    candidates {ch['candidates_before']} -> {ch['candidates_after']}")
            print(f"    chains     {ch['chains_before']} -> {ch['chains_after']}")
            if ch["metadata_changed_keys"]:
                print(f"    metadata changed: {ch['metadata_changed_keys']}")
            if ch["warnings_after"]:
                print(f"    warnings after: {ch['warnings_after']}")

    if not deterministic:
        return 1
    if args.label == "pre-fix-reproduction" and not all_match:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
