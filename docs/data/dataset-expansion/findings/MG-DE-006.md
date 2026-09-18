# MG-DE-006: Scientific usefulness of the qualified cohort is unreviewed

**Status:** Ready for verification
**Priority:** Scientific import gate
**Production blocker:** Yes

## Observation

MG-DE-005 established an immutable, source-complete, technically valid
1,727-material manifest. It also exposed material imbalance: lithium appears
in 1,213 records, sulfur in 15, 1,310 records belong to polymorph groups, and
`Li-Fe-S` and `Na-Ni-S` returned no records at the approved energy ceiling.
Those facts do not by themselves establish usefulness or unsuitability.

## Risk

Importing before review could present a focused and imbalanced cohort as a
representative materials dataset. It could also make sparse sulfide evidence,
source zeroes, near-stability, and polymorph multiplicity invisible to users.

## Required resolution

- verify the exact qualified manifest before analysis;
- record every requested system, including zero-result and sparse systems;
- measure chemistry-family, element, stability, and polymorph distributions;
- judge fitness only against the stated focused product scope;
- define Materials Project attribution presentation;
- retain limitations in product and dataset-version evidence;
- issue an explicit decision before any database import.

## Acceptance criteria

MG-DE-006 can close only when independent output from the offline review tool
has no integrity failures and the repository records a reviewed scientific
decision with its limitations. Tool execution alone does not close this
finding. Until closure, PostgreSQL, Neon, and production import remain
unauthorized.
