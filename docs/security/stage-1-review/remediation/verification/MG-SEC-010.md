# MG-SEC-010 Verification — Reproducible Production Dependencies

## Status

Verified on 2026-09-13. All twenty acceptance criteria passed.

Final implementation checkpoint:
`d06b8259d52fab65f31d7039448e44d05742f508`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Reviewed direct production requirements are exact-pinned | Pass |
| 2 | All transitive production requirements are exact-pinned | Pass |
| 3 | Production distributions carry accepted hashes | Pass |
| 4 | Unsafe build tools are explicitly pinned and hashed | Pass |
| 5 | Project runtime metadata agrees with the production inputs | Pass |
| 6 | Deployment installs the production lock with hash enforcement | Pass |
| 7 | Application installation cannot resolve a second dependency graph | Pass |
| 8 | Installed distributions reconcile exactly with the lock | Pass |
| 9 | The clean candidate environment passes `pip check` | Pass |
| 10 | Candidate application import succeeds as the runtime identity | Pass |
| 11 | Candidate database access succeeds with production configuration | Pass |
| 12 | A vulnerability gate runs for pushes and pull requests | Pass |
| 13 | The vulnerability gate supports manual and scheduled reassessment | Pass |
| 14 | Workflow Action and container references satisfy immutable-pin policy | Pass |
| 15 | The hosted Dependency Security workflow succeeds | Pass |
| 16 | The active production environment matches the reviewed lock | Pass |
| 17 | A fresh active-environment audit reports no known vulnerabilities | Pass |
| 18 | Application and supporting timers remain healthy | Pass |
| 19 | Representative scientific responses match complete pre-change JSON | Pass |
| 20 | Focused, lint, whitespace, and complete regression checks pass | Pass |

## Repository and automation evidence

- `scripts/check_dependency_contract.py` returned
  `dependency_contract_valid=true`; installed-environment mode returned
  `installed_environment_matches_lock=true`.
- `scripts/check_automation_pins.py` returned
  `automation_pins_valid=true`.
- The focused dependency, automation, and configuration suite passed 36 tests.
  Ruff and `git diff --check` passed. The complete suite passed 822 tests with
  one expected platform skip.
- Dependency Security run 1 succeeded in 1 minute 40 seconds. Secret Scan run
  88 succeeded in 8 seconds.
- A clean container installation enforced every production hash, passed
  dependency consistency, and installed MaterialGraph offline without resolving
  additional dependencies.

## Production evidence

- Before remediation, the deployed snapshot comparison found 16 requirement
  differences. A normalized audit found 17 unique vulnerabilities in four
  installed distributions.
- The candidate environment passed exact lock reconciliation, `pip check`,
  application import, and a database probe before activation.
- The active environment uses pip `26.2.1`, Pillow `12.3.0`,
  pydantic-settings `2.14.2`, Starlette `1.3.1`, FastAPI `0.136.3`, setuptools
  `84.0.0`, and wheel `0.48.0`.
- The post-change audit inspected 87 distributions and returned exit code zero,
  with zero affected distributions and zero known vulnerabilities.
- Screening, objective exploration, and scientific pathways returned HTTP
  `200`; their complete parsed JSON matched the respective pre-change captures.
- The application, Nginx, backup timer, and journal monitor remained active.
  Public health and a database-backed material endpoint returned HTTP `200`.
- No traceback, exception, internal-server-error, critical, or failure entry was
  present from the successful activation timestamp.

## Activation correction

Renaming the candidate virtual-environment directory invalidated absolute
console-script shebangs, so the first activation failed and automatically
restored the prior environment. The corrected activation retained the candidate
at its build path and exposed it through the stable `.venv` symlink. Health
recovered successfully, and the prior environment remained available for
rollback throughout verification.

## Conclusion

Production dependency resolution is exact, integrity-checked, mechanically
reconcilable, and continuously vulnerability-gated. Known affected packages
were upgraded without changing deterministic scientific responses.
`MG-SEC-010` is Verified.
