import re
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


def test_readme_discloses_that_graph_job_routes_are_not_public():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    normalized_readme = " ".join(readme.split())
    graph_job_paths = {
        path for path in app.openapi()["paths"] if "graph-job" in path
    }

    assert graph_job_paths == set()
    assert "PostgreSQL-backed graph-job routes and persistence" not in readme
    assert (
        "Public graph-job routes are intentionally not registered"
        in normalized_readme
    )


def test_readme_quick_start_documents_required_configuration():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    quick_start = readme.split("## Quick Start", maxsplit=1)[1].split(
        "## Documentation", maxsplit=1
    )[0]
    normalized_quick_start = quick_start.replace("`", "")

    assert ".env.example" in quick_start
    assert "DATABASE_URL is required" in normalized_quick_start
    assert (
        "MATERIALS_PROJECT_API_KEY is required only"
        in normalized_quick_start
    )
    assert "optional" in quick_start.lower()
    assert quick_start.index("DATABASE_URL") < quick_start.index(
        "alembic upgrade head"
    )


def test_deployment_guide_installs_reviewed_systemd_unit_before_startup():
    unit_path = PROJECT_ROOT / "materialgraph.service"
    deployment_path = PROJECT_ROOT / "docs/guide/DEPLOYMENT.md"
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    unit = unit_path.read_text(encoding="utf-8")
    deployment = deployment_path.read_text(encoding="utf-8")

    assert "WorkingDirectory=/opt/materialgraph" in unit
    assert "EnvironmentFile=/opt/materialgraph/.env" in unit
    assert "User=ubuntu" in unit
    assert "Group=ubuntu" in unit
    assert "--host 127.0.0.1 --port 8000" in unit
    assert "Restart=on-failure" in unit
    assert "DATABASE_URL=" not in unit
    assert "MATERIALS_PROJECT_API_KEY=" not in unit

    install_command = "sudo install -o root -g root -m 0644"
    assert deployment.index(install_command) < deployment.index(
        "sudo systemctl daemon-reload"
    )
    clone_command = (
        "git clone https://github.com/MaterialGraph/materialgraph.git "
        "/opt/materialgraph"
    )
    assert clone_command in deployment
    assert "cd /opt/materialgraph/materialgraph" not in deployment
    assert "docs/guide/DEPLOYMENT.md" in readme


def test_backup_units_are_persistent_bounded_and_do_not_embed_secrets():
    service = (PROJECT_ROOT / "materialgraph-backup.service").read_text(encoding="utf-8")
    timer = (PROJECT_ROOT / "materialgraph-backup.timer").read_text(encoding="utf-8")
    example = (PROJECT_ROOT / "materialgraph-backup.env.example").read_text(
        encoding="utf-8"
    )

    assert "EnvironmentFile=/etc/materialgraph/backup.env" in service
    assert "StateDirectory=materialgraph-backup" in service
    assert "StateDirectoryMode=0700" in service
    assert "UMask=0077" in service
    assert "TimeoutStartSec=30min" in service
    assert "NoNewPrivileges=true" in service
    assert "ProtectHome=tmpfs" in service
    assert "ProtectSystem=strict" in service
    assert "DATABASE_URL=" not in service
    assert "MATERIALGRAPH_BACKUP_BUCKET=" not in service
    assert "OnCalendar=*-*-* 02:15:00 UTC" in timer
    assert "RandomizedDelaySec=15min" in timer
    assert "Persistent=true" in timer
    assert "replace-with-private-backup-bucket" in example
    assert "DATABASE_" not in example


def test_independent_audit_closure_records_are_consistent():
    audit_root = PROJECT_ROOT / "docs/auditing/independent-audit"
    remediation_root = audit_root / "remediation"
    independent_register = (
        audit_root / "INDEPENDENT_AUDIT_REGISTER.md"
    ).read_text(encoding="utf-8")
    remediation_register = (
        remediation_root / "REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    closure = (audit_root / "FINAL_AUDIT_CLOSURE.md").read_text(
        encoding="utf-8"
    )

    confirmed_section = independent_register.split(
        "## Confirmed findings", maxsplit=1
    )[1].split("## Retired finding identifiers", maxsplit=1)[0]
    retired_section = independent_register.split(
        "## Retired finding identifiers", maxsplit=1
    )[1].split("## Open observations", maxsplit=1)[0]
    confirmed_rows = [
        line for line in confirmed_section.splitlines()
        if line.startswith("| `MG-IA-")
    ]
    retired_rows = [
        line for line in retired_section.splitlines()
        if line.startswith("| `MG-IA-")
    ]
    remediation_rows = [
        line for line in remediation_register.splitlines()
        if line.startswith("| `MG-IA-")
    ]

    assert len(confirmed_rows) == 21
    assert len(retired_rows) == 5
    assert len(remediation_rows) == 22
    assert sum("| Verified |" in row for row in remediation_rows) == 20
    assert sum(
        "| Not actionable |" in row for row in remediation_rows
    ) == 2
    assert not any("| Pending |" in row for row in remediation_rows)

    for row in remediation_rows:
        verification_path = re.findall(r"`([^`]+\.md)`", row)[-1]
        verification_file = remediation_root / verification_path

        assert verification_file.is_file()

        if "| Verified |" not in row:
            continue

        verification_record = verification_file.read_text(encoding="utf-8")
        status_section = verification_record.split(
            "## Status", maxsplit=1
        )[1].split("## ", maxsplit=1)[0]

        assert "verified" in status_section.lower()
        assert "pending" not in status_section.lower()

    assert "Actionable findings verified: **20 of 20**" in closure
    assert "Closure hardening: **1 (`MG-IA-022`)**" in closure


def test_root_readme_audit_status_and_local_links_are_current():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    local_targets = [
        target
        for target in re.findall(r"\]\(([^)]+)\)", readme)
        if "://" not in target and not target.startswith("#")
    ]

    assert "20 of 20 actionable findings verified" in readme
    assert "remediation in progress" not in readme.lower()
    assert "23 are resolved" not in readme
    assert "71 remain open" not in readme
    assert local_targets
    assert all((PROJECT_ROOT / target).exists() for target in local_targets)
