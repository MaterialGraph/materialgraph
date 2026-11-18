"""RRB-01 pre-check 2b runner. Read-only HTTP against a tunnelled production API.

Usage:
  python -I run.py lookup  BASE_URL OUTDIR
  python -I run.py execute BASE_URL OUTDIR DC2_MATERIAL_ID CAPTURE_REQUEST_FILE

Sends requests strictly sequentially. Every request is sent exactly once per run;
a network error or non-200 status is retried once and both attempts are recorded.
"""
import datetime as dt
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TIMEOUT = 180
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def http(method: str, url: str, body: bytes | None):
    req = urllib.request.Request(url, data=body, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    started = now()
    t0 = time.perf_counter()
    try:
        with OPENER.open(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
            return {"started_utc": started, "elapsed_s": round(time.perf_counter() - t0, 3),
                    "status": resp.status, "headers": dict(resp.headers.items()), "raw": raw, "error": None}
    except urllib.error.HTTPError as e:
        raw = e.read()
        return {"started_utc": started, "elapsed_s": round(time.perf_counter() - t0, 3),
                "status": e.code, "headers": dict(e.headers.items()) if e.headers else {}, "raw": raw,
                "error": f"HTTPError {e.code}"}
    except Exception as e:  # network error
        return {"started_utc": started, "elapsed_s": round(time.perf_counter() - t0, 3),
                "status": None, "headers": {}, "raw": b"", "error": f"{type(e).__name__}: {e}"}


def send(method, url, body, out: Path, name: str):
    attempts = []
    for attempt in (1, 2):
        r = http(method, url, body)
        raw = r.pop("raw")
        fname = f"{name}.attempt{attempt}.raw" if attempt == 2 or r["status"] != 200 else f"{name}.raw"
        (out / fname).write_bytes(raw)
        r.update({"attempt": attempt, "response_file": fname, "response_sha256": sha(raw),
                  "response_bytes": len(raw)})
        attempts.append(r)
        if r["status"] == 200:
            break
        print(f"  {name}: attempt {attempt} failed ({r['error'] or r['status']}); "
              + ("retrying once" if attempt == 1 else "giving up"), flush=True)
    return attempts


def body_for(material_case: dict, arm: str, limit: int) -> dict:
    return {
        "objective": {
            "avoid_elements": list(material_case["avoid"]),
            "prefer_elements": list(material_case["prefer"]) if arm == "informed" else [],
            "preserve_elements": [],
            "target_family": None,
            "max_hops": 2,
            "limit": limit,
            "prefer_lower_criticality": True,
            "require_stable_materials": False,
        },
        "mode": "balanced",
        "limit": limit,
    }


def lookup(base: str, outdir: Path):
    d = outdir / "lookup"
    d.mkdir(exist_ok=True)
    log = []
    for name, url in [
        ("dc2_lookup_formula", f"{base}/api/v1/materials/search?" + urllib.parse.urlencode(
            {"mode": "formula", "q": "Li3Fe2(PO4)3", "limit": 100})),
    ]:
        print(f"GET {name}", flush=True)
        attempts = send("GET", url, None, d, name)
        log.append({"name": name, "url": url, "attempts": attempts})
    (d / "lookup_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")


def execute(base: str, outdir: Path, dc2_id: int, capture_request: Path):
    req_dir, resp_dir = outdir / "requests", outdir / "responses"
    url_for = lambda mid: f"{base}/api/v1/materials/{mid}/discovery/objective/explore"
    plan = []
    cap_bytes = capture_request.read_bytes()
    for run in (1, 2):
        plan.append({"id": f"hist_dc1_informed_l5_run{run}", "set": "historical", "case": "DC1",
                     "arm": "informed", "config": "5,5", "run": run, "material_id": 5,
                     "body_bytes": cap_bytes, "body_source": str(capture_request)})
    cases = {"DC1": {"material_id": 5, "avoid": ["Li", "Co"], "prefer": ["Na", "K"]},
             "DC2": {"material_id": dc2_id, "avoid": ["Li"], "prefer": ["Na"]}}
    for run in (1, 2):
        for case, c in cases.items():
            for arm in ("informed", "avoid_only"):
                for lim in (5, 10):
                    b = body_for(c, arm, lim)
                    plan.append({"id": f"pin_{case.lower()}_{arm}_l{lim}_run{run}", "set": "pinned",
                                 "case": case, "arm": arm, "config": f"{lim},{lim}", "run": run,
                                 "material_id": c["material_id"],
                                 "body_bytes": json.dumps(b, separators=(",", ":")).encode("utf-8"),
                                 "body_source": "generated (pinned field set)"})
    manifest = {"base_url": base, "endpoint": "POST /api/v1/materials/{id}/discovery/objective/explore",
                "canonical_request_rule": "json.dumps(sort_keys=True, separators=(',',':'), ensure_ascii=False) UTF-8",
                "started_utc": now(), "requests": []}
    for i, p in enumerate(plan, 1):
        body = p.pop("body_bytes")
        (req_dir / f"{p['id']}.json").write_bytes(body)
        print(f"[{i:02d}/{len(plan)}] {p['id']}", flush=True)
        attempts = send("POST", url_for(p["material_id"]), body, resp_dir, p["id"])
        final = attempts[-1]
        p.update({"sequence": i, "request_file": f"requests/{p['id']}.json",
                  "request_sent_sha256": sha(body), "request_canonical_sha256": sha(canonical(json.loads(body))),
                  "attempts": attempts, "final_status": final["status"],
                  "final_response_file": f"responses/{final['response_file']}",
                  "final_response_sha256": final["response_sha256"]})
        manifest["requests"].append(p)
        print(f"      status={final['status']} {final['elapsed_s']}s sha={final['response_sha256'][:12]}", flush=True)
    manifest["finished_utc"] = now()
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    mode, base, outdir = sys.argv[1], sys.argv[2].rstrip("/"), Path(sys.argv[3])
    if mode == "lookup":
        lookup(base, outdir)
    else:
        execute(base, outdir, int(sys.argv[4]), Path(sys.argv[5]))
