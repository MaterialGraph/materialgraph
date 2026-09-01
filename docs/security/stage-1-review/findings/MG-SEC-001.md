# MG-SEC-001 — Public Expensive Endpoints Lack Rate and Concurrency Limiting

## Status

Open.

## Assessment

- Severity: **High**
- Confidence: **High**
- Affected component: public FastAPI scientific routes and Nginx proxy
- Code baseline: `32bc57cc78754e061f9a2f4294d81aa39e4f9955`
- Deployment checkpoint: `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Not resolved**

## Exact evidence

- `app/main.py` mounts the API without rate-limiting, concurrency, or
  admission-control middleware.
- Active routes have no rate-limit dependency or expensive-route concurrency
  gate.
- Public screening, scenario, substitution, discovery, graph-analytics, and
  research routes perform CPU- or database-intensive work.
- Effective deployed Nginx configuration has no `limit_req` or `limit_conn`.
- The prototype is Internet-accessible on port 80 and runs one Uvicorn process
  on the documented small EC2 host class.
- A deployed unauthenticated request with an empty JSON body invoked screening
  across all 28 candidate materials and returned a 21,685-byte response. This
  confirms that a minimal valid request can trigger the complete screening
  workload without an admission-control decision.

## Threat scenario

An unauthenticated client repeatedly submits concurrent expensive scientific
requests. Individual graph bounds do not limit aggregate CPU, worker-thread,
memory, or database-connection consumption. Legitimate requests can be denied
service and infrastructure or database cost can increase.

## Current safeguards

- Graph hop, depth, branching, state, path, and result limits bound individual
  requests.
- Uvicorn is loopback-bound behind Nginx.
- Port 8000 is not permitted by the EC2 security group.
- Graph-job routes are unmounted.

## Missing safeguards

- Per-client request-rate limits.
- Connection and expensive-route concurrency limits.
- Application admission control and defined overload responses.
- Trusted proxy and client-identity policy.
- Throttling, spoofed-header, and concurrency tests.

## Recommended remediation

Introduce coordinated Nginx request/connection limits and application-level
admission control, with stricter budgets for expensive scientific routes.
Define trusted proxy handling before relying on forwarded client addresses.

## Verification requirements

- Requests over configured rates return the documented rejection response.
- Concurrent expensive requests cannot consume all application capacity.
- Spoofed forwarding headers cannot bypass client identity controls.
- Health monitoring remains available during an abuse test.
- Normal scientific outputs and deterministic ordering remain unchanged.
