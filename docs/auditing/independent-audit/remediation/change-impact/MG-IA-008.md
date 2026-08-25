# MG-IA-008 Change Impact — Atomic Material-Import Failure Handling

## Status

Verified locally: 15 focused tests, 12 adjacent tests, 649 full-suite tests,
Ruff, and Git whitespace validation passed.

## Before

The material-import service flushed candidates sequentially and committed only
after the loop. If a later validation or database operation failed, earlier
mutations remained pending and database errors left the session in a failed
transaction state. A caller that caught the exception could later persist
partial work or encounter a pending-rollback error.

## After

The complete import batch commits on success. Any validation, flush, integrity,
or commit exception rolls back the transaction before the original exception
is re-raised. The same session can then perform another import.

## Impact

- Transaction integrity: **Yes** — failed batches no longer retain partial
  pending imports.
- Session recovery: **Yes** — failure paths perform the required rollback.
- Successful import behavior: **Unchanged** — one complete batch still commits
  and returns its imported count.
- Runtime API behavior: **No change** — the importer is script/service-facing.
- Scientific scoring or ranking: **No change**.
- Database schema or migration: **No change**.
- Exception visibility: **Unchanged** — the original exception is re-raised.
- Caller requirement: **Explicitly documented** — use a dedicated import
  session because the service owns its transaction.
