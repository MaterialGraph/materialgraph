import argparse
import json
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from app.services.material.neon_qualification import (
    APPROVED_MANIFEST_FILE_SHA256,
    NeonQualificationBudget,
    approved_manifest_file_sha256,
    sanitized_url_summary,
)
from app.services.material.production_preflight import (
    LIFECYCLE_TABLES,
    ProductionBaselineObservation,
    ProductionConnectionObservation,
    evaluate_production_preflight_observations,
)
from app.services.material.production_rollout import (
    ProductionBaseline,
    ProductionExpectedOutcome,
    ProductionResourceIdentity,
    ProductionRollbackBoundary,
    ProductionRolloutAuthorization,
    evaluate_production_rollout_contract,
    evaluate_production_rollout_document,
)
from app.services.material.real_data_qualification import canonical_sha256


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture an MG-DE-009 read-only production preflight."
    )
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pooled-url-env", default="DATABASE_URL")
    parser.add_argument("--direct-url-env", default="DATABASE_MIGRATION_URL")
    return parser


def capture_connection(connection) -> ProductionConnectionObservation:
    connection.execute(text("SET TRANSACTION READ ONLY"))
    row = connection.execute(
        text(
            """
            SELECT
                current_database() AS database,
                current_user AS username,
                current_setting('transaction_read_only') AS transaction_read_only
            """
        )
    ).mappings().one()
    driver_connection = connection.connection.driver_connection
    tls_in_use = bool(driver_connection.pgconn.ssl_in_use)
    return ProductionConnectionObservation(
        **row,
        tls_in_use=tls_in_use,
    )


def capture_baseline(connection) -> ProductionBaselineObservation:
    counts = connection.execute(
        text(
            """
            SELECT
                (SELECT count(*) FROM materials) AS material_count,
                (SELECT count(*) FROM elements) AS element_count,
                (SELECT count(*) FROM material_elements) AS material_element_count
            """
        )
    ).mappings().one()
    materials = [
        dict(row)
        for row in connection.execute(
            text(
                """
                SELECT id, mp_id, formula, pretty_formula, material_type,
                       band_gap, energy_above_hull, formation_energy_per_atom,
                       density, is_stable, source, raw_data
                FROM materials
                WHERE id <= 28
                ORDER BY id
                """
            )
        ).mappings()
    ]
    material_elements = [
        list(row)
        for row in connection.execute(
            text(
                """
                SELECT material_id, element_id, fraction, fraction_known
                FROM material_elements
                WHERE material_id <= 28
                ORDER BY material_id, element_id
                """
            )
        )
    ]
    sentinel = connection.execute(
        text("SELECT id, mp_id FROM materials WHERE id = 5")
    ).mappings().one()
    revision = connection.execute(
        text("SELECT version_num FROM alembic_version")
    ).scalar_one()
    table_presence = {
        table_name: bool(
            connection.execute(
                text("SELECT to_regclass(:table_name) IS NOT NULL"),
                {"table_name": f"public.{table_name}"},
            ).scalar_one()
        )
        for table_name in LIFECYCLE_TABLES
    }
    protected = {
        "materials": materials,
        "material_elements": material_elements,
    }
    return ProductionBaselineObservation(
        alembic_revision=revision,
        curated_records_sha256=canonical_sha256(protected),
        material_count=int(counts["material_count"]),
        element_count=int(counts["element_count"]),
        material_element_count=int(counts["material_element_count"]),
        sentinel_id=int(sentinel["id"]),
        sentinel_mp_id=sentinel["mp_id"],
        lifecycle_table_presence=table_presence,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.output.exists():
        raise ValueError(f"refusing to overwrite {args.output}")

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    pooled_url = os.environ.get(args.pooled_url_env, "")
    direct_url = os.environ.get(args.direct_url_env, "")
    document_issues = evaluate_production_rollout_document(contract)
    if document_issues:
        raise ValueError("invalid production contract: " + ", ".join(document_issues))

    target = ProductionResourceIdentity(**contract["production_target"])
    baseline = ProductionBaseline(**contract["expected_baseline"])
    issues = evaluate_production_rollout_contract(
        target=target,
        baseline=baseline,
        expected_outcome=ProductionExpectedOutcome(**contract["expected_outcome"]),
        authorization=ProductionRolloutAuthorization(**contract["authorization"]),
        rollback=ProductionRollbackBoundary(**contract["rollback_boundary"]),
        pooled_url=pooled_url,
        direct_url=direct_url,
        manifest=manifest,
        budget=NeonQualificationBudget(**contract["budget"]),
    )
    if approved_manifest_file_sha256(args.manifest) != APPROVED_MANIFEST_FILE_SHA256:
        issues.append("manifest_file_sha256")
    if issues:
        raise ValueError("production preflight guard failed: " + ", ".join(issues))

    engine_options = {
        "poolclass": NullPool,
        "connect_args": {
            "connect_timeout": 20,
            "application_name": "mg-de-009-read-only-preflight",
        },
    }
    direct_engine = create_engine(direct_url, **engine_options)
    pooled_engine = create_engine(pooled_url, **engine_options)
    try:
        with direct_engine.connect() as direct_connection:
            with direct_connection.begin():
                direct = capture_connection(direct_connection)
                observed = capture_baseline(direct_connection)
        with pooled_engine.connect() as pooled_connection:
            with pooled_connection.begin():
                pooled = capture_connection(pooled_connection)
    finally:
        direct_engine.dispose()
        pooled_engine.dispose()

    observation_issues = evaluate_production_preflight_observations(
        target=target,
        baseline=baseline,
        direct=direct,
        pooled=pooled,
        observed=observed,
    )
    result = {
        "schema_version": 1,
        "work_item": "MG-DE-009",
        "database_observations_valid": not observation_issues,
        "issues": observation_issues,
        "target": contract["production_target"],
        "direct_url": sanitized_url_summary(direct_url),
        "pooled_url": sanitized_url_summary(pooled_url),
        "direct_observation": direct.__dict__,
        "pooled_observation": pooled.__dict__,
        "baseline_observation": observed.__dict__,
        "provider_identity_verified": False,
        "gate_a_complete": False,
        "network_access_performed": True,
        "database_writes_performed": False,
        "migration_performed": False,
        "backup_performed": False,
        "restore_performed": False,
        "service_restart_performed": False,
        "production_execution_authorized": False,
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if not observation_issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
