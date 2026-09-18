# MG-DE-007: The approved real cohort lacks PostgreSQL qualification

**Status:** Closed
**Initial expansion blocker:** Yes (resolved for local PostgreSQL)
**Production blocker:** Yes (separate Neon and production gates remain)

## Finding

The exact 1,727-identity Materials Project cohort has passed manifest integrity
and scientific review, but has not been applied to PostgreSQL. Curated-row
preservation, `mp-19017` conflict behavior, polymorph crowding in actual
product responses, exact-manifest recovery, idempotency, real-data query
plans, and backup behavior therefore remain unproven.

## Acceptance criteria

- all requirements in the MG-DE-007 qualification plan pass;
- all 28 curated materials and complete reference responses are unchanged;
- all 28 curated overlaps are explained conflicts, including `mp-19017` for
  material ID 5;
- clean import and fresh rerun reconcile exactly;
- failed and committed chunk recovery complete without duplicate events or
  source identities;
- representative endpoints remain bounded and their formula crowding is
  explicitly measured without identity collapse;
- real-data plan, latency, query-count, database-time, allocation, and backup
  evidence is retained;
- focused/full tests and repository checks pass;
- Neon and production remain unauthorized.

## Evidence required

Independent execution against disposable local PostgreSQL plus preserved
external evidence inventory, hashes, environment details, and a reviewed
closure report.

## Resolution

The exact approved manifest completed independent disposable-PostgreSQL
qualification. All 28 curated overlaps produced explained conflicts, the
protected curated state and complete sentinel API responses were unchanged,
fresh rerun and both recovery modes reconciled exactly, and the custom-format
backup passed archive-list validation without restoration.

All representative requests returned HTTP 200. Broad list, neighbor, family,
and screening responses demonstrated material formula crowding, while bounded
ranked results were generally more diverse. Polymorph identities remain
preserved; presentation-level grouping or diversification is future product
work. See `MG-DE_REAL_DATA_QUALIFICATION_REPORT.md`.

MG-DE-007 does not authorize Neon or production writes. Isolated
non-production Neon qualification remains the next separately reviewed gate.
