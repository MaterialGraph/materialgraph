# MG-IA-003 Remediation Verification

## Title

Populated predecessor databases upgrade through the core-domain migration

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test database.

## Acceptance criteria

1. Revision `1d204c6d38c0` can add `materials.source` when valid material rows
   already exist at predecessor revision `4368e3ecc291`.
2. The migration does not invent Materials Project provenance for predecessor
   rows whose source is not established.
3. Existing rows receive an explicit governed value before the column becomes
   non-null.
4. The final migrated schema retains the application model's non-null source
   contract.
5. The regression test does not mutate the persistent test schema or require
   downgrading an existing database.

## Implemented changes

- Added `materials.source` as nullable during the migration transition.
- Backfilled predecessor rows with the explicit provenance state
  `legacy_unknown`.
- Altered the populated column to `NOT NULL` after the backfill.
- Added a PostgreSQL regression that applies both migrations inside an
  isolated temporary schema, inserts a predecessor material, verifies the
  backfill and final nullability, and rolls back the transaction.

## Verification results

Commands:

```powershell
pytest tests/migrations/test_core_domain_migration.py -v
pytest tests/services/material/test_material_import_service.py tests/test_project_configuration.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- populated-predecessor migration regression: **1 passed in 0.35 seconds**;
- adjacent import and project-configuration tests:
  **18 passed in 21.07 seconds**;
- complete test suite: **647 passed in 20.25 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; Windows emitted informational
  LF-to-CRLF working-copy warnings only.

The suite increased from 646 to 647 tests because this remediation added one
PostgreSQL migration regression.

## Existing-installation scope

Databases that already recorded revision `1d204c6d38c0` do not rerun the
edited migration and receive no data or schema mutation from this change. The
correction governs future migration replay and upgrades from the predecessor
revision. No production downgrade was performed or required.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-003` is verified as remediated.
