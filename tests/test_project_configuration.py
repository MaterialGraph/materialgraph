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


def test_secret_scanners_are_immutable_and_locally_contained():
    workflow = (
        PROJECT_ROOT / ".github/workflows/secret-scan.yml"
    ).read_text(encoding="utf-8")
    hook = (PROJECT_ROOT / ".githooks/pre-commit").read_text(encoding="utf-8")
    policy = (PROJECT_ROOT / "docs/security/AUTOMATION_PINNING.md").read_text(
        encoding="utf-8"
    )
    digest = (
        "sha256:75bdb2b2f4db213cde0b8295f13a88d6b333091bbfbf3012a4e083d00d31caba"
    )

    assert "actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8" in workflow
    assert workflow.count(digest) == 1
    assert hook.count(digest) == 1
    assert '--volume "$PWD:/repo:ro"' in workflow
    assert '--volume "$(pwd):/repo:ro"' in hook
    assert "--network none" in workflow
    assert "--network none" in hook
    assert "python scripts/check_automation_pins.py" in workflow
    assert "full 40-character commit SHA" in policy
    assert "blocks the commit" in policy


def test_production_dependencies_are_locked_audited_and_reconcilable():
    workflow = (
        PROJECT_ROOT / ".github/workflows/dependency-security.yml"
    ).read_text(encoding="utf-8")
    production_input = (
        PROJECT_ROOT / "requirements-production.in"
    ).read_text(encoding="utf-8")
    production_lock = (
        PROJECT_ROOT / "requirements-production.lock"
    ).read_text(encoding="utf-8")
    audit_lock = (PROJECT_ROOT / "requirements-audit.lock").read_text(
        encoding="utf-8"
    )
    deployment = (PROJECT_ROOT / "docs/guide/DEPLOYMENT.md").read_text(
        encoding="utf-8"
    )
    policy = (PROJECT_ROOT / "docs/security/DEPENDENCY_MANAGEMENT.md").read_text(
        encoding="utf-8"
    )

    image = (
        "python:3.12.3-slim@sha256:"
        "fd3817f3a855f6c2ada16ac9468e5ee93e361005bd226fd5a5ee1a504e038c84"
    )
    assert image in workflow
    assert image in policy
    assert 'cron: "17 4 * * 1"' in workflow
    assert "--require-hashes" in workflow
    assert "python -m pip_audit --require-hashes -r" in workflow
    assert "--no-index" in workflow
    assert "--check-installed" in workflow
    assert "pip-audit==2.10.1" in audit_lock
    assert "pillow==12.3.0" in production_input
    assert "pydantic-settings==2.14.2" in production_input
    assert "starlette==1.3.1" in production_input
    assert production_lock.count("--hash=sha256:") > 2_000
    assert audit_lock.count("--hash=sha256:") > 300
    assert "requirements-production.lock" in deployment
    assert "requirements.txt` or" in deployment
    assert "time-bounded, identifier-specific exception" in policy


def test_dependency_security_docs_do_not_overstate_branch_enforcement():
    deployment = (PROJECT_ROOT / "docs/guide/DEPLOYMENT.md").read_text(
        encoding="utf-8"
    )
    policy = (PROJECT_ROOT / "docs/security/DEPENDENCY_MANAGEMENT.md").read_text(
        encoding="utf-8"
    )

    assert "automated audit, not a GitHub-enforced merge gate" in policy
    assert "A passing result proves only" in policy
    assert "Do not deploy when either run is" in deployment
    assert "This is a manual operator precondition" in deployment


def test_dataset_expansion_qualification_is_isolated_and_bounded():
    qualifier = (
        PROJECT_ROOT / "scripts/qualify_dataset_expansion.py"
    ).read_text(encoding="utf-8")
    generator = (
        PROJECT_ROOT / "scripts/generate_dataset_expansion_fixture.py"
    ).read_text(encoding="utf-8")
    reference = (
        PROJECT_ROOT / "scripts/capture_curated_dataset_reference.py"
    ).read_text(encoding="utf-8")
    plan = (
        PROJECT_ROOT
        / "docs/data/dataset-expansion/MG-DE_BENCHMARK_PLAN.md"
    ).read_text(encoding="utf-8")

    assert '"test" not in lowered or "mg_de_004" not in lowered' in qualifier
    assert 'engine.dialect.name != "postgresql"' in qualifier
    assert "1 <= args.warm_runs <= 5" in qualifier
    assert "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)" in qualifier
    assert "build_representative_fixture_manifest" in generator
    assert '"test" not in actual.lower()' in reference
    assert "No concurrency or load test is authorized" in plan
    assert "Do not perform a restore under this plan" in plan


def test_real_source_pilot_is_manifest_only_and_neon_safe():
    importer = (
        PROJECT_ROOT / "scripts/import_materials_project.py"
    ).read_text(encoding="utf-8")
    inspector = (
        PROJECT_ROOT / "scripts/inspect_materials_manifest.py"
    ).read_text(encoding="utf-8")
    release_reader = (
        PROJECT_ROOT / "scripts/read_materials_project_release.py"
    ).read_text(encoding="utf-8")
    plan = (
        PROJECT_ROOT
        / "docs/data/dataset-expansion/MG-DE_REAL_SOURCE_PILOT.md"
    ).read_text(encoding="utf-8")

    before_apply, apply_path = importer.split("if args.apply:", maxsplit=1)
    assert "from app.core.database import" not in before_apply
    assert "from app.core.database import" in apply_path
    assert "--apply" in plan
    assert "Do not add `--apply`" in plan
    assert "Production or Neon writes authorized:** No" in plan
    assert "--maximum-energy-above-hull 0.05" in plan
    assert "materials-project-selection-v3" in plan
    assert "app.core.database" not in inspector
    assert "MaterialsProjectService" not in inspector
    assert "MATERIALS_PROJECT_API_KEY" in release_reader
    assert "api_key" not in release_reader.split("print(", maxsplit=1)[1]


def test_real_source_pilot_closure_is_evidence_bounded():
    root = PROJECT_ROOT / "docs/data/dataset-expansion"
    report = (root / "MG-DE_QUALIFIED_MANIFEST_REPORT.md").read_text(
        encoding="utf-8"
    )
    finding = (root / "findings/MG-DE-005.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert "1,727" in report
    assert (
        "902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9"
        in report
    )
    assert (
        "7939dcfd0fab9a8e7e43f7395c59c874673ed19aaf49d1a942650a69595e3daa"
        in report
    )
    assert "Li-Fe-S" in report and "Na-Ni-S" in report
    assert "**Import authorized:** No" in report
    assert "**Status:** Closed" in finding
    assert "MG-DE-001 through MG-DE-006 closed" in readme


def test_scientific_cohort_review_is_offline_and_does_not_authorize_import():
    root = PROJECT_ROOT / "docs/data/dataset-expansion"
    script = (
        PROJECT_ROOT / "scripts/review_materials_scientific_cohort.py"
    ).read_text(encoding="utf-8")
    plan = (root / "MG-DE_SCIENTIFIC_COHORT_REVIEW.md").read_text(
        encoding="utf-8"
    )
    finding = (root / "findings/MG-DE-006.md").read_text(encoding="utf-8")

    assert "app.core.database" not in script
    assert "MaterialsProjectService" not in script
    assert '"database_import_authorized": False' in script
    assert "No universal numeric balance threshold is invented" in plan
    assert "Accept for disposable PostgreSQL qualification" in plan
    assert "It does not authorize Neon, production" in plan
    report = (root / "MG-DE_SCIENTIFIC_COHORT_REPORT.md").read_text(
        encoding="utf-8"
    )
    assert "**Status:** Closed" in finding
    assert "Accept for disposable PostgreSQL qualification" in report
    assert (
        "1897c042a4884700ec52c222542840c1c1654033dc39b739c9c407fa21829740"
        in report
    )
    assert "Neon or production import authorized:** No" in report
    assert "largest formula groups contain 70 and 73" in report


def test_real_data_qualification_is_exact_isolated_and_neon_safe():
    root = PROJECT_ROOT / "docs/data/dataset-expansion"
    qualifier = (
        PROJECT_ROOT / "scripts/qualify_real_dataset_expansion.py"
    ).read_text(encoding="utf-8")
    capture = (
        PROJECT_ROOT / "scripts/capture_curated_database_state.py"
    ).read_text(encoding="utf-8")
    plan = (root / "MG-DE_REAL_DATA_QUALIFICATION.md").read_text(
        encoding="utf-8"
    )
    finding = (root / "findings/MG-DE-007.md").read_text(encoding="utf-8")

    assert '"mg_de_007" not in lowered' in qualifier
    assert 'engine.dialect.name != "postgresql"' in qualifier
    assert "APPROVED_MANIFEST_SHA256" in qualifier
    assert "evaluate_curated_preservation" in qualifier
    assert "evaluate_collision_event" in qualifier
    assert "summarize_formula_crowding" in qualifier
    assert "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)" in qualifier
    assert '"mg_de_007" not in lowered' in capture
    assert "CURATED_MATERIAL_COUNT" in capture
    assert "No concurrency or load test is authorized" in plan
    assert "Do not perform a restore under this plan" in plan
    assert "Neon or production writes authorized:** No" in plan
    assert "mp-19017" in plan
    assert "**Status:** In progress" in finding


def test_request_timeout_hierarchy_is_bounded_and_documented():
    nginx = (PROJECT_ROOT / "materialgraph.nginx").read_text(encoding="utf-8")
    deployment = (PROJECT_ROOT / "docs/guide/DEPLOYMENT.md").read_text(
        encoding="utf-8"
    )

    assert Settings.model_fields["database_pool_timeout_seconds"].default == 3
    assert Settings.model_fields["database_lock_timeout_ms"].default == 3_000
    assert (
        Settings.model_fields["database_statement_timeout_ms"].default
        == 15_000
    )
    assert (
        Settings.model_fields["expensive_request_timeout_seconds"].default
        == 20
    )
    assert nginx.count("proxy_connect_timeout 3s;") == 3
    assert nginx.count("proxy_send_timeout 10s;") == 3
    assert nginx.count("proxy_read_timeout 25s;") == 2
    assert nginx.count("proxy_read_timeout 20s;") == 1
    assert "database statement < application deadline" in deployment
    assert "compatible with the Neon pooled endpoint" in deployment
    assert "Database dependency failures explicitly roll back" in deployment
    assert "admission slot remains occupied" in deployment


def test_stage_one_request_timeout_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (
        security_root / "STAGE_1_FINDINGS_REGISTER.md"
    ).read_text(encoding="utf-8")
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-002.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-002.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-002.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-002`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-002` |")
    )
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]

    assert finding_row.endswith("| Verified |")
    assert "| 2 | Verified |" in remediation_row
    assert "Verified on 2026-09-13" in finding
    assert "Neon rejected those options" in change_impact
    assert "Python cannot safely terminate a running worker thread" in change_impact
    assert "All twenty acceptance criteria passed" in verification
    assert len(acceptance_rows) == 20
    assert "15.251 seconds" in verification
    assert "returned structured `504` in 0.051 seconds" in verification
    assert "Complete parsed JSON matched baseline" in verification
    assert "4869e39edb97c5c8c48c63b1819bb692f02f57b3" in verification


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


def test_material_import_documentation_is_manifest_first_and_test_safe():
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    getting_started = (
        PROJECT_ROOT / "docs/guide/getting_started.md"
    ).read_text(encoding="utf-8")
    script = (
        PROJECT_ROOT / "scripts/import_materials_project.py"
    ).read_text(encoding="utf-8")

    assert "python -m scripts.import_materials_project" in readme
    assert "--manifest ./materials-manifest.json" in readme
    assert "--source-release" in readme
    assert "--retrieved-at" in readme
    assert "--checkpoint ./materials-checkpoint.json" in getting_started
    assert "--expected-database-name materialgraph_test" in getting_started
    assert "--allow-non-test-database" in getting_started
    assert "--expected-database-name" in script
    assert "--source-release" in script
    assert "--retrieved-at" in script
    assert "refusing to apply to a non-test database" in script


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


def test_journal_limits_and_monitoring_are_repository_controlled():
    unit = (PROJECT_ROOT / "materialgraph.service").read_text(encoding="utf-8")
    journal = (PROJECT_ROOT / "materialgraph-journald.conf").read_text(
        encoding="utf-8"
    )
    monitor = (
        PROJECT_ROOT / "materialgraph-journal-monitor.service"
    ).read_text(encoding="utf-8")
    timer = (PROJECT_ROOT / "materialgraph-journal-monitor.timer").read_text(
        encoding="utf-8"
    )
    deployment = (PROJECT_ROOT / "docs/guide/DEPLOYMENT.md").read_text(
        encoding="utf-8"
    )

    assert "LogRateLimitIntervalSec=30s" in unit
    assert "LogRateLimitBurst=200" in unit
    assert "SystemMaxUse=256M" in journal
    assert "SystemKeepFree=1G" in journal
    assert "MaxRetentionSec=14day" in journal
    assert "RateLimitIntervalSec=30s" in journal
    assert "RateLimitBurst=1000" in journal
    assert "scripts/check_journal_usage.py" in monitor
    assert "OnCalendar=*-*-* 03:00:00 UTC" in timer
    assert "journal use reaches 230 MiB" in deployment
    assert "root-filesystem use reaches 80%" in deployment


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
    assert "Pydantic independently attempted to" in verification
    assert "Verified on 2026-09-12" in finding


def test_public_https_configuration_is_bounded_and_reproducible():
    nginx = (PROJECT_ROOT / "materialgraph.nginx").read_text(encoding="utf-8")
    deployment = (PROJECT_ROOT / "docs/guide/DEPLOYMENT.md").read_text(
        encoding="utf-8"
    )

    assert "listen 443 ssl;" in nginx
    assert "server_name materialgraph.org www.materialgraph.org;" in nginx
    assert "return 301 https://$host$request_uri;" in nginx
    assert 'Strict-Transport-Security "max-age=31536000" always' in nginx
    assert "includeSubDomains" not in nginx
    assert "preload" not in nginx
    assert "server_tokens off;" in nginx
    assert "proxy_pass http://127.0.0.1:8000;" in nginx
    assert "ssl_certificate /etc/letsencrypt/live/materialgraph.org/" in nginx
    assert "privkey.pem" in nginx
    assert "BEGIN PRIVATE KEY" not in nginx

    assert "python3-certbot-nginx" in deployment
    assert "sudo certbot renew --dry-run" in deployment
    assert "/opt/materialgraph/materialgraph.nginx" in deployment
    assert "https://materialgraph.org/health" in deployment


def test_public_expensive_request_controls_are_repository_controlled():
    nginx = (PROJECT_ROOT / "materialgraph.nginx").read_text(encoding="utf-8")
    application = (PROJECT_ROOT / "app/main.py").read_text(encoding="utf-8")
    admission = (PROJECT_ROOT / "app/core/admission_control.py").read_text(
        encoding="utf-8"
    )
    deployment = (PROJECT_ROOT / "docs/guide/DEPLOYMENT.md").read_text(
        encoding="utf-8"
    )

    assert "limit_req_zone $binary_remote_addr" in nginx
    assert "rate=2r/s" in nginx
    assert (
        "limit_conn_zone $binary_remote_addr zone=materialgraph_client:10m;"
        in nginx
    )
    assert "limit_conn_zone $server_name zone=materialgraph_site:10m;" in nginx
    assert nginx.count(
        "limit_req zone=materialgraph_expensive burst=4 nodelay;"
    ) == 2
    assert nginx.count("limit_conn materialgraph_client 2;") == 2
    assert nginx.count("limit_conn materialgraph_site 20;") == 3
    assert "limit_req_status 429" in nginx
    assert "limit_conn_status 429" in nginx
    assert "$proxy_add_x_forwarded_for" not in nginx
    assert nginx.count("proxy_set_header X-Forwarded-For $remote_addr;") == 3
    assert "ExpensiveRequestAdmissionMiddleware" in application
    assert "expensive_request_capacity_exceeded" in admission
    assert 'headers={"Retry-After": "1"}' in admission
    assert '"/health"' not in admission
    assert "DNS-only" in deployment
    assert "HTTP `429`" in deployment
    assert "structured HTTP `503`" in deployment


def test_stage_one_public_https_remediation_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (security_root / "STAGE_1_FINDINGS_REGISTER.md").read_text(
        encoding="utf-8"
    )
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-005.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-005.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-005.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-005`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-005` |")
    )
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]

    assert finding_row.endswith("| Verified |")
    assert "| 1 | Verified |" in remediation_row
    assert "Verified on 2026-09-12" in finding
    assert "Completed and verified on 2026-09-12" in change_impact
    assert "All sixteen acceptance criteria passed" in verification
    assert len(acceptance_rows) == 16
    assert "602538d5d439a90230a67ea0425fc376a54972b9" in verification
    assert "TLS 1.0 and 1.1" in verification
    assert "simulated renewal" in verification
    assert "complete parsed pre-change JSON exactly" in verification


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


def test_stage_one_objective_bounds_are_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (
        security_root / "STAGE_1_FINDINGS_REGISTER.md"
    ).read_text(encoding="utf-8")
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-008.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-008.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-008.md"
    ).read_text(encoding="utf-8")
    nginx = (PROJECT_ROOT / "materialgraph.nginx").read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-008`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-008` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 2 | Verified |" in remediation_row
    assert "Verified on 2026-09-13" in finding
    assert "32 entries" in change_impact
    assert "All twenty acceptance criteria passed" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 20
    assert "96d7f577c08c3bfb439b94bfbabc3f4d6a437f4d" in verification
    assert "2.076870 seconds" in verification
    assert "complete parsed chain response" in verification
    assert "client_max_body_size 32k;" in nginx


def test_stage_one_screening_logging_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (
        security_root / "STAGE_1_FINDINGS_REGISTER.md"
    ).read_text(encoding="utf-8")
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-009.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-009.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-009.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-009`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-009` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 2 | Verified |" in remediation_row
    assert "Verified on 2026-09-13" in finding
    assert "count-only application logs" in change_impact.lower()
    assert "All twenty acceptance criteria passed" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 20
    assert "34bb5e44ffaab4afcbe00aa71f3ac053486ee561" in verification
    assert "complete parsed pre-change JSON" in verification
    assert "largest measured completion entry was 255" in verification
    assert "does not misstate `200` as a strict observed ceiling" in verification
    normalized_verification = " ".join(verification.split())
    assert (
        "fell from 191.1 MiB before policy activation to 48.0 MiB afterward"
        in normalized_verification
    )


def test_stage_one_public_admission_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (
        security_root / "STAGE_1_FINDINGS_REGISTER.md"
    ).read_text(encoding="utf-8")
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-001.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-001.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-001.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-001`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-001` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 2 | Verified |" in remediation_row
    assert "Verified on 2026-09-13" in finding
    assert "two requests per second" in change_impact
    assert "All twenty acceptance criteria passed" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 20
    assert "8a1d2b8b5608cad41a7dba6ceb280dc22ada719b" in verification
    assert "seven proxy rejections (`429`)" in verification
    assert "expensive_request_capacity_exceeded" in verification
    assert "Retry-After: 1" in verification
    assert "matched their pre-change production captures exactly" in verification


def test_stage_one_automation_pinning_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (
        security_root / "STAGE_1_FINDINGS_REGISTER.md"
    ).read_text(encoding="utf-8")
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-011.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-011.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-011.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-011`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-011` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 3 | Verified |" in remediation_row
    assert "Verified on 2026-09-13" in finding
    assert "Reverting to mutable references is not an approved rollback" in (
        change_impact
    )
    assert "All eighteen acceptance criteria passed" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 18
    assert "2c43193c0a31f355f0658afeeb97cf12266e0f1c" in verification
    assert "full-history scan of 269 commits" in verification
    assert "produced a redacted finding" in verification
    assert "exit code 127" in verification
    assert "run 86 attempt 2 succeeded" in verification
    assert (
        "immutable references rather than a publisher allowlist" in verification
    )


def test_stage_one_dependency_security_is_verified_consistently():
    security_root = PROJECT_ROOT / "docs/security/stage-1-review"
    findings_register = (
        security_root / "STAGE_1_FINDINGS_REGISTER.md"
    ).read_text(encoding="utf-8")
    remediation_register = (
        security_root / "remediation/REMEDIATION_REGISTER.md"
    ).read_text(encoding="utf-8")
    finding = (security_root / "findings/MG-SEC-010.md").read_text(
        encoding="utf-8"
    )
    change_impact = (
        security_root / "remediation/change-impact/MG-SEC-010.md"
    ).read_text(encoding="utf-8")
    verification = (
        security_root / "remediation/verification/MG-SEC-010.md"
    ).read_text(encoding="utf-8")

    finding_row = next(
        line
        for line in findings_register.splitlines()
        if line.startswith("| [`MG-SEC-010`]")
    )
    remediation_row = next(
        line
        for line in remediation_register.splitlines()
        if line.startswith("| `MG-SEC-010` |")
    )

    assert finding_row.endswith("| Verified |")
    assert "| 3 | Verified |" in remediation_row
    assert "Verified on 2026-09-13" in finding
    assert "Hash enforcement rejects" in change_impact
    assert "All twenty acceptance criteria passed" in verification
    acceptance_rows = [
        line
        for line in verification.splitlines()
        if line.startswith("| ") and line.endswith("| Pass |")
    ]
    assert len(acceptance_rows) == 20
    assert "d06b8259d52fab65f31d7039448e44d05742f508" in verification
    assert "17 unique vulnerabilities" in verification
    assert "zero known vulnerabilities" in verification
    assert "matched the respective pre-change captures" in verification
    assert "stable `.venv` symlink" in verification


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
