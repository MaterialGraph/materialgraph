# MG-SA-001 — Expensive-work admission scope and proxy site-wide limit are incomplete

**Classification:** Implementation defect
**Priority:** High for correction; Medium present risk
**Affected Stage 1 controls:** `MG-SEC-001`, `MG-SEC-002`
**Status:** Confirmed during read-only assessment; not remediated

## Threat scenario

An unauthenticated caller, or callers using multiple source addresses,
repeatedly request material graph neighborhood or recommendation endpoints.
These endpoints perform multiple queries, graph traversal, full
structured-neighbor ranking, or criticality evaluation whose work scales with
the dataset. Because they are not classified as expensive, they do not consume
one of the two application admission slots and do not receive the 20-second
application deadline.

The ordinary Nginx path still provides a per-client connection cap, request
rate limit inherited at the server, explicit proxy timeouts, and the database
applies per-statement timeouts. Those layers reduce present risk, but they do
not provide the site-wide application capacity invariant documented for
expensive work. Sequential queries can also exceed a per-statement budget
without any application-wide deadline.

## Repository evidence: route classification

`app/core/admission_control.py` classifies only five exact POST paths and
`/materials/{id}/discovery|research`. The same function controls
`ExpensiveRequestDeadlineMiddleware`.

Mounted routes outside this class include:

- `/api/v1/materials/{id}/neighbors`;
- `/api/v1/materials/{id}/similar`;
- `/api/v1/materials/{id}/neighborhood`;
- `/api/v1/materials/{id}/criticality`;
- `/api/v1/materials/{id}/recommendations`; and
- `/api/v1/materials/{id}/recommendations/scenario`.

The neighborhood route permits depth two and up to 100 nodes and repeatedly
calls the neighbor service. Recommendation paths explicitly construct the full
similar-material candidate pool before applying the response limit.

`materialgraph.nginx` mirrors the same incomplete expensive-route patterns.

## Repository evidence: site-wide connection claim

The only Nginx connection zone is declared as:

```nginx
limit_conn_zone $binary_remote_addr zone=materialgraph_client:10m;
```

Both the expensive-route value of two and server-level value of 20 therefore
count connections per client address. Moving `limit_conn` to server scope does
not change the zone key into a site-wide key. A distributed set of clients does
not share the documented 20-connection budget.

The `MG-SEC-001` verification record nevertheless marks “site-wide concurrency
is 20” as passed. A true site-wide limit requires a distinct shared zone keyed
to a site/server value.

## Test defect interaction

`test_classifies_public_expensive_routes` checks only a manually enumerated
positive list that matches the implementation. It does not enumerate mounted
routes and compare them against an independently maintained security policy or
cost annotation. It therefore cannot fail when a new expensive route is
mounted but omitted from the classifier.

Configuration tests assert the existing connection-zone strings but do not
verify that per-client and site-wide limits use different keys.

## Safe bypass analysis

No load test was run. The route bypass is established statically: requests
matching these mounted paths take the ordinary branch in both middlewares and
the ordinary Nginx location. The proxy-limit defect follows directly from the
documented Nginx per-key semantics and the committed zone definition.

Present dataset size and remaining layers make catastrophic impact uncertain,
which is why present risk is Medium rather than High. The defect becomes
increasingly material as the scientific dataset grows or UI traffic increases.

## Required assurance correction

Do not mark this concern resolved during discovery. Before closing it, the
project should:

- define route cost independently of the runtime classifier;
- cover every mounted route and test future route completeness;
- verify Nginx/application route parity;
- implement separately keyed per-client and site-wide proxy limits;
- verify deadline/admission behavior for affected endpoints; and
- preserve complete scientific JSON and ordering.
