# MaterialGraph Independent-Audit Remediation

## Status

Initialization complete. No implementation remediation has started.

The governing independent audit is frozen at commit
`a1605e61f72035890692ab4df63ebd2f7b859069`. Findings, observations,
improvements, and reconciliation judgments must not be rewritten to make later
remediation appear part of the independent pass.

## Boundaries

- Remediation identifiers retain their corresponding `MG-IA-*` finding IDs.
- The completed `MG-AUD-*` register remains unchanged.
- Security concerns remain in the separate `MG-SEC-*` workstream.
- Every implementation change requires a regression test and recorded
  verification evidence.
- External behavior changes require a change-impact record.

## Workflow

1. Establish the exact remediation Git baseline and worktree state.
2. Resolve chronology for `MG-IA-011` and `MG-IA-016` from Git history.
3. Define acceptance criteria and affected callers before editing code.
4. Add or identify a regression test that fails for the confirmed behavior.
5. Apply the smallest coherent implementation correction.
6. Run focused, adjacent, full-suite, and Ruff verification.
7. Record commands, results, commit, affected contracts, and remaining risks.
8. Update the remediation register and change-impact history.

## Records

- `REMEDIATION_REGISTER.md` — authoritative remediation status table.
- `REMEDIATION_PLAN.md` — priority clusters, sequencing, and batch boundaries.
- `verification/` — exact test and inspection evidence.
- `change-impact/` — externally visible or system-level behavior changes.

## Current blocker

The audit workspace does not contain a usable repository checkout. Git cannot
resolve a worktree, HEAD, or history. The exact current MaterialGraph checkout
must be placed in this workspace before chronology inspection, test execution,
or implementation changes begin.
