# MG-SA-002 — Workflow success is overstated as an enforced security gate

**Classification:** Verification defect
**Priority:** Medium
**Affected Stage 1 controls:** `MG-SEC-010` and, secondarily, `MG-SEC-011`
**Status:** Confirmed during read-only assessment; not remediated

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
