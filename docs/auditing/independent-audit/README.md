# MaterialGraph Independent Audit

## Status

Independent inspection is in progress. No implementation remediation is authorized or underway. Reconciliation with the earlier `MG-AUD-001`–`MG-AUD-094` work has not begun.

## Review baseline

- Repository: `MaterialGraph/materialgraph`
- Branch at initialization: `main`
- Reviewed commit: `a1605e61f72035890692ab4df63ebd2f7b859069`
- Commit timestamp: 2026-08-21 06:49:29 UTC
- Tree SHA: `126dd7478eda3c97d10f5b2930493d3a41ffe622`
- Inventory: 252 tracked files, 45 directories, 200 Python files
- Runtime limitation: the exact checkout is not present in the audit workspace, so source compilation was possible for uploaded files but database-backed tests and full-repository caller searches were not executed here

The immutable commit is the controlling baseline. Uploaded files are treated as evidence for that baseline only where their content matches the reviewed repository revision.

## Independence boundary

During the independent pass:

- do not use previous `MG-AUD-*` findings or remediation records as a checklist;
- do not modify the completed `MG-AUD` register;
- do not begin reconciliation before independent inspection is complete;
- do not implement fixes;
- refer security matters to the separate `MG-SEC-*` workstream without assigning an `MG-IA` number.

References to earlier audit IDs encountered inside current tests are treated only as current-code text. Their earlier finding details are not consulted.

## Evidence threshold

A defect or material risk is confirmed only when the available evidence establishes:

1. a reachable or directly reproducible behavior;
2. an expected invariant or contract supported by code, schema, documentation, mathematics, or project principles;
3. a material technical or scientific consequence; and
4. enough context to exclude a reasonable intentional interpretation.

If any element remains uncertain, the item stays an observation. Later evidence may confirm, narrow, dismiss, or reclassify an item. Retired finding identifiers are not reused.

## Classification

- `MG-IA-NNN`: independently confirmed defect or material risk
- `MG-IA-IMP-NNN`: worthwhile improvement that is not a defect
- `OBS-NNN`: matter requiring more evidence

## Review method

Each component is traced vertically through persistence, services, schemas, routes, callers, tests, and non-audit documentation. Passing tests are evidence, not proof of correctness. Sound behavior and negative results are recorded alongside defects.

## Current progress

Reviewed so far:

- configuration, packaging, startup, health, and version resolution;
- SQLAlchemy domain models and all three Alembic revisions;
- Materials Project import orchestration and normalization;
- composition persistence and legacy fallback behavior;
- canonical risk seeding;
- material risk and criticality aggregation;
- stability evidence and material quality;
- candidate screening;
- sensitivity analysis;
- substitution analysis;
- supporting Pydantic schemas, routes, and tests supplied for those components.

Current strict-threshold result:

- 6 confirmed findings;
- 9 open observations;
- 2 improvements;
- 4 retired finding identifiers following evidence-threshold correction;
- 0 remediations;
- 0 reconciled items.

## Directory structure

- `INDEPENDENT_AUDIT_REGISTER.md` — canonical independent-pass register
- `evidence/` — stack evidence, inventory, and positive/negative checks
- `findings/` — one record per confirmed `MG-IA-*` item
- `improvements/` — worthwhile non-defect improvements
- `reconciliation/` — reserved until independent inspection is complete
