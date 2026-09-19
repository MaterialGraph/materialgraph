from pathlib import Path

from app.services.material.production_preflight import (
    LIFECYCLE_TABLES,
    ProductionBaselineObservation,
    ProductionConnectionObservation,
    evaluate_production_preflight_observations,
)


from app.services.material.production_rollout import (
    ProductionBaseline,
    ProductionResourceIdentity,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def target() -> ProductionResourceIdentity:
    return ProductionResourceIdentity(
        project_id="production-project",
        branch_id="production-branch",
        branch_name="production",
        endpoint_id="production-endpoint",
        database_name="materialgraph",
        pooled_role="materialgraph_runtime",
        direct_role="materialgraph_migration",
    )


def baseline() -> ProductionBaseline:
    return ProductionBaseline(
        current_revision="7a4c2e91b6d8",
        target_revision="c8f3a2d7e901",
        curated_records_sha256="a" * 64,
        material_count=28,
        element_count=9,
        material_element_count=94,
        sentinel_id=5,
        sentinel_mp_id="mp-19017",
    )


def connection(username: str) -> ProductionConnectionObservation:
    return ProductionConnectionObservation(
        database="materialgraph",
        username=username,
        transaction_read_only="on",
        tls_in_use=True,
    )


def observation() -> ProductionBaselineObservation:
    return ProductionBaselineObservation(
        alembic_revision="7a4c2e91b6d8",
        curated_records_sha256="a" * 64,
        material_count=28,
        element_count=9,
        material_element_count=94,
        sentinel_id=5,
        sentinel_mp_id="mp-19017",
        lifecycle_table_presence={name: False for name in LIFECYCLE_TABLES},
    )


def evaluate(**overrides) -> list[str]:
    values = {
        "target": target(),
        "baseline": baseline(),
        "direct": connection("materialgraph_migration"),
        "pooled": connection("materialgraph_runtime"),
        "observed": observation(),
    }
    values.update(overrides)
    return evaluate_production_preflight_observations(**values)


def test_preflight_accepts_exact_read_only_observations():
    assert evaluate() == []


def test_preflight_rejects_connection_identity_tls_and_read_write_mode():
    issues = evaluate(
        direct=ProductionConnectionObservation(
            database="wrong",
            username="wrong",
            transaction_read_only="off",
            tls_in_use=False,
        )
    )
    assert issues == [
        "direct_database",
        "direct_role",
        "direct_transaction_read_only",
        "direct_tls",
    ]


def test_preflight_rejects_baseline_drift_and_existing_lifecycle_tables():
    changed = ProductionBaselineObservation(
        **{
            **observation().__dict__,
            "alembic_revision": "unexpected",
            "curated_records_sha256": "b" * 64,
            "material_count": 29,
            "lifecycle_table_presence": {
                **observation().lifecycle_table_presence,
                "dataset_import_runs": True,
            },
        }
    )
    issues = evaluate(observed=changed)
    assert issues == [
        "observed_alembic_revision",
        "observed_curated_records_sha256",
        "observed_material_count",
        "observed_lifecycle_tables_already_present",
    ]


def test_preflight_requires_exact_lifecycle_table_set():
    changed = ProductionBaselineObservation(
        **{
            **observation().__dict__,
            "lifecycle_table_presence": {},
        }
    )
    assert evaluate(observed=changed) == ["observed_lifecycle_table_set"]


def test_capture_script_preserves_read_only_and_explicit_engine_boundaries():
    source = (
        PROJECT_ROOT / "scripts/capture_production_preflight.py"
    ).read_text(encoding="utf-8")

    assert "from app.core.database" not in source
    assert "poolclass\": NullPool" in source
    assert source.count('text("SET TRANSACTION READ ONLY")') == 1
    assert source.index("evaluate_production_rollout_document") < source.index(
        "direct_engine = create_engine"
    )
    assert source.index("evaluate_production_rollout_contract") < source.index(
        "direct_engine = create_engine"
    )
    for forbidden in (
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        "TRUNCATE ",
        "DROP TABLE",
        "CREATE TABLE",
        "ALTER TABLE",
    ):
        assert forbidden not in source.upper()
