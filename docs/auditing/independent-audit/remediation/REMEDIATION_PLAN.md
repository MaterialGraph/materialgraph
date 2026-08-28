# Independent-Audit Remediation Plan

## Status

Completed. All five batches were executed and verified. The final closure
review also hardened retired `MG-IA-022` by making Alembic's explicit
configuration invariant independent of import order. This document preserves
the planned sequencing; current status is authoritative in
`REMEDIATION_REGISTER.md`.

## Sequencing principle

Remediation follows technical dependency and risk, not numerical ID order.
Closely related findings may share one batch, but each retains separate
acceptance criteria and verification evidence.

## Initialization gate

Before Batch 1:

- obtain a usable MaterialGraph repository checkout;
- record HEAD, branch, tree, remotes, and worktree state;
- compare HEAD with audited commit
  `a1605e61f72035890692ab4df63ebd2f7b859069`;
- preserve unrelated user changes;
- inspect Git history for `MG-IA-011` and `MG-IA-016`; and
- confirm existing tests and all callers against the checkout.

## Proposed batches

### Batch 1 — bounded search and objective/null semantics

- `MG-IA-011`: neighborhood limits must bound accepted membership and
  descendant expansion.
- `MG-IA-016`: preferred elements must remain soft unless a separately
  documented hard constraint is requested.
- `MG-IA-017`: scientific-pathway summaries must propagate nullable risk
  without arithmetic failure or favorable classification.

These findings have strong current evidence and focused behavioral contracts.
They must still be implemented separately if their affected callers or tests
make a combined change unsafe.

### Batch 2 — persistence and quantitative scientific correctness

- `MG-IA-003`, `MG-IA-008`, `MG-IA-009`, `MG-IA-010`, `MG-IA-014`.

Migration and transaction items require isolated database verification.
Scientific calculations require numeric fixtures that demonstrate invariants,
not merely changed expected constants.

### Batch 3 — determinism, graph correctness, and bounded APIs

- `MG-IA-004`, `MG-IA-012`, `MG-IA-013`, `MG-IA-015`, `MG-IA-019`,
  `MG-IA-020`.

### Batch 4 — contracts, provenance, and configuration

- `MG-IA-007`, `MG-IA-018`, `MG-IA-021`.

### Batch 5 — documentation and deployment accuracy

- `MG-IA-023`, `MG-IA-024`, `MG-IA-025`, `MG-IA-026`.

Documentation corrections should follow the stabilized runtime contract so
they do not need to be rewritten during earlier code batches.

## Verification requirement per finding

Each `Verified` status requires:

- explicit acceptance criteria;
- pre-fix reproduction or failing regression test;
- focused test command and result;
- adjacent service/API test command and result;
- complete test-suite command and result;
- Ruff command and result;
- deterministic repeat or bounded-work check where applicable;
- API/schema and explanation review where applicable;
- database migration upgrade/downgrade evidence where applicable; and
- change-impact entry when external behavior changes.
