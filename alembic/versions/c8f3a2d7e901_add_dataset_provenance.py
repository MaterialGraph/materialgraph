"""add dataset provenance

Revision ID: c8f3a2d7e901
Revises: 7a4c2e91b6d8
Create Date: 2026-09-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c8f3a2d7e901"
down_revision: Union[str, Sequence[str], None] = "7a4c2e91b6d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_import_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_release", sa.String(length=100), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("manifest_sha256", sa.String(length=64), nullable=False),
        sa.Column("normalization_version", sa.String(length=100), nullable=False),
        sa.Column(
            "selection_contract_version", sa.String(length=100), nullable=False
        ),
        sa.Column("selection_scope_sha256", sa.String(length=64), nullable=False),
        sa.Column("license_identifier", sa.String(length=100), nullable=False),
        sa.Column("license_url", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("outcome_counts", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('running', 'completed', 'completed_with_conflicts')",
            name="ck_dataset_import_run_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_dataset_import_runs_manifest_sha256"),
        "dataset_import_runs",
        ["manifest_sha256"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dataset_import_runs_selection_scope_sha256"),
        "dataset_import_runs",
        ["selection_scope_sha256"],
        unique=False,
    )
    op.create_index(
        op.f("ix_dataset_import_runs_source"),
        "dataset_import_runs",
        ["source"],
        unique=False,
    )
    op.create_table(
        "material_source_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("material_id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=False),
        sa.Column("source_release", sa.String(length=100), nullable=False),
        sa.Column("source_record_sha256", sa.String(length=64), nullable=False),
        sa.Column("normalized_record_sha256", sa.String(length=64), nullable=False),
        sa.Column("normalization_version", sa.String(length=100), nullable=False),
        sa.Column(
            "selection_contract_version", sa.String(length=100), nullable=False
        ),
        sa.Column("selection_scope_sha256", sa.String(length=64), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latest_import_run_id", sa.String(length=36), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["latest_import_run_id"], ["dataset_import_runs.id"]
        ),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source", "source_id", name="uq_material_source_identity"
        ),
    )
    for column in (
        "active",
        "latest_import_run_id",
        "material_id",
        "selection_scope_sha256",
        "source",
        "source_id",
    ):
        op.create_index(
            op.f(f"ix_material_source_records_{column}"),
            "material_source_records",
            [column],
            unique=False,
        )
    op.create_table(
        "material_source_memberships",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_record_id", sa.Integer(), nullable=False),
        sa.Column(
            "selection_contract_version", sa.String(length=100), nullable=False
        ),
        sa.Column("selection_scope_sha256", sa.String(length=64), nullable=False),
        sa.Column("latest_import_run_id", sa.String(length=36), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["latest_import_run_id"], ["dataset_import_runs.id"]
        ),
        sa.ForeignKeyConstraint(
            ["source_record_id"],
            ["material_source_records.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_record_id",
            "selection_contract_version",
            "selection_scope_sha256",
            name="uq_material_source_scope_membership",
        ),
    )
    for column in (
        "active",
        "latest_import_run_id",
        "selection_scope_sha256",
        "source_record_id",
    ):
        op.create_index(
            op.f(f"ix_material_source_memberships_{column}"),
            "material_source_memberships",
            [column],
            unique=False,
        )
    op.create_table(
        "material_import_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("import_run_id", sa.String(length=36), nullable=False),
        sa.Column("event_key", sa.String(length=150), nullable=False),
        sa.Column("source_id", sa.String(length=100), nullable=True),
        sa.Column("material_id", sa.Integer(), nullable=True),
        sa.Column("outcome", sa.String(length=20), nullable=False),
        sa.Column("source_record_sha256", sa.String(length=64), nullable=True),
        sa.Column("normalized_record_sha256", sa.String(length=64), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["import_run_id"], ["dataset_import_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["material_id"], ["materials.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "outcome IN ('inserted', 'updated', 'unchanged', 'conflicted', "
            "'rejected', 'retired')",
            name="ck_material_import_event_outcome",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "import_run_id", "event_key", name="uq_material_import_run_event"
        ),
    )
    for column in ("import_run_id", "material_id", "outcome"):
        op.create_index(
            op.f(f"ix_material_import_events_{column}"),
            "material_import_events",
            [column],
            unique=False,
        )


def downgrade() -> None:
    for column in ("outcome", "material_id", "import_run_id"):
        op.drop_index(
            op.f(f"ix_material_import_events_{column}"),
            table_name="material_import_events",
        )
    op.drop_table("material_import_events")
    for column in (
        "source_record_id",
        "selection_scope_sha256",
        "latest_import_run_id",
        "active",
    ):
        op.drop_index(
            op.f(f"ix_material_source_memberships_{column}"),
            table_name="material_source_memberships",
        )
    op.drop_table("material_source_memberships")
    for column in (
        "source_id",
        "source",
        "selection_scope_sha256",
        "material_id",
        "latest_import_run_id",
        "active",
    ):
        op.drop_index(
            op.f(f"ix_material_source_records_{column}"),
            table_name="material_source_records",
        )
    op.drop_table("material_source_records")
    op.drop_index(
        op.f("ix_dataset_import_runs_source"), table_name="dataset_import_runs"
    )
    op.drop_index(
        op.f("ix_dataset_import_runs_selection_scope_sha256"),
        table_name="dataset_import_runs",
    )
    op.drop_index(
        op.f("ix_dataset_import_runs_manifest_sha256"),
        table_name="dataset_import_runs",
    )
    op.drop_table("dataset_import_runs")
