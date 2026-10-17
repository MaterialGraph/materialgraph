# Dependency Management

MaterialGraph production dependencies are controlled by two reviewed inputs and
their generated hash locks:

- `requirements-production.in` contains exact direct runtime and build-tool
  pins plus explicit security floors for affected transitive packages.
- `requirements-production.lock` is the authoritative Linux/Python 3.12
  production dependency contract.
- `requirements-audit.in` pins the vulnerability scanner.
- `requirements-audit.lock` supplies exact versions and hashes for the scanner
  and its dependencies.
- `requirements-test.in` pins test-only tooling: `pytest` and `httpx2`, the HTTP
  client required by Starlette's test client.
- `requirements-test.lock` is compiled from `requirements-production.in` and
  `requirements-test.in`, seeded from `requirements-production.lock`, so every
  production package keeps its exact production version.
  `scripts/check_dependency_contract.py` fails if any production pin differs.
  It is used only by the Backend Tests workflow and local test environments and
  is never a production installation source. Dependency Security audits it
  with `pip-audit` alongside the production lock.

`requirements.txt` is the cross-platform developer snapshot (Python 3.12). It is
not a production installation source. It pins every package in
`requirements-test.lock` at exactly the locked version, except the installer
tooling `pip`, `setuptools` and `wheel`, and adds only reviewed developer extras:
`ruff` and the Windows-only runtime dependencies `colorama`, `tzdata` and
`win32-setctime` (with `sys_platform` markers; `uvloop` is marked non-Windows).
`scripts/check_dependency_contract.py` fails on any drift or unreviewed extra,
so Dependabot alerts on `requirements.txt` reflect the locked versions.
`requirements-dev.txt` only includes `requirements.txt`.

## Dependabot policy

- **pip: alerts only.** `open-pull-requests-limit: 0` disables Python
  version-update pull requests. Such a pull request would edit
  `requirements.txt` alone and fail the dependency contract by design. A
  Dependabot alert (or a failing `pip-audit`) starts the reviewed update
  procedure below; the fix is a lock regeneration, and the alert closes when
  `main` pins a fixed version. A Dependabot security-update pull request that
  edits only `requirements.txt` is closed as superseded by that fix.
- **npm (`frontend/`): weekly, patch and minor only.** Major version updates are
  ignored because there is no frontend CI; they are planned as separate,
  locally qualified changes. Ignore rules can also suppress a major-version
  security pull request; the Dependabot alert and `npm audit` still report it.
- **GitHub Actions: weekly**, all update types.

## Workflow behavior and enforcement boundary

Every lock entry must use an exact version and at least one SHA-256 distribution
hash. Editable, VCS, direct URL, and trusted-host entries are prohibited. CI
installs with `--require-hashes`, verifies dependency consistency, builds the
application without dependency resolution or build isolation, and reconciles
the installed environment with the production lock.

The dependency-security workflow runs on every push and pull request and every
Monday at 04:17 UTC. It runs `pip-audit` against both the production lock and the
test lock; a vulnerability in either makes the job fail.
The schedule reassesses an unchanged lock against advisories published after
installation. A scanner result establishes affected installed code, not
application-path exploitability; reachability is assessed separately.

The workflow's `Locked dependency audit` job is a required status check for
merges to `main`. Classic branch protection (verified 2026-10-16) requires a
pull request and passing `Locked dependency audit`, `Gitleaks` and
`Backend pytest (ephemeral PostgreSQL)` checks on a branch that is up to date
with `main`, applies to administrators, and has no repository ruleset. This
gates merges only; it is configuration that an administrator can change, and it
does not cover the scheduled weekly audit or prove anything about a deployed
commit. A passing result proves only that the identified commit passed that
workflow execution.

Before a production deployment, the operator must identify the exact candidate
commit and confirm that both Dependency Security and Secret Scan completed
successfully for that SHA with their substantive audit/scan steps executed.
Missing, skipped, cancelled, or failing evidence stops the deployment. Record
the commit and workflow run URLs or run identifiers with the deployment
evidence. This is an explicit operator precondition, not a protected-branch
control. Reconsider a required-check ruleset when more maintainers, automated
deployment, or protected release branches are introduced.

## Reviewed lock generation

Locks are generated for Linux amd64 and Python 3.12.3 with the reviewed image:

`python:3.12.3-slim@sha256:fd3817f3a855f6c2ada16ac9468e5ee93e361005bd226fd5a5ee1a504e038c84`

The reviewed generator is `pip-tools==7.6.1`. Regeneration must use
`--generate-hashes`, `--allow-unsafe`, `--strip-extras`,
`--no-emit-index-url`, and `--no-emit-trusted-host`. Both input and lock diffs
must be reviewed. The generated locks must pass
`scripts/check_dependency_contract.py`, a clean hash-enforced installation,
`pip check`, `pip-audit`, focused compatibility tests, and the complete
scientific regression suite.

## Updating dependencies

1. Review the upstream release, compatibility constraints, and relevant
   security advisories.
2. Change the smallest necessary exact pins in the input files and
   `pyproject.toml`.
3. Regenerate the production and audit locks in the reviewed Linux container,
   then regenerate the test lock: copy the new `requirements-production.lock` to
   `requirements-test.lock` and compile `requirements-production.in` together
   with `requirements-test.in` into it using the same flags.
4. Review every direct and transitive version change and the generated hashes,
   then update `requirements.txt` to the new `requirements-test.lock` versions
   (the contract check lists every difference).
5. Run the dependency workflow locally or in CI and run the complete test suite.
6. Capture deterministic scientific baseline and post-change responses when a
   runtime dependency changes behavior or serialization.
7. Deploy through a fresh virtual environment, verify production-to-lock
   reconciliation, and retain the previous environment until health and
   scientific checks pass.

## Frontend dependencies

`frontend/package-lock.json` is the frontend dependency contract. Only `react`,
`react-dom` and `scheduler` ship to the browser; build and test tooling is
development-only. Dependabot watches `frontend/` weekly (patch and minor
updates; see Dependabot policy). There is no frontend CI
workflow, so a lock change is qualified locally from a clean export with
`npm ci`, `npm audit`, `npm test` and `npm run build`, recording the built asset
names; prefer lockfile-only fixes (`npm audit fix` without `--force`).

Ignored advisories require a time-bounded, identifier-specific exception that
documents reachability, compensating controls, an owner, and an expiry date.
MG-SEC-010 introduces no standing vulnerability exceptions.
