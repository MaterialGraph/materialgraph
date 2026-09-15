# MG-DE-002: Dataset provenance and refresh semantics are incomplete

**Status:** Ready for independent PostgreSQL verification
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

The finding is not closed. The migration, composed refresh lifecycle, complete
suite, and deterministic manifest behavior must be independently reproduced
against the PostgreSQL test database first. No source request, production
migration, or production import is authorized by this checkpoint.
