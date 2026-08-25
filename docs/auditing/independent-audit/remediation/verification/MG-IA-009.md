# MG-IA-009 Remediation Verification

## Title

Unknown composition remains distinguishable from quantitative composition

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL `materialgraph_test` database.

## Acceptance criteria

1. Membership-only imports remain usable for element membership without being
   represented as known quantitative composition.
2. Structured, validated composition is explicitly marked as known.
3. Historical rows are conservatively migrated as unknown rather than inferred
   from previously stored fallback values.
4. Backfill promotes evidence to known only when validated structured source
   composition is available.
5. Unknown composition does not produce a composition-weighted material
   criticality score.
6. Public element details expose unknown fractions as `null` and disclose the
   composition evidence status and coverage.
7. Material quality does not gain a criticality contribution derived from
   unknown composition and exposes the relevant evidence metadata.
8. The migration and backfill are operationally safe and the backfill is
   idempotent.

## Implemented changes

- Added `MaterialElement.fraction_known` as an explicit per-link evidence flag.
- Added Alembic revision `7a4c2e91b6d8`, conservatively marking all predecessor
  rows unknown with a non-null server default of `false`.
- Marked newly imported structured compositions known and membership-only
  fallback values unknown.
- Updated composition backfill to promote validated rows to known while
  reporting previous evidence state and counting evidence-only changes.
- Prevented weighted material criticality aggregation unless composition
  evidence is complete for every material-element link.
- Preserved element-level criticality evidence even when the material-level
  weighted aggregate is unavailable.
- Added public composition evidence status, completeness, coverage, counts,
  and unknown-element disclosure; unknown per-element fractions serialize as
  `null`.
- Propagated composition evidence metadata through material-quality responses.

## Database verification

The migration test ran against the explicitly selected PostgreSQL
`materialgraph_test` database and passed. `alembic upgrade head` then applied
revision `7a4c2e91b6d8` successfully.

The first successful backfill dry run reported:

- discovered and eligible materials: **28**;
- prospective updated materials: **28**;
- prospective updated links: **94**;
- failed materials: **0**;
- every predecessor `fraction_known` value: **false**;
- numeric fractions before and after: **unchanged**.

After applying the backfill, a second dry run reported:

- discovered and eligible materials: **28**;
- updated materials: **0**;
- updated links: **0**;
- already correct: **28**;
- failed materials: **0**.

This demonstrates that the operation annotates validated evidence without
rewriting the established normalized fraction values and is idempotent.

## Test verification

Commands:

```powershell
pytest tests/migrations/test_fraction_evidence_migration.py tests/services/material/test_material_composition_service.py tests/services/material/test_material_composition_evidence.py tests/services/material/test_material_import_service.py tests/services/material/test_criticality_service.py tests/services/material/test_material_quality_service.py tests/api/test_material_neighbors_api.py -v
pytest tests/services/material/test_similarity_service.py tests/services/material/test_recommendation_service.py tests/services/research/test_scientific_pathway_analysis_service.py tests/api/test_material_risks_api.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused migration, import, backfill, criticality, quality, and API tests:
  **55 passed**;
- adjacent similarity, recommendation, pathway-analysis, and risk-API tests:
  **63 passed in 1.49 seconds**;
- complete test suite: **655 passed in 17.73 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

The suite increased from 649 to 655 tests through one migration regression,
three composition-evidence regressions, one criticality regression, and one API
contract regression.

## Deployment boundary

Local verification does not authorize an automatic production data change.
For Neon or another deployed database, deploy the matching application model
and migration together, confirm the target database, apply the migration, run
the backfill in dry-run mode, review its summary, apply it explicitly, and
repeat the dry run to confirm idempotency. Take a restorable database backup or
branch before applying the production backfill.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-009` is verified as remediated.
