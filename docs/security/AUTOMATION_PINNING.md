# Automation Pinning Policy

## Scope

Every third-party GitHub Action must use a full 40-character commit SHA. Every
container executed by security automation must use a reviewed immutable digest.
A human-readable version comment or tag may accompany the immutable identity.

The current Gitleaks release is `v8.18.4`, pinned to the multi-platform manifest
digest recorded identically in `.github/workflows/secret-scan.yml` and
`.githooks/pre-commit`. The checkout action uses the `v5.0.0` release
commit.

## Updating a pin

1. Read the upstream release notes and security history.
2. Resolve the release tag to its full upstream commit or top-level
   multi-platform image digest.
3. Review the source diff from the currently approved version.
4. Update CI and local-hook image references in the same commit.
5. Run `python scripts/check_automation_pins.py` and its tests.
6. Run Gitleaks against complete history and staged-change test cases with
   redaction enabled.
7. Review the repository diff before merging.
8. Enable and retain GitHub's policy requiring full-length Action commit SHAs.

Never obtain an immutable identifier from an untrusted repost. Resolve it from
the upstream GitHub repository or registry, record the associated release, and
review both together.

## Local containment

The local hook mounts the repository read-only and runs Gitleaks with container
networking disabled. Staged scanning needs repository and index reads but does
not require write access or outbound traffic. Docker must obtain the pinned
image before the hook runs; an unavailable image or scanner failure returns a
nonzero status and blocks the commit.

## Verification

Use a disposable staged file containing a synthetic Gitleaks test credential.
Confirm that the commit is blocked and output remains redacted, then unstage and
delete the file. Do not use a real credential. Separately compare a tracked
sentinel file before and after scanning to prove the read-only mount prevents
scanner modification.
