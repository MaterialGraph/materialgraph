# MG-DE-004: Representative scale evidence is absent

**Status:** Open
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
