# MG-IA-008 Remediation Verification

## Title

Material-import batches roll back completely on failure

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test database.

## Acceptance criteria

1. A batch containing an earlier valid candidate and a later invalid candidate
   does not leave the earlier candidate pending or persistent.
2. Database flush or integrity failures roll back the failed transaction.
3. The session is usable for a subsequent successful import after either a
   validation or database failure.
4. Successful batches retain the existing commit behavior and imported-count
   contract.
5. Transaction ownership is explicit: the service commits the complete batch
   on success and rolls back all pending changes on failure.
6. The production caller continues to provide a dedicated import session, so
   rollback cannot discard unrelated application work.

## Caller and transaction review

Repository-wide caller tracing found one production caller:
`scripts/import_materials_project.py`. It creates a dedicated `SessionLocal`
session, passes it to `MaterialImportService`, and closes it after the import
loop. Tests instantiate the service with their isolated database session.

Because the service already committed on success, it already owned the session
transaction. The remediation preserves that contract and adds the missing
failure-side rollback rather than moving transaction ownership or introducing
a second nested boundary.

## Implemented changes

- Wrapped candidate mutation, flush, and commit behavior in one guarded batch.
- Added `Session.rollback()` for every exception path, then re-raised the
  original exception.
- Documented that callers must provide a session dedicated to the import
  operation.
- Added a valid-then-invalid regression proving earlier mutations are removed
  and the session can be reused.
- Added a real unique-constraint failure regression proving database failure
  rollback and subsequent session reuse.

## Verification results

Commands:

```powershell
pytest tests/services/material/test_material_import_service.py -v
pytest tests/scripts/test_backfill_material_element_fractions.py tests/test_project_configuration.py -v
pytest -q
ruff check .
git diff --check
```

Results:

- focused material-import tests: **15 passed in 10.10 seconds**;
- adjacent backfill and project-configuration tests:
  **12 passed in 0.19 seconds**;
- complete test suite: **649 passed in 25.74 seconds**;
- Ruff: **passed**;
- Git whitespace validation: **passed**.

The suite increased from 647 to 649 tests because this remediation added two
transaction-integrity regressions.

## Remaining boundary

The service-owned transaction includes every pending change on the supplied
session. This is intentional and now explicit. Reusing a session containing
unrelated pending application work would allow success to commit, or failure
to roll back, that unrelated work. The sole production caller avoids that risk
by creating a dedicated import session.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-008` is verified as remediated.
