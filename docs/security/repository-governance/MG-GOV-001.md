# MG-GOV-001 — GitHub repository governance hardening

**Status:** In progress
**Baseline:** `918abe01c444e5346b6e895dc42d2d7037f718f7`
**Production impact authorized:** None

## Objective

Make GitHub the enforced integration boundary for `main` while preserving the
existing deterministic application and production dataset state.

## Scope

- require changes to `main` to arrive through pull requests;
- require the `Gitleaks` and `Locked dependency audit` checks to pass;
- require branches to be current before merge;
- apply the rules to repository administrators without a routine bypass;
- prohibit force pushes and deletion of `main`;
- verify native secret scanning, push protection, dependency graph, Dependabot
  alerts, Dependabot security updates, and private vulnerability reporting;
- add Dependabot version-update configuration and a root security policy;
- inspect, but do not invent, a root software license;
- test repository-owned configuration and retain live-settings evidence.

Production access, deployment, restoration, service restart, environment
mutation, and database reads or writes are prohibited.

## Baseline inspection

The baseline repository was inspected at the exact commit above.

| Control | Baseline observation |
| --- | --- |
| Default branch | `main` |
| Repository visibility | Public |
| Repository rulesets | None returned by the GitHub rulesets API |
| Classic branch protection | Previously documented as absent; a fresh API read was denied to the installed integration and requires authenticated Settings verification |
| Secret Scan workflow | Present; runs Gitleaks on pushes and pull requests with immutable Action and image references |
| Dependency Security workflow | Present; runs the locked dependency audit on pushes, pull requests, and a weekly schedule |
| Dependabot configuration | Absent |
| Root `SECURITY.md` | Absent |
| Root `LICENSE` | Absent; GitHub reports no detected license |

The missing license is a legal/product decision, not a formatting defect.
`MG-GOV-001` does not select or add a license without an explicit owner
decision.

## Target GitHub settings

Configure a branch rule or ruleset targeting `main` with:

- pull requests required before merge;
- zero required approvals for the current solo-maintainer boundary;
- conversation resolution required;
- required status checks `Gitleaks` and `Locked dependency audit`;
- strict/up-to-date branch requirement enabled;
- administrator enforcement/no routine bypass;
- force pushes disabled;
- branch deletion disabled.

Requiring a pull request with zero approvals prevents direct pushes without
creating a one-person review deadlock. Review approval requirements must be
revisited when another trusted maintainer is added.

## Repository changes

- `.github/dependabot.yml` schedules weekly updates for Python and GitHub
  Actions dependencies.
- Root `SECURITY.md` defines private reporting expectations without publishing
  a personal address.
- Live dependency and deployment guidance will retain its current manual-boundary
  wording until the GitHub rule is verified, then be updated in the closure
  change.
- Project-configuration tests pin the intended workflow names, events,
  Dependabot ecosystems, root security policy, and governance record.

## Verification plan

1. Run focused project-configuration tests, automation-pin validation,
   dependency-contract validation, Ruff, and `git diff --check`.
2. Push this branch and confirm both security workflows pass for its exact SHA.
3. Create a pull request and configure the `main` protection rule using the
   exact check names observed from successful runs.
4. Re-read the rule/settings and capture evidence that pull requests, strict
   required checks, administrator enforcement, force-push prohibition, and
   deletion prohibition are active.
5. Verify the GitHub security settings individually: dependency graph,
   Dependabot alerts, Dependabot security updates, secret scanning, push
   protection, and private vulnerability reporting.
6. Test enforcement with a disposable branch: verify the pull request cannot
   merge while a required check is pending or failing, then verify normal merge
   after both required checks pass. Do not weaken or bypass the rule for the
   test.
7. Confirm `main` contains the reviewed merge commit and the worktree is clean.

## Rollback

Before merge, delete only the review branch if the work item is abandoned.
After merge, revert repository-file changes through a new reviewed pull request.
Changing or removing the GitHub rule is a separate administrative action and
must be recorded; published history must not be rewritten.

No rollback step may access or modify production services or databases.
