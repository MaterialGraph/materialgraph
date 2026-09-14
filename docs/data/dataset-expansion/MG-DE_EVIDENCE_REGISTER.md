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
| MG-DE-E-017 | Manifest application commits configured chunks and atomically checkpoints each completed boundary | Repository implementation and unit tests | MG-DE-001 | PostgreSQL lifecycle reproduction remains pending |
| MG-DE-E-018 | Import service bulk-loads existing material and element identities per chunk and returns reconciled counts | Repository implementation | MG-DE-001 | Focused PostgreSQL test execution remains pending |
| MG-DE-E-019 | CLI separates manifest building from application and requires exact database-name confirmation | Repository implementation and CLI tests | MG-DE-001 | Non-test application is deliberately not exercised or authorized |
| MG-DE-E-020 | [Materials Project `SummaryRester.search` documentation](https://materialsproject.github.io/api/_autosummary/mp_api.client.routes.materials.summary.SummaryRester.html) documents chemical-system filters, projected fields, `num_chunks`, `chunk_size`, `_page`, and `_sort_fields` | Primary upstream documentation and pinned client inspection | MG-DE-001 | Dataset release and licensing validation remain MG-DE-002 work |

## Evidence still required

- authoritative source API, licensing, and dataset-release documentation;
- approved selection and identity contract;
- deterministic representative fixture manifest;
- import dry-run, completion, rerun, interruption, and resume records;
- row-count and manifest reconciliation;
- SQL query plans and query-count measurements;
- latency and memory measurements for representative endpoints;
- backup size/duration evidence from the test environment;
- complete curated-response regression comparisons;
- bounded production-canary evidence, only after separate approval.
