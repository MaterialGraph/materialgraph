import re
from importlib import metadata
from pathlib import Path

from app.core.config import Settings, resolve_settings_env_file
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


def test_settings_dotenv_source_can_be_disabled_after_systemd_loads_it():
    assert resolve_settings_env_file({}) == ".env"
    assert resolve_settings_env_file({"MATERIALGRAPH_ENV_FILE": ""}) is None
    assert (
        resolve_settings_env_file(
            {"MATERIALGRAPH_ENV_FILE": "/etc/materialgraph/runtime.env"}
        )
        == "/etc/materialgraph/runtime.env"
    )


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
    assert "EnvironmentFile=/etc/materialgraph/runtime.env" in unit
    assert "Environment=MATERIALGRAPH_ENV_FILE=" in unit
    assert "User=materialgraph" in unit
    assert "Group=materialgraph" in unit
    assert "NoNewPrivileges=true" in unit
    assert "PrivateDevices=true" in unit
    assert "PrivateTmp=true" in unit
    assert "ProtectControlGroups=true" in unit
    assert "ProtectHome=true" in unit
    assert "ProtectKernelModules=true" in unit
    assert "ProtectKernelTunables=true" in unit
    assert "ProtectSystem=strict" in unit
    assert "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6" in unit
    assert "RestrictSUIDSGID=true" in unit
    assert "CapabilityBoundingSet=" in unit
    assert "AmbientCapabilities=" in unit
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


def test_stage_one_runtime_identity_remediation_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (security_root / "STAGE_1_FINDINGS_REGISTER.md").read_text(
        encoding="utf-8"
    )
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-004.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-004.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-004.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-004`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-004` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 1 | Verified |" in remediation_row
    assert "Completed and verified on 2026-09-12" in change_impact
    assert "passwordless sudo and belongs to `lxd`" in change_impact
    assert "Verified on 2026-09-12" in verification
    assert "All nineteen acceptance criteria passed" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 19
    assert "b2747f67fcdf78568891525e66814b5de2adfb83" in verification
    normalized_verification = " ".join(verification.split())
    assert (
        "Parsed material, screening, and discovery JSON responses matched "
        "the pre-change captures exactly."
        in normalized_verification
    )
    assert "Pydantic attempted a duplicate" in verification
    assert "Verified on 2026-09-12" in finding


def test_backup_units_are_persistent_bounded_and_do_not_embed_secrets():
    service = (PROJECT_ROOT / "materialgraph-backup.service").read_text(encoding="utf-8")
    timer = (PROJECT_ROOT / "materialgraph-backup.timer").read_text(encoding="utf-8")
    backup_script = (PROJECT_ROOT / "scripts/backup_database.py").read_text(
        encoding="utf-8"
    )
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
    assert (
        "MATERIALGRAPH_BACKUP_DATABASE_URL="
        "replace-with-dedicated-backup-role-url"
    ) in example
    assert (
        'required_setting("MATERIALGRAPH_BACKUP_DATABASE_URL")'
        in backup_script
    )
    assert "DATABASE_MIGRATION_URL" not in backup_script
    assert "dotenv_values" not in backup_script


def test_stage_one_recovery_verification_records_are_consistent():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (security_root / "STAGE_1_FINDINGS_REGISTER.md").read_text(
        encoding="utf-8"
    )
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-012.md").read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-012.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-012`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-012` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 0 | Verified |" in remediation_row
    assert "Verified on 2026-09-06" in finding
    assert "All twelve acceptance criteria passed" in verification
    assert "exactly, including material and formula ordering" in verification


def test_stage_one_database_transport_revalidation_is_consistent():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (security_root / "STAGE_1_FINDINGS_REGISTER.md").read_text(
        encoding="utf-8"
    )
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-006.md").read_text(
        encoding="utf-8"
    )
    verification = (
        security_root / "remediation/verification/MG-SEC-006.md"
    ).read_text(encoding="utf-8")

    confirmed_section = findings_register.split(
        "## Confirmed findings", maxsplit=1
    )[1].split("## Retired finding identifiers", maxsplit=1)[0]
    retired_section = findings_register.split(
        "## Retired finding identifiers", maxsplit=1
    )[1].split("## Review rule", maxsplit=1)[0]
    confirmed_rows = [
        line for line in confirmed_section.splitlines()
        if line.startswith("| [`MG-SEC-")
    ]
    retired_rows = [
        line for line in retired_section.splitlines()
        if line.startswith("| [`MG-SEC-")
    ]

    assert len(confirmed_rows) == 11
    assert len(retired_rows) == 1
    assert "[`MG-SEC-006`]" not in confirmed_section
    assert "[`MG-SEC-006`]" in retired_section
    assert "| `MG-SEC-006` | 1 | Retired |" in remediation_register
    assert "Retired after deployment revalidation" in finding
    normalized_verification = " ".join(verification.split())
    assert "The original finding was not supported" in normalized_verification
    assert "`sslmode=verify-full`" in verification
    assert "`channel_binding=require` was retained" in verification


def test_stage_one_database_privilege_remediation_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (security_root / "STAGE_1_FINDINGS_REGISTER.md").read_text(
        encoding="utf-8"
    )
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-007.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-007.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-007.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-007`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-007` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 1 | Verified |" in remediation_row
    assert "Verified on 2026-09-06" in finding
    assert "No paid Neon feature" in change_impact
    assert "SQL, not the Neon" in change_impact
    assert "All twenty acceptance criteria passed" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 20
    assert "`4cdfa87649d93e4f1c8040a94bf76328ea673a7e`" in verification
    assert (
        "Both restricted roles retain PostgreSQL's default database `TEMP`"
        in verification
    )
    assert "Complete parsed JSON for a material read" in verification
    assert "screening request, and discovery" in verification


def test_stage_one_environment_file_remediation_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (security_root / "STAGE_1_FINDINGS_REGISTER.md").read_text(
        encoding="utf-8"
    )
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-003.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-003.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-003.md"
    ).read_text(encoding="utf-8")
    unit = (PROJECT_ROOT / "materialgraph.service").read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-003`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-003` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 1 | Verified |" in remediation_row
    assert "Verified on 2026-09-10" in finding
    assert "No paid service" in change_impact
    assert "MG-SEC-004" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 13
    assert "All thirteen acceptance criteria passed" in verification
    assert "GitHub Secret Scan run 66 completed successfully" in verification
    assert "cb8e3b711b74ec0f7fe1158e7b2f6f18d03309f3" in verification
    assert "ExecStartPre=" in unit
    assert "scripts/verify_secret_file.py --owner-uid 0 --mode 0640" in unit
    assert "/etc/materialgraph/runtime.env" in unit


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
