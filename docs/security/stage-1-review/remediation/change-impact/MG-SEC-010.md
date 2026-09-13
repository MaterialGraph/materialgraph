# MG-SEC-010 Change Impact — Reproducible Production Dependencies

## Status

Completed and verified on 2026-09-13.

Final implementation checkpoint:
`d06b8259d52fab65f31d7039448e44d05742f508`.

## Baseline

Production was installed from unconstrained project metadata through an
editable installation. The pinned developer snapshot was not the deployment
contract, contained no distribution hashes, and differed from the deployed
environment. No automated or scheduled vulnerability gate existed.

## Approved change

1. Define reviewed direct production and audit inputs.
2. Generate exact transitive locks with distribution hashes.
3. Make deployment require the production lock and verify installed versions.
4. Install the application offline after dependency installation so editable
   metadata cannot resolve a second dependency graph.
5. Add push, pull-request, manual, and scheduled vulnerability checks.
6. Patch the affected Pillow, pydantic-settings, Starlette, and pip versions.
7. Document controlled lock regeneration, review, deployment, and exceptions.
8. Preserve complete deterministic scientific behavior through regression and
   deployed response-parity testing.

## Impact

- Fresh production environments resolve the reviewed dependency graph rather
  than whichever compatible releases are current at installation time.
- Hash enforcement rejects an unreviewed distribution artifact.
- Repository automation detects known vulnerabilities both when code changes
  and when new advisories appear later.
- The deployed environment can be reconciled mechanically with the lock.
- Developer snapshot pins no longer retain the three superseded vulnerable
  runtime versions.
- Versioned deployment environments and the stable `.venv` symlink are excluded
  from Git without hiding unrelated repository content.

## Deployment and rollback

A clean versioned candidate environment is built and verified before service
activation. The stable `/opt/materialgraph/.venv` path may point to that
versioned environment, preserving console-script shebang validity. The prior
environment remains available until health, audit, reconciliation, database,
and scientific parity checks pass. Rollback repoints or restores `.venv` and
restarts the service; no schema or data change is involved.

## Residual boundaries

An audit result reflects advisories known to the configured data sources at the
time of execution; it is not proof that dependencies contain no undiscovered
vulnerability. Dependency updates still require provenance, compatibility,
test, and scientific-output review. The developer snapshot remains a separate
cross-platform convenience artifact and is not the production authority.
