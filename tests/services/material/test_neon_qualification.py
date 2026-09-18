from app.services.material.neon_qualification import (
    NeonProductionIdentity,
    NeonQualificationBudget,
    NeonResourceIdentity,
    evaluate_neon_qualification_contract,
    sanitized_url_summary,
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


def resource() -> NeonResourceIdentity:
    return NeonResourceIdentity(
        project_id="silent-test-project",
        branch_id="br-mgde008",
        branch_name="mg-de-008-qualification-test",
        endpoint_id="ep-mgde008",
        database_name="materialgraph_test",
    )


def production() -> NeonProductionIdentity:
    return NeonProductionIdentity(
        project_id="production-project",
        branch_id="production-branch",
        endpoint_id="production-endpoint",
    )


POOLED = (
    "postgresql+psycopg://runtime:secret@ep-mgde008-pooler.us-east-2."
    "aws.neon.tech/materialgraph_test?sslmode=verify-full&channel_binding=require"
)
DIRECT = (
    "postgresql+psycopg://migration:secret@ep-mgde008.us-east-2."
    "aws.neon.tech/materialgraph_test?sslmode=verify-full&channel_binding=require"
)


def test_contract_accepts_distinct_bounded_nonproduction_target():
    assert evaluate_neon_qualification_contract(
        resource=resource(),
        production=production(),
        pooled_url=POOLED,
        direct_url=DIRECT,
        manifest=manifest(),
        budget=NeonQualificationBudget(),
    ) == []


def test_contract_rejects_production_collision_and_unsafe_branch():
    unsafe = NeonResourceIdentity(
        project_id=production().project_id,
        branch_id=production().branch_id,
        branch_name="main",
        endpoint_id=production().endpoint_id,
        database_name="materialgraph_test",
    )
    issues = evaluate_neon_qualification_contract(
        resource=unsafe,
        production=production(),
        pooled_url=POOLED,
        direct_url=DIRECT,
        manifest=manifest(),
        budget=NeonQualificationBudget(),
    )
    assert "branch_name" in issues
    assert "production_branch_id_collision" in issues


def test_contract_allows_isolated_branch_in_same_project():
    shared_project = NeonProductionIdentity(
        project_id=resource().project_id,
        branch_id="production-branch",
        endpoint_id="production-endpoint",
    )
    assert evaluate_neon_qualification_contract(
        resource=resource(),
        production=shared_project,
        pooled_url=POOLED,
        direct_url=DIRECT,
        manifest=manifest(),
        budget=NeonQualificationBudget(),
    ) == []


def test_contract_requires_pooled_direct_roles_and_strong_tls():
    issues = evaluate_neon_qualification_contract(
        resource=resource(),
        production=production(),
        pooled_url=DIRECT.replace("migration", "runtime"),
        direct_url=POOLED.replace("runtime", "migration").replace(
            "sslmode=verify-full", "sslmode=require"
        ),
        manifest=manifest(),
        budget=NeonQualificationBudget(),
    )
    assert "pooled_endpoint_role" in issues
    assert "direct_endpoint_role" in issues
    assert "direct_sslmode" in issues


def test_contract_rejects_parallel_or_excess_connection_budget():
    issues = evaluate_neon_qualification_contract(
        resource=resource(),
        production=production(),
        pooled_url=POOLED,
        direct_url=DIRECT,
        manifest=manifest(),
        budget=NeonQualificationBudget(
            max_connections=6,
            max_parallel_requests=2,
        ),
    )
    assert issues == ["budget_connections", "budget_parallel_requests"]


def test_sanitized_summary_does_not_expose_credentials():
    summary = sanitized_url_summary(POOLED)
    assert summary["username_present"] == "true"
    assert summary["password_present"] == "true"
    assert "secret" not in str(summary)
    assert "runtime" not in str(summary)
