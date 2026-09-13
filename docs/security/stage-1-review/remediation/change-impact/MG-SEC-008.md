# MG-SEC-008 Change Impact — Bounded Research Objectives

## Status

Completed and verified on 2026-09-13.

Implementation commit:
`96d7f577c08c3bfb439b94bfbabc3f4d6a437f4d`.

## Baseline

Research-objective `avoid_elements`, `prefer_elements`, and
`preserve_elements` accepted arbitrary collection sizes, duplicates, long
strings, and unknown symbols. Services repeatedly traversed those values for
each candidate. Nginx had no explicit request-body policy.

## Approved change

1. Limit each raw element collection to 32 entries.
2. Constrain individual symbols to the periodic-table representation.
3. Canonicalize case and whitespace through the authoritative element helper.
4. Deduplicate canonical symbols in first-seen order.
5. Apply the shared boundary to chains, exploration, and scientific pathways.
6. Reject request bodies larger than 32 KiB at Nginx.
7. Preserve scores, ordering, explanations, and declared constraint semantics.

## Impact

- Invalid collections fail with structured HTTP `422` before services run.
- Unexpectedly large bodies fail at the proxy with HTTP `413`.
- Equivalent duplicates no longer multiply formula parsing and scoring work.
- Valid objectives remain far below the proxy ceiling.
- The API schema advertises two-character symbols and 32-item collections.

## Operational note

Verification exposed an older unapplied `fraction_known` migration. A verified
backup preceded application of existing revision `7a4c2e91b6d8`. Alembic's
isolated environment startup was then repaired so `DATABASE_MIGRATION_URL`
alone supports model imports without persisting the migration credential into
the runtime service.

## Residual boundaries

This change does not implement rate limits, concurrency admission, deadlines,
or bounded screening logs. Those controls remain assigned to `MG-SEC-001`,
`MG-SEC-002`, and `MG-SEC-009` and can now be tuned against this maximum valid
request contract.
