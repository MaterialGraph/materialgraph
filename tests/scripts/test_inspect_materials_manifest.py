import json

import pytest

from app.services.material.manifest_inspection import (
    ManifestInspection,
    PropertyCoverage,
)
from app.services.material.pilot_contract import MG_DE_005_CHEMICAL_SYSTEMS
from scripts import inspect_materials_manifest


def inspection() -> ManifestInspection:
    coverage = {
        name: PropertyCoverage(present=750, missing=250, fraction=0.75)
        for name in (
            "band_gap",
            "energy_above_hull",
            "formation_energy_per_atom",
            "density",
        )
    }
    return ManifestInspection(
        manifest_sha256="a" * 64,
        source="materials_project",
        source_release="test-release",
        retrieved_at="2026-09-17T00:00:00+00:00",
        selection_contract_version="materials-project-selection-v3",
        normalization_version="materials-project-summary-v1",
        license_identifier="CC-BY-4.0",
        accepted=1_000,
        rejected=0,
        duplicate_source_ids=0,
        pages_fetched=10,
        source_records_seen=1_000,
        source_complete=True,
        chemical_systems=tuple(sorted(MG_DE_005_CHEMICAL_SYSTEMS)),
        stable_only=False,
        maximum_energy_above_hull=0.05,
        stable=1_000,
        unstable=0,
        unique_formulas=900,
        polymorph_formulas=50,
        polymorph_materials=150,
        element_counts={
            "Fe": 300,
            "Li": 300,
            "Mg": 100,
            "Mn": 200,
            "Na": 300,
            "O": 1_000,
            "P": 200,
        },
        chemical_system_counts={"Fe-Li-O-P": 200},
        rejection_reason_counts={},
        property_coverage=coverage,
    )


def test_cli_writes_report_and_returns_success(tmp_path, monkeypatch, capsys):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    output = tmp_path / "inspection.json"
    monkeypatch.setattr(
        inspect_materials_manifest,
        "inspect_material_manifest",
        lambda _path: inspection(),
    )

    result = inspect_materials_manifest.main(
        [
            "--manifest",
            str(manifest),
            "--output",
            str(output),
            "--minimum-property-coverage",
            "0.7",
            "--required-element",
            "Li",
            "--require-source-complete",
        ]
    )

    assert result == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["qualified"] is True
    assert report["gate_failures"] == []
    assert json.loads(capsys.readouterr().out)["qualified"] is True


def test_cli_returns_two_when_a_gate_fails(tmp_path, monkeypatch):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        inspect_materials_manifest,
        "inspect_material_manifest",
        lambda _path: inspection(),
    )

    result = inspect_materials_manifest.main(
        [
            "--manifest",
            str(manifest),
            "--required-element",
            "Co",
            "--minimum-property-coverage",
            "0.8",
        ]
    )

    assert result == 2


def test_cli_refuses_to_overwrite_report(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    output = tmp_path / "inspection.json"
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(ValueError, match="refusing to overwrite"):
        inspect_materials_manifest.main(
            ["--manifest", str(manifest), "--output", str(output)]
        )
