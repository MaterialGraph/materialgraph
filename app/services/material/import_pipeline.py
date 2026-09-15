from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID, uuid4

from app.services.material.project_service import (
    MaterialCandidate,
    MaterialFetchPage,
)

if TYPE_CHECKING:
    from app.services.material.import_service import (
        DatasetImportCompletion,
        DatasetImportRunSpec,
        MaterialRefreshResult,
    )


MANIFEST_SCHEMA_VERSION = 2
CHECKPOINT_SCHEMA_VERSION = 2
MATERIALS_PROJECT_LICENSE = "CC-BY-4.0"
MATERIALS_PROJECT_LICENSE_URL = (
    "https://creativecommons.org/licenses/by/4.0/"
)
NORMALIZATION_VERSION = "materials-project-summary-v1"
SELECTION_CONTRACT_VERSION = "materials-project-selection-v1"


class MaterialPageSource(Protocol):
    def fetch_materials_page(
        self,
        *,
        chemsys: str,
        page: int,
        page_size: int,
        stable_only: bool,
    ) -> MaterialFetchPage: ...


class MaterialBatchImporter(Protocol):
    def begin_import_run(
        self,
        *,
        spec: DatasetImportRunSpec,
        rejections: list[dict],
    ) -> None: ...

    def refresh_materials(
        self,
        candidates: list[MaterialCandidate],
        *,
        import_run_id: str,
    ) -> MaterialRefreshResult: ...

    def complete_import_run(
        self,
        *,
        import_run_id: str,
        manifest_source_ids: set[str],
        outcome_counts: dict[str, int],
        allow_retirement: bool,
    ) -> DatasetImportCompletion: ...

    def count_active_source_records(
        self,
        *,
        source: str,
        source_ids: set[str],
        selection_contract_version: str,
        selection_scope_sha256: str,
    ) -> int: ...


@dataclass(frozen=True)
class MaterialImportScope:
    chemical_systems: tuple[str, ...]
    page_size: int = 100
    chunk_size: int = 100
    max_materials: int = 1_000
    max_source_records: int = 2_000
    max_pages_per_system: int = 25
    max_fetch_attempts: int = 3
    stable_only: bool = True

    def __post_init__(self) -> None:
        normalized = tuple(
            sorted({value.strip() for value in self.chemical_systems if value.strip()})
        )
        if not normalized:
            raise ValueError("at least one chemical system is required")
        if len(normalized) > 100:
            raise ValueError("no more than 100 chemical systems are allowed")
        if any(
            re.fullmatch(r"[A-Z][a-z]?(?:-[A-Z][a-z]?)*", value) is None
            for value in normalized
        ):
            raise ValueError("chemical systems must contain hyphen-separated element symbols")
        if not 1 <= self.page_size <= 1_000:
            raise ValueError("page_size must be between 1 and 1000")
        if not 1 <= self.chunk_size <= 1_000:
            raise ValueError("chunk_size must be between 1 and 1000")
        if not 1 <= self.max_materials <= 10_000:
            raise ValueError("max_materials must be between 1 and 10000")
        if not self.max_materials <= self.max_source_records <= 20_000:
            raise ValueError(
                "max_source_records must be between max_materials and 20000"
            )
        if not 1 <= self.max_pages_per_system <= 1_000:
            raise ValueError("max_pages_per_system must be between 1 and 1000")
        if not 1 <= self.max_fetch_attempts <= 5:
            raise ValueError("max_fetch_attempts must be between 1 and 5")
        object.__setattr__(self, "chemical_systems", normalized)


@dataclass(frozen=True)
class MaterialDatasetContract:
    source_release: str
    retrieved_at: str
    normalization_version: str = NORMALIZATION_VERSION
    selection_contract_version: str = SELECTION_CONTRACT_VERSION
    license_identifier: str = MATERIALS_PROJECT_LICENSE
    license_url: str = MATERIALS_PROJECT_LICENSE_URL

    def __post_init__(self) -> None:
        values = {
            "source_release": (self.source_release, 100),
            "normalization_version": (self.normalization_version, 100),
            "selection_contract_version": (self.selection_contract_version, 100),
            "license_identifier": (self.license_identifier, 100),
            "license_url": (self.license_url, 500),
        }
        for name, (value, maximum) in values.items():
            if (
                not isinstance(value, str)
                or not value
                or value.strip() != value
                or len(value) > maximum
            ):
                raise ValueError(f"{name} is invalid")
        if not isinstance(self.retrieved_at, str):
            raise ValueError("retrieved_at must be an ISO-8601 timestamp")
        try:
            retrieved_at = datetime.fromisoformat(self.retrieved_at)
        except ValueError as error:
            raise ValueError("retrieved_at must be an ISO-8601 timestamp") from error
        if retrieved_at.tzinfo is None or retrieved_at.utcoffset() is None:
            raise ValueError("retrieved_at must include a timezone")
        if self.license_identifier != MATERIALS_PROJECT_LICENSE:
            raise ValueError("unsupported Materials Project license identifier")
        if self.license_url != MATERIALS_PROJECT_LICENSE_URL:
            raise ValueError("unsupported Materials Project license URL")


@dataclass(frozen=True)
class ManifestBuildResult:
    path: Path
    digest: str
    accepted: int
    rejected: int
    duplicate_source_ids: int
    pages_fetched: int


@dataclass(frozen=True)
class ManifestApplyResult:
    manifest_digest: str
    processed: int
    inserted: int
    updated: int
    unchanged: int
    conflicted: int
    rejected: int
    retired: int
    verified_present: int
    completed: bool

    @property
    def imported(self) -> int:
        """Compatibility count for newly inserted material rows."""
        return self.inserted

    @property
    def skipped(self) -> int:
        """Compatibility count for unchanged and conflicted rows."""
        return self.unchanged + self.conflicted


class MaterialImportPipeline:
    def __init__(
        self,
        source: MaterialPageSource,
        *,
        on_fetch_retry: Callable[[str, int, int], None] | None = None,
        retry_wait: Callable[[int], None] | None = None,
    ):
        self.source = source
        self.on_fetch_retry = on_fetch_retry
        self.retry_wait = retry_wait or self._default_retry_wait

    def build_manifest(
        self,
        *,
        scope: MaterialImportScope,
        dataset: MaterialDatasetContract,
        manifest_path: Path,
    ) -> ManifestBuildResult:
        candidates_by_id: dict[str, MaterialCandidate] = {}
        rejections: list[dict[str, Any]] = []
        duplicate_source_ids: set[str] = set()
        pages_fetched = 0
        source_records_seen = 0
        limit_reached = False

        for chemsys in scope.chemical_systems:
            page = 1
            while not limit_reached:
                if page > scope.max_pages_per_system:
                    raise ValueError(
                        f"source scope for {chemsys} exceeded max_pages_per_system"
                    )
                result = self._fetch_page_with_retry(
                    scope=scope,
                    chemsys=chemsys,
                    page=page,
                )
                pages_fetched += 1

                page_record_count = len(result.candidates) + len(result.rejections)
                if page_record_count > scope.page_size:
                    raise ValueError("source page exceeded the configured page_size")
                source_records_seen += page_record_count
                if source_records_seen > scope.max_source_records:
                    raise ValueError("source results exceeded max_source_records")

                rejections.extend(
                    {
                        "chemical_system": chemsys,
                        "page": page,
                        "source_id": rejected.source_id,
                        "reason": rejected.reason,
                    }
                    for rejected in result.rejections
                )

                for candidate in result.candidates:
                    if candidate.mp_id in candidates_by_id:
                        duplicate_source_ids.add(candidate.mp_id)
                        continue
                    candidates_by_id[candidate.mp_id] = candidate
                    if len(candidates_by_id) >= scope.max_materials:
                        limit_reached = True
                        break

                if page_record_count < scope.page_size:
                    break
                page += 1

        ordered_candidates = [
            self._candidate_to_dict(candidates_by_id[mp_id])
            for mp_id in sorted(candidates_by_id)
        ]
        ordered_rejections = sorted(
            rejections,
            key=lambda item: (
                item["chemical_system"] or "",
                item["page"],
                item["source_id"] or "",
            ),
        )
        if not ordered_candidates:
            raise ValueError("source traversal produced no accepted materials")
        payload: dict[str, Any] = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "source": "materials_project",
            "dataset": asdict(dataset),
            "scope": asdict(scope),
            "counts": {
                "accepted": len(ordered_candidates),
                "rejected": len(ordered_rejections),
                "duplicate_source_ids": len(duplicate_source_ids),
                "pages_fetched": pages_fetched,
                "source_records_seen": source_records_seen,
                "source_complete": not limit_reached,
            },
            "duplicate_source_ids": sorted(duplicate_source_ids),
            "rejections": ordered_rejections,
            "candidates": ordered_candidates,
        }
        digest = self._payload_digest(payload)
        document = {"manifest_sha256": digest, **payload}
        self._write_json_atomic(manifest_path, document)

        return ManifestBuildResult(
            path=manifest_path,
            digest=digest,
            accepted=len(ordered_candidates),
            rejected=len(ordered_rejections),
            duplicate_source_ids=len(duplicate_source_ids),
            pages_fetched=pages_fetched,
        )

    def _fetch_page_with_retry(
        self,
        *,
        scope: MaterialImportScope,
        chemsys: str,
        page: int,
    ) -> MaterialFetchPage:
        for attempt in range(1, scope.max_fetch_attempts + 1):
            try:
                return self.source.fetch_materials_page(
                    chemsys=chemsys,
                    page=page,
                    page_size=scope.page_size,
                    stable_only=scope.stable_only,
                )
            except Exception:
                if attempt == scope.max_fetch_attempts:
                    raise
                if self.on_fetch_retry is not None:
                    self.on_fetch_retry(chemsys, page, attempt)
                self.retry_wait(attempt)

        raise RuntimeError("unreachable fetch retry state")

    @staticmethod
    def _default_retry_wait(failed_attempt: int) -> None:
        time.sleep(min(2 ** (failed_attempt - 1), 4))

    @staticmethod
    def apply_manifest(
        *,
        manifest_path: Path,
        checkpoint_path: Path,
        importer: MaterialBatchImporter,
    ) -> ManifestApplyResult:
        manifest, digest = MaterialImportPipeline._load_manifest(manifest_path)
        from app.services.material.import_service import DatasetImportRunSpec

        candidates = [
            MaterialImportPipeline._candidate_from_dict(item)
            for item in manifest["candidates"]
        ]
        chunk_size = int(manifest["scope"]["chunk_size"])
        checkpoint = MaterialImportPipeline._load_checkpoint(
            checkpoint_path=checkpoint_path,
            manifest_digest=digest,
            candidate_count=len(candidates),
        )
        MaterialImportPipeline._write_json_atomic(checkpoint_path, checkpoint)
        dataset = manifest["dataset"]
        selection_scope_sha256 = MaterialImportPipeline._payload_digest(
            manifest["scope"]
        )
        importer.begin_import_run(
            spec=DatasetImportRunSpec(
                import_run_id=checkpoint["import_run_id"],
                source=manifest["source"],
                source_release=dataset["source_release"],
                retrieved_at=datetime.fromisoformat(dataset["retrieved_at"]),
                manifest_sha256=digest,
                normalization_version=dataset["normalization_version"],
                selection_contract_version=dataset["selection_contract_version"],
                selection_scope_sha256=selection_scope_sha256,
                license_identifier=dataset["license_identifier"],
                license_url=dataset["license_url"],
            ),
            rejections=manifest["rejections"],
        )

        while checkpoint["next_index"] < len(candidates):
            start = checkpoint["next_index"]
            chunk = candidates[start : start + chunk_size]
            result = importer.refresh_materials(
                chunk,
                import_run_id=checkpoint["import_run_id"],
            )
            MaterialImportPipeline._validate_batch_result(result, len(chunk))

            checkpoint["next_index"] += result.processed
            checkpoint["processed"] += result.processed
            checkpoint["inserted"] += result.inserted
            checkpoint["updated"] += result.updated
            checkpoint["unchanged"] += result.unchanged
            checkpoint["conflicted"] += result.conflicted
            checkpoint["completed"] = checkpoint["next_index"] == len(candidates)
            MaterialImportPipeline._write_json_atomic(checkpoint_path, checkpoint)

        manifest_mp_ids = {candidate.mp_id for candidate in candidates}
        accepted_without_conflict = len(candidates) - checkpoint["conflicted"]
        verified_present = importer.count_active_source_records(
            source=manifest["source"],
            source_ids=manifest_mp_ids,
            selection_contract_version=dataset["selection_contract_version"],
            selection_scope_sha256=selection_scope_sha256,
        )
        if verified_present != accepted_without_conflict:
            raise ValueError("database identities do not reconcile to the manifest")
        completion = importer.complete_import_run(
            import_run_id=checkpoint["import_run_id"],
            manifest_source_ids=manifest_mp_ids,
            outcome_counts={
                "inserted": checkpoint["inserted"],
                "updated": checkpoint["updated"],
                "unchanged": checkpoint["unchanged"],
                "conflicted": checkpoint["conflicted"],
                "rejected": len(manifest["rejections"]),
            },
            allow_retirement=bool(manifest["counts"]["source_complete"]),
        )

        return ManifestApplyResult(
            manifest_digest=digest,
            processed=checkpoint["processed"],
            inserted=checkpoint["inserted"],
            updated=checkpoint["updated"],
            unchanged=checkpoint["unchanged"],
            conflicted=checkpoint["conflicted"],
            rejected=len(manifest["rejections"]),
            retired=completion.retired,
            verified_present=verified_present,
            completed=checkpoint["completed"],
        )

    @staticmethod
    def _load_manifest(path: Path) -> tuple[dict[str, Any], str]:
        document = json.loads(path.read_text(encoding="utf-8"))
        digest = document.pop("manifest_sha256", None)
        if document.get("schema_version") != MANIFEST_SCHEMA_VERSION:
            raise ValueError("unsupported manifest schema version")
        if document.get("source") != "materials_project":
            raise ValueError("unsupported manifest source")
        MaterialDatasetContract(**document.get("dataset", {}))
        if (
            not isinstance(digest, str)
            or digest != MaterialImportPipeline._payload_digest(document)
        ):
            raise ValueError("manifest digest validation failed")
        if document["counts"]["accepted"] != len(document["candidates"]):
            raise ValueError("manifest accepted count does not reconcile")
        if document["counts"]["rejected"] != len(document["rejections"]):
            raise ValueError("manifest rejected count does not reconcile")
        if document["counts"]["duplicate_source_ids"] != len(
            document["duplicate_source_ids"]
        ):
            raise ValueError("manifest duplicate count does not reconcile")
        if not document["candidates"]:
            raise ValueError("manifest contains no accepted materials")
        if not isinstance(document["counts"].get("source_complete"), bool):
            raise ValueError("manifest source completion state is invalid")
        return document, digest

    @staticmethod
    def _load_checkpoint(
        *,
        checkpoint_path: Path,
        manifest_digest: str,
        candidate_count: int,
    ) -> dict[str, Any]:
        if not checkpoint_path.exists():
            return {
                "schema_version": CHECKPOINT_SCHEMA_VERSION,
                "manifest_sha256": manifest_digest,
                "import_run_id": str(uuid4()),
                "next_index": 0,
                "processed": 0,
                "inserted": 0,
                "updated": 0,
                "unchanged": 0,
                "conflicted": 0,
                "completed": candidate_count == 0,
            }

        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
            raise ValueError("unsupported checkpoint schema version")
        if checkpoint.get("manifest_sha256") != manifest_digest:
            raise ValueError("checkpoint does not match the manifest")
        try:
            import_run_id = checkpoint["import_run_id"]
            if str(UUID(import_run_id)) != import_run_id:
                raise ValueError
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("checkpoint import_run_id is invalid") from error
        next_index = checkpoint.get("next_index")
        if not isinstance(next_index, int) or not 0 <= next_index <= candidate_count:
            raise ValueError("checkpoint next_index is invalid")
        if checkpoint.get("processed") != next_index:
            raise ValueError("checkpoint processed count does not reconcile")
        outcome_total = sum(
            checkpoint.get(name, 0)
            for name in ("inserted", "updated", "unchanged", "conflicted")
        )
        if outcome_total != next_index:
            raise ValueError("checkpoint result counts do not reconcile")
        if checkpoint.get("completed") != (next_index == candidate_count):
            raise ValueError("checkpoint completion state does not reconcile")
        return checkpoint

    @staticmethod
    def _validate_batch_result(result: MaterialRefreshResult, expected: int) -> None:
        if result.processed != expected:
            raise ValueError("importer processed count does not match chunk size")
        if (
            result.inserted
            + result.updated
            + result.unchanged
            + result.conflicted
            != result.processed
        ):
            raise ValueError("importer result counts do not reconcile")

    @staticmethod
    def _candidate_to_dict(candidate: MaterialCandidate) -> dict[str, Any]:
        return asdict(candidate)

    @staticmethod
    def _candidate_from_dict(value: dict[str, Any]) -> MaterialCandidate:
        return MaterialCandidate(**value)

    @staticmethod
    def _payload_digest(payload: dict[str, Any]) -> str:
        canonical = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_name(f".{path.name}.tmp")
        serialized = json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        try:
            temporary_path.write_text(f"{serialized}\n", encoding="utf-8")
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, path)
        finally:
            temporary_path.unlink(missing_ok=True)
