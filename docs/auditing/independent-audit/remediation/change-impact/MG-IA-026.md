# MG-IA-026 Change Impact — Reproducible systemd Deployment

## Status

Verified locally: focused project-configuration tests, the full test suite,
Ruff, and Git whitespace validation passed.

## Before

The deployment guide named `/etc/systemd/system/materialgraph.service` and
immediately invoked systemd operations without creating or installing that
unit. Operators had to reconstruct the service user, working directory,
environment source, executable, bind address, and restart policy.

The checkout instructions also created `/opt/materialgraph` and then cloned a
nested `/opt/materialgraph/materialgraph` checkout, conflicting with the
documented environment-file path and established deployment layout. The root
README linked to a deployment-guide path that did not exist.

## After

The repository root contains a reviewed `materialgraph.service`. It runs as the
`ubuntu` user and group, uses `/opt/materialgraph` as its working directory,
loads `/opt/materialgraph/.env`, launches the checkout's virtual-environment
Uvicorn executable on `127.0.0.1:8000`, and restarts after failures. It contains
no credential values.

The guide installs this tracked unit into `/etc/systemd/system` with root
ownership and mode `0644` before reloading and starting systemd. Checkout and
routine-update paths consistently use `/opt/materialgraph`, and the README now
links to the actual deployment guide.

## Impact

- Fresh-server reproducibility: **Corrected** — the operated unit is supplied
  and installed before activation.
- Deployment-path consistency: **Corrected** — checkout, environment, service,
  and update paths agree.
- Process configuration: **Explicit** — identity, directory, environment,
  executable, bind address, port, and restart policy are version controlled.
- Secret isolation: **Preserved** — credentials remain in the untracked EC2
  environment file.
- Public network exposure: **Unchanged** — Uvicorn binds to loopback behind
  Nginx.
- Application runtime, API, database, and scientific behavior: **No change**.

## Scope decision

The canonical template is stored at the repository root as
`materialgraph.service`, matching the project's preferred layout. Committing
the template does not overwrite the currently installed EC2 unit; production
installation remains an explicit operator action.
