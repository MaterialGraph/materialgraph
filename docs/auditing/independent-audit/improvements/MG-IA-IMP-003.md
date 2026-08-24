# MG-IA-IMP-003 — Add a stable tie-breaker to graph-job listing

- Classification: worthwhile determinism improvement
- Priority: P3
- Status: proposed

## Evidence

`GraphJobService.list_jobs` orders only by descending `created_at`. Jobs created with equal database timestamps can therefore inherit unspecified row order, which can also affect offset pagination. Claim ordering already demonstrates the preferred pattern by using creation time followed by UUID.

The routes are intentionally absent from the public API, so no material public defect is confirmed.

## Recommended scope

Order listings by `created_at DESC, id DESC` (or another documented stable UUID direction) and add an equal-timestamp pagination regression test before the listing surface is enabled.
