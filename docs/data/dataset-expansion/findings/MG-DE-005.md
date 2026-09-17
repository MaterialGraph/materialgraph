# MG-DE-005: A reviewed real-source pilot manifest is absent

**Status:** Ready for controlled execution
**Priority:** Real-data expansion gate
**Production blocker:** Yes

## Observation

The ingestion lifecycle is qualified with a deterministic synthetic fixture,
but no immutable manifest from the current Materials Project API release has
been acquired and reviewed. Synthetic evidence cannot establish current source
terms, real property coverage, real rejection behavior, or the usefulness and
bias of the selected scientific cohort.

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

The [real-source pilot plan](../MG-DE_REAL_SOURCE_PILOT.md) fixes the initial
48-system, near-stable scientific scope and acceptance gates. The release
reader exposes only the authoritative database version. The offline inspector performs semantic
validation and produces a bounded cohort report without network or database
access. This finding remains open until independent acquisition and review
evidence are recorded.
