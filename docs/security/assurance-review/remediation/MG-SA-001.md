# MG-SA-001 Remediation — Expensive-work control completeness

**Classification:** Implementation defect
**Base checkpoint:** `154fd53fd0d1f7fdb195fb6e15e623d8ce0ba84a`
**Status:** Repository implementation complete; production verification pending

## Objective

Close the route-classification bypass and implement the documented aggregate
Nginx connection boundary without weakening the existing per-client controls,
timeout hierarchy, health availability, or deterministic scientific results.

## Implemented repository change

- The application expensive-request classifier now includes material neighbor,
  similarity, neighborhood, criticality, and both recommendation routes.
- The same material-route family is present in the expensive Nginx location,
  so these requests receive the 25-second proxy read budget, per-client rate
  limiting, and per-client connection limiting.
- Material IDs are matched as a bounded single path segment rather than digits
  only, preventing alternate accepted integer spellings such as `+5` from
  bypassing classification. Invalid identifiers are conservatively classified
  before application validation.
- Nginx now defines a distinct `$server_name`-keyed `materialgraph_site` zone
  with an aggregate limit of 20 connections.
- Both expensive locations explicitly apply `materialgraph_site 20` alongside
  `materialgraph_client 2`. This is necessary because Nginx inherits
  `limit_conn` directives from the previous configuration level only when the
  current level defines none.
- Current deployment guidance describes the corrected route and key semantics.

No scientific service, database schema, dependency, response model, ranking,
scoring, or evidence semantics changed.

## Independent policy and bypass tests

The route-completeness test maintains a security cost policy independently of
the runtime classifier. It enumerates every mounted FastAPI `APIRoute` and
fails if a route is added, removed, or changed without an explicit ordinary or
expensive classification.

For every policy route, the test materializes path parameters and compares the
application result with the committed Nginx regex locations. Separate
behavioral tests prove that each newly covered material-intelligence path:

- receives structured HTTP `503` while the admission slot is occupied; and
- receives structured HTTP `504` when its application deadline expires.

Additional bypass cases prove that positive-sign, negative, and invalid
material-ID path segments remain inside both application and proxy expensive
classes.

Configuration tests require distinct client/site zone keys, two expensive
per-client directives, and three aggregate directives: one at server scope and
one in each expensive location.

## Repository validation

| Check | Result |
|---|---|
| Admission, deadline, and project-configuration tests | `59 passed` |
| Complete canonical JSON for all six newly covered endpoints | Baseline and remediation outputs identical; SHA-256 `571981c82166b6df1da16972f732c66262aca4ca869a881963d1aa322a28380b` |
| Expanded affected-route API subset | `77 passed`, two fixture-data failures caused by absent risk-profile seed rows |
| Ruff for application and tests | Passed |
| `git diff --check` | Passed |
| Primary Nginx semantics | Confirmed against `ngx_http_limit_conn_module` documentation |
| Nginx syntax/effective configuration | Pending production candidate validation |
| Complete PostgreSQL-backed suite | Pending authoritative maintainer run |
| Representative complete scientific JSON comparison | Pending deployment verification |

The focused security tests used a disposable SQLite database only for the
GraphJob cleanup fixture. The expanded subset and JSON comparison used the
same isolated review fixture for both baseline and remediation. The two subset
failures were unchanged missing-seed limitations: `selected_profile_ids` was
empty and `material_risk_score` was `None`. They are not accepted as passing
integration evidence and do not replace the required PostgreSQL run.

A complete-suite attempt in the isolated environment collected 841 tests and
produced `809 passed, 27 failed, 5 skipped`. All 27 failures required canonical
seeded materials, relationships, risk profiles, or derived scientific scores
that the fixture does not contain. No changed security or configuration test
failed. This result is an environment limitation, not closure evidence. The
remediation adds 17 tests, so the prepared PostgreSQL environment is expected
to run 841 tests in total.

Primary semantics reference:
<https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html>.

## Production activation plan

Production is intentionally unchanged by the repository remediation. After the
bundle is independently accepted and `main` is pushed:

1. confirm the production worktree is clean and record its current commit;
2. fetch and fast-forward to the accepted remediation commit;
3. install the tracked Nginx file as the candidate site configuration;
4. run `sudo nginx -t` before any reload;
5. restart MaterialGraph for the Python classifier change and reload Nginx for
   the proxy change;
6. confirm both services, timers, HTTPS health, and the deployed commit;
7. run only bounded admission/deadline probes; and
8. compare representative screening, exploration, pathway, and newly covered
   material-intelligence responses with complete pre-change JSON.

No migration, dependency installation, database write, load test, or restore
operation is required.

## Rollback and failure handling

- Preserve the previous deployed commit and active Nginx site before
  activation.
- If `nginx -t` fails, do not reload; restore the prior site and validate it.
- If application startup or health fails, return the worktree to the recorded
  prior commit and restart only the application.
- If proxy behavior fails after reload, restore the prior site, run
  `nginx -t`, and reload Nginx.
- Reconfirm HTTPS health and service state after either rollback path.

The changes are code/configuration-only and do not require data rollback.

## Closure criteria

`MG-SA-001` remains open until all of the following are recorded:

- authoritative complete-suite success against `materialgraph_test`;
- accepted commit and successful relevant GitHub workflows;
- production Nginx syntax and effective configuration evidence;
- deployed route admission/deadline and aggregate/per-client limit evidence;
- complete scientific JSON preservation; and
- healthy post-change and rollback-ready production state.
