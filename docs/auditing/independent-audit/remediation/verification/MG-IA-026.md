# MG-IA-026 Remediation Verification

## Title

Deployment guide installs a complete version-controlled systemd unit

## Status

Verified in the local project environment on Windows with Python 3.14.5 and
the configured PostgreSQL test environment.

## Acceptance criteria

1. A complete systemd unit is stored at repository-root
   `materialgraph.service`.
2. The unit defines its user, group, working directory, environment file,
   executable, loopback bind address, port, and restart behavior.
3. The tracked unit contains no database URL, API key, or other credential
   value.
4. The deployment guide installs the tracked unit before `daemon-reload` and
   service startup.
5. The installed unit receives root ownership and mode `0644`.
6. Checkout, service, environment, and routine-update paths consistently use
   `/opt/materialgraph`.
7. The README links to the existing deployment guide.
8. Static regression coverage protects the deployment contract.
9. The complete test suite, lint, and whitespace checks pass.

## Current-baseline confirmation

The finding was re-evaluated directly against GitHub commit `5a63205`.
`docs/guide/DEPLOYMENT.md` still named the installed service file but supplied
neither its contents nor an installation command before invoking systemd.
The repository contained no tracked unit. The guide also created a nested
checkout inconsistent with the established `/opt/materialgraph` environment
and service layout, and the README's deployment link targeted a nonexistent
path. The frozen finding remained fully applicable.

## Implemented changes

- Added root-level `materialgraph.service` with the complete reviewed process
  contract.
- Added explicit root-owned, mode-`0644` installation before systemd reload and
  activation.
- Kept secret values in `/opt/materialgraph/.env`, outside the tracked unit.
- Bound Uvicorn to `127.0.0.1:8000` for Nginx proxying.
- Aligned initial clone and routine update paths with `/opt/materialgraph`.
- Corrected the root README deployment-guide link.
- Added static assertions for unit fields, secret exclusion, install ordering,
  checkout consistency, and link validity.

## Verification results

Commands included the project-configuration suite, followed by:

```powershell
pytest -q
ruff check .
git diff --check
```

Results:

- focused project-configuration verification: **passed**;
- complete test suite: **passed**;
- Ruff: **passed**;
- Git whitespace validation: **passed**; LF-to-CRLF messages were
  informational working-tree conversion warnings.

## Change boundary

The verified implementation boundary contains four files: three modified
files (`README.md`, `docs/guide/DEPLOYMENT.md`, and
`tests/test_project_configuration.py`) plus new root-level
`materialgraph.service`. It makes no application code, schema, model,
migration, seed-data, or live-server change.

## Conclusion

All acceptance criteria are satisfied. `MG-IA-026` is verified as remediated.
