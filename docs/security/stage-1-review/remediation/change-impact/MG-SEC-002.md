# MG-SEC-002 Change Impact — Scientific Request Timeout Hierarchy

## Status

Completed and verified on 2026-09-13.

Final implementation commit:
`4869e39edb97c5c8c48c63b1819bb692f02f57b3`.

## Baseline

Production defined no explicit Nginx proxy timeout. PostgreSQL sessions
reported `statement_timeout=0` and `lock_timeout=0`; SQLAlchemy configured
only stale-connection checking. Representative maximum-valid scientific work
completed in approximately seven seconds, but no project-controlled deadline
bounded an unexpectedly slow query or calculation.

## Approved change

1. Limit database connection and pool acquisition to three seconds.
2. Apply a three-second lock timeout and 15-second statement timeout to every
   PostgreSQL transaction.
3. Limit expensive application requests to 20 seconds.
4. Return structured HTTP `504` for application and database execution
   deadlines.
5. Return structured HTTP `503` with `Retry-After: 1` for pool-acquisition
   exhaustion.
6. Roll back failed database dependencies before closing their sessions.
7. Configure Nginx with a three-second connect timeout, 10-second send timeout,
   25-second expensive-route read timeout, and 20-second ordinary read timeout.
8. Discard responses produced after an application deadline.
9. Retain admission capacity until abandoned synchronous work actually exits.
10. Preserve complete deterministic scientific output for successful work.

## Impact

- PostgreSQL cancels unexpectedly long statements before the application or
  proxy deadline expires.
- Lock waits and connection-pool waits cannot remain unbounded.
- Timed-out work receives an explicit failure and cannot be represented as a
  complete scientific result.
- Repeated abandoned synchronous requests cannot exceed the existing expensive
  request admission capacity.
- Health and ordinary reads retain their separate proxy boundary.

## Compatibility correction

The initial implementation supplied lock and statement limits as PostgreSQL
startup options. Neon rejected those options on its pooled endpoint. Production
remained healthy at `/health`, but the failed database probe prevented closure.
The application was returned to the previous known-good revision, and commit
`0ac7bdc3d75f4d4bced01eaa15f2fb274b23143d` replaced startup options with
`SET LOCAL` statements applied at every transaction boundary. Connectivity and
effective values passed before the application was reactivated.

## Rollback

The active Nginx site was preserved as a root-owned mode-`0600` copy. A proxy
failure can restore that file, validate Nginx, and reload it. Application code
can return to the prior known-good commit and restart without schema or data
changes. The remediation introduces no migration.

## Residual boundary

Python cannot safely terminate a running worker thread. When synchronous work
outlives the 20-second response deadline, MaterialGraph discards its eventual
response and retains the admission slot until the thread exits. PostgreSQL work
is independently cancelled at 15 seconds. Existing request and traversal
bounds limit normal scientific computation; genuinely interruptible CPU work
would require cooperative checkpoints or process isolation in a future design.
