import argparse
import hashlib
import json
import subprocess
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import event, func, select, text

from app.core.database import SessionLocal, engine
from app.main import app
from app.models.dataset_import import DatasetImportRun, MaterialSourceRecord
from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.benchmark_fixture import FIXTURE_ID_PREFIX
from app.services.material.import_pipeline import MaterialImportPipeline


@dataclass(frozen=True)
class Scenario:
    name: str
    method: str
    path: str
    payload: dict[str, Any] | None = None
    expensive: bool = False


class QueryRecorder:
    def __init__(self) -> None:
        self.started: list[float] = []
        self.durations_ms: list[float] = []

    def before(self, *args) -> None:
        self.started.append(time.perf_counter())

    def after(self, *args) -> None:
        self.durations_ms.append(
            (time.perf_counter() - self.started.pop()) * 1_000
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the bounded, sequential MG-DE-004 qualification scenarios."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--expected-database-name", required=True)
    parser.add_argument("--warm-runs", type=int, default=2)
    return parser


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    if path.exists():
        raise ValueError(f"refusing to overwrite {path}")
    path.write_bytes(canonical_bytes(value) + b"\n")
    path.chmod(0o600)


def validate_environment(expected_database_name: str) -> None:
    actual = engine.url.database or ""
    if actual != expected_database_name:
        raise ValueError("configured database does not match the expected name")
    lowered = actual.lower()
    if "test" not in lowered or "mg_de_004" not in lowered:
        raise ValueError(
            "MG-DE-004 requires a dedicated test database containing mg_de_004"
        )
    if engine.dialect.name != "postgresql":
        raise ValueError("MG-DE-004 qualification requires PostgreSQL")


def scenarios(root_id: int, target_id: int) -> list[Scenario]:
    objective = {
        "avoid_elements": ["Li"],
        "prefer_elements": ["Na"],
        "preserve_elements": ["Fe", "P", "O"],
        "target_family": "phosphate",
        "max_hops": 2,
        "limit": 5,
        "prefer_lower_criticality": True,
        "require_stable_materials": False,
    }
    return [
        Scenario("material_list", "GET", "/api/v1/materials?limit=100"),
        Scenario("material_detail", "GET", f"/api/v1/materials/{root_id}/detail"),
        Scenario(
            "neighbors",
            "GET",
            f"/api/v1/materials/{root_id}/neighbors",
            expensive=True,
        ),
        Scenario(
            "similar",
            "GET",
            f"/api/v1/materials/{root_id}/similar?limit=10",
            expensive=True,
        ),
        Scenario("family", "GET", f"/api/v1/materials/{root_id}/families"),
        Scenario(
            "recommendations",
            "GET",
            f"/api/v1/materials/{root_id}/recommendations?limit=10",
            expensive=True,
        ),
        Scenario(
            "screening",
            "POST",
            "/api/v1/screening/candidates",
            {
                "scarce_elements": ["Li", "Co"],
                "avoid_elements": ["Li"],
                "require_stable": False,
                "max_energy_above_hull": 0.1,
            },
            True,
        ),
        Scenario(
            "substitution",
            "POST",
            "/api/v1/substitutions/analyze",
            {"material_id": root_id, "top_n": 5},
            True,
        ),
        Scenario(
            "discovery_candidates",
            "GET",
            f"/api/v1/materials/{root_id}/discovery/candidates?limit=10",
            expensive=True,
        ),
        Scenario(
            "discovery_graph",
            "GET",
            f"/api/v1/materials/{root_id}/discovery/graph?max_hops=2&limit=100",
            expensive=True,
        ),
        Scenario(
            "discovery_path",
            "GET",
            (
                f"/api/v1/materials/{root_id}/discovery/path"
                f"?target_material_id={target_id}&max_hops=2"
            ),
            expensive=True,
        ),
        Scenario(
            "scientific_pathways",
            "POST",
            f"/api/v1/materials/{root_id}/research/scientific-pathways",
            {"objective": objective},
            True,
        ),
    ]


@contextmanager
def record_queries():
    recorder = QueryRecorder()
    event.listen(engine, "before_cursor_execute", recorder.before)
    event.listen(engine, "after_cursor_execute", recorder.after)
    try:
        yield recorder
    finally:
        event.remove(engine, "before_cursor_execute", recorder.before)
        event.remove(engine, "after_cursor_execute", recorder.after)


def execute_scenario(client: TestClient, scenario: Scenario) -> tuple[dict, Any]:
    tracemalloc.start()
    started = time.perf_counter()
    try:
        with record_queries() as recorder:
            response = client.request(
                scenario.method,
                scenario.path,
                json=scenario.payload,
            )
        duration_ms = (time.perf_counter() - started) * 1_000
        _, peak_allocated_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    body = response.json()
    body_bytes = canonical_bytes(body)
    measurement = {
        "status_code": response.status_code,
        "wall_ms": round(duration_ms, 3),
        "query_count": len(recorder.durations_ms),
        "database_ms": round(sum(recorder.durations_ms), 3),
        "response_bytes": len(body_bytes),
        "response_sha256": hashlib.sha256(body_bytes).hexdigest(),
        "python_peak_allocated_bytes": peak_allocated_bytes,
    }
    if response.status_code != 200:
        raise RuntimeError(
            f"{scenario.name} returned {response.status_code}: {body!r}"
        )
    return measurement, body


def database_facts(manifest_digest: str) -> tuple[dict, int, int]:
    with SessionLocal() as db:
        fixture_ids = list(
            db.scalars(
                select(Material.id)
                .where(Material.mp_id.like(f"{FIXTURE_ID_PREFIX}%"))
                .order_by(Material.id)
                .limit(2)
            )
        )
        if len(fixture_ids) != 2:
            raise ValueError("fixture import is absent or incomplete")
        run = db.scalar(
            select(DatasetImportRun)
            .where(DatasetImportRun.manifest_sha256 == manifest_digest)
            .order_by(DatasetImportRun.started_at.desc())
        )
        if run is None or run.status not in {
            "completed",
            "completed_with_conflicts",
        }:
            raise ValueError("completed fixture import run was not found")
        counts = {
            "materials": db.scalar(select(func.count()).select_from(Material)),
            "elements": db.scalar(select(func.count()).select_from(Element)),
            "material_elements": db.scalar(
                select(func.count()).select_from(MaterialElement)
            ),
            "material_source_records": db.scalar(
                select(func.count()).select_from(MaterialSourceRecord)
            ),
        }
        settings = db.execute(
            text(
                "SELECT current_setting('server_version'), "
                "current_setting('statement_timeout'), "
                "current_setting('lock_timeout')"
            )
        ).one()
        plan = db.execute(
            text(
                "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
                "SELECT material_id, element_id FROM material_elements "
                "WHERE material_id = ANY(:ids)"
            ),
            {"ids": fixture_ids},
        ).scalar_one()
        return (
            {
                "row_counts": counts,
                "server_version": settings[0],
                "statement_timeout": settings[1],
                "lock_timeout": settings[2],
                "scoped_material_elements_plan": plan,
                "fixture_import_run_id": str(run.id),
                "fixture_import_status": run.status,
            },
            fixture_ids[0],
            fixture_ids[1],
        )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.warm_runs <= 5:
        raise ValueError("--warm-runs must be between 1 and 5")
    validate_environment(args.expected_database_name)
    if not args.manifest.is_file():
        raise ValueError("fixture manifest does not exist")
    manifest, digest = MaterialImportPipeline._load_manifest(args.manifest)
    if manifest["source"] != "synthetic_benchmark":
        raise ValueError("qualification requires the synthetic benchmark manifest")
    facts, root_id, target_id = database_facts(digest)
    args.output_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    results = []
    with TestClient(app) as client:
        for scenario in scenarios(root_id, target_id):
            runs = []
            snapshot = None
            for run_number in range(args.warm_runs + 1):
                measurement, body = execute_scenario(client, scenario)
                runs.append(measurement)
                if run_number == args.warm_runs:
                    snapshot = body
            snapshot_path = args.output_directory / f"{scenario.name}.json"
            write_json(snapshot_path, snapshot)
            results.append(
                {
                    **asdict(scenario),
                    "payload": scenario.payload,
                    "cold": runs[0],
                    "warm": runs[1:],
                    "snapshot": snapshot_path.name,
                }
            )

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    report = {
        "schema_version": 1,
        "method": "bounded sequential requests; no concurrency or load",
        "commit": commit,
        "manifest_sha256": digest,
        "database": facts,
        "scenarios": results,
    }
    write_json(args.output_directory / "qualification-report.json", report)
    print(
        json.dumps(
            {
                "output_directory": str(args.output_directory),
                "scenario_count": len(results),
                "manifest_sha256": digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
