# MG-DE Readiness Matrix

**Assessment baseline:** `60a6a9fe06ca9b0ba024b5507c6ac7e0307f7177`

| Area | Repository evidence | Initial result | Required gate |
|---|---|---|---|
| Storage engine | PostgreSQL/Neon; normalized material-element relationships | Suitable in principle for approximately 1,000 materials | Record test and production sizing evidence |
| Material identity | Unique `materials.mp_id`; source stored as a string | Partial | Approve canonical identity, polymorph, alias, and source-ID rules |
| Provenance | `source` and `raw_data` retained | Not sufficient for a reproducible dataset release | Persist source release, retrieval time, normalization version, and import identity |
| Source acquisition | Configurable deterministic paging, bounds, retries, rejections, and manifest implemented | Ready for test-database verification | Reproduce focused tests and bounded lifecycle evidence |
| Import transaction | Configurable chunks commit independently and checkpoint after success | Ready for test-database verification | Demonstrate failure and resume against PostgreSQL test database |
| Idempotency | Existing `mp_id` values are skipped | Prevents duplicates but does not define refresh correctness | Deterministic insert/update/unchanged/conflict policy |
| Recovery | Atomic checkpoint/resume and idempotent chunk replay implemented | Ready for test-database verification | Reproduce interruption, replay, and completion evidence |
| Validation | Composition validation, sanitized rejection records, manifest digest, counts, and final identity reconciliation exist | Ready for test-database verification | Execute complete bounded lifecycle |
| Candidate screening | Unscoped screening loads all materials | Scale-sensitive | SQL narrowing and benchmark evidence |
| Substitution analysis | Loads all materials other than the source | Scale-sensitive | SQL narrowing and bounded candidate generation |
| Discovery graph | Builds a complete material-element map | Scale-sensitive | Load only the active candidate/subgraph scope |
| Material families | Broad shared-element set classified in Python | Scale-sensitive for common elements | Candidate cap or ranked SQL narrowing with scientific semantics preserved |
| API listing | Limit/offset; maximum response limit 100 | Suitable for initial target | Verify stable ordering and query plans |
| Graph traversal | Existing depth, branching, and result bounds | Suitable foundation | Verify with dense representative neighborhoods |
| Indexes | Identity and relationship foreign-key indexes exist | Partial | Add indexes only from observed query plans |
| Scale tests | Existing suite exercises current small dataset | Evidence gap | Deterministic 1,000-material fixture and recorded benchmarks |
| Scientific regression | Existing deterministic tests and response comparisons | Suitable foundation | Complete pre/post JSON comparison for curated reference paths |
| Backup/recovery | Daily production backup controls exist | Unqualified for expanded data | Measure backup size/duration and review recovery objectives |
| Compute capacity | Production uses a small EC2 instance and managed PostgreSQL | Unqualified, not proven inadequate | Measure canary resource use before production expansion |

## Overall result

The initial target is feasible after the four open findings are addressed and
their acceptance gates are satisfied. Storage capacity alone is not treated as
readiness evidence.
