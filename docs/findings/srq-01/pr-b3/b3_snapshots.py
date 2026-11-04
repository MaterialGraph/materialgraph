"""PR-B3 snapshot helper (run from the repository root, after regenerating full snapshots).

1. Derive each pre-integration baseline as: full snapshot bytes up to
   ',"formula_correspondence":' plus the closing '}' (the existing derivation).
   Self-check first: the derivation must reproduce every committed baseline
   from its committed full snapshot; otherwise stop without writing.
2. Print a structural diff against HEAD for each case: ranked candidates,
   returned chains, and the AC8b check (same score and breakdown for every
   material and chain present in both versions).

Usage: python b3_snapshots.py [--write]
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("tests/fixtures/golden/srq01_pra")
CASES = ["cs01_source5_balanced", "q6_source28_balanced", "strict_source5_avoid_li"]
MARK = b',"formula_correspondence":'


def head_bytes(path: Path) -> bytes:
    return subprocess.run(["git", "show", f"HEAD:{path.as_posix()}"], capture_output=True, check=True).stdout


def derive(full: bytes) -> bytes:
    cut = full.index(MARK)
    return full[:cut] + b"}"


def chain_key(chain):
    return tuple(m.get("mp_id") for m in chain["materials"])


def main(write: bool) -> int:
    for case in CASES:
        if derive(head_bytes(ROOT / "full" / f"{case}.json")) != head_bytes(ROOT / f"{case}.json"):
            print(f"SELF-CHECK FAILED for {case}: derivation does not reproduce the committed baseline")
            return 1
    print("self-check passed: derivation reproduces all committed baselines")

    for case in CASES:
        full_path = ROOT / "full" / f"{case}.json"
        new_full = full_path.read_bytes()
        new_base = derive(new_full)
        base_path = ROOT / f"{case}.json"
        changed = new_base != base_path.read_bytes()
        if write and changed:
            base_path.write_bytes(new_base)
        old = json.loads(head_bytes(full_path))
        new = json.loads(new_full)
        print(f"\n=== {case} (baseline {'re-derived' if changed else 'unchanged'}{'' if write or not changed else ', not written'}) ===")
        old_ranked = [(c.get("mp_id"), c["score"]) for c in old["ranked_candidates"]]
        new_ranked = [(c.get("mp_id"), c["score"]) for c in new["ranked_candidates"]]
        print("ranked before:", old_ranked)
        print("ranked after: ", new_ranked)
        old_chains = {chain_key(c): c for c in old["chains"]}
        new_chains = {chain_key(c): c for c in new["chains"]}
        print("chains added:  ", [k for k in new_chains if k not in old_chains])
        print("chains dropped:", [k for k in old_chains if k not in new_chains])
        problems = []
        old_by_mp = {c.get("mp_id"): c for c in old["ranked_candidates"]}
        for c in new["ranked_candidates"]:
            before = old_by_mp.get(c.get("mp_id"))
            if before is not None and before["score"] != c["score"]:
                problems.append(f"candidate {c.get('mp_id')} score {before['score']} -> {c['score']}")
        for key, chain in new_chains.items():
            before = old_chains.get(key)
            if before is not None and (
                before.get("scientific_usefulness_score") != chain.get("scientific_usefulness_score")
                or before.get("score_breakdown") != chain.get("score_breakdown")
            ):
                problems.append(f"chain {key} score or breakdown changed")
        others = [k for k in new if k not in ("ranked_candidates", "chains", "formula_correspondence",
                                              "objective_coverage", "search_metadata") and old.get(k) != new.get(k)]
        if others:
            problems.append(f"other top-level fields changed: {others}")
        if old.get("search_metadata") != new.get("search_metadata"):
            diff = {k: (old["search_metadata"].get(k), v) for k, v in new["search_metadata"].items()
                    if old["search_metadata"].get(k) != v}
            print("search_metadata changes:", diff)
        report = new.get("formula_correspondence") or {}
        print("expansions:", [(e["expanded_material_id"], e["groups_found"], e["groups_admitted"],
                               [x["reason"] for x in e["excluded"]]) for e in report.get("expansions", [])])
        print("AC8b:", "PASS" if not problems else "FAIL")
        for problem in problems:
            print("  -", problem)
    if not write:
        print("\nDry run only. Re-run with --write to write the re-derived baselines.")
    return 0


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
