from pathlib import Path

import pytest

from scripts import import_materials_project


def test_build_mode_refuses_to_overwrite_manifest(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("existing", encoding="utf-8")

    with pytest.raises(ValueError, match="refusing to overwrite"):
        import_materials_project.main(["--manifest", str(manifest)])


def test_apply_mode_requires_checkpoint(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="--checkpoint is required"):
        import_materials_project.main(
            ["--manifest", str(manifest), "--apply"]
        )


def test_apply_mode_requires_exact_database_confirmation(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="--expected-database-name is required"):
        import_materials_project.main(
            [
                "--manifest",
                str(manifest),
                "--checkpoint",
                str(tmp_path / "checkpoint.json"),
                "--apply",
            ]
        )


def test_build_mode_requires_source_api_key(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("MATERIALS_PROJECT_API_KEY", raising=False)
    monkeypatch.setenv("MATERIALGRAPH_ENV_FILE", "")

    with pytest.raises(ValueError, match="MATERIALS_PROJECT_API_KEY"):
        import_materials_project.main(
            ["--manifest", str(tmp_path / "manifest.json")]
        )
