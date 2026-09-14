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

`requirements.txt` remains the cross-platform developer snapshot. It is not a
production installation source.

## Workflow behavior and enforcement boundary

Every lock entry must use an exact version and at least one SHA-256 distribution
hash. Editable, VCS, direct URL, and trusted-host entries are prohibited. CI
installs with `--require-hashes`, verifies dependency consistency, builds the
application without dependency resolution or build isolation, and reconciles
the installed environment with the production lock.

The dependency-security workflow runs on every push and pull request and every
Monday at 04:17 UTC. `pip-audit` returning a vulnerability makes the job fail.
The schedule reassesses an unchanged lock against advisories published after
installation. A scanner result establishes affected installed code, not
application-path exploitability; reachability is assessed separately.

The workflow is an automated audit, not a GitHub-enforced merge gate. At the
current solo-maintainer prototype boundary, `main` has no branch protection or
ruleset requiring the Dependency Security or Secret Scan checks. A direct push
or a commit-message skip instruction can therefore reach `main` without a
successful run. A passing result proves only that the identified commit passed
that workflow execution.

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
3. Regenerate both locks in the reviewed Linux container.
4. Review every direct and transitive version change and the generated hashes.
5. Run the dependency workflow locally or in CI and run the complete test suite.
6. Capture deterministic scientific baseline and post-change responses when a
   runtime dependency changes behavior or serialization.
7. Deploy through a fresh virtual environment, verify production-to-lock
   reconciliation, and retain the previous environment until health and
   scientific checks pass.

Ignored advisories require a time-bounded, identifier-specific exception that
documents reachability, compensating controls, an owner, and an expiry date.
MG-SEC-010 introduces no standing vulnerability exceptions.
