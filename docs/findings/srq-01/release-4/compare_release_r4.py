"""Release 4 (SRQ-01 PR-B) pre/post comparison. Standard library only; read-only.

  python3 compare_release_r4.py frozen PRE POST
      PASS only if byte-identical.
  python3 compare_release_r4.py aware PRE POST [--expect-nafepo4-group] [--expect-direct-nafepo4]
      Results are allowed to change (PR-B changes selection and order). PASS only if:
        - every ranked material present in both keeps its objective rule score;
        - every returned chain (by MP-ID path) present in both keeps its score
          and score breakdown;
        - POST reports formula groups and admission counts (both flags true,
          expansions present);
        - with --expect-nafepo4-group: a NaFePO4 record is a source analog with a
          non-empty formula group (admitted directly through its group);
        - with --expect-direct-nafepo4: a returned chain is exactly
          mp-19017 -> mp-19226; its transition is classified
          exact_alkali_replacement in the report; NaFePO4's group is exactly
          the four expected records with only mp-19226 traversed; and the
          source expansion reports at least one admitted exact-analog group.
      Prints every change so it can be compared with the local attribution.
  python3 compare_release_r4.py selftest PRE
      Dry run: proves the aware rules accept order/selection changes and reject
      score, breakdown and flag violations, and that frozen rejects one byte.
"""

import copy
import json
import os
import subprocess
import sys
import tempfile

NAFEPO4 = {"mp-19226", "mp-746030", "mp-753672", "mp-1192859"}
LIFEPO4 = "mp-19017"
REPRESENTATIVE = "mp-19226"


def frozen(pre_path, post_path):
    with open(pre_path, "rb") as a, open(post_path, "rb") as b:
        return [] if a.read() == b.read() else ["responses are not byte-identical"]


def _chains(doc):
    return {tuple(m.get("mp_id") for m in c["materials"]): c for c in doc.get("chains", [])}


def direct_nafepo4_problems(post):
    problems = []
    report = post.get("formula_correspondence") or {}
    chains = post.get("chains", [])
    position = next((i + 1 for i, c in enumerate(chains)
                     if [m.get("mp_id") for m in c["materials"]] == [LIFEPO4, REPRESENTATIVE]), None)
    if position is None:
        return ["no returned chain mp-19017 -> mp-19226"]
    step = next((t for t in report.get("transitions", [])
                 if t["chain_position"] == position and t["transition_index"] == 0), None)
    if step is None or step["correspondence"]["correspondence_class"] != "exact_alkali_replacement":
        problems.append("direct step not classified exact_alkali_replacement in the report")
    mp_by_id = {c["material_id"]: c.get("mp_id") for c in post["ranked_candidates"]}
    entry = next((e for e in report.get("source_correspondence", [])
                  if mp_by_id.get(e["material_id"]) == REPRESENTATIVE), None)
    if entry is None:
        problems.append("mp-19226 is not a reported source analog")
    else:
        members = {m["mp_id"] for m in entry.get("formula_group", [])}
        traversed = [m["mp_id"] for m in entry.get("formula_group", []) if m.get("traversed")]
        if members != NAFEPO4:
            problems.append(f"NaFePO4 group is {sorted(members)}, expected the four records")
        if traversed != [REPRESENTATIVE]:
            problems.append(f"traversed members {traversed}, expected only mp-19226")
    source_id = post.get("material_id")
    expansion = next((e for e in report.get("expansions", []) if e["expanded_material_id"] == source_id), None)
    if expansion is None or expansion.get("groups_admitted", 0) < 1:
        problems.append("source expansion does not report an admitted exact-analog group")
    return problems


def aware(pre_path, post_path, expect_group=False, expect_direct=False):
    with open(pre_path, encoding="utf-8") as h:
        pre = json.load(h)
    with open(post_path, encoding="utf-8") as h:
        post = json.load(h)
    problems = []
    pre_scores = {c.get("mp_id"): c["score"] for c in pre["ranked_candidates"]}
    post_ranked = [(c.get("mp_id"), c["score"]) for c in post["ranked_candidates"]]
    print("ranked before:", [(c.get("mp_id"), c["score"]) for c in pre["ranked_candidates"]])
    print("ranked after: ", post_ranked)
    for mp, score in post_ranked:
        if mp in pre_scores and pre_scores[mp] != score:
            problems.append(f"ranked material {mp} score {pre_scores[mp]} -> {score}")
    a, b = _chains(pre), _chains(post)
    print("chains added:  ", [k for k in b if k not in a])
    print("chains dropped:", [k for k in a if k not in b])
    for key, chain in b.items():
        if key in a and (a[key].get("scientific_usefulness_score") != chain.get("scientific_usefulness_score")
                         or a[key].get("score_breakdown") != chain.get("score_breakdown")):
            problems.append(f"chain {key} score or breakdown changed")
    report = post.get("formula_correspondence") or {}
    if report.get("formula_grouping_available") is not True:
        problems.append("formula_grouping_available is not true")
    if report.get("admission_reporting_available") is not True:
        problems.append("admission_reporting_available is not true")
    if not report.get("expansions"):
        problems.append("expansions missing or empty")
    mp_by_id = {c["material_id"]: c.get("mp_id") for c in post["ranked_candidates"]}
    groups = {mp_by_id.get(e["material_id"]): [m["mp_id"] for m in e.get("formula_group", [])]
              for e in report.get("source_correspondence", [])}
    print("source analogs and groups:", groups)
    direct = [k for k in b if len(k) == 2 and k[1] in NAFEPO4]
    print("direct chains to a NaFePO4 record:", direct)
    if expect_group and not any(mp in NAFEPO4 and members for mp, members in groups.items()):
        problems.append("no NaFePO4 source analog with a non-empty formula group")
    if expect_direct:
        problems.extend(direct_nafepo4_problems(post))
    meta = {k: (pre["search_metadata"].get(k), v) for k, v in post["search_metadata"].items()
            if pre["search_metadata"].get(k) != v}
    print("search_metadata changes:", meta)
    return problems


def _run(args):
    return subprocess.run([sys.executable, os.path.abspath(__file__), *args], capture_output=True, text=True).returncode


def selftest(pre_path):
    with open(pre_path, encoding="utf-8") as h:
        pre = json.load(h)
    pre.pop("formula_correspondence", None)
    base = copy.deepcopy(pre)
    base["ranked_candidates"] = list(reversed(base["ranked_candidates"]))
    base["chains"] = list(reversed(base["chains"]))
    first = next(iter(_chains(base)), None)
    base["formula_correspondence"] = {
        "formula_grouping_available": True, "admission_reporting_available": True,
        "expansions": [{"expanded_material_id": 5, "groups_found": 1, "groups_admitted": 1, "excluded": []}],
        "source_correspondence": [{"material_id": base["ranked_candidates"][0]["material_id"],
                                   "formula_group": [{"mp_id": "mp-19226"}]}],
    }
    base["ranked_candidates"][0]["mp_id"] = "mp-19226"

    def mutate(fn):
        doc = copy.deepcopy(base)
        fn(doc)
        return doc

    cases = [("order and selection changed (allowed)", base, 0, True),
             ("candidate score changed", mutate(lambda d: d["ranked_candidates"][-1].__setitem__(
                 "score", d["ranked_candidates"][-1]["score"] + 1)), 1, False),
             ("chain score changed", mutate(lambda d: d["chains"][0].__setitem__(
                 "scientific_usefulness_score", (d["chains"][0].get("scientific_usefulness_score") or 0) + 1)), 1, False),
             ("grouping flag false", mutate(lambda d: d["formula_correspondence"].__setitem__(
                 "formula_grouping_available", False)), 1, False),
             ("expansions empty", mutate(lambda d: d["formula_correspondence"].__setitem__("expansions", [])), 1, False),
             ("NaFePO4 group missing", mutate(lambda d: d["formula_correspondence"].__setitem__(
                 "source_correspondence", [])), 1, True)]
    direct = copy.deepcopy(base)
    lif = {"material_id": 5, "mp_id": LIFEPO4}
    naf = {"material_id": 10, "mp_id": REPRESENTATIVE}
    direct["material_id"] = 5
    direct["chains"].append({"materials": [lif, naf], "transitions": [{}],
                             "scientific_usefulness_score": 90.75, "score_breakdown": {}})
    direct["ranked_candidates"][0].update(material_id=10, mp_id=REPRESENTATIVE)
    position = len(direct["chains"])
    direct["formula_correspondence"].update(
        transitions=[{"chain_position": position, "transition_index": 0,
                      "correspondence": {"correspondence_class": "exact_alkali_replacement"}}],
        source_correspondence=[{"material_id": 10, "formula_group": [
            {"mp_id": mp, "traversed": mp == REPRESENTATIVE} for mp in sorted(NAFEPO4)]}],
        expansions=[{"expanded_material_id": 5, "groups_found": 1, "groups_admitted": 1, "excluded": []}])

    def dmutate(fn):
        doc = copy.deepcopy(direct)
        fn(doc)
        return doc

    direct_cases = [
        ("direct chain verified", direct, 0),
        ("direct chain missing", dmutate(lambda d: d["chains"].pop()), 1),
        ("direct step not exact", dmutate(lambda d: d["formula_correspondence"]["transitions"][0]["correspondence"]
                                          .__setitem__("correspondence_class", "not_exact_replacement")), 1),
        ("group incomplete", dmutate(lambda d: d["formula_correspondence"]["source_correspondence"][0]["formula_group"]
                                     .pop()), 1),
        ("source expansion admitted none", dmutate(lambda d: d["formula_correspondence"]["expansions"][0]
                                                   .__setitem__("groups_admitted", 0)), 1),
    ]
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        pre_file = os.path.join(tmp, "pre.json")
        with open(pre_file, "w", encoding="utf-8") as h:
            json.dump(pre, h)
        for name, doc, expected, flag in cases:
            post_file = os.path.join(tmp, "post.json")
            with open(post_file, "w", encoding="utf-8") as h:
                json.dump(doc, h)
            code = _run(["aware", pre_file, post_file] + (["--expect-nafepo4-group"] if flag else []))
            ok = code == expected
            failures += not ok
            print(f"{'ok ' if ok else 'BAD'} aware  {name}: exit {code}, expected {expected}")
        for name, doc, expected in direct_cases:
            post_file = os.path.join(tmp, "post.json")
            with open(post_file, "w", encoding="utf-8") as h:
                json.dump(doc, h)
            code = _run(["aware", pre_file, post_file, "--expect-direct-nafepo4"])
            ok = code == expected
            failures += not ok
            print(f"{'ok ' if ok else 'BAD'} direct {name}: exit {code}, expected {expected}")
        changed = os.path.join(tmp, "changed.json")
        raw = open(pre_file, "rb").read()
        with open(changed, "wb") as h:
            h.write(raw + b" ")
        for name, path, expected in (("frozen identical", pre_file, 0), ("frozen one byte changed", changed, 1)):
            code = _run(["frozen", pre_file, path])
            ok = code == expected
            failures += not ok
            print(f"{'ok ' if ok else 'BAD'} frozen {name}: exit {code}, expected {expected}")
    if first is None:
        print("note: PRE has no chains; chain-score case is weaker")
    print("SELFTEST PASS" if not failures else f"SELFTEST FAIL ({failures})")
    return 1 if failures else 0


def main():
    args = sys.argv[1:]
    if len(args) == 3 and args[0] == "frozen":
        problems = frozen(args[1], args[2])
    elif 3 <= len(args) <= 5 and args[0] == "aware":
        problems = aware(args[1], args[2], expect_group="--expect-nafepo4-group" in args,
                         expect_direct="--expect-direct-nafepo4" in args)
    elif len(args) == 2 and args[0] == "selftest":
        return selftest(args[1])
    else:
        print(__doc__)
        return 2
    for p in problems:
        print("PROBLEM:", p)
    print("PASS" if not problems else "FAIL")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
