## Getting Started

### Prerequisites

Before running MaterialGraph, ensure the following are installed:

* Python 3.11+
* PostgreSQL 15+
* Git
* Docker (required for the local Gitleaks pre-commit hook)
* Materials Project API Key

---

### Clone Repository

```bash
git clone https://github.com/MaterialGraph/materialgraph.git
cd materialgraph
```

---

### Create Virtual Environment

```bash
python -m venv .venv
```

Activate:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
pip install --no-deps -e .
```

---

### Configure Secret Scanning

MaterialGraph uses Gitleaks as a defense-in-depth control against accidental credential commits.

The repository includes a version-controlled pre-commit hook in:

```text
.githooks/pre-commit
```

After cloning the repository, enable the project hooks:

```bash
git config core.hooksPath .githooks
```

Verify:

```bash
git config --get core.hooksPath
```

Expected:

```text
.githooks
```

The pre-commit hook scans staged changes with Gitleaks before Git creates a commit. A detected potential secret, or a failed scan, blocks the commit.

The scanner image is pinned by immutable digest, receives a read-only repository
mount, and runs without container networking. The reviewed update procedure is
documented in [`../security/AUTOMATION_PINNING.md`](../security/AUTOMATION_PINNING.md).

The hook currently runs Gitleaks through Docker, so Docker must be available when committing from a development environment.

Secret scanning also runs independently in GitHub Actions on pushes and pull requests. The CI scan provides a second layer of protection and does not replace the local pre-commit check.

Do not bypass a secret-scanning failure merely to complete a commit. Determine whether the finding is a real credential or a false positive before changing the scanner configuration.

---

### Configure Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost/materialgraph

MATERIALS_PROJECT_API_KEY=your_materials_project_api_key
```

`DATABASE_URL` is required by the application and is also Alembic's default
migration target. A deployment may additionally set
`DATABASE_MIGRATION_URL` when migrations require a separate direct connection;
Alembic prefers that value when both variables are present. If neither database
variable is configured, migration commands fail without selecting a fallback
database.

The `.env` file is local configuration and must never be committed.

Use `.env.example` to document required variable names without storing credentials. Never place production passwords, API keys, access tokens, or connection strings containing real credentials in tracked files.

Before committing environment-related changes, verify:

```bash
git status --short
git ls-files -- .env
```

`.env` must not appear as a tracked file.

---

### Create Database

PostgreSQL:

```sql
CREATE DATABASE materialgraph;
```

---

### Run Database Migrations

```bash
alembic upgrade head
```

---

### Build and Apply a Material Import Manifest

MaterialGraph separates source acquisition from database writes. First build a
deterministic manifest. This requires `MATERIALS_PROJECT_API_KEY` but does not
write to the database:

Read the current source release before choosing the expected value (this makes
one metadata request and does not fetch material records):

```bash
python -c "import os; from dotenv import load_dotenv; from mp_api.client import MPRester; load_dotenv(); print(MPRester(os.environ['MATERIALS_PROJECT_API_KEY']).get_database_version())"
```

```bash
python -m scripts.import_materials_project \
  --manifest ./materials-manifest.json \
  --source-release 2026.09.01 \
  --retrieved-at 2026-09-15T00:00:00+00:00
```

Inspect and retain the reported manifest digest and counts. To apply the
validated manifest to a test database in atomic chunks, provide a separate
checkpoint path and the exact configured database name:

```bash
python -m scripts.import_materials_project \
  --manifest ./materials-manifest.json \
  --checkpoint ./materials-checkpoint.json \
  --expected-database-name materialgraph_test \
  --apply
```

Use the actual Materials Project database version and retrieval start time;
the example values are illustrative. The declared version is verified against
the API heartbeat before each page, and both values are protected by the
manifest digest.

If a chunk fails, rerun the same apply command. The validated checkpoint resumes
at the last completed chunk and import-run identity. Proven source identities
are classified as inserted, updated, or unchanged. Ambiguous identities fail
safe as conflicts, and completed identical scopes record retirements without
destructive material deletion.

The command refuses an unconfirmed database name and refuses a non-test database
unless `--allow-non-test-database` is supplied explicitly. Do not use that flag
without an approved production import procedure, backup, and rollback evidence.

Verify import:

```bash
python scripts/check_import_counts.py
```

Example output:

```text
Materials: 28
Elements: 9
MaterialElements: 94
```

---

### Start API Server

```bash
uvicorn app.main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

### Run Tests

Run all tests:

```bash
pytest
```

Run specific test groups:

```bash
pytest tests/services
```

```bash
pytest tests/api
```

---

## Example Workflows

### Candidate Screening

```text
POST /api/v1/screening/candidates
```

Evaluate battery material candidates under:

* lithium scarcity
* cobalt avoidance
* stability constraints
* supply-risk constraints

---

### Candidate Comparison

```text
POST /api/v1/comparison/materials
```

Compare two candidate materials and receive:

* screening scores
* risk scores
* ranking explanations

---

### Scenario Ranking

```text
POST /api/v1/scenarios/rank
```

Rank candidates under scenarios such as:

* lithium_supply_shock
* cobalt_avoidance
* low_supply_risk

---

### Sensitivity Analysis

```text
POST /api/v1/sensitivity/material
```

Analyze candidate robustness under changing supply-risk conditions.

---

### Substitution Analysis

```text
POST /api/v1/substitutions/analyze
```

Identify alternative candidate materials based on:

* chemistry similarity
* risk profile
* substitution potential

---
