# MG-DE Readiness Matrix

**Assessment baseline:** `60a6a9fe06ca9b0ba024b5507c6ac7e0307f7177`

| Area | Repository evidence | Initial result | Required gate |
|---|---|---|---|
| Storage engine | PostgreSQL/Neon; normalized material-element relationships | Suitable in principle for approximately 1,000 materials | Record test and production sizing evidence |
| Material identity | Source identity mapping and conservative polymorph/alias rules implemented | Verified against the PostgreSQL test database | Retain conflict and legacy-identity tests as regression gates |
| Provenance | Immutable run, source-record, and event models plus source and normalized digests implemented | Migration and lifecycle verified against PostgreSQL | Retain persistence and run-reconciliation tests as regression gates |
| Source acquisition | Configurable deterministic paging, bounds, retries, rejections, release reader, and offline manifest inspection implemented | First MG-DE-005 manifest failed closed at the material bound; revised 0.05 eV/atom scope ready | Capture and review a complete revised manifest before any database import |
| Import transaction | Configurable chunks commit independently and checkpoint after success | Verified against PostgreSQL test database | Retain the lifecycle test as a regression gate |
| Idempotency | Per-run event replay and deterministic insert/update/unchanged/conflict outcomes implemented | Same-run replay and fresh-run refresh independently verified | Retain composed lifecycle coverage as a regression gate |
| Recovery | Atomic checkpoint/resume and idempotent chunk replay implemented | Verified against PostgreSQL test database | Define production dataset-version rollback before an authorized canary |
| Validation | Composition validation, sanitized rejection records, manifest digest, counts, and final identity reconciliation exist | Qualified with the deterministic 1,000-material fixture | Repeat with an approved real-source manifest before production use |
| Candidate screening | Stable and energy constraints are applied in SQL before scoring | Qualified at the initial target | Retain result and query-count evidence for future scale steps |
| Substitution analysis | SQL loads only materials sharing at least one source element | Qualified at the initial target | Requalify for materially larger or denser datasets |
| Discovery graph | Composition is loaded incrementally for the bounded active frontier | Qualified at the initial target | Retain graph-density evidence and monitor query growth |
| Material families | SQL prefilter encodes the existing strong relationship predicates before material and composition loading | Qualified at the initial target | Requalify dense common-element behavior at the next scale step |
| API listing | Limit/offset; maximum response limit 100 | Qualified at the initial target | Preserve stable ordering and bounds |
| Graph traversal | Existing depth, branching, and result bounds | Qualified at the initial target | Query counts remain optimization signals |
| Indexes | Identity and relationship foreign-key indexes exist | Sufficient at the initial target | Add indexes only from future observed plans |
| Scale tests | Deterministic 1,000-material fixture and bounded sequential harness executed against PostgreSQL | Qualified | Repeat for real-source and materially larger targets |
| Scientific regression | Complete curated detail and criticality JSON matched before and after import and changed-source conflict | Qualified | Expand the invariant cohort with approved scientific capabilities |
| Backup/recovery | Custom-format backup and archive listing completed at the initial target | Backup creation qualified | Restoration remains separately authorized evidence |
| Compute capacity | Production uses a small EC2 instance and managed PostgreSQL | Unqualified, not proven inadequate | Measure canary resource use before production expansion |

## Overall result

The bounded initial test target is qualified and MG-DE-001 through MG-DE-004
are closed. This does not authorize a real-source or production import.
Production capacity, concurrency, restoration, and substantially larger scale
remain separate evidence gates; storage capacity alone is not readiness proof.
MG-DE-005 remains the next gate after its first manifest failed the completeness
criterion. Controlled reacquisition ends before any PostgreSQL or Neon write.
