"""Dataset-pinned qualification of the F12 material search (standard library only).

Runs GET requests against a MaterialGraph backend and checks it against an
expectations file. See README.md in this directory for usage and exit codes.

This file is deliberately not named test_*.py: it is not collected by pytest
and is not run by CI. It is run by hand against a chosen deployment.
"""

import argparse
import base64
import getpass
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

EXIT_PASS = 0
EXIT_CASE_FAILED = 1
EXIT_DATASET_MISMATCH = 2
EXIT_NO_FINGERPRINT = 3
EXIT_CONNECTION = 4

REQUEST_PAUSE_SECONDS = 0.25
TIMEOUT_SECONDS = 60
PAGE_SIZE = 100
SYMBOL = re.compile(r"[A-Z][a-z]?")


class ConnectionFailure(Exception):
    pass


class Client:
    """GET-only HTTP client. Credentials stay in memory and are never printed."""

    def __init__(self, base_url, authorization=None):
        self.base_url = base_url.rstrip("/")
        self._authorization = authorization

    def get(self, path, params=None):
        time.sleep(REQUEST_PAUSE_SECONDS)
        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, method="GET")
        request.add_header("Accept", "application/json")
        if self._authorization:
            request.add_header("Authorization", self._authorization)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return response.status, _json(response.read())
        except urllib.error.HTTPError as error:
            if error.code in (401, 403):
                raise ConnectionFailure(
                    f"GET {path} was refused with HTTP {error.code}: check the credentials."
                ) from None
            return error.code, _json(error.read())
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            reason = getattr(error, "reason", error)
            raise ConnectionFailure(f"GET {path} failed: {reason}") from None


def _json(raw):
    try:
        return json.loads(raw)
    except ValueError:
        return None


def basic_authorization():
    username = getpass.getpass("HTTP Basic Auth username: ")
    password = getpass.getpass("HTTP Basic Auth password: ")
    token = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
    return "Basic " + token


def fingerprint(rows):
    """SHA-256 of [[id, mp_id, formula, energy_above_hull], ...] sorted by id."""
    data = sorted(
        ([row["id"], row["mp_id"], row["formula"], row["energy_above_hull"]] for row in rows),
        key=lambda item: item[0],
    )
    text = json.dumps(data, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def list_all_materials(client):
    rows, offset = [], 0
    while True:
        status, page = client.get("/api/v1/materials", {"limit": PAGE_SIZE, "offset": offset})
        if status != 200 or not isinstance(page, list):
            raise ConnectionFailure(f"GET /api/v1/materials at offset {offset} returned HTTP {status}.")
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        offset += len(page)


def search(client, mode, query, limit=PAGE_SIZE, offset=0):
    return client.get(
        "/api/v1/materials/search",
        {"mode": mode, "q": query, "limit": limit, "offset": offset},
    )


def search_all(client, mode, query):
    status, first = search(client, mode, query)
    if status != 200:
        return status, first, []
    results = list(first["results"])
    while len(results) < first["total_matches"]:
        status, page = search(client, mode, query, offset=len(results))
        if status != 200 or not page["results"]:
            return status, page, results
        results.extend(page["results"])
    return 200, first, results


# Cases --------------------------------------------------------------------

def case_formula_includes(client, spec):
    status, body, results = search_all(client, "formula", spec["query"])
    ids = [item["material_id"] for item in results]
    ok = status == 200 and body["total_matches"] == spec["total_matches"] and spec["includes_material_id"] in ids
    return ok, f"HTTP {status}, total_matches {body.get('total_matches') if status == 200 else '-'}, includes {spec['includes_material_id']}: {spec['includes_material_id'] in ids}"


def case_material_ids(mode):
    def run(client, spec):
        status, body, results = search_all(client, mode, spec["query"])
        ids = [item["material_id"] for item in results]
        return status == 200 and ids == spec["material_ids"], f"HTTP {status}, material_ids {ids}"
    return run


def case_chemsys_elements(client, spec):
    status, body, results = search_all(client, "chemsys", spec["query"])
    wanted = set(spec["elements"])
    wrong = [item["material_id"] for item in results if set(SYMBOL.findall(item["formula"])) != wanted]
    total = body.get("total_matches") if status == 200 else None
    ok = status == 200 and total == spec["total_matches"] and len(results) == total and not wrong
    return ok, f"HTTP {status}, total_matches {total}, rows read {len(results)}, wrong element sets {wrong}"


def case_zero_matches(client, spec):
    status, body = search(client, "formula", spec["query"])
    scoped = body.get("scoped_message") if status == 200 else None
    ok = status == 200 and body["total_matches"] == spec["total_matches"] and bool(scoped)
    return ok, f"HTTP {status}, total_matches {body.get('total_matches') if status == 200 else '-'}, scoped_message present: {bool(scoped)}"


def case_invalid(client, spec):
    status, body = search(client, "formula", spec["query"])
    detail = body.get("detail") if isinstance(body, dict) else None
    code = detail.get("code") if isinstance(detail, dict) else None
    return status == spec["status"] and code == spec["code"], f"HTTP {status}, detail.code {code}"


def case_auto_local_id(client, spec):
    status, body = search(client, "auto", spec["query"])
    if status != 200:
        return False, f"HTTP {status}"
    mp_ids = [item["mp_id"] for item in body["results"]]
    ok = (body["interpretation"]["mode"] == spec["interpretation_mode"]
          and body["requested_mode"] == spec["requested_mode"] and mp_ids == spec["mp_ids"])
    return ok, (f"HTTP {status}, interpretation.mode {body['interpretation']['mode']}, "
                f"requested_mode {body['requested_mode']}, mp_ids {mp_ids}")


CASES = (
    ("formula_fepo4li", case_formula_includes),
    ("formula_nafepo4", case_material_ids("formula")),
    ("chemsys_li_fe_p_o", case_chemsys_elements),
    ("formula_ti2c", case_zero_matches),
    ("formula_lifepo4_invalid", case_invalid),
    ("mp_id_mp_19017", case_material_ids("mp_id")),
    ("auto_local_id", case_auto_local_id),
)


# Main ---------------------------------------------------------------------

def run(args, client, expectations, report):
    # Step 1: precondition, from a search response (Release 1 and F12 alike).
    status, body = search(client, "formula", "LiFePO4", limit=1)
    if status != 200 or not isinstance(body, dict) or "dataset" not in body:
        raise ConnectionFailure(f"The precondition search returned HTTP {status}.")
    dataset = body["dataset"]
    observed = {key: dataset.get(key) for key in ("source_release", "dataset_total", "composition_exclusion_count")}
    report["precondition"] = {"observed": observed}
    print(f"Step 1  precondition: source_release {observed['source_release']}, dataset_total "
          f"{observed['dataset_total']}, composition_exclusion_count {observed['composition_exclusion_count']}")
    mismatched = [key for key in observed if observed[key] != expectations[key]]
    if mismatched:
        for key in mismatched:
            print(f"        {key}: expected {expectations[key]!r}, observed {observed[key]!r}")
        print("fixture is for a different dataset")
        return EXIT_DATASET_MISMATCH
    print("        matches the expectations. Release and count are a precondition, not proof of identity.")

    # Step 2: fingerprint of every material identity.
    rows = list_all_materials(client)
    digest = fingerprint(rows)
    report["fingerprint"] = {"observed": digest, "rows": len(rows)}
    print(f"Step 2  fingerprint: {digest} ({len(rows)} rows)")
    if len(rows) != observed["dataset_total"] or len({row["id"] for row in rows}) != len(rows):
        print(f"        the material list has {len(rows)} rows for dataset_total {observed['dataset_total']}")
        print("dataset differs from the qualified fixture")
        return EXIT_DATASET_MISMATCH
    if args.mode == "baseline":
        print("Baseline captured. No search cases run in baseline mode.")
        return EXIT_PASS
    if expectations.get("fingerprint") is None:
        print("The expectations file has no fingerprint. Capture one with --mode baseline and add it "
              "through a reviewed change before qualifying.")
        return EXIT_NO_FINGERPRINT
    if digest != expectations["fingerprint"]:
        print(f"        expected {expectations['fingerprint']}")
        print("dataset differs from the qualified fixture")
        return EXIT_DATASET_MISMATCH

    # Step 3: cases.
    failed = 0
    report["cases"] = []
    for name, check in CASES:
        ok, observation = check(client, expectations["cases"][name])
        failed += not ok
        report["cases"].append({"case": name, "result": "PASS" if ok else "FAIL", "observed": observation})
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {observation}")
    status, summary = client.get("/api/v1/materials/dataset-summary")
    ok = status == 200 and summary == dataset
    failed += not ok
    observation = f"HTTP {status}, equals the Step 1 dataset block: {summary == dataset}"
    report["cases"].append({"case": "dataset_summary", "result": "PASS" if ok else "FAIL", "observed": observation})
    print(f"{'PASS' if ok else 'FAIL'}  dataset_summary: {observation}")
    print(f"{len(report['cases']) - failed} passed, {failed} failed")
    return EXIT_CASE_FAILED if failed else EXIT_PASS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", required=True, help="for example http://127.0.0.1:8000")
    parser.add_argument("--expectations", required=True, help="expectations JSON file")
    parser.add_argument("--mode", choices=("baseline", "qualify"), default="qualify")
    parser.add_argument("--no-auth", action="store_true", help="send no credentials (local use)")
    parser.add_argument("--report", help="write a JSON report (no credentials) to this path")
    args = parser.parse_args(argv)

    with open(args.expectations, encoding="utf-8") as handle:
        expectations = json.load(handle)
    client = Client(args.base_url, None if args.no_auth else basic_authorization())
    report = {"base_url": args.base_url, "expectations": args.expectations, "mode": args.mode}
    print(f"Qualifying {args.base_url} in {args.mode} mode against {args.expectations}")
    try:
        code = run(args, client, expectations, report)
    except ConnectionFailure as error:
        print(f"ERROR: {error}")
        code = EXIT_CONNECTION
    report["exit_code"] = code
    if args.report:
        with open(args.report, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
