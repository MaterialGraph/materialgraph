import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.services.material.import_pipeline import (
    MaterialDatasetContract,
    MaterialImportPipeline,
    MaterialImportScope,
    SYNTHETIC_BENCHMARK_LICENSE,
    SYNTHETIC_BENCHMARK_LICENSE_URL,
    SYNTHETIC_BENCHMARK_SOURCE,
)
from app.services.material.import_service import (
    DatasetImportCompletion,
    MaterialRefreshResult,
    MaterialImportService,
)
from app.services.material.project_service import (
    MaterialCandidate,
    MaterialCandidateRejection,
    MaterialFetchPage,
)


TEST_DATASET = MaterialDatasetContract(
    source_release="test-release-2026-09-15",
    retrieved_at="2026-09-15T00:00:00+00:00",
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

    def begin_import_run(self, *, spec, rejections):
        self.spec = spec
        self.rejections = rejections

    def refresh_materials(self, candidates, *, import_run_id):
        assert import_run_id == self.spec.import_run_id
        self.calls.append([candidate.mp_id for candidate in candidates])
        if len(self.calls) == self.fail_on_call:
            raise RuntimeError("controlled chunk failure")
        previously_present = sum(
            candidate.mp_id in self.present for candidate in candidates
        )
        self.present.update(candidate.mp_id for candidate in candidates)
        return MaterialRefreshResult(
            processed=len(candidates),
            inserted=len(candidates) - previously_present,
            updated=0,
            unchanged=previously_present,
            conflicted=0,
        )

    def count_active_source_records(self, *, source, source_ids, **_scope):
        assert source == "materials_project"
        return len(source_ids & self.present)

    def complete_import_run(
        self,
        *,
        import_run_id,
        manifest_source_ids,
        outcome_counts,
        allow_retirement,
    ):
        assert import_run_id == self.spec.import_run_id
        assert manifest_source_ids == self.present
        assert sum(outcome_counts.values()) == len(self.present) + len(self.rejections)
        assert isinstance(allow_retirement, bool)
        self.allow_retirement = allow_retirement
        return DatasetImportCompletion(retired=0)


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
        dataset=TEST_DATASET,
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

    with pytest.raises(ValueError, match="maximum_energy_above_hull"):
        MaterialImportScope(
            chemical_systems=("Li-O",),
            maximum_energy_above_hull=0.1,
        )

    with pytest.raises(ValueError, match="hyphen-separated element symbols"):
        MaterialImportScope(chemical_systems=("not-a-system",))


def test_dataset_contract_requires_timezone_and_matching_source_license():
    with pytest.raises(ValueError, match="include a timezone"):
        MaterialDatasetContract(
            source_release="test-release",
            retrieved_at="2026-09-15T00:00:00",
        )

    with pytest.raises(ValueError, match="source and license"):
        MaterialDatasetContract(
            source_release="test-release",
            retrieved_at="2026-09-15T00:00:00+00:00",
            license_identifier="unknown",
        )

    synthetic = MaterialDatasetContract(
        source_release="mg-de-004-fixture-v1",
        retrieved_at="2026-09-16T00:00:00+00:00",
        normalization_version="mg-de-004-synthetic-v1",
        selection_contract_version="mg-de-004-selection-v1",
        license_identifier=SYNTHETIC_BENCHMARK_LICENSE,
        license_url=SYNTHETIC_BENCHMARK_LICENSE_URL,
        source=SYNTHETIC_BENCHMARK_SOURCE,
    )

    assert synthetic.source == SYNTHETIC_BENCHMARK_SOURCE


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
        dataset=TEST_DATASET,
        manifest_path=path,
    )
    document = json.loads(path.read_text(encoding="utf-8"))

    assert result.accepted == 2
    assert result.rejected == 1
    assert result.duplicate_source_ids == 1
    assert result.pages_fetched == 3
    assert document["dataset"] == {
        "license_identifier": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "normalization_version": "materials-project-summary-v1",
        "retrieved_at": "2026-09-15T00:00:00+00:00",
        "selection_contract_version": "materials-project-selection-v3",
        "source": "materials_project",
        "source_release": "test-release-2026-09-15",
    }
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
        dataset=TEST_DATASET,
        manifest_path=first_path,
    )
    second = MaterialImportPipeline(second_source).build_manifest(
        scope=scope,
        dataset=TEST_DATASET,
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
            return MaterialFetchPage([make_candidate("mp-retry")], [])

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
        dataset=TEST_DATASET,
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
            dataset=TEST_DATASET,
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
            dataset=TEST_DATASET,
            manifest_path=tmp_path / "manifest.json",
        )


def test_build_manifest_rejects_an_empty_source_scope(tmp_path):
    with pytest.raises(ValueError, match="no accepted materials"):
        MaterialImportPipeline(FakeSource({})).build_manifest(
            scope=MaterialImportScope(chemical_systems=("Li-O",)),
            dataset=TEST_DATASET,
            manifest_path=tmp_path / "manifest.json",
        )


def test_truncated_manifest_cannot_infer_retirement(tmp_path):
    source = FakeSource(
        {
            ("Li-O", 1): MaterialFetchPage(
                candidates=[make_candidate("mp-1"), make_candidate("mp-2")],
                rejections=[],
            )
        }
    )
    manifest_path = tmp_path / "manifest.json"
    MaterialImportPipeline(source).build_manifest(
        scope=MaterialImportScope(
            chemical_systems=("Li-O",),
            page_size=2,
            max_materials=1,
            max_source_records=2,
        ),
        dataset=TEST_DATASET,
        manifest_path=manifest_path,
    )
    importer = FakeImporter()

    result = MaterialImportPipeline.apply_manifest(
        manifest_path=manifest_path,
        checkpoint_path=tmp_path / "checkpoint.json",
        importer=importer,
    )

    assert result.inserted == 1
    assert importer.allow_retirement is False


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
    prefix = f"mp-tl-{uuid4().hex[:16]}"
    candidates = [
        make_candidate(f"{prefix}-{suffix}")
        for suffix in ("a", "b", "c")
    ]
    assert all(len(candidate.mp_id) <= 50 for candidate in candidates)
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
        dataset=TEST_DATASET,
        manifest_path=manifest_path,
    )

    delegate = MaterialImportService(db_session)

    class InterruptBeforeSecondChunk:
        def __init__(self):
            self.calls = 0

        def begin_import_run(self, **kwargs):
            return delegate.begin_import_run(**kwargs)

        def refresh_materials(self, chunk, *, import_run_id):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("controlled PostgreSQL lifecycle interruption")
            return delegate.refresh_materials(
                chunk,
                import_run_id=import_run_id,
            )

        def count_active_source_records(self, **kwargs):
            return delegate.count_active_source_records(**kwargs)

        def complete_import_run(self, **kwargs):
            return delegate.complete_import_run(**kwargs)

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
        def count_active_source_records(self, **_kwargs):
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
                "schema_version": 2,
                "manifest_sha256": "wrong",
                "import_run_id": str(uuid4()),
                "next_index": 0,
                "processed": 0,
                "inserted": 0,
                "updated": 0,
                "unchanged": 0,
                "conflicted": 0,
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
