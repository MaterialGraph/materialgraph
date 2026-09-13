# MG-SEC-002 Verification — Scientific Request Timeout Hierarchy

## Status

Verified on 2026-09-13. All twenty acceptance criteria passed.

Final implementation:
`4869e39edb97c5c8c48c63b1819bb692f02f57b3`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Database connection and pool acquisition waits are bounded at three seconds | Pass |
| 2 | Every PostgreSQL transaction applies a three-second lock timeout | Pass |
| 3 | Every PostgreSQL transaction applies a 15-second statement timeout | Pass |
| 4 | Transaction-local settings work through the deployed Neon pooled endpoint | Pass |
| 5 | An artificial long SQL statement is cancelled with timeout SQLSTATE `57014` | Pass |
| 6 | The artificial SQL timeout occurs within the database budget | Pass |
| 7 | A failed database dependency explicitly rolls back and closes | Pass |
| 8 | The timed-out connection executes successfully after rollback | Pass |
| 9 | A fresh pooled connection succeeds after the database timeout | Pass |
| 10 | Expensive application requests have a 20-second deadline | Pass |
| 11 | An application deadline returns structured HTTP `504` | Pass |
| 12 | Repeated application deadlines do not prevent later successful execution | Pass |
| 13 | Work completing after the response deadline cannot send a late success | Pass |
| 14 | Abandoned synchronous work retains its admission slot until exit | Pass |
| 15 | Concurrent work is rejected while abandoned work holds full capacity | Pass |
| 16 | Nginx connect, send, and read timeouts are explicit | Pass |
| 17 | Database, application, and expensive proxy deadlines are ordered inside-out | Pass |
| 18 | Screening, exploration, and pathway responses match complete baseline JSON | Pass |
| 19 | The deployed Nginx file matches the repository and the worktree is clean | Pass |
| 20 | Application, Nginx, dependent timers, and trusted HTTPS health remain active | Pass |

## Production evidence

- Before remediation, Nginx had no explicit proxy timeouts and PostgreSQL
  reported `statement_timeout=0`, `lock_timeout=0`, and
  `idle_in_transaction_session_timeout=5min`.
- Baseline screening, exploration, and pathway requests returned `200` in
  0.949, 7.431, and 7.033 seconds. Their complete JSON was retained.
- The final engine connected through Neon pooling and reported
  `statement_timeout=15s`, `lock_timeout=3s`, and the unchanged five-minute
  idle-in-transaction timeout.
- `SELECT pg_sleep(20)` was cancelled with SQLSTATE `57014` in 15.251 seconds.
  Explicit rollback restored the same connection, and a fresh pooled connection
  also returned `SELECT 1`.
- Two consecutive artificial application delays returned structured `504`
  with code `expensive_request_deadline_exceeded`; the following normal call
  returned `200`.
- A synchronous thread-pool probe returned structured `504` in 0.051 seconds.
  The abandoned work retained its admission slot, concurrent work returned
  `503`, and capacity was released after the worker exited.
- Effective Nginx configuration contained three-second connect and 10-second
  send limits, 25-second expensive-route reads, and 20-second ordinary reads.
- Post-change screening, exploration, and pathway requests returned `200` in
  0.738, 7.377, and 7.207 seconds. Complete parsed JSON matched baseline
  responses exactly.
- Production ran commit
  `4869e39edb97c5c8c48c63b1819bb692f02f57b3`; its worktree was clean, its
  deployed Nginx site matched the repository, health and a database-backed
  material endpoint returned `200`, and no unexpected application error was
  present after the final activation.

## Repository evidence

- The final focused timeout, admission, and project-configuration suite passed
  with 42 tests.
- The complete suite passed with 812 tests and one platform skip.
- Ruff and `git diff --check` passed.

## Residual interpretation

Python worker threads are not forcibly terminated. A synchronous calculation
that outlives the response deadline continues under its retained admission
slot, and its response is discarded. This is deliberate safe abandonment:
repeat callers cannot create unbounded worker growth, database statements stop
at the earlier server deadline, and capacity returns only after work exits.

## Conclusion

Scientific requests now have a measured inside-out database, application, and
proxy timeout hierarchy. Timeout failures are explicit, database state and
pool capacity recover, late work cannot be reported as successful, and normal
scientific results remain unchanged. `MG-SEC-002` is Verified.
