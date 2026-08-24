# Root File Inventory Evidence

## Batch 1 — environment template, packaging, dependencies, and Alembic configuration

Reviewed `.env.example`, `alembic.ini`, `pyproject.toml`, `requirements.txt`, and `requirements-dev.txt`. The real `.env` was correctly withheld; it is neither needed nor appropriate for this architecture/scientific audit.

## Results

- `.env.example` contains empty placeholders rather than secrets. `PROJECT_NAME`, `ENVIRONMENT`, `DATABASE_URL`, `MATERIALS_PROJECT_API_KEY`, and `LOG_LEVEL` correspond to declared settings fields. `MP_API_URL` has no settings field or runtime consumer (`MG-IA-021`).
- `pyproject.toml` parses successfully. It declares Python 3.11+, the application runtime dependencies, setuptools package discovery limited to `app*`, and pytest root import configuration. Package version `0.1.0` versus capability/release documentation remains `OBS-001` pending version-policy evidence.
- `requirements.txt` provides a fully pinned environment snapshot, including the declared runtime dependencies and current development tools. `requirements-dev.txt` includes that base file and repeats unpinned direct dev requirements. This is installable intent, but lock-generation/reproducibility policy and cross-platform execution evidence are not supplied; no defect is inferred merely from using both project metadata and a pinned requirements snapshot.
- `alembic.ini` is structurally conventional and points to the repository migration directory. Its local PostgreSQL URL is not treated as the effective production URL because the previously reviewed `alembic/env.py` replaces migration configuration from application settings. No new migration-configuration defect is confirmed by the placeholder.

## Missing regression coverage

- No test accounts for every key exposed by `.env.example`.
- No supplied packaging test builds a wheel/sdist and imports the installed application from outside the source tree.
- No supplied clean-environment record installs both production and development dependency paths and runs the complete test suite at the reviewed commit.

These are evidence/coverage limitations unless later execution demonstrates a packaging or dependency failure.
