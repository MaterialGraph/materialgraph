# Stack 02 Evidence — Models, Migrations, and Material Intelligence

## Scope

Reviewed ORM models; all three Alembic revisions; Materials Project wrapper, client normalization, importer, composition service, core/risk seeders; risk evidence policy; risk and criticality services/schemas/routes/tests; stability evidence; quality; candidate screening; sensitivity; substitution; and supplied regression tests.

All uploaded Python files compiled successfully. `criticality_service(4).py` and `criticality_service(5).py` were byte-identical.

## Vertical traces

### Migration

The linear revision chain is `4368e3ecc291` → `1d204c6d38c0` → `f1a8b10be960`. Head schema generally matches the supplied ORM models. Adding non-null `materials.source` without a default/backfill cannot upgrade a valid populated predecessor database (`MG-IA-003`).

### Composition/import

Structured Materials Project amounts are normalized to positive finite fractions with exact membership validation. Legacy/manual missing composition instead becomes `1.0` per element, is persisted as `fraction`, and is consumed as equal composition by criticality and quality (`MG-IA-009`). The importer commits on success but does not roll back partial pending changes on failure (`MG-IA-008`). First-page selection and skip-existing behavior remain policy observations.

### Risk/criticality

Canonical risk data is validated on a 1–10 scale, source-labelled, deterministic, and idempotent. Missing and all-null evidence remain unknown. Coverage is explicit. Computed outputs omit the stored source of the selected profile (`MG-IA-007`). Criticality result ordering lacks a deterministic secondary key for equal/unknown scores (`MG-IA-004`).

### Screening/quality/substitution

Unknown risk receives no numeric low-risk benefit. Screening and substitution use stable ID tie-breakers. Substitution exposes missing evidence and deliberately ranks known evidence before unknown evidence. Stability evidence avoids double-counting correlated fields. Quality requires complete risk evidence for a risk-derived bonus. Partial-criticality quality semantics remain an observation.

### Sensitivity

Baseline screening penalizes an aggregate material-risk mean. Sensitivity applies a one-dimension change directly at the full aggregate penalty weight rather than recomputing through dimension and material aggregation. Supplied tests characterize this formula but do not verify parity with baseline recomputation (`MG-IA-010`).

## Negative findings

No defect was confirmed merely because database check constraints, ORM relationships, or alternate weighting methods were absent. Equal-element risk aggregation and evidence-tier substitution ranking are explicit policies, not implementation defects. Unknown-energy filtering remains unresolved because hard-constraint semantics were not supplied.

## Execution limitation

The review used immutable repository retrieval and directly supplied files. Database migrations and pytest were not executed in this workspace; confirmed findings rely on direct SQL/Python semantics and caller traces. Runtime-dependent matters remain observations.
