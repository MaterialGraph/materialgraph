# MG-DE-005: A reviewed real-source pilot manifest is absent

**Status:** Closed
**Priority:** Real-data expansion gate
**Production blocker:** Yes

## Observation

The first immutable manifest from Materials Project release `2026.04.13`
correctly failed the source-completeness gate at 3,000 materials. The revised
version 3 acquisition at 0.05 eV/atom completed all 48 source queries and
passed every MG-DE-005 structural, provenance, boundedness, elemental, and
property-coverage gate with 1,727 accepted identities.

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
produces a bounded cohort report without network or database access. The
independent inspection and source-terms record close this finding. The
[qualified manifest report](../MG-DE_QUALIFIED_MANIFEST_REPORT.md) preserves
the exact evidence and limitations. Scientific cohort review is intentionally
separated into MG-DE-006, and no database import is authorized by this closure.
