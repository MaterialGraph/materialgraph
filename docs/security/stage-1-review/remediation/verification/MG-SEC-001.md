# MG-SEC-001 Verification — Public Work Admission Control

## Status

Verified on 2026-09-13. All twenty acceptance criteria passed.

Implementation: `8a1d2b8b5608cad41a7dba6ceb280dc22ada719b`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Every mounted expensive scientific route belongs to the admission class | Pass |
| 2 | Health and ordinary read routes remain outside the application gate | Pass |
| 3 | Application concurrency configuration is constrained from 1 through 32 | Pass |
| 4 | Production application admission capacity is two | Pass |
| 5 | A request over application capacity receives HTTP `503` | Pass |
| 6 | Application overload responses use a stable structured error code | Pass |
| 7 | Application overload responses include `Retry-After: 1` | Pass |
| 8 | Health returns `200` while both expensive application slots are occupied | Pass |
| 9 | Application rejection logs are bounded and omit request payloads | Pass |
| 10 | Nginx keys public admission to `$binary_remote_addr` | Pass |
| 11 | Expensive proxy rate is two requests per second with burst four | Pass |
| 12 | Expensive per-client concurrency is two and site-wide concurrency is 20 | Pass |
| 13 | Proxy rate and connection rejections use HTTP `429` | Pass |
| 14 | A 12-request burst produces observed proxy `429` responses | Pass |
| 15 | Nginx overwrites forwarded client headers with `$remote_addr` | Pass |
| 16 | Spoofed forwarding headers do not reach application client identity | Pass |
| 17 | Screening, exploration, and pathway outputs match complete baseline JSON | Pass |
| 18 | The deployed Nginx site matches the repository and passes syntax validation | Pass |
| 19 | MaterialGraph, Nginx, backup and monitor scheduling remain active | Pass |
| 20 | Trusted HTTPS health remains `200` after overload verification | Pass |

## Production evidence

- The production host reported two processors, 911 MiB memory, no swap, and one
  Uvicorn process. This supports the conservative two-request application
  capacity selected for the current prototype.
- Effective Nginx configuration reported the source-address rate and connection
  zones, `2r/s`, burst four, expensive concurrency two, site concurrency 20,
  and `429` rejection statuses.
- Twelve simultaneous malformed requests to the screening route produced five
  application validation responses (`422`) and seven proxy rejections (`429`).
  Health immediately afterward returned `200`.
- A request containing spoofed `X-Forwarded-For` and `X-Real-IP` test addresses
  reached Uvicorn as the actual `35.154.84.47` connection address. Neither
  spoofed value appeared in the application journal.
- Two deliberately incomplete loopback requests occupied both application
  admission slots without entering scientific service work. The next expensive
  request returned structured `503` with code
  `expensive_request_capacity_exceeded` and `Retry-After: 1`; concurrent health
  returned `200`.
- The overload journal entry contained bounded route class, method, and capacity
  metadata and no request body or element collection.
- Complete parsed screening, objective-exploration, and scientific-pathway JSON
  matched their pre-change production captures exactly.
- The deployed Nginx site matched the tracked file, the production worktree was
  clean, MaterialGraph and Nginx were active, backup and journal-monitor timers
  were active, and trusted HTTPS health returned `200`.

## Probe interpretation

Two earlier concurrency attempts completed before the saturation probe arrived
and returned `200` or `422`; they were treated as inconclusive rather than as
evidence. The final incomplete-body method deterministically held admission
before request parsing and demonstrated the intended `503` boundary without
running scientific work.

## Repository evidence

- Focused admission and project-configuration verification passed with 32 tests.
- The complete suite passed with 802 tests and one platform skip.
- Ruff and `git diff --check` passed.

## Conclusion

Public expensive work now has spoof-resistant per-client proxy throttling and a
global application capacity boundary. Overload produces explicit retryable
responses, health remains available, and admitted scientific behavior remains
unchanged. `MG-SEC-001` is Verified.
