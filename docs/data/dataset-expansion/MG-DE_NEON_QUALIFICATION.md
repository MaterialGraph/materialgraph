# MG-DE-008 Isolated Neon Qualification Plan

**Status:** Closed on 2026-09-19; all reviewed gates, evidence review, and cleanup passed
**Execution report:**
[`MG-DE_NEON_QUALIFICATION_REPORT.md`](MG-DE_NEON_QUALIFICATION_REPORT.md)
**Production writes authorized:** No
**Neon resource creation authorized by this change:** No

## Purpose

MG-DE-007 established correctness and bounded behavior against disposable local
PostgreSQL. MG-DE-008 must determine what changes when the exact approved
cohort runs on an isolated, managed, remote Neon target. It evaluates connection
roles, network-sensitive performance, interruption recovery, bounded resource
use, and complete cleanup. It is not a production canary.

## Immutable input

Execution must use the approved 1,727-identity manifest with payload digest
`902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`.
The manifest contract, curated-state baseline, 28 expected conflicts, and
`mp-19017` sentinel from MG-DE-007 remain unchanged.

## Gate 0: authorization and identity

Before any connection or resource mutation, an operator must provide a reviewed
non-secret contract containing the qualification project, branch, endpoint, and
database identifiers plus a production denylist. The branch name must contain
`mg-de-008` and a non-production marker. Qualification and production branch
and endpoint identifiers must differ. A qualification branch may share the
reviewed project with production, but it must never share the production branch
or either production endpoint.

SQL alone cannot prove the Neon project or branch identity. Retain independent
provider metadata showing the project, branch, endpoints, creation time, region,
parent, and later deletion. Never place credentials or complete connection URLs
in evidence.

The offline contract validator requires:

- a pooled runtime URL and a distinct direct migration URL;
- different runtime and migration database roles;
- Neon hosts with `sslmode=verify-full` and `channel_binding=require`;
- the exact expected database name and approved manifest;
- at most five connections and one request/import actor at a time;
- explicit positive wall-clock, active-compute, and storage-delta budgets.

Validation performs no network access, resource creation, or database write.
A passing validation report is necessary but does not authorize execution.
Start from `MG-DE_NEON_QUALIFICATION_CONTRACT.example.json`; do not add
credentials or connection URLs to that file.

## Gate A: connection management

After separate human authorization to provision the target:

1. create only the reviewed isolated branch or project;
2. prove the direct URL is used for migrations and administrative preparation;
3. prove the pooled URL is used by normal application and import sessions;
4. capture cold connect, warm connect, checkout, and trivial round-trip timing;
5. verify bounded pool timeouts, pre-ping behavior, transaction-local timeouts,
   role separation, TLS policy, and clean rollback after disconnect;
6. record sanitized endpoint and server metadata without secrets.

## Gate B: exact import and recovery

Import into an empty isolated database copied from the curated 28-material
baseline. Reconcile 1,727 processed identities, 1,699 inserted records, and 28
explained curated conflicts. Preserve the full curated hash and API sentinel.

Repeat the MG-DE-007 idempotent rerun, failed-first-chunk recovery, and
committed-chunk recovery. Add controlled remote disconnects at those two
boundaries. Recovery must resume from durable state with unique event keys,
unchanged curated data, and no duplicate source identity. Provider outage or
chaos testing beyond the controlled client disconnects requires separate
authorization.

## Gate C: remote performance

Run the same 12 sequential representative scenarios and retain end-to-end
latency, database time, query count, response size, and server-side plans.
Compare like-for-like warm runs with MG-DE-007. Give explicit attention to
discovery path and scientific pathways, which measured approximately 8.95 and
5.60 seconds locally. Record timeout or failure as a failure, not a missing
measurement.

No concurrency or load test is authorized. Any proposed performance threshold
must be reviewed before execution; this plan does not retroactively invent a
pass threshold from observed results.

## Gate D: resource and cost boundary

The initial default ceiling is two hours wall clock, 3,600 active-compute
seconds, 256 MiB storage delta, five database connections, and one active
request/import actor. Capture provider measurements before and after the run.
Stop on any ceiling breach. A change to a ceiling requires a reviewed contract,
not an ad hoc retry.

## Gate E: cleanup and evidence

Retain sanitized contract validation, provider identity proof, timings, plans,
reconciliation, recovery, resource use, and an evidence inventory. Then delete
only the identified qualification resource and independently prove it is absent.
Clear connection values from the shell. Do not delete, reset, restore, or write
to the production branch. Do not perform a production restore under this plan.

## Polymorph product requirement

MG-DE-008 must preserve MG-DE-007 response-level identity and formula metrics.
It must not change ranking or collapse identities. Frontend work must show both
material-identity count and unique-formula count, identify formula-equivalent
groups as potentially meaningful polymorphs, and let a researcher inspect each
identity. Grouping is presentation, not deduplication.

## Closure boundary

MG-DE-008 closes only after an independently reviewed isolated execution passes
all gates and cleanup is proven. Closure may support a separately authorized
production rollout decision. It does not itself authorize production import,
deployment, public publication, concurrency testing, or a production canary.
