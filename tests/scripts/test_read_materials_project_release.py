import json

import pytest

from scripts import read_materials_project_release


def test_release_reader_prints_only_release(monkeypatch, capsys):
    monkeypatch.setenv("MATERIALGRAPH_ENV_FILE", "")
    monkeypatch.setenv("MATERIALS_PROJECT_API_KEY", "secret-test-key")

    class FakeService:
        def __init__(self, api_key):
            assert api_key == "secret-test-key"

        def get_database_version(self):
            return "2026_09_01"

    monkeypatch.setattr(
        read_materials_project_release,
        "MaterialsProjectService",
        FakeService,
    )

    assert read_materials_project_release.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "source_release": "2026_09_01"
    }


def test_release_reader_requires_key(monkeypatch):
    monkeypatch.setenv("MATERIALGRAPH_ENV_FILE", "")
    monkeypatch.delenv("MATERIALS_PROJECT_API_KEY", raising=False)

    with pytest.raises(ValueError, match="MATERIALS_PROJECT_API_KEY"):
        read_materials_project_release.main()
