# MG-IA-026 — Deployment guide never creates the systemd service it operates

- Classification: deployment documentation defect
- Priority: P3
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `DEPLOYMENT.md`, “Application Deployment” and “systemd Service”
- production systemd service setup
- fresh-server deployment workflow

## Exact evidence

The guide creates `/opt/materialgraph`, clones and installs the application,
runs migrations, and verifies a manual Uvicorn start. Its systemd section then
names `/etc/systemd/system/materialgraph.service` and immediately instructs the
operator to run `systemctl daemon-reload`, `start`, and `enable`.

No preceding or subsequent step creates that unit file, supplies its contents,
copies a version-controlled unit into place, or links to a complete unit
definition. The guide also does not specify the service's `WorkingDirectory`,
`EnvironmentFile`, `ExecStart`, user, or restart policy.

## Expected behavior

A fresh-server deployment guide that includes systemd activation should provide
or reference the exact unit definition and install it before invoking
`systemctl start` and `systemctl enable`.

## Actual behavior

Following the documented sequence on a fresh EC2 instance reaches systemd
commands without an installed `materialgraph.service` unit.

## Technical impact

The documented production deployment is not reproducible from the guide alone.
Operators must reconstruct deployment-critical process configuration from
outside evidence, which can change the environment file, working directory,
interpreter, bind address, and restart behavior.

## Reproduction

On a fresh Ubuntu instance, follow the guide through manual FastAPI verification
and then run its first systemd commands without independently creating
`/etc/systemd/system/materialgraph.service`. `systemctl start materialgraph`
cannot start a unit that has not been installed.

## Relevant existing tests

The supplied health and project-configuration tests verify application behavior
and version/configuration resolution. They do not install or validate production
systemd configuration.

## Missing regression coverage

- No version-controlled unit file was supplied for static verification.
- No deployment smoke test validates a clean EC2/systemd setup.
- No documented check verifies the running service's working directory,
  environment-file source, interpreter, or bind address.

## Caller and workflow trace

Nginx proxies to `127.0.0.1:8000`, while routine deployment operations restart
`materialgraph` and then curl the local health endpoint. Those steps depend on
the omitted unit definition to launch Uvicorn with the correct checkout and
environment.

## Recommended remediation scope

Add a version-controlled systemd unit template or the complete reviewed unit
definition to the deployment guide. Include installation, ownership and mode,
`WorkingDirectory`, `EnvironmentFile`, virtual-environment `ExecStart`, bind
address/port, restart behavior, daemon reload, enable/start, and verification.
Keep credential values outside the tracked unit and repository.
