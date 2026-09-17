# MG-DE-005 Implementation Record

**Baseline:** `2e356a18e5b96ba3324edcc413dc0062187ba22c`
**Status:** Ready for controlled manifest reacquisition
**Database synchronization authorized:** No

## Implemented boundary

- fixed the real-source pilot to 48 exact chemical systems, an explicit
  0.05 eV/atom near-stability ceiling, and a 3,000-material bound;
- added a minimal release reader that never emits the API key;
- added offline manifest inspection with explicit count, elemental coverage,
  property coverage, completion, formula, polymorph, stability, duplicate, and
  rejection evidence;
- strengthened manifest loading so a valid digest alone cannot bypass
  normalized scope, count, source-identity, ordering, finite-value, elemental,
  or composition-fraction invariants;
- retained refusal to overwrite manifest and inspection outputs;
- preserved manifest-only acquisition as the default, without importing
  database modules.

## Scope revision

The first execution at 0.1 eV/atom stopped at 3,000 accepted identities before
15 Na systems were visited. The non-qualifying manifest was retained as
external evidence and was never imported. Offline sensitivity found 1,455 of
the truncated records at 0.05 eV/atom. The revised implementation increments
the selection contract to version 3 and enforces 0.05 eV/atom in the offline
inspector before controlled reacquisition.

## Acceptance boundary

Repository tests can verify deterministic validation and offline behavior, but
they do not establish the current Materials Project release, license terms, API
response, cohort size, or scientific usefulness. MG-DE-005 closes only after an
independent operator records an accepted manifest and inspection report and a
reviewer accepts the cohort and attribution evidence.

## Rollback

This implementation does not change a schema or database. Before integration,
rollback is deletion of the branch. After integration, revert the implementation
commit. Any independently captured manifest remains external evidence and must
not be applied merely because the tooling was reverted or retained.
