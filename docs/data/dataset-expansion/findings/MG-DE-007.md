# MG-DE-007: The approved real cohort lacks PostgreSQL qualification

**Status:** In progress
**Initial expansion blocker:** Yes
**Production blocker:** Yes

## Finding

The exact 1,727-identity Materials Project cohort has passed manifest integrity
and scientific review, but has not been applied to PostgreSQL. Curated-row
preservation, `mp-19017` conflict behavior, polymorph crowding in actual
product responses, exact-manifest recovery, idempotency, real-data query
plans, and backup behavior therefore remain unproven.

## Acceptance criteria

- all requirements in the MG-DE-007 qualification plan pass;
- all 28 curated materials and complete reference responses are unchanged;
- `mp-19017` is an explained conflict for material ID 5;
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
