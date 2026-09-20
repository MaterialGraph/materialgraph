"""Bounded local diagnosis for the material-neighborhood endpoint.

This script intentionally supports only a disposable SQLite database whose
filename contains ``neighborhood_perf_test``.  It performs no network access
and does not modify application behavior.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import event, func, insert, select
from sqlalchemy.engine import Engine

from app.core.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.models.application import Application
from app.models.element import Element
from app.models.material import Material
from app.models.material_application import MaterialApplication
from app.models.material_element import MaterialElement
from app.schemas.material_neighborhood import MaterialNeighborhoodResponse
from app.services.material.neighbor_service import MaterialNeighborService
from app.services.material.neighborhood_service import MaterialNeighborhoodService


ELEMENTS = ("Li", "Fe", "P", "O", "Na", "Mn", "Co", "Ni", "Si", "S")
APPLICATIONS = ("battery", "catalyst", "structural")


@dataclass
class QueryRecorder:
    starts: list[float] = field(default_factory=list)
    durations_ms: list[float] = field(default_factory=list)
    statements: list[str] = field(default_factory=list)

    def before(self, _conn, _cursor, statement, _parameters, _context, _many) -> None:
        self.starts.append(time.perf_counter())
        self.statements.append(statement)

    def after(self, *_args) -> None:
        self.durations_ms.append((time.perf_counter() - self.starts.pop()) * 1_000)


class ProfiledNeighborService(MaterialNeighborService):
    def __init__(self, db):
        super().__init__(db)
        self.calls = 0
        self.call_ms = 0.0
        self.build_ms = 0.0

    def get_neighbors(self, material_id: int) -> dict:
        started = time.perf_counter()
        try:
            return super().get_neighbors(material_id)
        finally:
            self.calls += 1
            self.call_ms += (time.perf_counter() - started) * 1_000

    def _build_neighbors(self, *, neighbor_scores, materials_by_id):
        started = time.perf_counter()
        try:
            return super()._build_neighbors(
                neighbor_scores=neighbor_scores,
                materials_by_id=materials_by_id,
            )
        finally:
            self.build_ms += (time.perf_counter() - started) * 1_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--materials", type=int, default=1_727)
    parser.add_argument("--depth", type=int, default=2, choices=(1, 2))
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--warm-runs", type=int, default=3)
    parser.add_argument(
        "--rtt-ms",
        type=int,
        nargs="+",
        default=(0, 25, 50, 100),
        help="Artificial per-query round-trip delays for endpoint sensitivity.",
    )
    return parser.parse_args()


def validate_environment(
    output: Path,
    materials: int,
    limit: int,
    warm_runs: int,
    rtt_values: list[int],
) -> None:
    database = engine.url.database or ""
    if engine.dialect.name != "sqlite" or "neighborhood_perf_test" not in database:
        raise RuntimeError(
            "diagnosis requires a disposable SQLite database containing "
            "'neighborhood_perf_test' in its filename"
        )
    if not 25 <= materials <= 10_000:
        raise ValueError("--materials must be between 25 and 10000")
    if not 1 <= limit <= 100:
        raise ValueError("--limit must be between 1 and 100")
    if not 1 <= warm_runs <= 5:
        raise ValueError("--warm-runs must be between 1 and 5")
    if not rtt_values or any(value < 0 or value > 100 for value in rtt_values):
        raise ValueError("--rtt-ms values must be between 0 and 100")
    if output.exists():
        raise ValueError(f"refusing to overwrite {output}")


def seed_fixture(material_count: int) -> dict[str, int]:
    Base.metadata.create_all(
        engine,
        tables=[
            Element.__table__,
            Application.__table__,
            Material.__table__,
            MaterialElement.__table__,
            MaterialApplication.__table__,
        ],
    )
    with engine.begin() as connection:
        existing = connection.scalar(select(func.count()).select_from(Material))
        if existing:
            if existing != material_count:
                raise RuntimeError("existing fixture has an unexpected material count")
        else:
            connection.execute(
                insert(Element),
                [
                    {"id": index, "symbol": symbol, "name": symbol}
                    for index, symbol in enumerate(ELEMENTS, start=1)
                ],
            )
            connection.execute(
                insert(Application),
                [
                    {"id": index, "name": name}
                    for index, name in enumerate(APPLICATIONS, start=1)
                ],
            )
            connection.execute(
                insert(Material),
                [
                    {
                        "id": material_id,
                        "mp_id": f"perf-{material_id:05d}",
                        "formula": f"M{material_id}O2",
                        "pretty_formula": f"M{material_id}O2",
                        "material_type": "synthetic_performance_fixture",
                        "energy_above_hull": (material_id % 21) / 100,
                        "is_stable": material_id % 21 == 0,
                        "source": "synthetic_performance_fixture",
                    }
                    for material_id in range(1, material_count + 1)
                ],
            )
            material_elements = []
            material_applications = []
            for material_id in range(1, material_count + 1):
                # O is deliberately common, while the other memberships create
                # dense and sparse sub-neighborhoods deterministically.
                element_ids = {4, 1 + (material_id % len(ELEMENTS))}
                if material_id % 3 == 0:
                    element_ids.add(2)
                if material_id % 5 == 0:
                    element_ids.add(3)
                for element_id in sorted(element_ids):
                    material_elements.append(
                        {
                            "material_id": material_id,
                            "element_id": element_id,
                            "fraction": 1.0 / len(element_ids),
                            "fraction_known": True,
                        }
                    )
                if material_id <= 28 or material_id % 17 == 0:
                    material_applications.append(
                        {
                            "material_id": material_id,
                            "application_id": 1 + (material_id % len(APPLICATIONS)),
                            "suitability_score": 0.5,
                        }
                    )
            connection.execute(insert(MaterialElement), material_elements)
            connection.execute(insert(MaterialApplication), material_applications)

        return {
            "materials": connection.scalar(select(func.count()).select_from(Material)),
            "elements": connection.scalar(select(func.count()).select_from(Element)),
            "material_elements": connection.scalar(
                select(func.count()).select_from(MaterialElement)
            ),
            "material_applications": connection.scalar(
                select(func.count()).select_from(MaterialApplication)
            ),
        }


def classify_statement(statement: str) -> str:
    lowered = " ".join(statement.lower().split())
    for table in (
        "material_elements",
        "material_applications",
        "materials",
        "elements",
        "applications",
    ):
        if f" {table} " in f" {lowered} ":
            return table
    return "other"


@contextmanager
def record_queries(target_engine: Engine):
    recorder = QueryRecorder()
    event.listen(target_engine, "before_cursor_execute", recorder.before)
    event.listen(target_engine, "after_cursor_execute", recorder.after)
    try:
        yield recorder
    finally:
        event.remove(target_engine, "before_cursor_execute", recorder.before)
        event.remove(target_engine, "after_cursor_execute", recorder.after)


@contextmanager
def simulated_round_trip(target_engine: Engine, milliseconds: int):
    def delay(*_args) -> None:
        time.sleep(milliseconds / 1_000)

    if milliseconds:
        event.listen(target_engine, "before_cursor_execute", delay)
    try:
        yield
    finally:
        if milliseconds:
            event.remove(target_engine, "before_cursor_execute", delay)


def service_measurement(depth: int, limit: int) -> tuple[dict[str, Any], dict]:
    with SessionLocal() as db, record_queries(engine) as queries:
        service = MaterialNeighborhoodService(db)
        profiled = ProfiledNeighborService(db)
        service.neighbor_service = profiled
        started = time.perf_counter()
        result = service.get_neighborhood(material_id=1, depth=depth, limit=limit)
        service_ms = (time.perf_counter() - started) * 1_000

    serialization_started = time.perf_counter()
    validated = MaterialNeighborhoodResponse.model_validate(result)
    payload = validated.model_dump_json().encode("utf-8")
    serialization_ms = (time.perf_counter() - serialization_started) * 1_000
    database_ms = sum(queries.durations_ms)
    statement_counts = Counter(classify_statement(item) for item in queries.statements)
    return (
        {
            "service_ms": round(service_ms, 3),
            "database_query_count": len(queries.statements),
            "database_execute_ms": round(database_ms, 3),
            "query_count_by_table": dict(sorted(statement_counts.items())),
            "neighbor_service_calls": profiled.calls,
            "neighbor_service_ms": round(profiled.call_ms, 3),
            "neighbor_build_and_score_ms": round(profiled.build_ms, 3),
            "neighborhood_graph_ms_estimate": round(
                max(0.0, service_ms - profiled.call_ms), 3
            ),
            "neighbor_query_materialization_and_collection_ms_estimate": round(
                max(0.0, profiled.call_ms - database_ms - profiled.build_ms), 3
            ),
            "serialization_ms": round(serialization_ms, 3),
            "payload_bytes": len(payload),
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "node_count": result["node_count"],
            "edge_count": result["edge_count"],
        },
        result,
    )


def endpoint_measurement(depth: int, limit: int, rtt_ms: int) -> dict[str, Any]:
    def override_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    path = f"/api/v1/materials/1/neighborhood?depth={depth}&limit={limit}"
    try:
        with simulated_round_trip(engine, rtt_ms), record_queries(engine) as queries:
            with TestClient(app) as client:
                started = time.perf_counter()
                response = client.get(path)
                wall_ms = (time.perf_counter() - started) * 1_000
    finally:
        app.dependency_overrides.clear()
    if response.status_code != 200:
        raise RuntimeError(f"endpoint returned {response.status_code}: {response.text}")
    return {
        "simulated_rtt_ms_per_query": rtt_ms,
        "wall_ms": round(wall_ms, 3),
        "database_query_count": len(queries.statements),
        "database_execute_ms_including_simulated_rtt": round(
            sum(queries.durations_ms), 3
        ),
        "payload_bytes": len(response.content),
        "payload_sha256": hashlib.sha256(response.content).hexdigest(),
    }


def main() -> int:
    args = parse_args()
    validate_environment(
        args.output,
        args.materials,
        args.limit,
        args.warm_runs,
        args.rtt_ms,
    )
    counts = seed_fixture(args.materials)

    service_runs = []
    expected_result = None
    for _ in range(args.warm_runs + 1):
        measurement, result = service_measurement(args.depth, args.limit)
        service_runs.append(measurement)
        if expected_result is None:
            expected_result = result
        elif result != expected_result:
            raise RuntimeError("repeated service result changed")

    endpoint_runs = [
        endpoint_measurement(args.depth, args.limit, rtt_ms)
        for rtt_ms in args.rtt_ms
    ]
    warm_service_ms = [item["service_ms"] for item in service_runs[1:]]
    report = {
        "schema_version": 1,
        "method": "bounded sequential local diagnosis; no concurrency or network",
        "fixture": {
            "kind": "deterministic synthetic production-count fixture",
            "row_counts": counts,
        },
        "request": {"material_id": 1, "depth": args.depth, "limit": args.limit},
        "service_runs": {
            "cold": service_runs[0],
            "warm": service_runs[1:],
            "warm_median_service_ms": round(statistics.median(warm_service_ms), 3),
        },
        "endpoint_latency_sensitivity": endpoint_runs,
        "semantic_stability": {
            "repeated_results_identical": True,
            "canonical_result_sha256": hashlib.sha256(
                json.dumps(
                    expected_result,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
        },
        "limitations": [
            "SQLite does not reproduce PostgreSQL execution plans or Neon network behavior.",
            "The fixture matches production material count but not the exact production cohort.",
            "Artificial per-query delay is a sensitivity test, not a production measurement.",
            "Sequential measurements do not establish concurrency capacity.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(args.output), "status": "complete"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
