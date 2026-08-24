# MG-IA-008 — Failed material-import batch can leave partial pending session changes

- Classification: transaction-integrity risk
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Evidence

`import_materials()` mutates and flushes each candidate sequentially, commits after the loop, and has no exception rollback. A later invalid candidate can raise after earlier candidates were added and flushed.

Affected files/functions: `app/services/material/import_service.py:import_materials`, `_create_material`, and `_link_elements`; invoked by `scripts/import_materials_project.py:main`.

## Expected versus actual

A failed batch should have an explicit atomicity contract. Because the service owns the success commit but not failure cleanup, callers can catch an exception and later commit partial changes left by the failed operation.

## Impact

Failed imports can become partially persistent and leave the session unusable after database exceptions unless callers know to roll it back.

## Tests

Supplied tests reject invalid single candidates but do not exercise valid-then-invalid batches, flush failures, rollback, or session reuse.

## Reproduction and caller trace

Call `import_materials([valid_candidate, invalid_candidate])`, catch the exception, then inspect `Session.new`/the transaction or commit the session. The command wrapper closes its session, but the reusable service owns its success commit and exposes no failure-cleanup contract.

## Remediation scope

Define transaction ownership, validate before mutation where possible, and guarantee rollback or caller-controlled transaction semantics with atomicity tests.
