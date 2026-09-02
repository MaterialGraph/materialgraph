# MG-SEC-012 — Production Recovery Is Limited to an Untested Six-Hour History Window

## Status

Open.

## Assessment

- Severity: **Medium**
- Confidence: **High**
- Affected component: Neon production database and backup and recovery process
- Application evidence baseline:
  `32bc57cc78754e061f9a2f4294d81aa39e4f9955`
- Recovery evidence checkpoint:
  `3ee4944cfb31a6158839f74a23545286f56281f3`
- Resolution version or commit: **Not resolved**

## Exact evidence

- The production Neon project reports a six-hour history-retention window.
- Point-in-time restore is available only to a selected point within that
  window.
- No manual snapshot exists and no snapshot schedule is configured.
- No external logical or physical database backup is maintained.
- MaterialGraph has never completed a Neon restore or recovery test.
- No recovery runbook, recovery-point objective, or recovery-time objective is
  documented inside or outside the repository.
- Repository migrations, seeds, and import mechanisms can reconstruct some
  database state, but no evidence establishes that they reproduce the complete
  deployed production state.

## Threat scenario

An operator error, faulty migration, unintended import, application defect, or
credential misuse corrupts or deletes production data. If the damage is
discovered after the six-hour history window, no retained recovery point or
independent backup is available. If it is discovered within the window, the
untested recovery procedure may still fail or take longer than operationally
acceptable. Curated or imported production state can be permanently lost and
the service can remain unavailable while data is reconstructed manually.

## Current safeguards

- Neon supports point-in-time restoration within the six-hour history window.
- The Neon console exposes a manual snapshot capability.
- Schema migrations, seed scripts, and import mechanisms can reconstruct some
  project data.
- The current prototype contains no private user or tenant data.

## Missing safeguards

- A recovery-point objective and recovery-time objective appropriate to the
  value and reproducibility of current production data.
- Retention sufficient to meet the recovery-point objective.
- An independent or otherwise durable database backup.
- A scheduled backup or snapshot policy.
- A documented, access-controlled recovery runbook.
- A completed isolated restore test with recorded duration and results.
- Scientific and relational integrity checks for restored data.

## Recommended remediation

Define an initial RPO and RTO based on the cost of reconstructing curated and
imported production state. Establish a scheduled logical backup or longer
provider retention and keep at least one recovery copy independent of the
active database. Document recovery ownership and procedure, then restore into
an isolated database or branch and verify schema version, row counts,
relationships, representative scientific records, and application
connectivity. Do not use production as the first restore-test target.

## Verification requirements

- The documented retention and backup schedule meet the approved RPO.
- A backup can be restored into an isolated target without changing production.
- The restoration completes within the approved RTO.
- Alembic schema state and expected table and relationship counts reconcile.
- Representative scientific records and deterministic API results reconcile
  with the source checkpoint.
- Application connectivity succeeds using an isolated recovery configuration.
- The test records its source recovery point, target, duration, validation
  results, limitations, and cleanup outcome without recording credentials.
- A subsequent operator can execute the runbook without undocumented steps.
