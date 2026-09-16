# MG-DE-004: Representative scale evidence is absent

**Status:** Closed
**Priority:** Cross-cutting verification
**Initial expansion blocker:** Yes

## Observation

The complete automated suite and existing performance baseline cover the small
curated dataset. There is no deterministic fixture or benchmark representing
the proposed first expansion target, and expanded-dataset backup duration has
not been measured.

## Impact

The project cannot yet make evidence-based claims about import completion,
request latency, query behavior, memory use, backup behavior, or infrastructure
fitness at approximately 1,000 materials.

## Required outcome

- deterministic representative fixture and manifest;
- benchmark harness or reproducible bounded commands;
- recorded import, query, graph-density, and backup measurements;
- complete curated scientific regression comparisons;
- documented acceptance thresholds and environment.

## Acceptance evidence

The benchmark plan must be executed in an isolated test environment against the
reviewed commit. Results must distinguish measured facts from estimates. A
production canary remains separately authorized work.

## Implementation status

The deterministic synthetic fixture, strict disposable-database guard,
sequential measurement harness, complete-response capture, and comparison
tools were executed independently against PostgreSQL 16.14 at commit
`69f0bda15f2a2ffe76c265ecc3bbfe60fc35f7a7`.

Clean import, identical rerun, changed-source outcomes, failed-chunk rollback,
checkpoint-lag replay, database reconciliation, 12 request scenarios, memory,
query counts, an analyzed query plan, complete curated JSON comparisons, and a
validated custom-format backup all passed. See
[the qualification report](../MG-DE_QUALIFICATION_REPORT.md).

Closure applies only to the bounded approximately 1,000-material test target.
It does not authorize a production canary, real-source import, restoration,
concurrency test, or infrastructure claim.
