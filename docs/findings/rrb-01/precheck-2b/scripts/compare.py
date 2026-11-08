"""RRB-01 pre-check 2b checks. Reads manifest.json + saved responses; writes reports/.

Usage: python -I compare.py OUTDIR CAPTURE_RESPONSE CAPTURE_REQUEST PERIODIC_TABLE_PY
Rules are applied exactly as frozen in the brief, with the approved change that the
previously unassigned fields are an EXACT limit-equivalence rule (no field outside a verdict).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
CAPTURE_RESPONSE = Path(sys.argv[2])
CAPTURE_REQUEST = Path(sys.argv[3])
ns: dict = {}
exec(Path(sys.argv[4]).read_text(encoding="utf-8"), ns)  # frozen app/domain/periodic_table.py (stdlib only)
ELEMENT_SYMBOLS = ns["ELEMENT_SYMBOLS"]

MANIFEST = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
REQ = {r["id"]: r for r in MANIFEST["requests"]}


def sha(b): return hashlib.sha256(b).hexdigest()
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
def raw(rid): return (OUT / REQ[rid]["final_response_file"]).read_bytes()
def doc(rid): return json.loads(raw(rid))


def diff(a, b, path="$", out=None):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            p = f"{path}.{k}"
            if k not in a: out.append({"path": p, "a": "<absent>", "b": b[k]})
            elif k not in b: out.append({"path": p, "a": a[k], "b": "<absent>"})
            else: diff(a[k], b[k], p, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append({"path": f"{path}.<length>", "a": len(a), "b": len(b)})
        for i in range(min(len(a), len(b))):
            diff(a[i], b[i], f"{path}[{i}]", out)
        for i in range(len(b), len(a)): out.append({"path": f"{path}[{i}]", "a": a[i], "b": "<absent>"})
        for i in range(len(a), len(b)): out.append({"path": f"{path}[{i}]", "a": "<absent>", "b": b[i]})
    elif type(a) is not type(b) or a != b:
        out.append({"path": path, "a": a, "b": b})
    return out


def get(d, path, default="<absent>"):
    cur = d
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur: cur = cur[part]
        else: return default
    return cur


# ---------------- strict parse (verbatim port of 50dd3ed app/utils/chemical_formula.py:22-73)
_TOK = re.compile(r"(?P<symbol>[A-Z][a-z]?)(?:\d+(?:\.\d+)?)?|(?P<open>\()|(?P<close>\))(?:\d+(?:\.\d+)?)?")


def strict(formula):
    if not isinstance(formula, str): return None
    text = formula.strip()
    if not text: return None
    pos = depth = 0; prev_open = False; syms = set()
    while pos < len(text):
        m = _TOK.match(text, pos)
        if m is None or m.end() == pos: return None
        s = m.group("symbol")
        if s is not None:
            if s not in ELEMENT_SYMBOLS: return None
            syms.add(s); prev_open = False
        elif m.group("open") is not None:
            depth += 1; prev_open = True
        else:
            depth -= 1
            if depth < 0 or prev_open: return None
            prev_open = False
        pos = m.end()
    if depth != 0 or not syms: return None
    return frozenset(syms)


# ---------------- check 2: repeatability
def repeatability(rid1, rid2):
    b1, b2 = raw(rid1), raw(rid2)
    d = diff(json.loads(b1), json.loads(b2))
    return {"run1": rid1, "run2": rid2, "run1_sha256": sha(b1), "run2_sha256": sha(b2),
            "byte_identical": b1 == b2, "canonical_identical": not d, "canonical_differences": d,
            "result": "PASS" if b1 == b2 and not d else "FAIL"}


# ---------------- check 3: limit equivalence
POLICY_PATHS = ["objective_policy", "mode", "constraint_policy", "avoid_policy", "prefer_policy",
                "candidate_score_offset", "warnings", "explanation",
                "objective_coverage.mode", "objective_coverage.avoid_policy_explanation"]
OBJECTIVE_FIELDS = ["avoid_elements", "prefer_elements", "preserve_elements", "target_family", "max_hops",
                    "prefer_lower_criticality", "require_stable_materials"]
SM_ALLOWED = {"requested_result_limit", "returned_chain_count", "result_truncated"}
TRUNC = "Results were limited; coverage may differ for unreturned results."
UNASSIGNED = ["material_id", "base_formula", "objective_coverage.contract_version", "objective_coverage.scope",
              "objective_coverage.element_evaluation_basis", "objective_coverage.source_material",
              "objective_coverage.terms_not_evaluated", "formula_correspondence.contract_version",
              "formula_correspondence.basis", "formula_correspondence.tolerance",
              "formula_correspondence.formula_grouping_available",
              "formula_correspondence.admission_reporting_available", "formula_correspondence.limitations"]


def rule(name, diffs, extra=None):
    r = {"rule": name, "result": "PASS" if not diffs else "FAIL", "differences": diffs}
    if extra: r.update(extra)
    return r


def limit_equivalence(r5, r10):
    a, b = doc(r5), doc(r10)
    rules = []
    # EXACT
    rc5, rc10 = a["ranked_candidates"], b["ranked_candidates"]
    n = min(5, len(rc5))
    d = diff(rc5[:5], rc10[:5], "ranked_candidates[:5]")
    rules.append(rule("EXACT ranked_candidates first 5 (all item fields)", d,
                      {"compared_items": n, "len_l5": len(rc5), "len_l10": len(rc10)}))
    ch5, ch10 = a["chains"], b["chains"]
    d = diff(ch5[:5], ch10[:5], "chains[:5]")
    rules.append(rule("EXACT chains first 5 (all item fields)", d,
                      {"compared_items": min(5, len(ch5)), "len_l5": len(ch5), "len_l10": len(ch10)}))
    sm5 = {k: v for k, v in a["search_metadata"].items() if k not in SM_ALLOWED}
    sm10 = {k: v for k, v in b["search_metadata"].items() if k not in SM_ALLOWED}
    rules.append(rule("EXACT search_metadata except requested_result_limit/returned_chain_count/result_truncated",
                      diff(sm5, sm10, "search_metadata")))
    rules.append(rule("EXACT objective_coverage.ranked_material_pool_count",
                      diff(get(a, "objective_coverage.ranked_material_pool_count"),
                           get(b, "objective_coverage.ranked_material_pool_count"),
                           "objective_coverage.ranked_material_pool_count")))
    fc_a, fc_b = "formula_correspondence" in a, "formula_correspondence" in b
    d = []
    if fc_a != fc_b:
        d.append({"path": "formula_correspondence", "a": "<present>" if fc_a else "<absent>",
                  "b": "<present>" if fc_b else "<absent>"})
    elif fc_a:
        d += diff(a["formula_correspondence"]["expansions"], b["formula_correspondence"]["expansions"],
                  "formula_correspondence.expansions")
        g5 = {e["candidate_rank"]: e["formula_group"] for e in a["formula_correspondence"]["source_correspondence"]
              if e["candidate_rank"] <= 5}
        g10 = {e["candidate_rank"]: e["formula_group"] for e in b["formula_correspondence"]["source_correspondence"]
               if e["candidate_rank"] <= 5}
        d += diff({str(k): v for k, v in g5.items()}, {str(k): v for k, v in g10.items()},
                  "formula_correspondence.source_correspondence[rank<=5].formula_group")
    rules.append(rule("EXACT formula_correspondence.expansions and formula_group entries", d,
                      {"formula_correspondence_present": [fc_a, fc_b]}))
    d = []
    for p in POLICY_PATHS:
        d += diff(get(a, p), get(b, p), p)
    rules.append(rule("EXACT policy fields", d, {"paths": POLICY_PATHS}))
    oa = {k: a["objective"].get(k, "<absent>") for k in OBJECTIVE_FIELDS}
    ob = {k: b["objective"].get(k, "<absent>") for k in OBJECTIVE_FIELDS}
    rules.append(rule("EXACT objective fields except objective.limit", diff(oa, ob, "objective")))

    # ALLOWED DIFFERENCES (values reported; only the limitations rule can fail)
    allowed_vals = {}
    for p in ["objective.limit", "search_metadata.requested_result_limit", "search_metadata.returned_chain_count",
              "search_metadata.result_truncated", "objective_coverage.returned_chain_count",
              "objective_coverage.returned_ranked_material_count"]:
        allowed_vals[p] = [get(a, p), get(b, p)]
    allowed_vals["len(ranked_candidates)"] = [len(rc5), len(rc10)]
    allowed_vals["len(chains)"] = [len(ch5), len(ch10)]
    for key in ["preferred_elements", "avoided_elements_in_ranked_materials"]:
        for i, e in enumerate(get(a, f"objective_coverage.{key}", [])):
            e10 = get(b, f"objective_coverage.{key}", [])
            allowed_vals[f"objective_coverage.{key}[{i}].total_count"] = [e["total_count"],
                                                                           e10[i]["total_count"] if i < len(e10) else "<absent>"]
    for i, e in enumerate(get(a, "objective_coverage.avoided_elements_in_returned_chains", [])):
        e10 = get(b, "objective_coverage.avoided_elements_in_returned_chains", [])
        allowed_vals[f"objective_coverage.avoided_elements_in_returned_chains[{i}].total_chain_count"] = [
            e["total_chain_count"], e10[i]["total_chain_count"] if i < len(e10) else "<absent>"]
    la, lb = a["objective_coverage"]["limitations"], b["objective_coverage"]["limitations"]
    st = [a["search_metadata"]["search_truncated"], b["search_metadata"]["search_truncated"]]
    d = diff([x for x in la if x != TRUNC], [x for x in lb if x != TRUNC], "objective_coverage.limitations(non-truncation)")
    trunc_presence = [TRUNC in la, TRUNC in lb]
    if trunc_presence[0] != trunc_presence[1] and st[0] != st[1]:
        d.append({"path": "objective_coverage.limitations(truncation string)", "a": trunc_presence[0],
                  "b": trunc_presence[1], "note": "search_truncated differs", "search_truncated": st})
    rules.append(rule("ALLOWED truncation string in objective_coverage.limitations only if search_truncated identical",
                      d, {"truncation_string_present": trunc_presence, "search_truncated": st}))
    # PER-POSITION
    def by_pos(x, key, field):
        return [e for e in x if e[field] <= 5]
    d = diff(by_pos(a["objective_coverage"]["chain_avoidance"], None, "chain_position"),
             by_pos(b["objective_coverage"]["chain_avoidance"], None, "chain_position"),
             "objective_coverage.chain_avoidance[chain_position<=5]")
    rules.append(rule("PER-POSITION chain_avoidance at chain_position <= 5", d))
    d = []
    if fc_a and fc_b:
        d += diff(by_pos(a["formula_correspondence"]["transitions"], None, "chain_position"),
                  by_pos(b["formula_correspondence"]["transitions"], None, "chain_position"),
                  "formula_correspondence.transitions[chain_position<=5]")
    rules.append(rule("PER-POSITION formula_correspondence.transitions at chain_position <= 5", d,
                      {"applicable": fc_a and fc_b}))
    d = []
    if fc_a and fc_b:
        d += diff(by_pos(a["formula_correspondence"]["source_correspondence"], None, "candidate_rank"),
                  by_pos(b["formula_correspondence"]["source_correspondence"], None, "candidate_rank"),
                  "formula_correspondence.source_correspondence[candidate_rank<=5]")
    rules.append(rule("PER-POSITION source_correspondence at candidate_rank <= 5", d,
                      {"applicable": fc_a and fc_b}))
    d = []
    for p in UNASSIGNED:
        d += diff(get(a, p), get(b, p), p)
    rules.append(rule("EXACT other limit-independent fields (pre-check 2a S; added at approval)", d,
                      {"paths": UNASSIGNED}))
    return {"l5": r5, "l10": r10,
            "result": "PASS" if all(r["result"] == "PASS" for r in rules) else "FAIL",
            "rules": rules, "allowed_difference_values": allowed_vals}


# ---------------- aggregates: internal consistency per response
def status_prefer(c, e): return "not_evaluated" if e == 0 else ("represented" if c > 0 else "not_represented")
def status_avoid(c, e): return "present" if c > 0 else ("not_evaluated" if e == 0 else "not_observed")


def aggregates(rid):
    d = doc(rid)
    oc = d["objective_coverage"]
    obj = d["objective"]
    issues, checks = [], []

    def check(path, got, exp):
        checks.append(path)
        if got != exp: issues.append({"path": path, "reported": got, "recomputed": exp})

    check("objective_coverage.returned_ranked_material_count", oc["returned_ranked_material_count"], len(d["ranked_candidates"]))
    check("objective_coverage.returned_chain_count", oc["returned_chain_count"], len(d["chains"]))
    check("search_metadata.returned_chain_count", d["search_metadata"]["returned_chain_count"], len(d["chains"]))
    ranked = [strict(c.get("formula")) for c in d["ranked_candidates"]]
    for key, elems, stat in [("preferred_elements", obj["prefer_elements"], status_prefer),
                             ("avoided_elements_in_ranked_materials", obj["avoid_elements"], status_avoid)]:
        exp_list = []
        for el in elems:
            ev = [s for s in ranked if s is not None]
            c = sum(1 for s in ev if el in s)
            exp_list.append({"element": el, "unit": "returned_ranked_materials", "containing_count": c,
                             "evaluated_count": len(ev), "not_evaluated_count": len(ranked) - len(ev),
                             "total_count": len(ranked), "status": stat(c, len(ev)),
                             "coverage_complete": len(ranked) == len(ev)})
        for x in diff(oc[key], exp_list, f"objective_coverage.{key}"):
            issues.append({"path": x["path"], "reported": x["a"], "recomputed": x["b"]})
        checks.append(f"objective_coverage.{key}")
    members = [[(i, m["material_id"], strict(m.get("formula") or m.get("pretty_formula")))
                for i, m in enumerate(ch["materials"]) if i > 0] for ch in d["chains"]]
    exp_chains = []
    for el in obj["avoid_elements"]:
        pos, ne = [], 0
        for p, mem in enumerate(members, 1):
            if any(s is not None and el in s for _, _, s in mem): pos.append(p)
            elif any(s is None for _, _, s in mem): ne += 1
        ev = len(members) - ne
        exp_chains.append({"element": el, "unit": "returned_chains_excluding_source", "containing_chain_count": len(pos),
                           "evaluated_chain_count": ev, "not_evaluated_chain_count": ne,
                           "total_chain_count": len(members), "chain_positions": pos,
                           "status": status_avoid(len(pos), ev), "coverage_complete": ne == 0})
    for x in diff(oc["avoided_elements_in_returned_chains"], exp_chains, "objective_coverage.avoided_elements_in_returned_chains"):
        issues.append({"path": x["path"], "reported": x["a"], "recomputed": x["b"]})
    checks.append("objective_coverage.avoided_elements_in_returned_chains")
    exp_ca = []
    for p, mem in enumerate(members, 1):
        last = mem[-1][0] if mem else 0
        flagged = []
        for i, mid, s in mem:
            if s is None: continue
            present = [e for e in obj["avoid_elements"] if e in s]
            if present:
                flagged.append({"material_id": mid, "chain_material_index": i,
                                "role": "final" if i == last else "intermediate", "avoided_elements": present})
        exp_ca.append({"chain_position": p, "materials_with_avoided_elements": flagged,
                       "not_evaluated_material_ids": [mid for _, mid, s in mem if s is None]})
    for x in diff(oc["chain_avoidance"], exp_ca, "objective_coverage.chain_avoidance"):
        issues.append({"path": x["path"], "reported": x["a"], "recomputed": x["b"]})
    checks.append("objective_coverage.chain_avoidance")
    src = strict(d.get("base_formula"))
    check("objective_coverage.source_material.avoided_elements_present",
          oc["source_material"].get("avoided_elements_present"),
          None if src is None else [e for e in obj["avoid_elements"] if e in src])
    not_determinable = []
    if "formula_correspondence" in d:
        fc = d["formula_correspondence"]
        check("formula_correspondence.not_evaluated_count", fc["not_evaluated_count"], len(fc["not_evaluated_material_ids"]))
        not_determinable.append("formula_correspondence.not_evaluated_material_ids membership: depends on stored "
                                "raw_data composition validity (DB), not present in the response")
        not_determinable.append("formula_correspondence.not_evaluated_material_ids order: sort key needs MP IDs of "
                                "materials that may not appear in the response")
    return {"response": rid, "result": "PASS" if not issues else "FAIL", "checked": checks,
            "inconsistencies": issues, "not_determinable": not_determinable}


# ---------------- check 1
def acceptance(rids):
    rows = []
    for rid in rids:
        r = REQ[rid]
        sent = json.loads((OUT / r["request_file"]).read_bytes())
        body = doc(rid) if r["final_status"] == 200 else None
        echo_diff = diff({k: v for k, v in sent["objective"].items()}, body["objective"], "objective") if body else None
        rows.append({"request": rid, "final_status": r["final_status"], "attempts": len(r["attempts"]),
                     "attempt_errors": [a["error"] for a in r["attempts"] if a["error"]],
                     "objective_echo_differences": echo_diff,
                     "mode_echo": body.get("mode") if body else None,
                     "result": "PASS" if r["final_status"] == 200 and not echo_diff and body.get("mode") == sent["mode"]
                     else "FAIL"})
    return rows


def historical():
    cap_req, cap_resp = CAPTURE_REQUEST.read_bytes(), CAPTURE_RESPONSE.read_bytes()
    cap_req_obj = json.loads(cap_req)
    pinned_fields = ["avoid_elements", "prefer_elements", "preserve_elements", "target_family", "max_hops", "limit",
                     "prefer_lower_criticality", "require_stable_materials"]
    out = {"capture_request_file": str(CAPTURE_REQUEST), "capture_request_sha256": sha(cap_req),
           "capture_request_canonical_sha256": sha(canon(cap_req_obj)),
           "capture_response_file": str(CAPTURE_RESPONSE), "capture_response_sha256": sha(cap_resp),
           "capture_request_missing_fields": [f for f in pinned_fields if f not in cap_req_obj["objective"]]
           + [f for f in ["mode", "limit"] if f not in cap_req_obj],
           "runs": []}
    for rid in ["hist_dc1_informed_l5_run1", "hist_dc1_informed_l5_run2"]:
        sent = (OUT / REQ[rid]["request_file"]).read_bytes()
        rb = raw(rid)
        d = diff(json.loads(cap_resp), json.loads(rb), "$")
        out["runs"].append({"request": rid, "request_bytes_identical_to_capture": sent == cap_req,
                            "response_sha256": sha(rb), "byte_identical_to_capture": rb == cap_resp,
                            "canonical_differences_vs_capture (a=capture, b=run)": d,
                            "result": "PASS" if not d else "FAIL"})
    out["acceptance"] = acceptance(["hist_dc1_informed_l5_run1", "hist_dc1_informed_l5_run2"])
    out["repeatability"] = repeatability("hist_dc1_informed_l5_run1", "hist_dc1_informed_l5_run2")
    return out


def case_report(case):
    c = case.lower()
    rids = [r for r in REQ if r.startswith(f"pin_{c}_")]
    rep = {"case": case, "material_id": REQ[rids[0]]["material_id"],
           "requests": {r: {"sequence": REQ[r]["sequence"], "request_canonical_sha256": REQ[r]["request_canonical_sha256"],
                            "response_sha256": REQ[r]["final_response_sha256"], "status": REQ[r]["final_status"]}
                        for r in rids},
           "check1_explicit_field_acceptance": acceptance(rids), "check2_repeatability": [],
           "check3_limit_equivalence": [], "aggregates_internal_consistency": []}
    for arm in ("informed", "avoid_only"):
        for lim in (5, 10):
            rep["check2_repeatability"].append(repeatability(f"pin_{c}_{arm}_l{lim}_run1", f"pin_{c}_{arm}_l{lim}_run2"))
        for run in (1, 2):
            le = limit_equivalence(f"pin_{c}_{arm}_l5_run{run}", f"pin_{c}_{arm}_l10_run{run}")
            le.update({"arm": arm, "run": run})
            rep["check3_limit_equivalence"].append(le)
    for r in rids:
        rep["aggregates_internal_consistency"].append(aggregates(r))
    return rep


def main():
    rdir = OUT / "reports"
    hist = historical()
    (rdir / "historical_dc1.json").write_text(json.dumps(hist, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = {"historical_dc1": {
        "acceptance": [x["result"] for x in hist["acceptance"]],
        "vs_capture": [{"request": x["request"], "result": x["result"], "byte_identical": x["byte_identical_to_capture"],
                        "difference_count": len(x["canonical_differences_vs_capture (a=capture, b=run)"])}
                       for x in hist["runs"]],
        "repeatability": hist["repeatability"]["result"]}}
    for case in ("DC1", "DC2"):
        rep = case_report(case)
        (rdir / f"{case.lower()}_pinned.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
        summary[case] = {
            "check1": {x["request"]: x["result"] for x in rep["check1_explicit_field_acceptance"]},
            "check2": {f'{x["run1"]} vs run2': {"result": x["result"], "byte_identical": x["byte_identical"],
                                               "canonical_difference_count": len(x["canonical_differences"])}
                       for x in rep["check2_repeatability"]},
            "check3": {f'{x["arm"]} run{x["run"]}': {"result": x["result"],
                                                    "rules": {r["rule"]: r["result"] for r in x["rules"]},
                                                    "allowed_difference_values": x["allowed_difference_values"]}
                       for x in rep["check3_limit_equivalence"]},
            "aggregates": {x["response"]: x["result"] for x in rep["aggregates_internal_consistency"]}}
    (rdir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))


main()
