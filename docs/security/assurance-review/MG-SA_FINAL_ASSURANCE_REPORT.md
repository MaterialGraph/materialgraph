# MaterialGraph Stage 1 Final Assurance Report

**Review date:** 2026-09-14
**Commit:** `5e794292eb7e712d1840095254cd72217d553cb5`
**Phase:** Read-only repository and GitHub assessment complete; remediation not started

## Executive conclusion

Stage 1 remains substantially valid. The remediation architecture is coherent,
proportionate to a public deterministic scientific prototype, and materially
stronger than the frozen pre-remediation baseline. Nine of eleven Verified
controls are sound in repository implementation, and the reasoning that
retired `MG-SEC-006` is correct.

Two assurance defects prevent an unqualified all-controls-confirmed conclusion:

1. `MG-SA-001` is an implementation defect in `MG-SEC-001/002`: mounted
   material-intelligence routes that scale with graph/data size bypass both the
   expensive-work admission gate and application deadline. The claimed Nginx
   site-wide connection cap is also implemented with a per-client key.
2. `MG-SA-002` is a verification defect in `MG-SEC-010`: current workflows
   passed, but no branch/ruleset/deployment rule makes them an enforced gate.

No regression and no separate new current vulnerability outside the original
Stage 1 control set was confirmed.

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

`MG-SA-001` should be corrected before dataset expansion or increased public UI
traffic. It is already a current control bypass, although the small dataset and
remaining proxy/database bounds reduce current severity.

No application or deployment remediation was performed during the assessment.

## Verification claims needing qualification

- `MG-SEC-001` criterion “every mounted expensive scientific route” is false at
  the reviewed commit.
- `MG-SEC-001` criterion “site-wide concurrency is 20” is false because its
  connection zone is keyed by client address.
- `MG-SEC-002` application-deadline coverage has the same route-scope gap.
- `MG-SEC-010` proves successful automated audit runs, not an enforced gate on
  `main` or deployment.
- The local complete-suite result (`823 passed, 1 skipped`) and all effective
  production state claims remain historical evidence until independently
  reproduced. The focused security/configuration subset was reproduced with
  `91 passed`. A complete-suite invocation against an unseeded disposable
  SQLite database produced `747 passed, 72 failed, 5 skipped`; the failures
  consistently reflected missing seeded scientific data, so this is recorded
  as an environment limitation rather than contradictory product evidence.
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
is **valid with two exceptions**: `MG-SEC-001/002` should not remain
unqualified as fully verified until `MG-SA-001` is fixed, and `MG-SEC-010` must
distinguish an automated audit from an enforced gate. The frozen MG-SEC history
should remain unchanged; these exceptions belong in this MG-SA workstream.

## Frontend/UI readiness

The project is ready to proceed with frontend/UI development in a controlled
development environment. Frontend work does not add the excluded account or
private-data boundary by itself.

It is not yet advisable to treat Stage 1 as fully assured for increased public
traffic or dataset expansion. Correct `MG-SA-001` before UI launch materially
increases traffic to the affected intelligence routes. Complete approved
read-only production evidence before claiming deployed controls are currently
reconciled.

## Next decision

The next remediation step is `MG-SA-001`. It requires a separately approved,
focused implementation change and must not be treated as resolved until local,
deployment, bypass, and scientific-regression evidence pass.
