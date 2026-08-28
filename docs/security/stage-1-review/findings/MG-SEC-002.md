# MG-SEC-002 — Scientific Requests Lack an Enforced Deadline and Timeout Hierarchy

## Status

Open.

## Assessment

- Severity: **Medium**
- Confidence: **High**
- Affected component: FastAPI execution, synchronous scientific services,
  Nginx proxy, and SQLAlchemy database access
- Code baseline: `32bc57cc78754e061f9a2f4294d81aa39e4f9955`
- Deployment checkpoint: `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Not resolved**

## Exact evidence

- No FastAPI request-deadline middleware or route-specific execution deadline
  exists.
- No cancellation signal is propagated through synchronous scientific work.
- `create_engine()` configures `pool_pre_ping=True` but no project-defined
  statement, lock, or pool-acquisition timeout.
- Effective deployed Nginx configuration defines no explicit proxy connect,
  send, or read timeout.
- No timeout, rollback, or cancellation regression tests were found.

## Threat scenario

A slow database query or unexpectedly long scientific operation occupies a
worker thread and database connection without a MaterialGraph-defined deadline.
Several such requests can progressively exhaust capacity. A client disconnect
does not demonstrate cancellation of synchronous work already executing.

## Current safeguards

- Graph traversal and enumeration have explicit per-request bounds.
- Uvicorn is supervised by systemd.
- SQLAlchemy checks stale pooled connections.

## Missing safeguards

- Coordinated Nginx, application, and PostgreSQL deadlines.
- Route-specific budgets for expensive work.
- Defined pool-wait and lock limits.
- Safe rollback and abandonment behavior.
- Timeout and repeated-recovery tests.

## Recommended remediation

Define an end-to-end timeout hierarchy. Simple reads and expensive scientific
routes may use different documented budgets. A timeout must roll back database
work and must never report a partial scientific result as complete.

## Verification requirements

- Artificially delayed SQL and service calls stop within their budgets.
- Transactions roll back and connections return to the pool.
- Timed-out calculations are not reported as successful.
- Repeated timeouts do not permanently reduce capacity.
- Normal deterministic scientific results remain unchanged.
