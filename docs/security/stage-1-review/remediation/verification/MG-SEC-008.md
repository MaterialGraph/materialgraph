# MG-SEC-008 Verification — Bounded Research Objectives

## Status

Verified on 2026-09-13. All twenty acceptance criteria passed.

Implementation: `96d7f577c08c3bfb439b94bfbabc3f4d6a437f4d`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Each raw objective element collection is limited to 32 entries | Pass |
| 2 | The schema advertises a maximum of 32 items per collection | Pass |
| 3 | The schema constrains canonical symbols to two characters | Pass |
| 4 | Valid symbols are canonicalized through the periodic-table helper | Pass |
| 5 | Canonical duplicates are removed in deterministic first-seen order | Pass |
| 6 | Oversized chain objectives return structured HTTP `422` | Pass |
| 7 | Oversized exploration objectives return structured HTTP `422` | Pass |
| 8 | Oversized scientific-pathway objectives return structured HTTP `422` | Pass |
| 9 | Overlong symbols return `422` consistently across all affected endpoints | Pass |
| 10 | Unknown symbols return `422` consistently across all affected endpoints | Pass |
| 11 | Rejected objectives do not enter scientific chain processing | Pass |
| 12 | Nginx declares an explicit 32 KiB request-body limit | Pass |
| 13 | A 40,056-byte public request is rejected by Nginx with HTTP `413` | Pass |
| 14 | A request with 32 entries in every collection returns HTTP `200` | Pass |
| 15 | The maximum valid request completes within the five-second budget | Pass |
| 16 | Canonical and duplicate mixed-case objectives produce identical complete JSON | Pass |
| 17 | Chain output matches complete parsed pre-change JSON | Pass |
| 18 | Exploration and scientific-pathway outputs match complete parsed pre-change JSON | Pass |
| 19 | Direct isolated Alembic startup succeeds and reports database head | Pass |
| 20 | MaterialGraph, Nginx, backup scheduling, and HTTPS health remain active | Pass |

## Production evidence

- Nine combinations covering the three endpoints and oversized, overlong, or
  unknown-symbol input returned structured `422` responses. The corresponding
  journal interval contained request records but no chain-service traversal.
- A duplicated mixed-case objective normalized to `Li`, `Na`, and
  `Fe`, `P`, `O`; its complete parsed chain response equaled the canonical
  response.
- Complete parsed chain, exploration, and scientific-pathway JSON matched the
  pre-change captures exactly.
- Nginx rejected a 40,056-byte body with `413`.
- A 778-byte maximum-cardinality request containing 32 entries in each of the
  three collections returned `200` in 2.076870 seconds, within the documented
  five-second prototype budget.
- The deployed Nginx site matched `materialgraph.nginx`; MaterialGraph, Nginx,
  and the backup timer remained active and HTTPS health returned `200`.

## Migration reconciliation

Baseline capture initially exposed schema drift: production lacked the
existing `fraction_known` column. A verified backup completed before migration
`7a4c2e91b6d8` was applied. The migration reached repository head, affected
endpoints recovered, and isolated Alembic invocation subsequently worked
directly with the root-owned migration environment.

The migration-role password was rotated after an unsafe diagnostic displayed
the prior value. The replacement credential was verified without disclosure.

## Repository evidence

- Focused verification passed with 47 tests.
- The complete suite passed with 777 tests and one platform skip.
- Ruff and `git diff --check` passed.

## Conclusion

Public research-objective work is bounded and normalized before scientific
services, oversized bodies are rejected at the proxy, maximum valid work meets
the measured budget, and deterministic scientific behavior is unchanged.
`MG-SEC-008` is Verified.
