# MaterialGraph Dataset Expansion

**Namespace:** `MG-DE-*`
**Status:** MG-DE-001 and MG-DE-002 closed; MG-DE-003 and MG-DE-004 open
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
test database. Several request-time query paths and representative-scale
behavior remain unqualified. No production migration or import is authorized.

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
- **Closed:** Acceptance criteria and required evidence are satisfied.
- **Accepted limitation:** Bounded limitation judged proportionate to the
  current target.
- **Future scale:** Work needed beyond the initial target, not a blocker for it.

## Records

- [Readiness matrix](MG-DE_READINESS_MATRIX.md)
- [Evidence register](MG-DE_EVIDENCE_REGISTER.md)
- [Decision register](MG-DE_DECISIONS.md)
- [Benchmark plan](MG-DE_BENCHMARK_PLAN.md)
- [Materials Project source contract](MG-DE_SOURCE_CONTRACT.md)
- [Findings](findings/README.md)
- [Implementation records](implementation/README.md)

## Gate sequence

1. Approve the source and scientific dataset contract.
2. Resolve provenance and ingestion lifecycle gaps.
3. Narrow scale-sensitive request paths.
4. Generate and exercise a deterministic representative fixture.
5. Complete test-database import, rerun, interruption, and rollback checks.
6. Measure query plans, latency, memory, backup behavior, and scientific
   regression.
7. Review the evidence before authorizing any production canary.
