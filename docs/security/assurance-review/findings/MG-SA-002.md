# MG-SA-002 — Workflow success is overstated as an enforced security gate

**Classification:** Verification defect
**Priority:** Medium
**Affected Stage 1 controls:** `MG-SEC-010` and, secondarily, `MG-SEC-011`
**Status:** Verified and closed on 2026-09-14

## Assurance claim

Stage 1 describes production dependencies as vulnerability-gated and lists a
passing push/pull-request workflow as acceptance evidence.

## Independent evidence

For the reviewed SHA, the Dependency Security and Secret Scan jobs both ran and
passed. The dependency job performed a real hash-locked clean installation,
`pip check`, installed-version reconciliation, and `pip-audit`, which reported
zero known vulnerabilities. The secret job ran the pinned scanner and reported
no leaks.

GitHub's branch and ruleset APIs independently show that `main` is unprotected,
has no applicable ruleset, and has no required status checks. GitHub documents
that Actions checks can also be skipped on `push` and `pull_request` events by
commit-message instructions.

## Why this is a verification defect

The current evidence proves that the reviewed SHA passed two workflows. It
does not prove that a future commit must pass before it becomes `main` or is
deployed. A direct push, skipped workflow, cancelled/failing run, or deployment
performed before completion can therefore bypass the claimed gate without
changing the workflow files.

The underlying lock, audit, reconciliation, and immutable-reference controls
are correctly implemented for runs that execute. The defect is the stronger
verification claim, not evidence of a vulnerable dependency in the reviewed
commit.

## Required assurance correction

At minimum, future records must say “automated checks run and alert” unless an
enforced rule or deployment precondition is independently verified. If the
project chooses an enforced gate, its bypass policy and deployment coupling
must be tested. This assessment makes no GitHub setting change.

## Remediation disposition

The live dependency and deployment guidance now explicitly identifies the
workflows as automated audits rather than protected-branch gates. Production
deployment requires successful Dependency Security and Secret Scan evidence
for the exact candidate SHA, including confirmation that substantive steps were
not skipped. The current solo-maintainer lack of protected-branch enforcement
remains an accepted residual risk and is not presented as a verified control.

See [`../remediation/MG-SA-002.md`](../remediation/MG-SA-002.md). Closure is
supported by maintainer validation, successful workflows on the accepted
correction commit, and fresh read-only branch/ruleset evidence.

## Closure evidence

- Accepted correction commit:
  `7786aa954fd1c83d49900dd03dad02924a3d8111`.
- The focused configuration suite passed with `32 passed`; the authoritative
  complete suite passed with `841 passed, 1 skipped`; both repository
  validators, Ruff, whitespace, and worktree checks passed.
- Fresh GitHub Settings evidence showed no repository rulesets and no classic
  branch protection, confirming rather than contradicting the corrected manual
  enforcement boundary.
- Secret Scan run `34831604742`, job `103935983896`, passed on attempt one for
  the exact correction SHA; automation-pin validation and Gitleaks both ran and
  succeeded.
- Dependency Security run `34831604715`, job `103935983504`, passed on attempt
  one for the exact correction SHA; pin and contract validation, hash-locked
  tooling installation, production-lock audit, clean environment build,
  `pip check`, and installed-version reconciliation all ran and succeeded.

The verification defect is closed because the live claims now match the actual
control boundary. This closure does not claim that GitHub blocks unchecked
updates to `main`.
