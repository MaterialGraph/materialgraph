# MG-SEC-009 Verification — Bounded Screening Logs

## Status

Verified on 2026-09-13. All twenty acceptance criteria passed.

Implementation: `34bb5e44ffaab4afcbe00aa71f3ac053486ee561`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Each raw screening element collection is limited to 32 entries | Pass |
| 2 | Element symbols are constrained to two characters and validated | Pass |
| 3 | Valid symbols are canonicalized and deduplicated in first-seen order | Pass |
| 4 | Oversized screening collections return structured HTTP `422` | Pass |
| 5 | Overlong symbols return structured HTTP `422` | Pass |
| 6 | Unknown symbols return structured HTTP `422` | Pass |
| 7 | Rejected requests do not enter the screening service | Pass |
| 8 | Successful screening logs contain counts and bounded boolean metadata | Pass |
| 9 | Successful screening logs do not contain submitted element collections | Pass |
| 10 | A maximum-cardinality completion log remains below 256 bytes | Pass |
| 11 | A maximum valid 32-plus-32 request returns HTTP `200` | Pass |
| 12 | Canonical and duplicate mixed-case input preserves complete response equality | Pass |
| 13 | Normal screening output matches complete parsed pre-change JSON | Pass |
| 14 | MaterialGraph declares a 30-second, 200-message base rate policy | Pass |
| 15 | Journald declares explicit storage, free-space, retention, and rate policies | Pass |
| 16 | The journal monitor uses allocated Linux blocks and bounded thresholds | Pass |
| 17 | The daily monitor timer is installed, enabled, and active | Pass |
| 18 | A production monitor run completes successfully with `status=ok` | Pass |
| 19 | Journal allocation remains below its limit and root filesystem use below threshold | Pass |
| 20 | MaterialGraph, Nginx, backup scheduling, and HTTPS health remain active | Pass |

## Production evidence

- The canonical screening request returned 28 results. Its complete parsed JSON
  matched the pre-change capture exactly.
- Mixed-case, whitespace-padded duplicates normalized to the same request and
  produced an identical complete response.
- Collections with 33 entries, an overlong value, or an unknown symbol each
  returned structured `422`; the corresponding interval contained zero
  `candidate_screening_completed` entries.
- A request containing 32 scarce and 32 avoided elements returned `200` in
  0.418 seconds with valid JSON and 28 results.
- Success entries contained only outcome, result count, normalized collection
  counts, and boolean flags. The largest measured completion entry was 255
  bytes and contained no submitted collection.
- Effective MaterialGraph properties reported `LogRateLimitIntervalUSec=30s`
  and `LogRateLimitBurst=200`.
- Effective journald configuration reported persistent storage, `SystemMaxUse`
  256 MiB, `SystemKeepFree` 1 GiB, 14-day retention, and a 30-second/1,000-message
  base rate policy.
- The corrected allocation-aware monitor reported `status=ok`, 50,339,840
  allocated journal bytes, and 70.55% filesystem use. Its one-shot unit finished
  successfully; its daily timer was enabled and active.
- `journalctl --disk-usage` fell from 191.1 MiB before policy activation to
  48.0 MiB afterward. Final root-filesystem use was 71%.
- MaterialGraph and Nginx were active, HTTPS health returned `200`, and backup,
  certificate-renewal, and journal-monitor timers were active.

## Rate-policy interpretation

A controlled 220-request local health probe completed with 220 successful
responses and 220 recorded access entries. This confirms availability during
the probe but not suppression. Journald can adapt its configured base burst to
available disk space, so verification relies on the effective unit property and
does not misstate `200` as a strict observed ceiling.

## Deployment incident

The first activation exposed permissions created by a lingering evidence-shell
`umask 077`: the capability-free runtime could not read a newly pulled schema
file and the monitor could not read its script. After tracked files regained
read permission and the shell returned to `umask 022`, the worktree stayed clean,
MaterialGraph recovered to HTTP `200`, and the monitor passed. The failed and
successful unit entries remain journaled as operational evidence.

## Repository evidence

- Focused verification passed with 41 tests before the allocation fix.
- The complete suite passed with 792 tests and one platform skip.
- Ruff and `git diff --check` passed.
- The allocated-block correction added a focused regression and was deployed at
  the implementation commit above.

## Conclusion

Screening input cardinality and symbols are validated before service work,
application logs no longer scale with submitted collections, journal storage
has explicit bounds, and scheduled monitoring reports resource pressure without
changing deterministic scientific behavior. `MG-SEC-009` is Verified.
