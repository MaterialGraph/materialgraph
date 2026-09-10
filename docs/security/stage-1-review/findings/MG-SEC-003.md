# MG-SEC-003 — Production Environment File Is World-Readable

## Status

In remediation as of 2026-09-10.

## Assessment

- Severity: **Medium**
- Confidence: **High**
- Affected component: production EC2 filesystem and secret storage
- Deployment checkpoint: `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Remediation baseline:
  `28d205db60467a949a74f6e38135c20825b55502`
- Resolution version or commit: **Pending deployment verification**

## Exact evidence

- `/opt/materialgraph/.env` is owned by `ubuntu:ubuntu` with mode `664`.
- Parent directories permit traversal by local users.
- The environment file supplies production configuration to systemd and is
  documented to contain application credentials.

No secret value or environment-file content was inspected or recorded.

The deployed mode was subsequently corrected to `600` during approved
MG-SEC-007 work. MG-SEC-003 now adds fail-closed pre-start enforcement and
independent deployment verification; the original evidence remains preserved
above for audit history.

## Threat scenario

Any unprivileged local account or process with limited execution on the host
can read the production environment file. That access can expose database or
external-service credentials and expand a restricted local compromise beyond
the EC2 instance.

## Current safeguards

- The file is outside source control.
- Environment paths are ignored by Git.
- Credential rotation and Gitleaks controls are documented.
- SSH ingress is restricted to one source address.

## Missing safeguards

- Owner-only mode such as `600`, or a deliberately designed group-readable
  `640` boundary.
- Dedicated service identity and least-privilege ownership model.
- Deployment verification that rejects unsafe secret-file permissions.

## Recommended remediation

Restrict the file to the minimum identity that requires it and align ownership
with the dedicated runtime-service design. Add a deployment check for owner,
group, and mode without printing file contents.

## Verification requirements

- Unauthorized local identities cannot read the environment file.
- systemd can still load the environment and start MaterialGraph.
- Database and external integrations remain functional.
- No secret value appears in test, command, or log output.

Current implementation and acceptance evidence are maintained in
[`../remediation/`](../remediation/README.md). The administrative authority of
the current service account remains separate MG-SEC-004 scope.
