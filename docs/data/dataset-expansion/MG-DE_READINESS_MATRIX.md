# MG-DE Readiness Matrix

**Assessment baseline:** `60a6a9fe06ca9b0ba024b5507c6ac7e0307f7177`

| Area | Repository evidence | Initial result | Required gate |
|---|---|---|---|
| Storage engine | PostgreSQL/Neon; normalized material-element relationships | Suitable in principle for approximately 1,000 materials | Record test and production sizing evidence |
| Material identity | Source identity mapping and conservative polymorph/alias rules implemented | Verified against the PostgreSQL test database | Retain conflict and legacy-identity tests as regression gates |
| Provenance | Immutable run, source-record, and event models plus source and normalized digests implemented | Migration and lifecycle verified against PostgreSQL | Retain persistence and run-reconciliation tests as regression gates |
| Source acquisition | Configurable deterministic paging, bounds, retries, rejections, release reader, and offline manifest inspection implemented | Revised MG-DE-005 manifest completed with 1,727 accepted identities and passed technical, scientific, and local PostgreSQL qualification | Retain the immutable manifest and external evidence through the Neon gate |
| Import transaction | Configurable chunks commit independently and checkpoint after success | Verified against PostgreSQL test database | Retain the lifecycle test as a regression gate |
| Idempotency | Per-run event replay and deterministic insert/update/unchanged/conflict outcomes implemented | Same-run replay and fresh-run refresh independently verified | Retain composed lifecycle coverage as a regression gate |
| Recovery | Atomic checkpoint/resume and idempotent chunk replay implemented | Failed first chunk and stale-checkpoint committed replay verified with the exact real manifest | Execute controlled client-disconnect recovery on the isolated Neon target |
| Validation | Composition validation, sanitized rejection records, manifest digest, counts, and final identity reconciliation exist | Qualified with the exact approved 1,727-identity manifest | Repeat in isolated non-production Neon before any canary |
| Candidate screening | Stable and energy constraints are applied in SQL before scoring | Qualified at the initial target | Retain result and query-count evidence for future scale steps |
| Substitution analysis | SQL loads only materials sharing at least one source element | Qualified at the initial target | Requalify for materially larger or denser datasets |
| Discovery graph | Composition is loaded incrementally for the bounded active frontier | Qualified at the initial target | Retain graph-density evidence and monitor query growth |
| Material families | SQL prefilter encodes the existing strong relationship predicates before material and composition loading | Qualified at the initial target | Requalify dense common-element behavior at the next scale step |
| API listing | Limit/offset; maximum response limit 100 | Qualified at the initial target | Preserve stable ordering and bounds |
| Graph traversal | Existing depth, branching, and result bounds | Qualified at the initial target | Query counts remain optimization signals |
| Indexes | Identity and relationship foreign-key indexes exist | Sufficient at the initial target | Add indexes only from future observed plans |
| Scale tests | Deterministic fixture and exact real cohort executed with bounded sequential local PostgreSQL and isolated Neon harnesses | Qualified at the reviewed local and remote target with recorded latency findings | Optimize observed heavy paths before any separately authorized production expansion; concurrency remains separately authorized |
| Scientific regression | Canonical state for all 28 curated materials and complete sentinel detail/criticality JSON matched before and after real import and rerun | Qualified | Expand the invariant cohort with approved scientific capabilities |
| Backup/recovery | Real-data custom-format backup and archive listing completed | 750,478-byte archive with 124 listed entries qualified | Restoration remains separately authorized evidence |
| Compute capacity | Production uses a small EC2 instance and managed PostgreSQL | Unqualified, not proven inadequate | Measure canary resource use before production expansion |

## Overall result

The bounded initial test target is qualified and MG-DE-001 through MG-DE-004
are closed. This does not authorize a real-source or production import.
Production capacity, concurrency, restoration, and substantially larger scale
remain separate evidence gates; storage capacity alone is not readiness proof.
MG-DE-005 through MG-DE-007 are closed with a technically qualified,
scientifically accepted, and locally PostgreSQL-qualified external manifest.
Broad response crowding and the heavier discovery paths are accepted signals,
not hidden successes. MG-DE-008 independently qualified the exact cohort on an
isolated non-production Neon branch and completed evidence and cleanup gates.
Production writes remain separately unauthorized.
