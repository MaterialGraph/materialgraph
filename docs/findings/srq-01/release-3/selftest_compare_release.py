"""Dry run for compare_release.py: proves it accepts the expected R7.2 change
and rejects deliberate unintended changes. Standard library only.

Usage: python selftest_compare_release.py PRE.json
PRE.json: an objective-aware response captured before deployment (for
example docs/findings/srq-01/cs01-response.json). Writes temporary files to
a temporary directory only.
"""

import copy
import json
import os
import subprocess
import sys
import tempfile

OLD = ("Appears in an eligible composition chain with relationship type "
       "different alkali metal (composition not compared).")
NEW = ("Appears in an eligible composition chain containing a step classified as "
       "different alkali metal (element ratios differ).")
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "compare_release.py")


def expected_post(pre):
    post = copy.deepcopy(pre)
    for candidate in post["ranked_candidates"]:
        candidate["reasons"] = [NEW if r == OLD else r for r in candidate["reasons"]]
    post["formula_correspondence"] = {"source_correspondence": [], "transitions": [],
                                      "not_evaluated_material_ids": [],
                                      "formula_grouping_available": False,
                                      "admission_reporting_available": False}
    return post


def mutations(post):
    def m(fn):
        doc = copy.deepcopy(post)
        fn(doc)
        return doc
    rc = "ranked_candidates"
    yield "candidate identity changed", m(lambda d: d[rc][0].__setitem__("material_id", 999999))
    yield "candidate ranking swapped", m(lambda d: d[rc].__setitem__(slice(0, 2), [d[rc][1], d[rc][0]]))
    yield "candidate score changed", m(lambda d: d[rc][0].__setitem__("score", d[rc][0]["score"] + 1))
    yield "chain order swapped", m(lambda d: d["chains"].__setitem__(slice(0, 2), [d["chains"][1], d["chains"][0]]))
    yield "chain material changed", m(lambda d: d["chains"][0]["materials"][-1].__setitem__("material_id", 999999))
    yield "search metadata changed", m(lambda d: d["search_metadata"].__setitem__("generated_chain_count", -1))
    yield "objective coverage changed", m(lambda d: d["objective_coverage"].__setitem__("returned_chain_count", -1))
    yield "unrelated reason added", m(lambda d: d[rc][0]["reasons"].append("Unexpected reason."))
    yield "report missing", m(lambda d: d.pop("formula_correspondence"))


def run(mode, pre_path, post_path):
    result = subprocess.run([sys.executable, SCRIPT, mode, pre_path, post_path],
                            capture_output=True, text=True)
    return result.returncode


def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        pre = json.load(handle)
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        pre_path = os.path.join(tmp, "pre.json")
        with open(pre_path, "w", encoding="utf-8") as handle:
            json.dump(pre, handle)
        post = expected_post(pre)
        cases = [("expected R7.2 change", post, 0)] + [(name, doc, 1) for name, doc in mutations(post)]
        for name, doc, expected in cases:
            path = os.path.join(tmp, "post.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(doc, handle)
            code = run("aware", pre_path, path)
            ok = code == expected
            failures += not ok
            print(f"{'ok ' if ok else 'BAD'} aware  {name}: exit {code}, expected {expected}")
        raw = open(pre_path, "rb").read()
        changed = os.path.join(tmp, "changed.json")
        with open(changed, "wb") as handle:
            handle.write(raw[:-1] + (b" " if raw[-1:] != b" " else b"\n"))
        for name, path, expected in (("frozen identical", pre_path, 0), ("frozen one byte changed", changed, 1)):
            code = run("frozen", pre_path, path)
            ok = code == expected
            failures += not ok
            print(f"{'ok ' if ok else 'BAD'} frozen {name}: exit {code}, expected {expected}")
    print("SELFTEST PASS" if not failures else f"SELFTEST FAIL ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
