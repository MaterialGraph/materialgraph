# MG-SEC-011 Change Impact — Immutable Secret-Scanning Automation

## Status

Completed and verified on 2026-09-13.

Implementation commit:
`2c43193c0a31f355f0658afeeb97cf12266e0f1c`.

## Baseline

The secret-scan workflow used a mutable checkout tag and both CI and the local
hook used a mutable Gitleaks tag. The local container had network access and a
read-write repository mount. Repository policy did not require full-length
commit pins.

## Approved change

1. Pin `actions/checkout` to a reviewed full commit SHA and retain its release
   annotation for maintainability.
2. Pin the same reviewed Gitleaks tag-and-digest reference in CI and the local
   pre-commit hook.
3. Disable networking for scanner containers and mount the repository
   read-only.
4. Preserve complete-history scanning in CI and staged-change scanning in the
   local hook.
5. Keep the hook fail closed when Docker, the image, or scanning is unavailable.
6. Validate automation references with a first-party script and regression
   tests.
7. Require full-length Action commit SHAs through repository policy.
8. Document the review and update process for immutable automation references.

## Impact

- A changed upstream tag cannot silently alter the Action or scanner code that
  executes for the reviewed configuration.
- Scanner code receives neither an outbound network route nor write access to
  repository content at runtime.
- CI and developer hooks use one auditable scanner artifact.
- Repository policy rejects mutable third-party Action references even if a
  future workflow bypasses the repository validator.
- A missing scanner remains a blocking condition rather than silently skipping
  secret detection.

## Operational boundary

`--network none` applies to the running scanner container. The container engine
may need registry access to fetch the exact digest before execution. The
read-only mount prevents modification but does not prevent the trusted scanner
from reading files supplied within its scan source.

## Rollback

The change affects repository automation and policy, not the production
application or database. A reviewed replacement requires resolving new
upstream identifiers, updating both scanner references together, running the
validator and security tests, and confirming a policy-enforced workflow run.
Reverting to mutable references is not an approved rollback.

## Residual boundaries

The repository permits actions from any publisher when they are pinned to a
full commit SHA; it does not maintain a publisher allowlist. Digest and commit
updates still require human provenance review. Production dependency locking
and vulnerability gating remain assigned to `MG-SEC-010`.
