# MG-IA-003 — Core-domain migration can fail on a populated predecessor database

- Classification: migration correctness and deployment risk
- Priority: P2
- Confidence: high
- Disposition: confirmed
- Baseline: `a1605e61f72035890692ab4df63ebd2f7b859069`

## Evidence

Revision `1d204c6d38c0` adds `materials.source` as non-null without a server default, nullable transition, or backfill. Revision `4368e3ecc291` permits valid existing material rows.

Affected files/functions: `alembic/versions/4368e3ecc291_create_initial_material_tables.py:upgrade`, `alembic/versions/1d204c6d38c0_create_core_domain_models.py:upgrade`, and `app/models/material.py:Material.source`.

## Expected versus actual

A valid predecessor database should upgrade to the next revision. PostgreSQL cannot add this non-null column to a nonempty table because existing rows receive no value.

## Impact

Deployment succeeds on empty databases but can fail on populated installations, making upgrade reliability depend on undocumented population history.

## Reproduction

Upgrade to `4368e3ecc291`, insert one valid material, then run `alembic upgrade 1d204c6d38c0`.

## Tests

No supplied migration test upgrades a populated predecessor database. Empty-database deployment success does not exercise this path.

## Caller trace

Alembic executes this revision during `alembic upgrade head`; the documented getting-started workflow invokes that command. Existing deployments are the affected caller context.

## Remediation scope

Use an explicit nullable/backfill/non-null sequence or a migration-only default. The provenance value must be governed rather than guessed.
