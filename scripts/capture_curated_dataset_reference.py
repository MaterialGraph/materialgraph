import argparse
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.database import engine
from app.main import app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture complete deterministic curated API responses."
    )
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--expected-database-name", required=True)
    parser.add_argument("--material-id", type=int, required=True)
    return parser


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    actual = engine.url.database or ""
    if actual != args.expected_database_name or "test" not in actual.lower():
        raise ValueError("configured database is not the expected test database")
    args.output_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    paths = {
        "detail": f"/api/v1/materials/{args.material_id}/detail",
        "criticality": f"/api/v1/materials/{args.material_id}/criticality",
    }
    report = {}
    with TestClient(app) as client:
        for name, path in paths.items():
            response = client.get(path)
            if response.status_code != 200:
                raise RuntimeError(f"{name} returned {response.status_code}")
            body = canonical_bytes(response.json()) + b"\n"
            output = args.output_directory / f"{name}.json"
            output.write_bytes(body)
            output.chmod(0o600)
            report[name] = hashlib.sha256(body).hexdigest()
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
