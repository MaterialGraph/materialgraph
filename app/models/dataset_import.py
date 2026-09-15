from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DatasetImportRun(Base):
    __tablename__ = "dataset_import_runs"
    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'completed', 'completed_with_conflicts')",
            name="ck_dataset_import_run_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    source_release: Mapped[str] = mapped_column(String(100))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    manifest_sha256: Mapped[str] = mapped_column(String(64), index=True)
    normalization_version: Mapped[str] = mapped_column(String(100))
    selection_contract_version: Mapped[str] = mapped_column(String(100))
    selection_scope_sha256: Mapped[str] = mapped_column(String(64), index=True)
    license_identifier: Mapped[str] = mapped_column(String(100))
    license_url: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="running")
    outcome_counts: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class MaterialSourceRecord(Base):
    __tablename__ = "material_source_records"
    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_material_source_identity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE"), index=True
    )
    source: Mapped[str] = mapped_column(String(100), index=True)
    source_id: Mapped[str] = mapped_column(String(100), index=True)
    source_release: Mapped[str] = mapped_column(String(100))
    source_record_sha256: Mapped[str] = mapped_column(String(64))
    normalized_record_sha256: Mapped[str] = mapped_column(String(64))
    normalization_version: Mapped[str] = mapped_column(String(100))
    selection_contract_version: Mapped[str] = mapped_column(String(100))
    selection_scope_sha256: Mapped[str] = mapped_column(String(64), index=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latest_import_run_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_import_runs.id"), index=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class MaterialSourceMembership(Base):
    __tablename__ = "material_source_memberships"
    __table_args__ = (
        UniqueConstraint(
            "source_record_id",
            "selection_contract_version",
            "selection_scope_sha256",
            name="uq_material_source_scope_membership",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source_record_id: Mapped[int] = mapped_column(
        ForeignKey("material_source_records.id", ondelete="CASCADE"), index=True
    )
    selection_contract_version: Mapped[str] = mapped_column(String(100))
    selection_scope_sha256: Mapped[str] = mapped_column(String(64), index=True)
    latest_import_run_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_import_runs.id"), index=True
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)


class MaterialImportEvent(Base):
    __tablename__ = "material_import_events"
    __table_args__ = (
        UniqueConstraint(
            "import_run_id",
            "event_key",
            name="uq_material_import_run_event",
        ),
        CheckConstraint(
            "outcome IN ('inserted', 'updated', 'unchanged', 'conflicted', "
            "'rejected', 'retired')",
            name="ck_material_import_event_outcome",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    import_run_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_import_runs.id", ondelete="CASCADE"), index=True
    )
    event_key: Mapped[str] = mapped_column(String(150))
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    material_id: Mapped[int | None] = mapped_column(
        ForeignKey("materials.id", ondelete="SET NULL"), nullable=True, index=True
    )
    outcome: Mapped[str] = mapped_column(String(20), index=True)
    source_record_sha256: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    normalized_record_sha256: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
