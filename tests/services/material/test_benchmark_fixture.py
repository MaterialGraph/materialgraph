import json

from app.services.material.benchmark_fixture import (
    FIXTURE_CHEMICAL_SYSTEMS,
    FIXTURE_ID_PREFIX,
    FIXTURE_SCHEMA_VERSION,
    FIXTURE_SEED,
    FIXTURE_SOURCE_RELEASE,
    build_representative_fixture_manifest,
)
from app.services.material.import_pipeline import (
    MaterialImportPipeline,
    SYNTHETIC_BENCHMARK_LICENSE,
    SYNTHETIC_BENCHMARK_SOURCE,
)


def test_representative_fixture_is_deterministic_and_complete(tmp_path):
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    first = build_representative_fixture_manifest(manifest_path=first_path)
    second = build_representative_fixture_manifest(manifest_path=second_path)

    assert first.digest == second.digest
    assert first_path.read_bytes() == second_path.read_bytes()
    assert first.accepted == 1_000
    assert first.rejected > 0
    assert first.duplicate_source_ids > 0

    validated_manifest, validated_digest = MaterialImportPipeline._load_manifest(
        first_path
    )
    assert validated_digest == first.digest
    assert validated_manifest["counts"]["accepted"] == 1_000

    manifest = json.loads(first_path.read_text(encoding="utf-8"))
    assert manifest["counts"]["source_complete"] is True
    assert manifest["source"] == SYNTHETIC_BENCHMARK_SOURCE
    assert manifest["dataset"]["source"] == SYNTHETIC_BENCHMARK_SOURCE
    assert manifest["dataset"]["source_release"] == FIXTURE_SOURCE_RELEASE
    assert manifest["dataset"]["license_identifier"] == (
        SYNTHETIC_BENCHMARK_LICENSE
    )
    assert tuple(manifest["scope"]["chemical_systems"]) == tuple(
        sorted(FIXTURE_CHEMICAL_SYSTEMS)
    )

    candidates = manifest["candidates"]
    source_ids = [candidate["mp_id"] for candidate in candidates]
    assert len(source_ids) == len(set(source_ids)) == 1_000
    assert all(source_id.startswith(FIXTURE_ID_PREFIX) for source_id in source_ids)

    cohorts = {candidate["raw_data"]["cohort"] for candidate in candidates}
    assert cohorts == {
        "dense_oxide",
        "dense_phosphate",
        "missing_optional",
        "polymorph",
        "sparse",
    }
    assert all(
        candidate["raw_data"]["fixture_schema_version"]
        == FIXTURE_SCHEMA_VERSION
        for candidate in candidates
    )
    assert all(
        candidate["raw_data"]["fixture_seed"] == FIXTURE_SEED
        for candidate in candidates
    )
    assert any(candidate["band_gap"] is None for candidate in candidates)
    assert any(candidate["density"] is None for candidate in candidates)
    assert any(candidate["is_stable"] for candidate in candidates)
    assert any(not candidate["is_stable"] for candidate in candidates)


def test_small_fixture_handles_empty_chemical_system_streams(tmp_path):
    result = build_representative_fixture_manifest(
        manifest_path=tmp_path / "small.json",
        target_materials=3,
        chunk_size=2,
    )

    assert result.accepted == 3
