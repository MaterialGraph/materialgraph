import argparse
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

from app.core.database import SessionLocal, engine
from app.main import app
from app.models.dataset_import import (
    DatasetImportRun,
    MaterialImportEvent,
    MaterialSourceMembership,
    MaterialSourceRecord,
)
from app.models.material import Material
from app.services.material.import_pipeline import MaterialImportPipeline
from app.services.material.real_data_qualification import (
    APPROVED_ACCEPTED,
    APPROVED_MANIFEST_SHA256,
    COLLISION_SOURCE_ID,
    CURATED_MATERIAL_COUNT,
    EXPECTED_CURATED_CONFLICTS,
    evaluate_collision_event,
    evaluate_curated_preservation,
    evaluate_manifest_contract,
    extract_identity_formula_pairs,
    summarize_formula_crowding,
)
from capture_curated_database_state import capture
from qualify_dataset_expansion import (
    execute_scenario,
    scenarios,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Qualify the exact approved MG-DE-007 real-source cohort."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--before-curated-state", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--expected-database-name", required=True)
    parser.add_argument("--warm-runs", type=int, default=2)
    return parser


def validate_environment(expected_database_name: str) -> None:
    actual = engine.url.database or ""
    if actual != expected_database_name:
        raise ValueError("configured database does not match the expected name")
    lowered = actual.lower()
    if "test" not in lowered or "mg_de_007" not in lowered:
        raise ValueError("MG-DE-007 requires a dedicated mg_de_007 test database")
    if engine.dialect.name != "postgresql":
        raise ValueError("MG-DE-007 qualification requires PostgreSQL")


def reconciliation() -> tuple[dict, int]:
    with SessionLocal() as db:
        run = db.scalar(
            select(DatasetImportRun)
            .where(
                DatasetImportRun.manifest_sha256
                == APPROVED_MANIFEST_SHA256
            )
            .order_by(DatasetImportRun.started_at.desc())
        )
        if run is None:
            raise ValueError("approved manifest import run was not found")
        event_counts = dict(
            db.execute(
                select(MaterialImportEvent.outcome, func.count())
                .where(MaterialImportEvent.import_run_id == run.id)
                .group_by(MaterialImportEvent.outcome)
            ).all()
        )
        collision = db.scalar(
            select(MaterialImportEvent).where(
                MaterialImportEvent.import_run_id == run.id,
                MaterialImportEvent.source_id == COLLISION_SOURCE_ID,
            )
        )
        collision_document = (
            {
                "source_id": collision.source_id,
                "material_id": collision.material_id,
                "outcome": collision.outcome,
                "reason": collision.reason,
            }
            if collision is not None
            else None
        )
        source_records = db.scalar(
            select(func.count())
            .select_from(MaterialSourceRecord)
            .where(MaterialSourceRecord.source == "materials_project")
        )
        active_records = db.scalar(
            select(func.count())
            .select_from(MaterialSourceRecord)
            .where(
                MaterialSourceRecord.source == "materials_project",
                MaterialSourceRecord.active.is_(True),
            )
        )
        memberships = db.scalar(
            select(func.count()).select_from(MaterialSourceMembership)
        )
        total_materials = db.scalar(select(func.count()).select_from(Material))
        target_id = db.scalar(
            select(Material.id)
            .where(Material.id > 28)
            .order_by(Material.id)
            .limit(1)
        )
        if target_id is None:
            raise ValueError("real-source imported materials were not found")
        plan = db.execute(
            text(
                "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) "
                "SELECT id, mp_id, formula FROM materials "
                "WHERE formula = (SELECT formula FROM materials WHERE id = :id) "
                "ORDER BY id"
            ),
            {"id": target_id},
        ).scalar_one()
        failures = evaluate_collision_event(collision_document)
        expected_records = APPROVED_ACCEPTED - EXPECTED_CURATED_CONFLICTS
        if run.status != "completed_with_conflicts":
            failures.append("run_status")
        if event_counts != {
            "conflicted": EXPECTED_CURATED_CONFLICTS,
            "inserted": expected_records,
        }:
            failures.append("event_counts")
        if source_records != expected_records or active_records != expected_records:
            failures.append("source_records")
        if memberships != expected_records:
            failures.append("memberships")
        if total_materials != CURATED_MATERIAL_COUNT + expected_records:
            failures.append("material_count")
        return (
            {
                "run_id": str(run.id),
                "run_status": run.status,
                "run_outcome_counts": run.outcome_counts,
                "event_counts": event_counts,
                "collision": collision_document,
                "source_records": source_records,
                "active_source_records": active_records,
                "memberships": memberships,
                "materials": total_materials,
                "formula_lookup_plan": plan,
                "gate_failures": failures,
            },
            target_id,
        )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not 1 <= args.warm_runs <= 5:
        raise ValueError("--warm-runs must be between 1 and 5")
    validate_environment(args.expected_database_name)
    document = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest, digest = MaterialImportPipeline._load_manifest(args.manifest)
    failures = evaluate_manifest_contract(document)
    if digest != APPROVED_MANIFEST_SHA256:
        failures.append("verified_manifest_sha256")
    before = json.loads(args.before_curated_state.read_text(encoding="utf-8"))
    after = capture()
    failures.extend(evaluate_curated_preservation(before, after))
    facts, target_id = reconciliation()
    failures.extend(facts["gate_failures"])
    if failures:
        raise ValueError("MG-DE-007 gate failures: " + ", ".join(failures))

    args.output_directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    results = []
    with TestClient(app) as client:
        for scenario in scenarios(5, target_id):
            runs = []
            body = None
            for _run_number in range(args.warm_runs + 1):
                measurement, body = execute_scenario(client, scenario)
                runs.append(measurement)
            pairs = extract_identity_formula_pairs(body)
            crowding = summarize_formula_crowding(pairs)
            snapshot_path = args.output_directory / f"{scenario.name}.json"
            write_json(snapshot_path, body)
            results.append(
                {
                    **asdict(scenario),
                    "cold": runs[0],
                    "warm": runs[1:],
                    "snapshot": snapshot_path.name,
                    "formula_crowding": crowding.to_dict(),
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
        "work_item": "MG-DE-007",
        "method": "bounded sequential requests; no concurrency or load",
        "commit": commit,
        "manifest_sha256": digest,
        "manifest_counts": manifest["counts"],
        "curated_preservation": {"before": before, "after": after},
        "database_reconciliation": facts,
        "scenarios": results,
        "neon_authorized": False,
        "production_authorized": False,
    }
    write_json(args.output_directory / "qualification-report.json", report)
    print(
        json.dumps(
            {
                "manifest_sha256": digest,
                "scenario_count": len(results),
                "gate_failures": [],
                "output_directory": str(args.output_directory),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
