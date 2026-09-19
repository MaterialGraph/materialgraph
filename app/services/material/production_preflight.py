from dataclasses import dataclass

from app.services.material.production_rollout import (
    ProductionBaseline,
    ProductionResourceIdentity,
)


LIFECYCLE_TABLES = (
    "dataset_import_runs",
    "material_source_records",
    "material_source_memberships",
    "material_import_events",
)


@dataclass(frozen=True)
class ProductionConnectionObservation:
    database: str
    username: str
    transaction_read_only: str
    tls_in_use: bool


@dataclass(frozen=True)
class ProductionBaselineObservation:
    alembic_revision: str
    curated_records_sha256: str
    material_count: int
    element_count: int
    material_element_count: int
    sentinel_id: int
    sentinel_mp_id: str
    lifecycle_table_presence: dict[str, bool]


def evaluate_production_preflight_observations(
    *,
    target: ProductionResourceIdentity,
    baseline: ProductionBaseline,
    direct: ProductionConnectionObservation,
    pooled: ProductionConnectionObservation,
    observed: ProductionBaselineObservation,
) -> list[str]:
    issues: list[str] = []

    connection_expectations = (
        ("direct", direct, target.direct_role),
        ("pooled", pooled, target.pooled_role),
    )
    for label, observation, expected_role in connection_expectations:
        if observation.database != target.database_name:
            issues.append(f"{label}_database")
        if observation.username != expected_role:
            issues.append(f"{label}_role")
        if observation.transaction_read_only != "on":
            issues.append(f"{label}_transaction_read_only")
        if not observation.tls_in_use:
            issues.append(f"{label}_tls")

    if observed.alembic_revision != baseline.current_revision:
        issues.append("observed_alembic_revision")
    if observed.curated_records_sha256 != baseline.curated_records_sha256:
        issues.append("observed_curated_records_sha256")
    if observed.material_count != baseline.material_count:
        issues.append("observed_material_count")
    if observed.element_count != baseline.element_count:
        issues.append("observed_element_count")
    if observed.material_element_count != baseline.material_element_count:
        issues.append("observed_material_element_count")
    if observed.sentinel_id != baseline.sentinel_id:
        issues.append("observed_sentinel_id")
    if observed.sentinel_mp_id != baseline.sentinel_mp_id:
        issues.append("observed_sentinel_mp_id")

    if set(observed.lifecycle_table_presence) != set(LIFECYCLE_TABLES):
        issues.append("observed_lifecycle_table_set")
    elif any(observed.lifecycle_table_presence.values()):
        issues.append("observed_lifecycle_tables_already_present")

    return issues
