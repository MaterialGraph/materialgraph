# MG-SEC-011 — Mutable Third-Party Automation References Permit Unreviewed Code Execution

## Status

Open.

## Assessment

- Severity: **Medium**
- Confidence: **High**
- Affected component: repository-local Gitleaks pre-commit hook and GitHub
  Actions secret-scan workflow
- Application evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Repository-policy evidence checkpoint:
  `5bf859ae70444d223a147018c48f80bee1d90e21`
- Resolution version or commit: **Not resolved**

## Exact evidence

- The GitHub Actions workflow references `actions/checkout@v4`, a mutable
  version tag rather than a full commit SHA.
- CI and the repository-local pre-commit hook reference
  `ghcr.io/gitleaks/gitleaks:v8.18.4`, a mutable container tag rather than an
  immutable image digest.
- Repository policy permits all actions and reusable workflows.
- Repository policy does not require actions to be pinned to full-length commit
  SHAs.
- The local hook mounts the complete working repository read-write at `/repo`
  inside the tagged container. That mount can include ignored configuration
  files such as `.env`.
- The container invocation declares no outbound network restriction.
- The most recent inspected Secret Scan completed successfully; successful
  execution establishes current operation but not future tag immutability.

## Threat scenario

If an upstream release tag is maliciously repointed, or the upstream publisher
or registry is compromised, a fresh CI runner or developer image pull can
execute different code without a reviewed MaterialGraph change. In the local
hook, that code receives read-write access to the repository and can read or
transmit ignored configuration files and modify working-tree content.

## Current safeguards

- GitHub's default workflow token has read-only repository contents and packages
  permission.
- The workflow explicitly declares `contents: read`.
- GitHub Actions cannot create or approve pull requests.
- First-time external contributors require workflow approval.
- No self-hosted runner exposes EC2 or another persistent host.
- The repository is public, reducing confidentiality impact for tracked source.
- Gitleaks uses a version tag rather than `latest`.
- The latest inspected Secret Scan completed successfully.

## Missing safeguards

- Full commit-SHA pinning for GitHub Actions.
- Immutable digest pinning for the Gitleaks container.
- A repository policy requiring immutable Action references.
- A read-only repository mount where Gitleaks operation permits it.
- Network restriction or equivalent containment for the local scanner.
- A documented process for reviewing and updating pinned automation versions.

## Recommended remediation

Pin every third-party Action to a reviewed full commit SHA and annotate the
human-readable release version. Pin the Gitleaks image to a reviewed digest in
both CI and the local hook. Evaluate a read-only mount and network containment
without weakening staged-secret detection, and enable repository SHA-pinning
policy after every workflow reference complies.

## Verification requirements

- Workflow validation confirms every third-party Action uses a full commit SHA.
- CI and the local hook use the same reviewed Gitleaks image digest.
- Repository policy rejects newly introduced mutable Action references.
- Gitleaks continues to scan complete history in CI and staged changes locally.
- The local hook fails closed when the image is unavailable or scanning fails.
- A controlled test confirms the scanner cannot modify repository content when
  a read-only mount is adopted.
- Secret-detection tests pass without printing secret values.
