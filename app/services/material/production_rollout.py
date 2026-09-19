from dataclasses import dataclass
from string import hexdigits

from sqlalchemy.engine import make_url

from app.services.material.neon_qualification import NeonQualificationBudget
from app.services.material.real_data_qualification import (
    APPROVED_MANIFEST_SHA256,
    evaluate_manifest_contract,
)


EXPECTED_PRODUCTION_CURRENT_REVISION = "7a4c2e91b6d8"
EXPECTED_PRODUCTION_TARGET_REVISION = "c8f3a2d7e901"
EXPECTED_CURATED_MATERIAL_COUNT = 28
EXPECTED_ELEMENT_COUNT = 9
EXPECTED_MATERIAL_ELEMENT_COUNT = 94
EXPECTED_SENTINEL_ID = 5
EXPECTED_SENTINEL_MP_ID = "mp-19017"
EXPECTED_PROCESSED = 1_727
EXPECTED_INSERTED = 1_699
EXPECTED_CONFLICTED = 28
REQUIRED_CONTRACT_FIELDS = {
    "production_target": frozenset(
        {
            "project_id",
            "branch_id",
            "branch_name",
            "endpoint_id",
            "database_name",
            "pooled_role",
            "direct_role",
        }
    ),
    "expected_baseline": frozenset(
        {
            "current_revision",
            "target_revision",
            "curated_records_sha256",
            "material_count",
            "element_count",
            "material_element_count",
            "sentinel_id",
            "sentinel_mp_id",
        }
    ),
    "expected_outcome": frozenset(
        {"processed", "inserted", "conflicted", "updated", "rejected", "retired"}
    ),
    "authorization": frozenset(
        {
            "migration_authorized",
            "import_authorized",
            "restore_authorized",
            "service_restart_authorized",
        }
    ),
    "rollback_boundary": frozenset(
        {
            "backup_required",
            "backup_hash_required",
            "archive_listing_required",
            "pre_import_snapshot_required",
            "minimum_observation_minutes",
        }
    ),
    "budget": frozenset(
        {
            "max_wall_clock_minutes",
            "max_active_compute_seconds",
            "max_storage_delta_bytes",
            "max_connections",
            "max_parallel_requests",
        }
    ),
}


def evaluate_production_rollout_document(contract: dict) -> list[str]:
    issues: list[str] = []
    if contract.get("schema_version") != 1:
        issues.append("contract_schema_version")

    for section_name, required_fields in REQUIRED_CONTRACT_FIELDS.items():
        section = contract.get(section_name)
        if not isinstance(section, dict):
            issues.append(f"contract_{section_name}")
            continue
        for field_name in sorted(required_fields - section.keys()):
            issues.append(f"contract_{section_name}_{field_name}")

    return issues


@dataclass(frozen=True)
class ProductionResourceIdentity:
    project_id: str
    branch_id: str
    branch_name: str
    endpoint_id: str
    database_name: str
    pooled_role: str
    direct_role: str


@dataclass(frozen=True)
class ProductionBaseline:
    current_revision: str
    target_revision: str
    curated_records_sha256: str
    material_count: int
    element_count: int
    material_element_count: int
    sentinel_id: int
    sentinel_mp_id: str


@dataclass(frozen=True)
class ProductionExpectedOutcome:
    processed: int = EXPECTED_PROCESSED
    inserted: int = EXPECTED_INSERTED
    conflicted: int = EXPECTED_CONFLICTED
    updated: int = 0
    rejected: int = 0
    retired: int = 0


@dataclass(frozen=True)
class ProductionRolloutAuthorization:
    migration_authorized: bool = False
    import_authorized: bool = False
    restore_authorized: bool = False
    service_restart_authorized: bool = False


@dataclass(frozen=True)
class ProductionRollbackBoundary:
    backup_required: bool = True
    backup_hash_required: bool = True
    archive_listing_required: bool = True
    pre_import_snapshot_required: bool = True
    minimum_observation_minutes: int = 15


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(character in hexdigits for character in value)


def _url_issues(
    value: str,
    *,
    target: ProductionResourceIdentity,
    endpoint_role: str,
) -> list[str]:
    try:
        url = make_url(value)
    except (TypeError, ValueError):
        return [f"{endpoint_role}_url_invalid"]

    issues: list[str] = []
    if url.drivername != "postgresql+psycopg":
        issues.append(f"{endpoint_role}_driver")
    if not url.host or not url.host.lower().endswith(".neon.tech"):
        issues.append(f"{endpoint_role}_host")
    elif not url.host.lower().startswith(
        (
            f"{target.endpoint_id.lower()}.",
            f"{target.endpoint_id.lower()}-pooler.",
        )
    ):
        issues.append(f"{endpoint_role}_endpoint_id")
    if url.database != target.database_name:
        issues.append(f"{endpoint_role}_database")

    expected_role = (
        target.pooled_role if endpoint_role == "pooled" else target.direct_role
    )
    if url.username != expected_role:
        issues.append(f"{endpoint_role}_database_role")
    if not url.password:
        issues.append(f"{endpoint_role}_password")
    if str(url.query.get("sslmode", "")).lower() != "verify-full":
        issues.append(f"{endpoint_role}_sslmode")
    if str(url.query.get("channel_binding", "")).lower() != "require":
        issues.append(f"{endpoint_role}_channel_binding")

    is_pooler = bool(url.host and "-pooler." in url.host.lower())
    if endpoint_role == "pooled" and not is_pooler:
        issues.append("pooled_endpoint_role")
    if endpoint_role == "direct" and is_pooler:
        issues.append("direct_endpoint_role")
    return issues


def evaluate_production_rollout_contract(
    *,
    target: ProductionResourceIdentity,
    baseline: ProductionBaseline,
    expected_outcome: ProductionExpectedOutcome,
    authorization: ProductionRolloutAuthorization,
    rollback: ProductionRollbackBoundary,
    pooled_url: str,
    direct_url: str,
    manifest: dict,
    budget: NeonQualificationBudget,
) -> list[str]:
    issues: list[str] = []

    required_identity = {
        "project_id": target.project_id,
        "branch_id": target.branch_id,
        "endpoint_id": target.endpoint_id,
        "database_name": target.database_name,
        "pooled_role": target.pooled_role,
        "direct_role": target.direct_role,
    }
    for field_name, value in required_identity.items():
        if not value.strip():
            issues.append(f"target_{field_name}")
    if target.branch_name.strip().lower() != "production":
        issues.append("target_branch_name")
    if target.pooled_role == target.direct_role:
        issues.append("database_roles_not_distinct")

    issues.extend(_url_issues(pooled_url, target=target, endpoint_role="pooled"))
    issues.extend(_url_issues(direct_url, target=target, endpoint_role="direct"))
    try:
        pooled = make_url(pooled_url)
        direct = make_url(direct_url)
        if pooled.host == direct.host:
            issues.append("endpoint_hosts_not_distinct")
    except (TypeError, ValueError):
        pass

    issues.extend(
        f"manifest_{issue}" for issue in evaluate_manifest_contract(manifest)
    )
    if manifest.get("manifest_sha256") != APPROVED_MANIFEST_SHA256:
        issues.append("manifest_digest")

    if baseline.current_revision != EXPECTED_PRODUCTION_CURRENT_REVISION:
        issues.append("baseline_current_revision")
    if baseline.target_revision != EXPECTED_PRODUCTION_TARGET_REVISION:
        issues.append("baseline_target_revision")
    if not _is_sha256(baseline.curated_records_sha256):
        issues.append("baseline_curated_records_sha256")
    if baseline.material_count != EXPECTED_CURATED_MATERIAL_COUNT:
        issues.append("baseline_material_count")
    if baseline.element_count != EXPECTED_ELEMENT_COUNT:
        issues.append("baseline_element_count")
    if baseline.material_element_count != EXPECTED_MATERIAL_ELEMENT_COUNT:
        issues.append("baseline_material_element_count")
    if baseline.sentinel_id != EXPECTED_SENTINEL_ID:
        issues.append("baseline_sentinel_id")
    if baseline.sentinel_mp_id != EXPECTED_SENTINEL_MP_ID:
        issues.append("baseline_sentinel_mp_id")

    expected_values = {
        "processed": EXPECTED_PROCESSED,
        "inserted": EXPECTED_INSERTED,
        "conflicted": EXPECTED_CONFLICTED,
        "updated": 0,
        "rejected": 0,
        "retired": 0,
    }
    for field_name, expected in expected_values.items():
        if getattr(expected_outcome, field_name) != expected:
            issues.append(f"expected_{field_name}")

    if authorization.migration_authorized:
        issues.append("migration_authorization_must_be_false")
    if authorization.import_authorized:
        issues.append("import_authorization_must_be_false")
    if authorization.restore_authorized:
        issues.append("restore_authorization_must_be_false")
    if authorization.service_restart_authorized:
        issues.append("service_restart_authorization_must_be_false")

    required_rollback_controls = {
        "backup_required": rollback.backup_required,
        "backup_hash_required": rollback.backup_hash_required,
        "archive_listing_required": rollback.archive_listing_required,
        "pre_import_snapshot_required": rollback.pre_import_snapshot_required,
    }
    for field_name, enabled in required_rollback_controls.items():
        if not enabled:
            issues.append(f"rollback_{field_name}")
    if not 15 <= rollback.minimum_observation_minutes <= 60:
        issues.append("rollback_observation_minutes")

    maximum_budget = NeonQualificationBudget()
    if not 0 < budget.max_wall_clock_minutes <= maximum_budget.max_wall_clock_minutes:
        issues.append("budget_wall_clock")
    if not (
        0
        < budget.max_active_compute_seconds
        <= maximum_budget.max_active_compute_seconds
    ):
        issues.append("budget_compute")
    if not 0 < budget.max_storage_delta_bytes <= maximum_budget.max_storage_delta_bytes:
        issues.append("budget_storage")
    if budget.max_connections not in range(1, 6):
        issues.append("budget_connections")
    if budget.max_parallel_requests != 1:
        issues.append("budget_parallel_requests")

    return list(dict.fromkeys(issues))
