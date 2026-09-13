# MG-SEC-011 Verification — Immutable Secret-Scanning Automation

## Status

Verified on 2026-09-13. All eighteen acceptance criteria passed.

Final implementation:
`2c43193c0a31f355f0658afeeb97cf12266e0f1c`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Every third-party workflow Action reference uses a full commit SHA | Pass |
| 2 | Checkout uses reviewed commit `08c6903cd8c0fde910a37f88322edcfb5dd907a8` | Pass |
| 3 | Checkout is annotated as release `v5.0.0` | Pass |
| 4 | CI uses a tag-and-digest-pinned Gitleaks image | Pass |
| 5 | The local hook uses the identical Gitleaks image reference | Pass |
| 6 | CI scanner execution has networking disabled | Pass |
| 7 | Local scanner execution has networking disabled | Pass |
| 8 | CI mounts the repository read-only | Pass |
| 9 | The local hook mounts the repository read-only | Pass |
| 10 | CI continues to scan complete repository history | Pass |
| 11 | The local hook detects and redacts a staged synthetic secret | Pass |
| 12 | A detected secret blocks the commit | Pass |
| 13 | An unavailable scanner blocks the commit | Pass |
| 14 | A controlled scanner write cannot modify repository content | Pass |
| 15 | The first-party pin validator and regression tests pass | Pass |
| 16 | The complete repository test and lint suites pass | Pass |
| 17 | Repository policy requires full-length Action commit SHAs | Pass |
| 18 | A Secret Scan rerun succeeds with the policy active | Pass |

## Repository evidence

- `scripts/check_automation_pins.py` returned
  `automation_pins_valid=true` and verifies both workflow Action references and
  the shared Gitleaks digest.
- The focused automation and project-configuration suite passed 30 tests. Ruff
  and `git diff --check` passed. The complete suite passed with 816 tests and
  one platform skip.
- The pinned scanner completed a full-history scan of 269 commits in 4.63
  seconds with no leaks.
- A staged synthetic AWS access-key pattern produced a redacted finding. The
  hook returned exit code 1, reported that the commit was blocked, and left the
  worktree clean after probe removal.
- Removing Docker from the hook's effective path produced exit code 127 and
  blocked the commit, demonstrating fail-closed behavior.
- A write probe through `/repo:ro` failed with exit code 1 and created no file.
- The checkout `v5.0.0` tag resolved to full commit
  `08c6903cd8c0fde910a37f88322edcfb5dd907a8`.
- The reviewed Gitleaks multi-platform OCI digest is
  `sha256:75bdb2b2f4db213cde0b8295f13a88d6b333091bbfbf3012a4e083d00d31caba`.

## Hosted-policy evidence

- GitHub repository settings confirmed that full-length Action commit SHA
  pinning is required. General Action use remains permitted, so this evidence
  establishes immutable references rather than a publisher allowlist.
- Secret Scan run 85 succeeded after the pinned checkout runtime update.
- With the repository policy active, Secret Scan run 86 attempt 2 succeeded in
  13 seconds. Its Gitleaks job succeeded in 8 seconds, with no policy rejection
  or Node.js deprecation annotation.

## Residual interpretation

Commit and digest pinning prevents unreviewed tag movement from changing
executed code, but it does not prove the upstream artifact is benign. Updates
still require provenance review. Runtime network isolation does not prevent an
initial exact-digest pull by the container engine, and a read-only mount still
allows the scanner to inspect its source.

## Conclusion

Third-party secret-scanning automation now executes from reviewed immutable
references under repository enforcement. CI and the local hook use the same
contained scanner, staged scanning fails closed, secret values are redacted,
and controlled writes cannot alter repository content. `MG-SEC-011` is
Verified.
