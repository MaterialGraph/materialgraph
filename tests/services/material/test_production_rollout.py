from app.services.material.neon_qualification import NeonQualificationBudget
from app.services.material.production_rollout import (
    ProductionBaseline,
    ProductionExpectedOutcome,
    ProductionResourceIdentity,
    ProductionRollbackBoundary,
    ProductionRolloutAuthorization,
    evaluate_production_rollout_document,
    evaluate_production_rollout_contract,
)
from app.services.material.real_data_qualification import (
    APPROVED_MANIFEST_SHA256,
)


def manifest() -> dict:
    return {
        "manifest_sha256": APPROVED_MANIFEST_SHA256,
        "source": "materials_project",
        "dataset": {
            "selection_contract_version": "materials-project-selection-v3"
        },
        "counts": {
            "accepted": 1727,
            "source_complete": True,
            "duplicate_source_ids": 0,
        },
    }


def target() -> ProductionResourceIdentity:
    return ProductionResourceIdentity(
        project_id="reviewed-project",
        branch_id="reviewed-production-branch",
        branch_name="production",
        endpoint_id="reviewed-production-endpoint",
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


POOLED = (
    "postgresql+psycopg://materialgraph_runtime:secret@"
    "reviewed-production-endpoint-pooler.us-east-2.aws.neon.tech/"
    "materialgraph?sslmode=verify-full&channel_binding=require"
)
DIRECT = (
    "postgresql+psycopg://materialgraph_migration:secret@"
    "reviewed-production-endpoint.us-east-2.aws.neon.tech/"
    "materialgraph?sslmode=verify-full&channel_binding=require"
)


def evaluate(**overrides) -> list[str]:
    values = {
        "target": target(),
        "baseline": baseline(),
        "expected_outcome": ProductionExpectedOutcome(),
        "authorization": ProductionRolloutAuthorization(),
        "rollback": ProductionRollbackBoundary(),
        "pooled_url": POOLED,
        "direct_url": DIRECT,
        "manifest": manifest(),
        "budget": NeonQualificationBudget(),
    }
    values.update(overrides)
    return evaluate_production_rollout_contract(**values)


def test_contract_accepts_reviewed_target_with_execution_disabled():
    assert evaluate() == []


def test_contract_document_requires_explicit_sections_and_fields():
    issues = evaluate_production_rollout_document(
        {
            "schema_version": 2,
            "production_target": {},
            "expected_baseline": {},
            "expected_outcome": {},
            "authorization": {},
            "rollback_boundary": {},
        }
    )

    assert "contract_schema_version" in issues
    assert "contract_production_target_project_id" in issues
    assert "contract_expected_baseline_curated_records_sha256" in issues
    assert "contract_expected_outcome_processed" in issues
    assert "contract_authorization_import_authorized" in issues
    assert "contract_rollback_boundary_backup_required" in issues
    assert "contract_budget" in issues


def test_contract_rejects_nonproduction_identity_and_wrong_endpoint():
    wrong_target = ProductionResourceIdentity(
        **{
            **target().__dict__,
            "branch_name": "mg-de-009-test",
            "endpoint_id": "different-endpoint",
        }
    )
    issues = evaluate(target=wrong_target)
    assert "target_branch_name" in issues
    assert "pooled_endpoint_id" in issues
    assert "direct_endpoint_id" in issues


def test_contract_rejects_roles_driver_and_weak_tls():
    issues = evaluate(
        pooled_url=POOLED.replace(
            "materialgraph_runtime",
            "materialgraph_migration",
        ),
        direct_url=DIRECT.replace(
            "postgresql+psycopg",
            "postgresql",
        ).replace("sslmode=verify-full", "sslmode=require"),
    )
    assert "pooled_database_role" in issues
    assert "direct_driver" in issues
    assert "direct_sslmode" in issues


def test_contract_rejects_changed_baseline_and_outcome():
    changed_baseline = ProductionBaseline(
        **{
            **baseline().__dict__,
            "current_revision": "unexpected",
            "material_count": 29,
            "sentinel_mp_id": "mp-other",
        }
    )
    changed_outcome = ProductionExpectedOutcome(
        processed=1727,
        inserted=1700,
        conflicted=27,
    )
    issues = evaluate(
        baseline=changed_baseline,
        expected_outcome=changed_outcome,
    )
    assert "baseline_current_revision" in issues
    assert "baseline_material_count" in issues
    assert "baseline_sentinel_mp_id" in issues
    assert "expected_inserted" in issues
    assert "expected_conflicted" in issues


def test_contract_rejects_any_premature_execution_authorization():
    issues = evaluate(
        authorization=ProductionRolloutAuthorization(
            migration_authorized=True,
            import_authorized=True,
            restore_authorized=True,
            service_restart_authorized=True,
        )
    )
    assert issues == [
        "migration_authorization_must_be_false",
        "import_authorization_must_be_false",
        "restore_authorization_must_be_false",
        "service_restart_authorization_must_be_false",
    ]


def test_contract_requires_rollback_controls_and_sequential_budget():
    issues = evaluate(
        rollback=ProductionRollbackBoundary(
            backup_required=False,
            backup_hash_required=False,
            archive_listing_required=False,
            pre_import_snapshot_required=False,
            minimum_observation_minutes=5,
        ),
        budget=NeonQualificationBudget(
            max_connections=6,
            max_parallel_requests=2,
        ),
    )
    assert issues == [
        "rollback_backup_required",
        "rollback_backup_hash_required",
        "rollback_archive_listing_required",
        "rollback_pre_import_snapshot_required",
        "rollback_observation_minutes",
        "budget_connections",
        "budget_parallel_requests",
    ]
