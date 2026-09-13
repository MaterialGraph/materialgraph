# MG-SEC-001 Change Impact — Public Work Admission Control

## Status

Completed and verified on 2026-09-13.

Implementation commit:
`8a1d2b8b5608cad41a7dba6ceb280dc22ada719b`.

## Baseline

The public proxy had no request-rate or connection limits, and the application
had no concurrency admission decision. One Uvicorn process ran on a two-vCPU,
911 MiB host. Nginx appended caller-supplied forwarding data, so forwarded
client identity was not a suitable independent application trust boundary.

## Approved change

1. Classify screening, comparison, scenario, sensitivity, substitution,
   discovery, and research operations as expensive public work.
2. Limit expensive work by Nginx source address to two requests per second with
   a four-request burst and two concurrent connections.
3. Limit each source address to 20 concurrent HTTPS connections overall.
4. Return HTTP `429` for proxy rate or connection rejection.
5. Derive proxy admission identity from `$binary_remote_addr` and overwrite
   forwarded client headers with `$remote_addr`.
6. Admit no more than two expensive application requests globally by default.
7. Return structured HTTP `503` with `Retry-After: 1` when application capacity
   is full.
8. Keep health and ordinary read routes outside the application gate.
9. Preserve complete deterministic scientific results for admitted requests.

## Impact

- One source cannot submit unbounded bursts or concurrent connections to the
  expensive route set.
- Aggregate expensive work cannot occupy more than two application admission
  slots, preserving event-loop capacity for health requests.
- Rejected work receives an explicit retryable response rather than a partial
  scientific result.
- Caller-supplied `X-Forwarded-For` and `X-Real-IP` values cannot select the
  identity forwarded by the direct-origin Nginx deployment.
- The application concurrency value is configurable only from 1 through 32;
  the production default of two matches the current host capacity.

## Rollback

The active Nginx site was preserved as a root-owned mode-`0600` copy before the
candidate was installed. Nginx syntax and isolated application import passed
before activation. A failed proxy activation can restore that site, validate
it, and reload Nginx. A failed application activation can return to the prior
known-good commit and restart the service without changing data or schema.

## Residual boundaries

The current policy assumes DNS-only direct-origin traffic. Cloudflare proxying
or a future load balancer requires explicit trusted-proxy ranges and a revised
client-identity policy before activation. Request deadlines and coordinated
proxy, application, pool, lock, and statement timeouts remain assigned to
`MG-SEC-002`.
