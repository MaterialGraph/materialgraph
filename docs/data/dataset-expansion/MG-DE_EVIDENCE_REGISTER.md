# MG-DE Evidence Register

**Baseline:** `60a6a9fe06ca9b0ba024b5507c6ac7e0307f7177`

| ID | Evidence | Type | Supports | Limitation |
|---|---|---|---|---|
| MG-DE-E-001 | `scripts/import_materials_project.py` defines five chemical systems and calls `fetch_materials(..., limit=25)` | Repository | MG-DE-001 | Does not establish upstream total-result behavior |
| MG-DE-E-002 | `app/services/material/project_service.py` requests one chunk with `chunk_size=limit` | Repository | MG-DE-001 | Source API behavior and terms require primary-source validation before implementation |
| MG-DE-E-003 | `app/services/material/import_service.py` imports a candidate sequence in one transaction | Repository | MG-DE-001 | No representative large transaction was executed |
| MG-DE-E-004 | Import service checks each `mp_id` and skips an existing record | Repository | MG-DE-001, MG-DE-002 | Duplicate prevention is not a refresh or conflict policy |
| MG-DE-E-005 | Import tests cover creation, duplicate skip, normalized composition, invalid membership/fractions, rollback, and post-error recovery | Test code | Existing ingestion foundation | Tests do not cover pagination, checkpoints, refreshes, or scale |
| MG-DE-E-006 | `Material` stores a unique `mp_id`, `source`, and JSON `raw_data` | Repository | MG-DE-002 | No dataset release, retrieval time, import run, or normalization identity |
| MG-DE-E-007 | Architecture documentation calls for canonical identity, provenance, licensing, retrieval time, dataset version, normalization, conflicts, missing values, and uncertainty | Repository documentation | MG-DE-002 | Design intent is not implementation evidence |
| MG-DE-E-008 | Candidate screening unscoped mode queries all `Material` rows | Repository | MG-DE-003 | No 1,000-material runtime measurement yet |
| MG-DE-E-009 | Substitution analysis queries all materials except the source | Repository | MG-DE-003 | Downstream limits do not prevent the initial broad load |
| MG-DE-E-010 | Discovery graph builder loads all material-element relationships into a map | Repository | MG-DE-003 | Existing database is too small to establish scaling behavior |
| MG-DE-E-011 | Family service collects all candidates sharing any base element, then loads and classifies them in Python | Repository | MG-DE-003 | Common-element density has not been benchmarked |
| MG-DE-E-012 | API schemas and discovery services apply response, depth, and branching bounds | Repository and tests | Existing scale safeguards | Does not bound every upstream database candidate set |
| MG-DE-E-013 | `docs/performance_baseline.md` records existing small-dataset timings | Repository documentation | MG-DE-004 | Explicitly not representative of the expansion target |
| MG-DE-E-014 | Production deployment documentation identifies a small EC2 instance and Neon PostgreSQL | Deployment documentation | Operational qualification | Documentation is not a resource-utilization measurement |
| MG-DE-E-015 | Stage 1 records document daily backup, retention, verification, and recovery controls | Repository documentation and prior production evidence | Operational foundation | Expanded-dataset backup duration and recovery objectives are unmeasured |
| MG-DE-E-016 | `import_pipeline.py` builds canonical SHA-256 manifests from deterministic bounded pages | Repository implementation and unit tests | MG-DE-001 | No real source request was made during implementation verification |
| MG-DE-E-017 | Manifest application commits configured chunks and atomically checkpoints each completed boundary | Repository implementation and unit tests | MG-DE-001 | Production use remains unauthorized |
| MG-DE-E-018 | Import service bulk-loads existing material and element identities per chunk and returns reconciled counts | Repository implementation and PostgreSQL integration test | MG-DE-001 | Representative-scale measurement remains MG-DE-004 work |
| MG-DE-E-019 | CLI separates manifest building from application and requires exact database-name confirmation | Repository implementation and CLI tests | MG-DE-001 | Non-test application is deliberately not exercised or authorized |
| MG-DE-E-020 | [Materials Project `SummaryRester.search` documentation](https://materialsproject.github.io/api/_autosummary/mp_api.client.routes.materials.summary.SummaryRester.html) documents chemical-system filters, projected fields, `num_chunks`, `chunk_size`, `_page`, and `_sort_fields` | Primary upstream documentation and pinned client inspection | MG-DE-001 | Dataset release and licensing validation remain MG-DE-002 work |
| MG-DE-E-021 | `test_postgresql_manifest_lifecycle_interrupts_resumes_and_reruns` composes the manifest pipeline with the real SQLAlchemy importer and guarded PostgreSQL test session | Repository integration test, independently passed against `materialgraph_test` on 2026-09-15 | MG-DE-001 | Bounded test evidence; no production or representative-scale import |
| MG-DE-E-022 | Initial independent execution reached PostgreSQL but the generated fixture identity exceeded the existing `materials.mp_id` 50-character limit | Independent test-database execution, 2026-09-15 | MG-DE-001 test verification | Fixture defect prevented lifecycle assertions; production and source data were not involved |
| MG-DE-E-023 | At commit `6dfe67d817b8ac848bb41d2783e27c7ed6b27d27`, independent validation reported: PostgreSQL lifecycle 1 passed; focused import suite 67 passed; complete suite 860 passed, 1 skipped; Ruff, automation pins, dependency contract, and diff check passed | Independent local validation, 2026-09-15 | MG-DE-001 closure | Test database only; no external source request or production import |
| MG-DE-E-024 | GitHub Dependency Security run 11 and Secret Scan run 97 passed for commit `6dfe67d817b8ac848bb41d2783e27c7ed6b27d27` | GitHub workflow evidence, 2026-09-15 | MG-DE-001 closure | These workflows do not replace functional import tests |
| MG-DE-E-025 | Materials Project states its data is CC BY 4.0; the pinned client exposes the current API database version through its heartbeat contract | Primary source documentation and pinned-client inspection | MG-DE-002 | Historical query pinning is not claimed; contributed datasets with different terms are excluded |
| MG-DE-E-026 | Manifest schema v2 requires release, timezone-aware retrieval time, license, normalization version, and selection-contract version under the manifest digest | Repository implementation and tests | MG-DE-002 | Independent source acquisition is not performed in this change |
| MG-DE-E-027 | Migration `c8f3a2d7e901` adds immutable import-run headers, current source-identity records, per-scope memberships, and append-only outcome events | Repository migration and model implementation | MG-DE-002 | Independent PostgreSQL migration verification pending |
| MG-DE-E-028 | Refresh service implements inserted, updated, unchanged, conflicted, rejected, and retired outcomes with per-run replay safety | Repository implementation and tests | MG-DE-002 | Independent PostgreSQL composed lifecycle pending |
| MG-DE-E-029 | [MG-DE source contract](MG-DE_SOURCE_CONTRACT.md) defines inclusion, license, identity, polymorph, alias, missingness, refresh, and retirement boundaries | Governing dataset documentation | MG-DE-002 | Production publication remains unauthorized |
| MG-DE-E-030 | Isolated validation reported 56 non-PostgreSQL focused tests passed with 1 PostgreSQL lifecycle test deselected; two provenance/overlapping-scope service scenarios passed against a disposable SQLite subset; 870 tests collected; Ruff, automation pins, dependency contract, Python compilation, Alembic single-head, PostgreSQL DDL compilation, documentation links, and diff checks passed | Local implementation validation, 2026-09-15 | MG-DE-002 implementation | SQLite smoke checks are not closure evidence; PostgreSQL execution and complete suite remain required |

## Evidence still required

- authoritative source API, licensing, and dataset-release documentation;
- approved selection and identity contract;
- deterministic representative fixture manifest;
- representative-fixture import dry-run, completion, rerun, interruption, and resume records;
- representative-fixture row-count and manifest reconciliation;
- SQL query plans and query-count measurements;
- latency and memory measurements for representative endpoints;
- backup size/duration evidence from the test environment;
- complete curated-response regression comparisons;
- bounded production-canary evidence, only after separate approval.
