# MG-DE-002: Dataset provenance and refresh semantics are incomplete

**Status:** Closed
**Priority:** First implementation wave
**Initial expansion blocker:** Yes

## Observation

Materials retain a source string and raw JSON, and `mp_id` is unique. The model
does not identify the upstream dataset release, retrieval event, import run, or
normalization contract. When an `mp_id` already exists, the importer skips it;
it does not determine whether the source record is unchanged, updated,
conflicting, or retired.

## Impact

The expanded dataset would not be reproducible as a named scientific release,
and later refreshes could silently retain stale data or apply inconsistent
normalization. Source identity is also not sufficient by itself to define
canonical material, structure, phase, polymorph, and alias relationships.

## Required outcome

- approved source, licensing, and inclusion contract;
- source release/version and retrieval timestamp;
- immutable import-run identity and manifest digest;
- versioned normalization contract;
- canonical/source identity and polymorph/alias rules;
- explicit insert, update, unchanged, conflict, reject, and retirement states;
- preserved missingness and uncertainty semantics.

## Acceptance evidence

Migration and service tests must demonstrate provenance persistence and every
refresh state. A complete manifest must reproduce the accepted dataset from the
same authorized source inputs.

## Implementation checkpoint

Manifest schema v2 now binds the declared Materials Project database release,
timezone-aware retrieval time, CC BY 4.0 license, normalization version,
selection-contract version, and complete selection scope into the manifest
digest. The source client verifies the API heartbeat release before every page
and fails closed if it changes or differs from the declaration.

Migration `c8f3a2d7e901` adds immutable import-run headers, current source identity
records, per-scope memberships, and append-only outcome events. The refresh service classifies
inserted, updated, unchanged, conflicted, rejected, and retired records; same-run
chunk replay reuses recorded outcomes. Missing optional values remain null, and
ambiguous pre-existing identities are preserved as conflicts.

## Closure evidence

Independent verification at commit
`3e8eb2975a679594b73dcc86c6ebe99d415864fd` confirmed the single Alembic head
`c8f3a2d7e901` against `materialgraph_test`. The PostgreSQL migration test, all
18 refresh-service tests, and the PostgreSQL interruption/resume lifecycle test
passed. The complete focused suite reported 76 passed, and the complete suite
reported 869 passed with 1 skipped. Automation-pin, dependency-contract, Ruff,
and diff-hygiene checks also passed.

GitHub Dependency Security run 13 and Secret Scan run 99 passed for the same
commit. This closes the provenance and refresh-semantics implementation gap for
the initial expansion gate. It does not qualify representative-scale behavior
under MG-DE-004 and does not authorize a source request, production migration,
or production import.
