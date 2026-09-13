# MG-SEC-009 Change Impact — Bounded Screening Logs

## Status

Completed and verified on 2026-09-13.

Implementation commit:
`34bb5e44ffaab4afcbe00aa71f3ac053486ee561`.

## Baseline

Public screening accepted unbounded `scarce_elements` and `avoid_elements`
collections and wrote both complete user-controlled collections to the system
journal at `INFO`. The host had no project-specific journal storage, retention,
rate, or disk-monitoring policy. A safe local probe showed that a 157,871-byte
request could create a 177,850-byte log entry.

## Approved change

1. Limit each raw screening element collection to 32 entries.
2. Constrain, canonicalize, validate, and deterministically deduplicate element
   symbols before service work.
3. Replace complete request collections in success logs with bounded counts and
   boolean outcome metadata.
4. Apply a per-service 30-second, 200-message systemd log-rate policy.
5. Configure persistent journald storage with a 256 MiB maximum, 1 GiB free-space
   reserve, 14-day retention, and a 30-second/1,000-message base rate policy.
6. Run a daily one-shot monitor that fails and emits bounded numeric evidence
   when journal allocation reaches 230 MiB or root filesystem use reaches 80%.
7. Preserve screening results and deterministic ordering.

## Impact

- Invalid collections fail with structured HTTP `422` before screening runs.
- Count-only application logs replace complete user-controlled element lists.
- Equivalent case, whitespace, and duplicate variants produce the canonical
  request behavior.
- Successful logs have constant-size fields rather than request-sized lists.
- Journal retention is now explicit and repository controlled.
- Scheduled monitoring exposes journal or root-filesystem pressure through a
  failed systemd unit and bounded journal entry.
- The monitor measures allocated blocks on Linux so sparse journal files do not
  create false warnings from logical size alone.

## Deployment and recovery note

An evidence-shell `umask 077` remained active during the production pull and
created newly introduced tracked files without group or other read bits. The
capability-free application and monitor correctly failed to read those files.
Tracked files were restored to repository-compatible readability, the shell
umask was reset to `022`, the worktree remained clean, and both services then
passed. No application, policy, or data rollback was required.

## Residual boundaries

The configured journald burst is a base policy and systemd may adapt effective
suppression according to available disk space. A controlled 220-request health
probe completed successfully and did not trigger suppression; it is not
evidence of a strict 200-message ceiling. Aggregate public request admission and
concurrency controls remain assigned to `MG-SEC-001`.
