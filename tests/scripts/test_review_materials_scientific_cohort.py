import json
from pathlib import Path

import pytest

from scripts.review_materials_scientific_cohort import main
from tests.services.material.test_material_manifest_inspection import (
    candidate,
    write_manifest,
)


def test_review_cli_fails_closed_for_an_unexpected_manifest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    manifest = tmp_path / "manifest.json"
    output = tmp_path / "review.json"
    write_manifest(
        manifest,
        [candidate("mp-1", formula="LiFeO2", elements=["Li", "Fe", "O"])],
    )

    assert main(["--manifest", str(manifest), "--output", str(output)]) == 2

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["ready_for_scientific_decision"] is False
    assert report["database_import_authorized"] is False
    assert "manifest_sha256" in capsys.readouterr().out


def test_review_cli_refuses_to_overwrite(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    output = tmp_path / "review.json"
    write_manifest(
        manifest,
        [candidate("mp-1", formula="LiFeO2", elements=["Li", "Fe", "O"])],
    )
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(ValueError, match="refusing to overwrite"):
        main(["--manifest", str(manifest), "--output", str(output)])
