from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

from app.services.material.project_service import (
    MaterialCandidate,
    MaterialFetchPage,
)

if TYPE_CHECKING:
    from app.services.material.import_service import MaterialImportResult


MANIFEST_SCHEMA_VERSION = 1
CHECKPOINT_SCHEMA_VERSION = 1


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
    def import_materials_with_result(
        self,
        candidates: list[MaterialCandidate],
    ) -> MaterialImportResult: ...

    def count_existing_materials(self, mp_ids: set[str]) -> int: ...


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
    imported: int
    skipped: int
    verified_present: int
    completed: bool


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
        payload: dict[str, Any] = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "source": "materials_project",
            "scope": asdict(scope),
            "counts": {
                "accepted": len(ordered_candidates),
                "rejected": len(ordered_rejections),
                "duplicate_source_ids": len(duplicate_source_ids),
                "pages_fetched": pages_fetched,
                "source_records_seen": source_records_seen,
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

        while checkpoint["next_index"] < len(candidates):
            start = checkpoint["next_index"]
            chunk = candidates[start : start + chunk_size]
            result = importer.import_materials_with_result(chunk)
            MaterialImportPipeline._validate_batch_result(result, len(chunk))

            checkpoint["next_index"] += result.processed
            checkpoint["processed"] += result.processed
            checkpoint["imported"] += result.imported
            checkpoint["skipped"] += result.skipped
            checkpoint["completed"] = checkpoint["next_index"] == len(candidates)
            MaterialImportPipeline._write_json_atomic(checkpoint_path, checkpoint)

        manifest_mp_ids = {candidate.mp_id for candidate in candidates}
        verified_present = importer.count_existing_materials(manifest_mp_ids)
        if verified_present != len(candidates):
            raise ValueError("database identities do not reconcile to the manifest")

        return ManifestApplyResult(
            manifest_digest=digest,
            processed=checkpoint["processed"],
            imported=checkpoint["imported"],
            skipped=checkpoint["skipped"],
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
                "next_index": 0,
                "processed": 0,
                "imported": 0,
                "skipped": 0,
                "completed": candidate_count == 0,
            }

        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("schema_version") != CHECKPOINT_SCHEMA_VERSION:
            raise ValueError("unsupported checkpoint schema version")
        if checkpoint.get("manifest_sha256") != manifest_digest:
            raise ValueError("checkpoint does not match the manifest")
        next_index = checkpoint.get("next_index")
        if not isinstance(next_index, int) or not 0 <= next_index <= candidate_count:
            raise ValueError("checkpoint next_index is invalid")
        if checkpoint.get("processed") != next_index:
            raise ValueError("checkpoint processed count does not reconcile")
        if checkpoint.get("imported", 0) + checkpoint.get("skipped", 0) != next_index:
            raise ValueError("checkpoint result counts do not reconcile")
        if checkpoint.get("completed") != (next_index == candidate_count):
            raise ValueError("checkpoint completion state does not reconcile")
        return checkpoint

    @staticmethod
    def _validate_batch_result(result: MaterialImportResult, expected: int) -> None:
        if result.processed != expected:
            raise ValueError("importer processed count does not match chunk size")
        if result.imported + result.skipped != result.processed:
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
