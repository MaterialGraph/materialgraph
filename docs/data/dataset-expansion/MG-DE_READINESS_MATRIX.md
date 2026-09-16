# MG-DE Readiness Matrix

**Assessment baseline:** `60a6a9fe06ca9b0ba024b5507c6ac7e0307f7177`

| Area | Repository evidence | Initial result | Required gate |
|---|---|---|---|
| Storage engine | PostgreSQL/Neon; normalized material-element relationships | Suitable in principle for approximately 1,000 materials | Record test and production sizing evidence |
| Material identity | Source identity mapping and conservative polymorph/alias rules implemented | Verified against the PostgreSQL test database | Retain conflict and legacy-identity tests as regression gates |
| Provenance | Immutable run, source-record, and event models plus source and normalized digests implemented | Migration and lifecycle verified against PostgreSQL | Retain persistence and run-reconciliation tests as regression gates |
| Source acquisition | Configurable deterministic paging, bounds, retries, rejections, and manifest implemented | Source, licensing, release, and selection contract approved under MG-DE-002 | Capture an authorized representative-source manifest under MG-DE-004 |
| Import transaction | Configurable chunks commit independently and checkpoint after success | Verified against PostgreSQL test database | Retain the lifecycle test as a regression gate |
| Idempotency | Per-run event replay and deterministic insert/update/unchanged/conflict outcomes implemented | Same-run replay and fresh-run refresh independently verified | Retain composed lifecycle coverage as a regression gate |
| Recovery | Atomic checkpoint/resume and idempotent chunk replay implemented | Verified against PostgreSQL test database | Define production dataset-version rollback before an authorized canary |
| Validation | Composition validation, sanitized rejection records, manifest digest, counts, and final identity reconciliation exist | Verified for the bounded lifecycle | Extend to the approved representative fixture under MG-DE-004 |
| Candidate screening | Stable and energy constraints are applied in SQL before scoring | Ready for PostgreSQL verification | Confirm preserved results and measure the bounded representative fixture |
| Substitution analysis | SQL loads only materials sharing at least one source element | Ready for PostgreSQL verification | Confirm zero-similarity exclusion is semantics-preserving and measure the representative fixture |
| Discovery graph | Composition is loaded incrementally for the bounded active frontier | Ready for PostgreSQL verification | Confirm scoped query behavior through graph modes and dense neighborhoods |
| Material families | SQL prefilter encodes the existing strong relationship predicates before material and composition loading | Ready for PostgreSQL verification | Confirm equivalence to exhaustive classification and measure dense common-element cases |
| API listing | Limit/offset; maximum response limit 100 | Suitable for initial target | Verify stable ordering and query plans |
| Graph traversal | Existing depth, branching, and result bounds | Suitable foundation | Verify with dense representative neighborhoods |
| Indexes | Identity and relationship foreign-key indexes exist | Partial | Add indexes only from observed query plans |
| Scale tests | Deterministic 1,000-material synthetic fixture and bounded sequential qualification harness implemented | Ready for independent execution | Record PostgreSQL import, query, memory, regression, and backup evidence |
| Scientific regression | Existing deterministic tests and response comparisons | Suitable foundation | Complete pre/post JSON comparison for curated reference paths |
| Backup/recovery | Daily production backup controls exist | Unqualified for expanded data | Measure backup size/duration and review recovery objectives |
| Compute capacity | Production uses a small EC2 instance and managed PostgreSQL | Unqualified, not proven inadequate | Measure canary resource use before production expansion |

## Overall result

The initial target is feasible after the four open findings are addressed and
their acceptance gates are satisfied. Storage capacity alone is not treated as
readiness evidence.
