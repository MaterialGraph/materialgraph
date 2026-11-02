"""Compare pre- and post-deployment Objective Explore responses (SRQ-01 PR-A release).

Usage:
  python3 compare_release.py frozen PRE.json POST.json
  python3 compare_release.py aware  PRE.json POST.json

frozen: responses must be byte-identical.
aware:  post = pre + appended "formula_correspondence"; every other field
        identical except ranked_candidates[*].reasons, where only the R7.2
        alkali reason strings may change. Prints a summary of the report.

Standard library only. Read-only: never writes files.
"""

import json
import sys

OLD_ALKALI_REASON = (
    "Appears in an eligible composition chain with relationship type "
    "different alkali metal (composition not compared)."
)
NEW_REASON_PREFIX = "Appears in an eligible composition chain containing a step classified as "


def without_reasons(document: dict) -> dict:
    copy = json.loads(json.dumps(document))
    for candidate in copy.get("ranked_candidates", []):
        candidate.pop("reasons", None)
    return copy


def frozen(pre_path: str, post_path: str) -> list[str]:
    with open(pre_path, "rb") as pre, open(post_path, "rb") as post:
        return [] if pre.read() == post.read() else ["responses are not byte-identical"]


def aware(pre_path: str, post_path: str) -> list[str]:
    with open(pre_path, encoding="utf-8") as handle:
        pre = json.load(handle)
    with open(post_path, encoding="utf-8") as handle:
        post = json.load(handle)
    problems = []
    if "formula_correspondence" in pre:
        problems.append("pre-deployment response already has formula_correspondence")
    if "formula_correspondence" not in post:
        problems.append("post-deployment response has no formula_correspondence")
    if list(post)[-1:] != ["formula_correspondence"]:
        problems.append("formula_correspondence is not the last key")
    stripped = {key: value for key, value in post.items() if key != "formula_correspondence"}
    if list(pre) != list(stripped):
        problems.append("top-level keys or key order differ")
    if without_reasons(pre) != without_reasons(stripped):
        problems.append("content other than reasons differs (scores, ranks, chains, metadata or coverage)")
    for before, after in zip(pre.get("ranked_candidates", []), stripped.get("ranked_candidates", [])):
        kept_before = [r for r in before.get("reasons", []) if r != OLD_ALKALI_REASON]
        kept_after = [r for r in after.get("reasons", []) if not r.startswith(NEW_REASON_PREFIX)]
        if kept_before != kept_after:
            problems.append(f"reasons for material {before.get('material_id')} differ beyond R7.2")
        if any("composition not compared" in r for r in after.get("reasons", [])):
            problems.append(f"material {after.get('material_id')} still says 'composition not compared'")
    report = post.get("formula_correspondence") or {}
    print("source_correspondence:", [
        (entry["candidate_rank"], entry["material_id"], entry["correspondence"]["correspondence_class"])
        for entry in report.get("source_correspondence", [])
    ])
    counts: dict[str, int] = {}
    for entry in report.get("transitions", []):
        c = entry["correspondence"]
        key = f"{c['correspondence_class']}/{c['reason']}"
        counts[key] = counts.get(key, 0) + 1
    print("transitions by class/reason:", counts)
    print("not_evaluated_material_ids:", report.get("not_evaluated_material_ids"))
    print("flags: grouping", report.get("formula_grouping_available"),
          "admission", report.get("admission_reporting_available"))
    return problems


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("frozen", "aware"):
        print(__doc__)
        return 2
    problems = frozen(sys.argv[2], sys.argv[3]) if sys.argv[1] == "frozen" else aware(sys.argv[2], sys.argv[3])
    for problem in problems:
        print("PROBLEM:", problem)
    print("PASS" if not problems else "FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
