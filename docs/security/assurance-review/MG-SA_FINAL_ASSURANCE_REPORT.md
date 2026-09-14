# MaterialGraph Stage 1 Final Assurance Report

**Review date:** 2026-09-14
**Commit:** `5e794292eb7e712d1840095254cd72217d553cb5`
**Accepted assurance baseline:** `154fd53fd0d1f7fdb195fb6e15e623d8ce0ba84a`
**Deployed remediation:** `9a7fb1115e00d4e3a1864bf86e1423f522af2af1`
**Phase:** `MG-SA-001` verified and closed; `MG-SA-002` remains open

## Executive conclusion

Stage 1 remains substantially valid. The remediation architecture is coherent,
proportionate to a public deterministic scientific prototype, and materially
stronger than the frozen pre-remediation baseline. Nine of eleven Verified
controls are sound in repository implementation, and the reasoning that
retired `MG-SEC-006` is correct.

Two assurance defects prevented an unqualified all-controls-confirmed
conclusion at the reviewed implementation:

1. `MG-SA-001` is an implementation defect in `MG-SEC-001/002`: mounted
   material-intelligence routes that scale with graph/data size bypass both the
   expensive-work admission gate and application deadline. The claimed Nginx
   site-wide connection cap is also implemented with a per-client key.
2. `MG-SA-002` is a verification defect in `MG-SEC-010`: current workflows
   passed, but no branch/ruleset/deployment rule makes them an enforced gate.

No regression and no separate new current vulnerability outside the original
Stage 1 control set was confirmed.

The `MG-SA-001` correction expanded application and proxy coverage to all
identified expensive material-intelligence routes, introduced an independent
complete mounted-route cost policy, and implemented distinct per-client and
aggregate Nginx connection zones. The authoritative suite, GitHub workflows,
production activation, direct classifier check, effective configuration,
bounded proxy probe, health checks, and complete scientific-response
comparisons passed. `MG-SA-001` is verified and closed.

`MG-SA-002` remains the only open assurance defect. It concerns whether
successful workflows are enforced, not the security result of the current
dependency or secret scans.

## Controls confirmed sound

- Secret-file metadata is fail-closed in code and startup configuration.
- The dedicated systemd identity and filesystem/capability restrictions are
  internally consistent.
- TLS configuration and the database-transport retirement rationale are sound
  in repository and historical evidence.
- Restricted database runtime/backup roles and isolated migration authority
  are proportionate; default `TEMP` is an explicit residual.
- Research and screening cardinality bounds occur before expensive processing;
  log messages use bounded counts rather than input collections.
- Database pool/connect, lock, and statement timeouts are applied with correct
  exception handling and transaction rollback behavior.
- For classified routes, a timed-out synchronous task retains admission
  capacity until exit, avoiding false slot release.
- Journald limits, daily disk monitoring, backup creation, checksum/manifest,
  retention, and isolated restoration form a coherent recovery design.
- Action SHA/container digest pinning and scanner read-only/no-network
  containment are correct.
- The hash-locked dependency contract, exact installed-environment
  reconciliation, and vulnerability audit are real controls, not string-only
  checks.
- Historical scientific regression evidence compares complete parsed JSON and
  ordering rather than selected keys.

## Controls needing correction

No remaining application or deployment correction is required for
`MG-SA-001`. `MG-SA-002` still requires either accurately qualified
automated-check language or an independently verified branch/deployment
enforcement policy.

## Verification claims needing qualification

- At the original reviewed commit, `MG-SEC-001` criteria “every mounted
  expensive scientific route” and “site-wide concurrency is 20” were false.
  The deployed correction now supports both claims.
- At the original reviewed commit, `MG-SEC-002` application-deadline coverage
  had the same route-scope gap. Repository and deployed coverage are corrected.
- `MG-SEC-010` proves successful automated audit runs, not an enforced gate on
  `main` or deployment.
- The original complete-suite result (`823 passed, 1 skipped`) remains
  historical evidence for its checkpoint. The remediation suite was
  independently run against the prepared PostgreSQL test database and passed
  with `840 passed, 1 skipped`. Isolated SQLite failures remain recorded as
  environment limitations rather than contradictory product evidence.
- The GitHub setting requiring full Action SHA pins could not be independently
  read through the available interface; repository references themselves are
  correctly pinned.

## Accepted residual risks

- solo-maintainer source governance without signed commits or branch
  protection, subject to the separate gate wording defect;
- database `TEMP` privilege for restricted roles;
- unrestricted EC2 egress under the current no-account/no-private-data/no-LLM
  boundary;
- public API documentation, liveness, and limited version/environment metadata;
- backup execution under the deployment account; and
- lack of a production destructive or recurring restore exercise during this
  read-only review.

## Future hardening

- canonicalize the HTTP redirect and reject unknown Host values;
- make backup code identity record or require a clean worktree;
- bind the development PostgreSQL port to loopback;
- validate substitution `top_n` semantics; and
- revisit egress, branch governance, authenticated documentation, audit
  logging, and restore cadence when the product gains accounts, private data,
  uploads, billing, organizations, keys, or LLM features.

## Stage 1 validity

Stage 1 remains valid as the governing security baseline and as evidence that
the original eleven findings were materially addressed. Its assurance status
is **valid with one verification exception**: `MG-SEC-010` must distinguish an
automated audit from an enforced gate unless a branch or deployment rule is
independently verified. The `MG-SEC-001/002` assurance exception is closed.
The frozen MG-SEC history remains unchanged; assurance corrections belong in
this MG-SA workstream.

## Frontend/UI readiness

The project is ready to proceed with frontend/UI development in a controlled
development environment. Frontend work does not add the excluded account or
private-data boundary by itself.

The project is ready to proceed with frontend/UI development and controlled
dataset expansion within the present product boundary. The resource controls
that matter before UI-driven traffic growth are now deployed and verified.
`MG-SA-002` should still be resolved or explicitly accepted before describing
the CI checks as mandatory gates.

## Next decision

Record and integrate this `MG-SA-001` closure evidence, remove temporary
rollback artifacts only after acceptance, and then address the separate
`MG-SA-002` GitHub enforcement/claim decision.
