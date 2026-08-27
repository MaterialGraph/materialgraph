from importlib import metadata
from pathlib import Path

from app.core.config import Settings
from app.main import app
from app.version import PROJECT_VERSION, UNKNOWN_VERSION, get_project_version


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_requirements_do_not_install_another_materialgraph_checkout():
    requirements = (PROJECT_ROOT / "requirements.txt").read_text(
        encoding="utf-8"
    )

    assert "#egg=materialgraph" not in requirements.lower()
    assert "materialgraph.git" not in requirements.lower()


def test_materials_project_environment_key_matches_settings_and_docs():
    env_example = (PROJECT_ROOT / ".env.example").read_text(
        encoding="utf-8"
    )
    getting_started_files = list(
        (PROJECT_ROOT / "docs").rglob("getting_started.md")
    )

    assert len(getting_started_files) == 1

    getting_started = getting_started_files[0].read_text(
        encoding="utf-8"
    )

    assert "materials_project_api_key" in Settings.model_fields
    assert "MATERIALS_PROJECT_API_KEY=" in env_example
    assert "MATERIALS_PROJECT_API_KEY=" in getting_started
    assert "MP_API_KEY=" not in getting_started


def test_every_advertised_environment_key_maps_to_settings_field():
    env_example = (PROJECT_ROOT / ".env.example").read_text(
        encoding="utf-8"
    )
    advertised_keys = {
        line.partition("=")[0].strip().lower()
        for line in env_example.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert advertised_keys <= set(Settings.model_fields)
    assert "MP_API_URL=" not in env_example


def test_runtime_version_uses_installed_package_metadata(monkeypatch):
    monkeypatch.setattr(
        metadata,
        "version",
        lambda distribution_name: "9.8.7",
    )

    assert get_project_version() == "9.8.7"


def test_runtime_version_has_non_release_fallback(monkeypatch):
    def missing_distribution(distribution_name):
        raise metadata.PackageNotFoundError(distribution_name)

    monkeypatch.setattr(metadata, "version", missing_distribution)

    assert get_project_version() == UNKNOWN_VERSION
    assert UNKNOWN_VERSION == "0+unknown"


def test_fastapi_uses_resolved_package_version():
    assert "project_version" not in Settings.model_fields
    assert app.version == PROJECT_VERSION