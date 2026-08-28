# MG-SEC-010 — Production Dependencies Are Neither Reproducibly Installed Nor Vulnerability-Gated

## Status

Open.

## Assessment

- Severity: **Medium**
- Confidence: **High**
- Affected component: Python packaging, production deployment, and dependency
  maintenance
- Application evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Deployment evidence checkpoint:
  `b2df9b0fcbf0c4a84430f5511b0391ea414eb9bc`
- Resolution version or commit: **Not resolved**

## Exact evidence

- `pyproject.toml` declares all direct runtime dependencies without version
  constraints.
- The production deployment guide runs `pip install -e .`; it does not install
  from the pinned `requirements.txt` snapshot or enforce distribution hashes.
- Production contained Starlette `1.2.1` while the snapshot pinned Starlette
  `1.2.0`, demonstrating that the documented production installation can drift
  from the reviewed snapshot.
- The local and deployed environments passed `pip check`; dependency
  consistency does not establish reproducibility or absence of vulnerabilities.
- Independent OSV and PyPI audits returned nonzero results for three package
  families in the pinned snapshot: Pillow `12.2.0`, pydantic-settings `2.14.1`,
  and Starlette `1.2.0`.
- Production contained Pillow `12.2.0`, pydantic-settings `2.14.1`, and Starlette
  `1.2.1`, all within the affected ranges reported by the reviewed advisories.
- No automated dependency-vulnerability scanner, dependency-review workflow,
  Dependabot, or Renovate configuration is present.
- Current code tracing did not establish reachability for the specific Pillow,
  pydantic-settings, or Starlette advisory paths. They are therefore supporting
  evidence of the missing dependency gate, not three separately confirmed
  application vulnerabilities.

## Threat scenario

A fresh or replacement production deployment resolves unconstrained direct and
transitive dependencies from the package index. A newly vulnerable,
unexpectedly changed, or compromised release can enter the environment without
an explicit reviewed dependency change. Known vulnerabilities can subsequently
remain installed because no automated scan gates repository changes or
periodically assesses the maintained dependency contract.

## Current safeguards

- Production uses a dedicated Python virtual environment.
- A fully version-pinned snapshot exists in `requirements.txt`.
- Both inspected environments pass `pip check`.
- Gitleaks protects against committed secrets and runs with read-only repository
  permission in CI.
- Current application tracing found no reachable path for the reviewed
  advisories.

## Missing safeguards

- One authoritative, reviewed production dependency contract.
- Exact version constraints for production resolution.
- Hash verification or equivalent distribution-integrity enforcement.
- Automated vulnerability scanning and scheduled reassessment.
- Production-versus-lock or production-versus-constraint verification.
- A documented process for reviewing, updating, and retiring dependency pins.

## Recommended remediation

Define one authoritative production lock or constraints workflow generated from
reviewed direct requirements, with exact versions and hashes. Make deployment
consume that artifact, add an automated vulnerability gate and scheduled scan,
and establish an explicit update process. Upgrade affected packages only after
compatibility and scientific regression testing; do not infer application
exploitability solely from scanner presence.

## Verification requirements

- A clean production build resolves exactly the reviewed dependency set.
- Distribution hashes or an equivalent integrity mechanism are enforced.
- CI fails on newly introduced actionable vulnerabilities according to a
  documented policy.
- Scheduled scans detect advisories published after dependency installation.
- Deployed versions can be reconciled mechanically with the authoritative
  dependency artifact.
- FastAPI, configuration, scientific, migration, and complete regression tests
  pass after dependency updates.
- Deterministic scientific outputs and ordering remain unchanged.
