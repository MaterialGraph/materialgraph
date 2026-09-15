import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.services.material.import_pipeline import (
    MaterialImportPipeline,
    MaterialImportScope,
)
from app.services.material.import_service import (
    MaterialImportResult,
    MaterialImportService,
)
from app.services.material.project_service import (
    MaterialCandidate,
    MaterialCandidateRejection,
    MaterialFetchPage,
)


def make_candidate(mp_id: str) -> MaterialCandidate:
    return MaterialCandidate(
        mp_id=mp_id,
        formula="LiO",
        pretty_formula="LiO",
        elements=["Li", "O"],
        band_gap=1.0,
        energy_above_hull=0.0,
        formation_energy_per_atom=-1.0,
        density=2.0,
        is_stable=True,
        raw_data={"material_id": mp_id},
        composition_fractions={"Li": 0.5, "O": 0.5},
    )


class FakeSource:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def fetch_materials_page(self, **kwargs) -> MaterialFetchPage:
        self.calls.append(kwargs)
        key = (kwargs["chemsys"], kwargs["page"])
        value = self.pages.get(key, MaterialFetchPage([], []))
        if isinstance(value, Exception):
            raise value
        return value


class FakeImporter:
    def __init__(
        self,
        fail_on_call: int | None = None,
        present: set[str] | None = None,
    ):
        self.fail_on_call = fail_on_call
        self.present = present if present is not None else set()
        self.calls: list[list[str]] = []

    def import_materials_with_result(self, candidates):
        self.calls.append([candidate.mp_id for candidate in candidates])
        if len(self.calls) == self.fail_on_call:
            raise RuntimeError("controlled chunk failure")
        self.present.update(candidate.mp_id for candidate in candidates)
        return MaterialImportResult(
            processed=len(candidates),
            imported=len(candidates),
            skipped=0,
        )

    def count_existing_materials(self, mp_ids):
        return len(mp_ids & self.present)


def build_manifest(tmp_path: Path, *, chunk_size: int = 2) -> Path:
    source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-3"), make_candidate("mp-1")],
                rejections=[],
            ),
            ("Li-O", 2): MaterialFetchPage(
                candidates=[make_candidate("mp-2")],
                rejections=[],
            ),
        }
    )
    path = tmp_path / "manifest.json"
    MaterialImportPipeline(source).build_manifest(
        scope=MaterialImportScope(
            chemical_systems=("Li-O",),
            page_size=2,
            chunk_size=chunk_size,
        ),
        manifest_path=path,
    )
    return path


def test_scope_is_normalized_and_bounded():
    scope = MaterialImportScope(
        chemical_systems=(" Na-O ", "Li-O", "Na-O"),
        page_size=25,
        chunk_size=10,
        max_materials=100,
    )

    assert scope.chemical_systems == ("Li-O", "Na-O")

    with pytest.raises(ValueError, match="page_size"):
        MaterialImportScope(chemical_systems=("Li-O",), page_size=0)

    with pytest.raises(ValueError, match="hyphen-separated element symbols"):
        MaterialImportScope(chemical_systems=("not-a-system",))


def test_build_manifest_paginates_deduplicates_and_records_rejections(tmp_path):
    source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-2")],
                rejections=[
                    MaterialCandidateRejection(
                        source_id="mp-invalid",
                        reason="normalization_error",
                    )
                ],
            ),
            ("Li-O", 2): MaterialFetchPage(
                candidates=[make_candidate("mp-1")],
                rejections=[],
            ),
            ("Na-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-2")],
                rejections=[],
            ),
        }
    )
    path = tmp_path / "manifest.json"

    result = MaterialImportPipeline(source).build_manifest(
        scope=MaterialImportScope(
            chemical_systems=("Na-O", "Li-O"),
            page_size=2,
            max_materials=10,
        ),
        manifest_path=path,
    )
    document = json.loads(path.read_text(encoding="utf-8"))

    assert result.accepted == 2
    assert result.rejected == 1
    assert result.duplicate_source_ids == 1
    assert result.pages_fetched == 3
    assert [item["mp_id"] for item in document["candidates"]] == ["mp-1", "mp-2"]
    assert document["duplicate_source_ids"] == ["mp-2"]
    assert document["rejections"] == [
        {
            "chemical_system": "Li-O",
            "page": 1,
            "reason": "normalization_error",
            "source_id": "mp-invalid",
        }
    ]


def test_manifest_is_byte_deterministic_for_equivalent_source_order(tmp_path):
    first_source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-2"), make_candidate("mp-1")],
                rejections=[],
            )
        }
    )
    second_source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-1"), make_candidate("mp-2")],
                rejections=[],
            )
        }
    )
    scope = MaterialImportScope(chemical_systems=("Li-O",), page_size=3)
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    first = MaterialImportPipeline(first_source).build_manifest(
        scope=scope,
        manifest_path=first_path,
    )
    second = MaterialImportPipeline(second_source).build_manifest(
        scope=scope,
        manifest_path=second_path,
    )

    assert first.digest == second.digest
    assert first_path.read_bytes() == second_path.read_bytes()


def test_build_manifest_retries_a_page_with_a_fixed_bound(tmp_path):
    class RetryingSource:
        def __init__(self):
            self.attempts = 0

        def fetch_materials_page(self, **_kwargs):
            self.attempts += 1
            if self.attempts < 3:
                raise RuntimeError("temporary source failure")
            return MaterialFetchPage([], [])

    source = RetryingSource()
    retries = []
    pipeline = MaterialImportPipeline(
        source,
        on_fetch_retry=lambda chemsys, page, attempt: retries.append(
            (chemsys, page, attempt)
        ),
        retry_wait=lambda _attempt: None,
    )

    pipeline.build_manifest(
        scope=MaterialImportScope(
            chemical_systems=("Li-O",),
            max_fetch_attempts=3,
        ),
        manifest_path=tmp_path / "manifest.json",
    )

    assert source.attempts == 3
    assert retries == [("Li-O", 1, 1), ("Li-O", 1, 2)]


def test_build_manifest_fails_closed_at_page_bound(tmp_path):
    source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-1")],
                rejections=[],
            )
        }
    )

    with pytest.raises(ValueError, match="exceeded max_pages_per_system"):
        MaterialImportPipeline(source).build_manifest(
            scope=MaterialImportScope(
                chemical_systems=("Li-O",),
                page_size=1,
                max_materials=10,
                max_pages_per_system=1,
            ),
            manifest_path=tmp_path / "manifest.json",
        )

    assert not (tmp_path / "manifest.json").exists()


def test_build_manifest_fails_closed_at_source_record_bound(tmp_path):
    source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-1"), make_candidate("mp-2")],
                rejections=[],
            )
        }
    )

    with pytest.raises(ValueError, match="exceeded max_source_records"):
        MaterialImportPipeline(source).build_manifest(
            scope=MaterialImportScope(
                chemical_systems=("Li-O",),
                page_size=2,
                max_materials=1,
                max_source_records=1,
            ),
            manifest_path=tmp_path / "manifest.json",
        )


def test_apply_manifest_checkpoints_each_committed_chunk_and_resumes(tmp_path):
    manifest_path = build_manifest(tmp_path)
    checkpoint_path = tmp_path / "checkpoint.json"
    present: set[str] = set()
    failing_importer = FakeImporter(fail_on_call=2, present=present)

    with pytest.raises(RuntimeError, match="controlled chunk failure"):
        MaterialImportPipeline.apply_manifest(
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
            importer=failing_importer,
        )

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["next_index"] == 2
    assert failing_importer.calls == [["mp-1", "mp-2"], ["mp-3"]]

    resumed_importer = FakeImporter(present=present)
    result = MaterialImportPipeline.apply_manifest(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        importer=resumed_importer,
    )

    assert resumed_importer.calls == [["mp-3"]]
    assert result.completed is True
    assert result.processed == 3
    assert result.imported == 3
    assert result.skipped == 0
    assert result.verified_present == 3


def test_postgresql_manifest_lifecycle_interrupts_resumes_and_reruns(
    db_session,
    tmp_path,
):
    prefix = f"mp-test-lifecycle-{uuid4()}"
    candidates = [
        make_candidate(f"{prefix}-{suffix}")
        for suffix in ("a", "b", "c")
    ]
    source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=candidates[:2],
                rejections=[],
            ),
            ("Li-O", 2): MaterialFetchPage(
                candidates=candidates[2:],
                rejections=[],
            ),
        }
    )
    manifest_path = tmp_path / "postgres-manifest.json"
    checkpoint_path = tmp_path / "postgres-checkpoint.json"
    MaterialImportPipeline(source).build_manifest(
        scope=MaterialImportScope(
            chemical_systems=("Li-O",),
            page_size=2,
            chunk_size=2,
        ),
        manifest_path=manifest_path,
    )

    delegate = MaterialImportService(db_session)

    class InterruptBeforeSecondChunk:
        def __init__(self):
            self.calls = 0

        def import_materials_with_result(self, chunk):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("controlled PostgreSQL lifecycle interruption")
            return delegate.import_materials_with_result(chunk)

        def count_existing_materials(self, mp_ids):
            return delegate.count_existing_materials(mp_ids)

    with pytest.raises(
        RuntimeError,
        match="controlled PostgreSQL lifecycle interruption",
    ):
        MaterialImportPipeline.apply_manifest(
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
            importer=InterruptBeforeSecondChunk(),
        )

    all_mp_ids = {candidate.mp_id for candidate in candidates}
    first_chunk_mp_ids = {candidate.mp_id for candidate in candidates[:2]}
    interrupted_checkpoint = json.loads(
        checkpoint_path.read_text(encoding="utf-8")
    )
    assert interrupted_checkpoint["next_index"] == 2
    assert delegate.count_existing_materials(first_chunk_mp_ids) == 2
    assert delegate.count_existing_materials(all_mp_ids) == 2

    resumed = MaterialImportPipeline.apply_manifest(
        manifest_path=manifest_path,
        checkpoint_path=checkpoint_path,
        importer=delegate,
    )
    assert resumed.completed is True
    assert resumed.processed == 3
    assert resumed.imported == 3
    assert resumed.skipped == 0
    assert resumed.verified_present == 3
    assert delegate.count_existing_materials(all_mp_ids) == 3

    clean_rerun = MaterialImportPipeline.apply_manifest(
        manifest_path=manifest_path,
        checkpoint_path=tmp_path / "postgres-rerun-checkpoint.json",
        importer=delegate,
    )
    assert clean_rerun.completed is True
    assert clean_rerun.processed == 3
    assert clean_rerun.imported == 0
    assert clean_rerun.skipped == 3
    assert clean_rerun.verified_present == 3
    assert delegate.count_existing_materials(all_mp_ids) == 3


def test_apply_manifest_rejects_tampering(tmp_path):
    manifest_path = build_manifest(tmp_path)
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    document["candidates"][0]["formula"] = "changed"
    manifest_path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="digest validation failed"):
        MaterialImportPipeline.apply_manifest(
            manifest_path=manifest_path,
            checkpoint_path=tmp_path / "checkpoint.json",
            importer=FakeImporter(),
        )


def test_apply_manifest_fails_if_database_does_not_reconcile(tmp_path):
    manifest_path = build_manifest(tmp_path)

    class NonPersistingImporter(FakeImporter):
        def count_existing_materials(self, _mp_ids):
            return 0

    with pytest.raises(ValueError, match="database identities do not reconcile"):
        MaterialImportPipeline.apply_manifest(
            manifest_path=manifest_path,
            checkpoint_path=tmp_path / "checkpoint.json",
            importer=NonPersistingImporter(),
        )


def test_apply_manifest_rejects_checkpoint_for_another_manifest(tmp_path):
    manifest_path = build_manifest(tmp_path)
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "manifest_sha256": "wrong",
                "next_index": 0,
                "processed": 0,
                "imported": 0,
                "skipped": 0,
                "completed": False,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="does not match"):
        MaterialImportPipeline.apply_manifest(
            manifest_path=manifest_path,
            checkpoint_path=checkpoint_path,
            importer=FakeImporter(),
        )
