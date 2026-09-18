# MG-DE-006 Implementation Record

**Baseline:** `250753628ec84d6e0c269b722c84e0ba4bd61aea`
**Status:** Verified and closed
**Database synchronization authorized:** No

## Implemented boundary

- added an offline scientific cohort analyzer with no application database or
  Materials Project client dependency;
- measures all requested systems, zero-result and sparse systems, chemistry
  families, elements, disjoint energy bands, and formula multiplicity;
- binds execution to the exact MG-DE-005 payload digest, source, selection
  contract, accepted count, completeness, and duplicate count;
- keeps integrity readiness separate from the pending scientific decision;
- emits `database_import_authorized: false` and refuses to overwrite evidence.

## Scientific boundary

The implementation reports facts and does not encode arbitrary scientific
balance thresholds. Independent review must decide whether lithium dominance,
thin sulfide coverage, two complete-query source zeroes, the near-stable
majority, and polymorph density are proportionate to the focused initial use.

## Independent result

At commit `c7ebc1a1a2b4be66036b1a56b68b384226830095`, focused validation
reported 43 passed and the complete suite reported 901 passed, 1 skipped.
Automation pins, the dependency contract, Ruff, and the diff check passed.

The exact qualified manifest passed every integrity gate. Independent offline
review recorded 46 represented systems, two source-zero systems, 15 sulfides,
141 source-stable materials, 1,586 bounded near-stable materials, 651 unique
formulas, and 1,310 materials in polymorph groups. The reviewed decision and
limitations are preserved in the
[scientific cohort report](../MG-DE_SCIENTIFIC_COHORT_REPORT.md).

## Rollback

No schema, database, deployment, or external evidence is changed. Before
integration, delete the branch. After integration, revert the implementation
commit. Reverting the tool does not authorize use of the manifest.
