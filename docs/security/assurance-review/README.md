# MaterialGraph Security Assurance Review

**Namespace:** `MG-SA-*`
**Assessment date:** 2026-09-14
**Status:** `MG-SA-001` repository remediation implemented; production verification pending
**Implementation under review:** `5e794292eb7e712d1840095254cd72217d553cb5`
**Accepted assurance baseline:** `154fd53fd0d1f7fdb195fb6e15e623d8ce0ba84a`

## Purpose and separation

This is an independent post-remediation assurance workstream. It does not edit,
replace, close, or merge into the historical `MG-SEC-*` inspection and
remediation records under [`../stage-1-review/`](../stage-1-review/). Those
records remain immutable source evidence.

The review asks whether the Stage 1 controls are correctly implemented,
effective against their documented scenarios, proportionate to the current
public scientific prototype, internally consistent, resistant to meaningful
bypass, and sufficient for the current product boundary.

## Scope

Included:

- the complete `docs/security` baseline and linked deployment guidance;
- application request validation, admission, deadline, database-timeout, and
  logging controls;
- Nginx, systemd, environment-file, TLS, database-role, backup, journal, and
  monitoring configuration committed at the checkpoint;
- GitHub Actions, local hook, dependency locks, audit inputs, and validator
  scripts;
- security tests and tests that claim consistency with deployed controls;
- safe bypass and failure-mode analysis; and
- preservation of deterministic scientific behavior.

Excluded during the assessment phase:

- production requests or commands;
- service restarts, restoration, load generation, destructive probes,
  migrations, upgrades, and configuration changes;
- accounts, private data, uploads, billing, organizations, API keys, and LLM
  features that do not exist in the present boundary.

## Method

Controls were reviewed in dependency and risk order: evidence identity;
external exposure; resource containment; secrets and privilege; recovery;
logging and capacity; supply chain; operations; scientific regression; and
cross-control bypass analysis.

Each control was traced through:

1. documented threat scenario;
2. repository implementation;
3. behavioral or structural tests;
4. committed deployment configuration;
5. historical production evidence;
6. independently reproducible GitHub evidence; and
7. bypass and failure-mode analysis.

## Evidence rules

- Repository, GitHub, historical production, and independently reproduced
  evidence are labelled separately.
- A historical `Verified` label is not treated as proof by itself.
- String/configuration-presence tests prove consistency, not runtime effect.
- A successful workflow run proves that commit passed that run; it does not
  prove the workflow is an enforced gate.
- Missing live evidence is recorded as a limitation, not converted into a pass
  or failure.
- A concern uses exactly one required classification: Verification defect,
  Implementation defect, Regression, New current finding, Future hardening,
  Accepted residual risk, Documentation inconsistency, or No issue.
- Separate finding files exist only for confirmed defects.

## Authoritative repository evidence

The initial review used the complete-history bundle
`materialgraph-security-assurance-5e794292.bundle`.

| Attribute | Verified value |
|---|---|
| Bundle verification | Passed |
| Bundle SHA-256 | `d08488b6d6a46a1ba016e316579072f45dbb8f68e07cac7024b9703bdada1925` |
| Bundle `main` | `5e794292eb7e712d1840095254cd72217d553cb5` |
| Bundle `HEAD` | `5e794292eb7e712d1840095254cd72217d553cb5` |
| Commit tree | `8eb718f62840ebfedfaecfdc30013e2a0bd06e94` |
| Review checkout | Isolated, detached at assessment start, and clean |

The bundle commit, rather than separately supplied copies, is authoritative.

## Current disposition

The focused security suite passes (`91 passed`), and the automation-pin,
dependency-contract, Ruff, whitespace, and clean-worktree checks pass.

Two defects are confirmed:

- [`MG-SA-001`](findings/MG-SA-001.md) — Implementation defect: expensive
  material-intelligence routes bypass admission/deadline controls, and the
  documented Nginx site-wide connection cap is actually keyed per client.
- [`MG-SA-002`](findings/MG-SA-002.md) — Verification defect: successful GitHub
  workflows are described as a gate although `main` has no rule requiring
  them.

No regression and no separate new current vulnerability outside the Stage 1
control set was confirmed. Most Stage 1 controls are sound in repository
design; deployed state remains pending read-only live confirmation.

The `MG-SA-001` repository correction now covers every mounted route through an
independent cost-policy inventory, aligns the Nginx and application expensive
route sets, and separates per-client from aggregate connection keys. It remains
open until authoritative complete-suite, GitHub, and production evidence pass.

## Registers and reports

- [`MG-SA_CONTROL_MATRIX.md`](MG-SA_CONTROL_MATRIX.md)
- [`MG-SA_EVIDENCE_REGISTER.md`](MG-SA_EVIDENCE_REGISTER.md)
- [`MG-SA_OBSERVATIONS.md`](MG-SA_OBSERVATIONS.md)
- [`MG-SA_FINAL_ASSURANCE_REPORT.md`](MG-SA_FINAL_ASSURANCE_REPORT.md)
- [`findings/`](findings/)
- [`remediation/`](remediation/)
