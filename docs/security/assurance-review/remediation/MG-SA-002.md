# MG-SA-002 Remediation — Qualify automated checks and require deployment evidence

**Classification:** Verification defect
**Finding:** [`../findings/MG-SA-002.md`](../findings/MG-SA-002.md)
**Status:** Repository correction implemented; maintainer and GitHub verification pending
**Remediation checkpoint:** Pending accepted commit

## Decision

MaterialGraph will not add mandatory pull requests or protected-branch status
checks solely to close this verification defect. That governance change is not
proportionate to the current solo-maintainer public scientific prototype and
would conflict with the reviewed bundle/fast-forward integration workflow.

The correction instead makes the security boundary exact:

- Dependency Security and Secret Scan are automated audits that fail when their
  executed checks find a violation.
- A successful run is evidence for its exact commit only.
- GitHub does not currently prevent an unchecked direct push from reaching
  `main`.
- Production deployment has a documented manual precondition requiring both
  workflows to succeed for the exact candidate commit, with substantive steps
  inspected and run evidence retained.

Direct/force-update governance remains the separately classified accepted
residual risk in `MG-SA-O-007`. Required checks should be reconsidered when the
project adds maintainers, automated deployment, or protected release branches.

## Repository changes

- `docs/security/DEPENDENCY_MANAGEMENT.md` distinguishes workflow failure
  behavior from protected-branch enforcement and defines the exact-SHA
  deployment precondition.
- `docs/guide/DEPLOYMENT.md` requires Dependency Security and Secret Scan
  evidence before production synchronization and explicitly states that the
  precondition is manual.
- `tests/test_project_configuration.py` prevents the live dependency and
  deployment guidance from silently regressing to an enforced-gate claim.
- The cumulative assurance README, matrix, registers, finding index, and final
  report are updated without modifying the frozen `MG-SEC-*` history.

No application code, dependency input, lock, workflow, Nginx, systemd,
database, backup, or production configuration changes are included.

## Isolated review validation

- The focused project-configuration suite passed with `32 passed` against a
  disposable SQLite database containing only the fixture-required graph-job
  table.
- The automation-pin and dependency-contract validators passed, Ruff passed,
  and `git diff --check` passed.
- A complete-suite diagnostic produced `675 passed, 162 failed, 5 skipped` in
  the isolated environment. The failures were database-backed tests attempting
  to use schema and canonical data that the disposable database did not
  contain. This is not authoritative acceptance evidence and does not replace
  the required prepared PostgreSQL `materialgraph_test` run.

## Bypass and failure analysis

- A direct push, workflow skip instruction, cancelled run, or failed run can
  still update `main`; the corrected records no longer claim otherwise.
- The deployment process can still be bypassed by an operator with host access.
  This is explicit manual operational trust, not an automated enforcement
  claim.
- Checking only a branch name or latest run is insufficient; evidence must
  match the exact candidate SHA.
- Checking only the overall conclusion is insufficient; substantive scan and
  audit steps must not be skipped.
- Scheduled dependency audits remain useful for advisories published after a
  commit, but do not retroactively block an already deployed environment.

## Validation and acceptance criteria

Before closure:

1. Confirm the remediation commit descends directly from the accepted
   `0023ea9cd9dec25608ba5887e1f61cfee111da3c` checkpoint.
2. Review the diff and confirm that the frozen
   `docs/security/stage-1-review/` history is unchanged.
3. Run the applicable focused configuration tests, automation/dependency
   validators, Ruff, complete suite, and `git diff --check` against the prepared
   test database.
4. Confirm the accepted commit's Dependency Security and Secret Scan workflows
   completed successfully and their substantive steps executed.
5. Recheck the GitHub branch/ruleset state and record whether `main` remains
   unprotected; do not infer it from workflow success.
6. Record the accepted commit and evidence in this workstream, then mark the
   verification defect closed.

## Deployment and rollback

This correction is documentation-only. It requires no production pull,
dependency installation, migration, application restart, Nginx reload, or
scientific-response comparison.

Before integration, rollback is deletion of the review branch. After a
fast-forward integration but before push, reset `main` only through the retained
backup branch. After push, prefer a reviewed revert of the documentation commit
rather than rewriting published history.
