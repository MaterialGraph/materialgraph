# MaterialGraph Dataset Expansion

**Namespace:** `MG-DE-*`
**Status:** MG-DE-001 through MG-DE-008 closed; production expansion remains separately unauthorized
**Baseline commit:** `60a6a9fe06ca9b0ba024b5507c6ac7e0307f7177`
**Initial scale target:** Approximately 1,000 representative materials

## Purpose

This workstream governs the controlled expansion of MaterialGraph from its
small curated dataset to a scientifically representative dataset. It keeps
dataset engineering separate from the historical architecture (`MG-AUD-*`),
implementation (`MG-IA-*`), security (`MG-SEC-*`), and security assurance
(`MG-SA-*`) records.

The first target is deliberately bounded. It is intended to expose ingestion,
identity, query, graph-density, backup, and operational scaling behavior before
any substantially larger collection is attempted.

## Current conclusion

The resumable import lifecycle, dataset provenance, and conservative refresh
semantics are implemented and independently verified against the PostgreSQL
test database. Exact SQL and active-frontier narrowing is implemented for the
identified scale-sensitive request paths. Independent PostgreSQL qualification
with a deterministic 1,000-material synthetic fixture confirmed ingestion,
rerun, refresh, failure recovery, representative requests, curated scientific
invariants, and backup creation within the initial acceptance gates. No
production migration or import is authorized.

The first MG-DE-005 manifest-only execution reached its 3,000-material ceiling
before completing all 48 systems and was not qualified or imported. The
revised 0.05 eV/atom version 3 contract completed with 1,727 identities and
passed all technical manifest gates. MG-DE-006 accepted it with explicit
scientific limitations for disposable local PostgreSQL qualification only.
MG-DE-007 then qualified the exact manifest locally with 1,699 inserts and 28
protected curated conflicts, preserved all curated state, measured real-data
crowding and endpoint behavior, verified recovery and idempotency, and
validated backup creation without restoration. MG-DE-008 qualified the same
manifest on an isolated Neon branch, preserving the same import and recovery
outcomes within the reviewed resource ceilings. The remote run retained
performance findings for discovery path, scientific pathways, and formula
lookup. Its evidence and cleanup were independently verified. Production
import and deployment remain unauthorized.

## Scope

The workstream covers:

- dataset inclusion and exclusion rules;
- source authority, licensing, release identity, and retrieval evidence;
- canonical material, composition, phase, structure, polymorph, and alias
  semantics;
- deterministic normalization and missing-value handling;
- paginated, chunked, resumable, and observable ingestion;
- refresh, conflict, retirement, and rollback semantics;
- query and graph behavior at representative scale;
- index and query-plan evidence;
- deterministic scientific regression checks;
- backup size, duration, recovery objectives, and production rollout gates.

It does not authorize a production import, dependency upgrade, schema
migration, service restart, backup restoration, or infrastructure resize.

## Evidence rules

1. Repository behavior is established from the checked-out commit, not from
   prose claims.
2. Source records, import manifests, and derived records must remain
   distinguishable.
3. Counts alone do not prove scientific correctness or provenance.
4. Performance conclusions require a representative fixture and recorded
   environment, dataset size, latency, memory, query-count, and query-plan
   evidence.
5. Rerunning an identical import must produce a deterministic outcome.
6. Missing evidence is recorded as a limitation, not converted to success or
   failure.
7. Existing curated scientific responses must be compared as complete JSON
   across relevant changes.
8. Production evidence and local/test evidence remain explicitly separated.

## Status vocabulary

- **Open:** Confirmed gap requiring work before the initial expansion gate.
- **In progress:** Approved implementation is underway but not verified.
- **Ready for verification:** Implementation and local evidence exist; closure
  evidence is incomplete.
- **Ready for controlled execution:** Safeguards and an execution plan exist,
  but independent external-source evidence has not yet been captured.
- **Closed:** Acceptance criteria and required evidence are satisfied.
- **Accepted limitation:** Bounded limitation judged proportionate to the
  current target.
- **Future scale:** Work needed beyond the initial target, not a blocker for it.

## Records

- [Readiness matrix](MG-DE_READINESS_MATRIX.md)
- [Evidence register](MG-DE_EVIDENCE_REGISTER.md)
- [Decision register](MG-DE_DECISIONS.md)
- [Benchmark plan](MG-DE_BENCHMARK_PLAN.md)
- [Representative-scale qualification report](MG-DE_QUALIFICATION_REPORT.md)
- [Materials Project source contract](MG-DE_SOURCE_CONTRACT.md)
- [MG-DE-005 real-source pilot plan](MG-DE_REAL_SOURCE_PILOT.md)
- [MG-DE-005 qualified manifest report](MG-DE_QUALIFIED_MANIFEST_REPORT.md)
- [MG-DE-006 scientific cohort review plan](MG-DE_SCIENTIFIC_COHORT_REVIEW.md)
- [MG-DE-006 scientific cohort report](MG-DE_SCIENTIFIC_COHORT_REPORT.md)
- [MG-DE-007 real-data PostgreSQL qualification plan](MG-DE_REAL_DATA_QUALIFICATION.md)
- [MG-DE-007 real-data PostgreSQL qualification report](MG-DE_REAL_DATA_QUALIFICATION_REPORT.md)
- [MG-DE-008 isolated Neon qualification plan](MG-DE_NEON_QUALIFICATION.md)
- [MG-DE-008 isolated Neon qualification report](MG-DE_NEON_QUALIFICATION_REPORT.md)
- [MG-DE-008 offline contract template](MG-DE_NEON_QUALIFICATION_CONTRACT.example.json)
- [Findings](findings/README.md)
- [Implementation records](implementation/README.md)

## Gate sequence

1. Approve the source and scientific dataset contract.
2. Resolve provenance and ingestion lifecycle gaps.
3. Narrow scale-sensitive request paths.
4. Generate and exercise a deterministic representative fixture. **Complete.**
5. Complete test-database import, rerun, interruption, and rollback checks.
   **Complete.**
6. Measure query plans, latency, memory, backup behavior, and scientific
   regression. **Complete for the isolated initial test target.**
7. Review real-source evidence and scientific cohort suitability before any
   database import. **MG-DE-005 and MG-DE-006 complete.**
8. Qualify the exact approved manifest in disposable local PostgreSQL.
   **MG-DE-007 complete with accepted limitations. MG-DE-008 isolated Neon
   qualification and cleanup are complete with recorded performance findings;
   production expansion remains separately unauthorized.**
