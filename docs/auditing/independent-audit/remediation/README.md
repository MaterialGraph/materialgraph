# MaterialGraph Independent-Audit Remediation

## Status

Complete. All 20 actionable independent findings are verified, `MG-IA-011` is
not actionable after exact-baseline revalidation, and no remediation row is
pending. Retired `MG-IA-022` received separately recorded defense-in-depth
hardening during closure. See `../FINAL_AUDIT_CLOSURE.md`.

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

## Closure

The repository baseline, chronology, focused/adjacent/full verification, Ruff,
and Git whitespace evidence are recorded per finding. The remediation register
is authoritative for current status. Security remains a separate active
`MG-SEC-*` workstream.
