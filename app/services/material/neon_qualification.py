from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.engine import URL, make_url

from app.services.material.real_data_qualification import (
    APPROVED_MANIFEST_SHA256,
    evaluate_manifest_contract,
)

APPROVED_MANIFEST_FILE_SHA256 = (
    "7939dcfd0fab9a8e7e43f7395c59c874673ed19aaf49d1a942650a69595e3daa"
)


@dataclass(frozen=True)
class NeonResourceIdentity:
    project_id: str
    branch_id: str
    branch_name: str
    endpoint_id: str
    database_name: str


@dataclass(frozen=True)
class NeonProductionIdentity:
    project_id: str
    branch_id: str
    endpoint_id: str


@dataclass(frozen=True)
class NeonQualificationBudget:
    max_wall_clock_minutes: int = 120
    max_active_compute_seconds: int = 3_600
    max_storage_delta_bytes: int = 268_435_456
    max_connections: int = 5
    max_parallel_requests: int = 1


def _url_issues(
    value: str,
    *,
    expected_database: str,
    expected_endpoint_id: str,
    endpoint_role: str,
) -> list[str]:
    try:
        url = make_url(value)
    except (TypeError, ValueError):
        return [f"{endpoint_role}_url_invalid"]

    issues: list[str] = []
    if url.get_backend_name() != "postgresql":
        issues.append(f"{endpoint_role}_backend")
    if not url.host or not url.host.lower().endswith(".neon.tech"):
        issues.append(f"{endpoint_role}_host")
    elif not url.host.lower().startswith(
        (f"{expected_endpoint_id.lower()}.", f"{expected_endpoint_id.lower()}-pooler.")
    ):
        issues.append(f"{endpoint_role}_endpoint_id")
    if url.database != expected_database:
        issues.append(f"{endpoint_role}_database")

    sslmode = str(url.query.get("sslmode", "")).lower()
    if sslmode != "verify-full":
        issues.append(f"{endpoint_role}_sslmode")
    channel_binding = str(url.query.get("channel_binding", "")).lower()
    if channel_binding != "require":
        issues.append(f"{endpoint_role}_channel_binding")

    is_pooler = bool(url.host and "-pooler." in url.host.lower())
    if endpoint_role == "pooled" and not is_pooler:
        issues.append("pooled_endpoint_role")
    if endpoint_role == "direct" and is_pooler:
        issues.append("direct_endpoint_role")
    return issues


def evaluate_neon_qualification_contract(
    *,
    resource: NeonResourceIdentity,
    production: NeonProductionIdentity,
    pooled_url: str,
    direct_url: str,
    manifest: dict,
    budget: NeonQualificationBudget,
) -> list[str]:
    issues: list[str] = []

    safe_branch_name = resource.branch_name.lower().replace("_", "-")
    if "mg-de-008" not in safe_branch_name or not any(
        marker in safe_branch_name
        for marker in ("test", "qualification", "nonprod")
    ):
        issues.append("branch_name")

    comparisons = (
        ("branch_id", resource.branch_id, production.branch_id),
        ("endpoint_id", resource.endpoint_id, production.endpoint_id),
    )
    if not resource.project_id.strip():
        issues.append("qualification_project_id")
    if not production.project_id.strip():
        issues.append("production_project_id")
    for field_name, qualification_value, production_value in comparisons:
        if not qualification_value.strip():
            issues.append(f"qualification_{field_name}")
        if not production_value.strip():
            issues.append(f"production_{field_name}")
        if qualification_value.strip() == production_value.strip():
            issues.append(f"production_{field_name}_collision")
    issues.extend(
        _url_issues(
            pooled_url,
            expected_database=resource.database_name,
            expected_endpoint_id=resource.endpoint_id,
            endpoint_role="pooled",
        )
    )
    issues.extend(
        _url_issues(
            direct_url,
            expected_database=resource.database_name,
            expected_endpoint_id=resource.endpoint_id,
            endpoint_role="direct",
        )
    )

    try:
        pooled = make_url(pooled_url)
        direct = make_url(direct_url)
        if pooled.host == direct.host:
            issues.append("endpoint_hosts_not_distinct")
        if pooled.username == direct.username:
            issues.append("database_roles_not_distinct")
    except (TypeError, ValueError):
        pass

    issues.extend(f"manifest_{issue}" for issue in evaluate_manifest_contract(manifest))
    if manifest.get("manifest_sha256") != APPROVED_MANIFEST_SHA256:
        issues.append("manifest_digest")

    default_budget = NeonQualificationBudget()
    if not 0 < budget.max_wall_clock_minutes <= default_budget.max_wall_clock_minutes:
        issues.append("budget_wall_clock")
    if not (
        0
        < budget.max_active_compute_seconds
        <= default_budget.max_active_compute_seconds
    ):
        issues.append("budget_compute")
    if not 0 < budget.max_storage_delta_bytes <= default_budget.max_storage_delta_bytes:
        issues.append("budget_storage")
    if budget.max_connections not in range(1, 6):
        issues.append("budget_connections")
    if budget.max_parallel_requests != 1:
        issues.append("budget_parallel_requests")

    return list(dict.fromkeys(issues))


def sanitized_url_summary(value: str) -> dict[str, str | int | None]:
    try:
        url: URL = make_url(value)
    except (TypeError, ValueError):
        return {
            "driver": None,
            "host": None,
            "port": None,
            "database": None,
            "username_present": "false",
            "password_present": "false",
            "sslmode": None,
            "channel_binding": None,
        }
    return {
        "driver": url.drivername,
        "host": url.host,
        "port": url.port,
        "database": url.database,
        "username_present": str(bool(url.username)).lower(),
        "password_present": str(bool(url.password)).lower(),
        "sslmode": url.query.get("sslmode"),
        "channel_binding": url.query.get("channel_binding"),
    }


def approved_manifest_file_sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
