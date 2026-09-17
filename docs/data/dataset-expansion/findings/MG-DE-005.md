# MG-DE-005: A reviewed real-source pilot manifest is absent

**Status:** Ready for controlled re-execution
**Priority:** Real-data expansion gate
**Production blocker:** Yes

## Observation

The first immutable manifest from Materials Project release `2026.04.13` was
captured and inspected without database access. It reached the 3,000-material
bound before most Na systems were traversed and correctly failed the
source-completeness gate. A revised manifest under the reviewed 0.05 eV/atom
selection ceiling has not yet been acquired and reviewed.

## Risk

Importing directly from a live API would make the dataset scope difficult to
reproduce and could introduce unreviewed licensing, selection, missing-value,
identity, or coverage assumptions. Using the production Neon database for the
first execution would combine source discovery with an irreversible operational
change.

## Required resolution

- approve a focused, bounded source selection before retrieval;
- record the current authoritative source release and retrieval time;
- create an immutable manifest without database access;
- validate its digest and semantic structure offline;
- record cohort, coverage, duplicate, rejection, and completion evidence;
- independently review current attribution and source terms;
- keep PostgreSQL import, Neon qualification, and production rollout outside
  MG-DE-005.

## Implemented control

The [real-source pilot plan](../MG-DE_REAL_SOURCE_PILOT.md) preserves the
48-system scientific scope and acceptance gates while narrowing the
near-stability ceiling from 0.1 to 0.05 eV/atom based on recorded offline
sensitivity evidence. The release reader exposes only the authoritative
database version. The offline inspector performs semantic validation and
produces a bounded cohort report without network or database access. This
finding remains open until the revised manifest passes independent inspection
and scientific and attribution review.
