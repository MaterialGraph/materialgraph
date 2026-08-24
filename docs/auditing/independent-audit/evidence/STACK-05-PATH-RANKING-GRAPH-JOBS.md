# Stack 05 Evidence — Path Ranking and Graph Jobs

## Scope

Reviewed the path-ranking service and supplied tests; graph-job ORM/schema evidence from earlier stacks; graph-job service, dormant route module, and service/API tests.

The newly supplied path-ranking service is byte-identical to the previously reviewed copy.

## Path-ranking verification

Tests directly protect proportional multi-element objective credit, order independence, endpoint-state semantics, path-wide event explanations, reversal handling, unknown endpoint composition, structured-composition precedence, efficiency penalties for reversals, quality bottlenecks, and score-breakdown arithmetic.

No new defect was confirmed. The difference between edge-intelligence and path-ranking plausibility constants remains `OBS-013`: current tests characterize alkali-path totals but do not establish why identical transition categories use different numerical plausibility mappings.

## Graph-job lifecycle trace

`create_job` persists `PENDING`. `claim_next_pending_job` selects the oldest pending job with stable UUID tie-breaking and PostgreSQL `FOR UPDATE SKIP LOCKED`, then commits `RUNNING` with `started_at`. Completion and failure are single conditional updates restricted to `RUNNING`, so only one competing terminal transition succeeds. Tests cover invalid transitions, unknown IDs, locked rows, FIFO claims, and concurrent complete-versus-fail behavior.

The graph-job route module describes background processing but is intentionally not included in the application: API tests require 404 for create/list/get and absence from OpenAPI. No supplied worker or scheduler consumes jobs. Without an operational contract, missing lease/retry/stale-job recovery is retained as `OBS-016`, not classified as a current public defect.

## Determinism and pagination

Claim order is deterministic. Listing orders only by creation timestamp and has no UUID tie-breaker. Because the listing route is dormant, this is `MG-IA-IMP-003` rather than a confirmed public defect.

## Negative findings

No race was confirmed in claim or terminal state transitions. Pending jobs cannot complete or fail directly; completed and failed jobs reject later mutation; result/error payloads remain associated with the successful terminal transition.

## Missing evidence

Before graph jobs are enabled, review any worker entry point, dispatch registry, supported job-type/input contracts, lease/heartbeat model, retries, cancellation, timeouts, stale-job recovery, shutdown behavior, and deployment process supervision.

## Execution limitation

PostgreSQL-specific concurrency tests were inspected but not executed in this workspace. Their SQL semantics align with the implementation; runtime confirmation remains dependent on the repository's configured PostgreSQL test environment.
