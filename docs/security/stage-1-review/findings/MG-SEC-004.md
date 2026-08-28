# MG-SEC-004 — Internet-Facing Service Runs with Passwordless Root Authority

## Status

Open.

## Assessment

- Severity: **High**
- Confidence: **High**
- Affected component: systemd runtime identity and EC2 privilege boundary
- Deployment checkpoint: `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Not resolved**

## Exact evidence

- MaterialGraph runs as `ubuntu:ubuntu`.
- The runtime account belongs to `sudo` and `lxd`.
- Sudo policy grants `(ALL) NOPASSWD: ALL`.
- The same account owns the application directory and production environment
  file.
- Effective systemd properties include `NoNewPrivileges=no`, `PrivateTmp=no`,
  `ProtectSystem=no`, and `ProtectHome=no`.

## Threat scenario

Code execution through the public application or a runtime dependency gives an
attacker the `ubuntu` service identity. That identity can immediately execute
arbitrary commands as root without a password, modify code and configuration,
read secrets, and establish host-level persistence.

## Current safeguards

- Uvicorn is exposed only through Nginx.
- Port 8000 is loopback-bound and absent from security-group ingress.
- Current features do not intentionally execute uploaded or user-provided code.
- SSH ingress is source-restricted.

## Missing safeguards

- Dedicated non-login runtime user with no administrative groups.
- Separation between deployment and runtime identities.
- `NoNewPrivileges=true` and appropriate systemd sandboxing.
- Read-only application code and narrowly writable runtime paths.
- Verification of required filesystem and network access after hardening.

## Recommended remediation

Run MaterialGraph under a dedicated least-privilege service account. Keep
deployment and administrative authority outside the runtime identity, then add
systemd hardening incrementally based on demonstrated runtime requirements.

## Verification requirements

- The service identity cannot use sudo, LXD, or obtain root authority.
- Application code and deployment configuration are not writable by the
  runtime identity unless explicitly required.
- MaterialGraph starts, restarts, logs, and connects to required services.
- Scientific endpoint results and deterministic ordering remain unchanged.
