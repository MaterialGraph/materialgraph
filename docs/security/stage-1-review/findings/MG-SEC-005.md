# MG-SEC-005 — Public API Traffic Is Served over Unencrypted HTTP

## Status

Verified on 2026-09-12.

## Assessment

- Severity: **Medium**
- Confidence: **High**
- Affected component: public Nginx and EC2 network boundary
- Deployment checkpoint: `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Remediation baseline:
  `602538d5d439a90230a67ea0425fc376a54972b9`

## Exact evidence

- EC2 permits TCP port 80 from all IPv4 addresses.
- Nginx listens publicly on port 80 and proxies all paths to MaterialGraph.
- EC2 also permits port 443, but no process listens on that port.
- Effective Nginx configuration has no certificate, TLS server block, or
  HTTP-to-HTTPS redirect.

## Threat scenario

A network-positioned attacker can observe or modify research objectives, API
responses, documentation, and health responses in transit. Modified scientific
results undermine MaterialGraph's integrity and explainability guarantees.

## Current safeguards

- Current prototype data is public.
- Authentication, private workspaces, billing, and uploads are not implemented.
- Uvicorn itself is not directly exposed.

## Missing safeguards

- Active HTTPS listener and certificate.
- Modern TLS protocol policy.
- HTTP-to-HTTPS redirect.
- Certificate-renewal procedure and monitoring.
- Deployment verification that public routes are served securely.

## Recommended remediation

Configure an HTTPS Nginx server with a trusted certificate and modern protocol
policy, redirect HTTP to HTTPS, and document renewal and failure handling. The
currently configured legacy TLS protocol values should not be carried into the
active TLS policy.

## Verification requirements

- HTTPS serves every intended public route with a valid certificate.
- HTTP redirects to HTTPS without proxying scientific requests in plaintext.
- Obsolete TLS versions are rejected.
- Certificate renewal is tested or monitored.
- Scientific responses are unchanged after transport hardening.

## Resolution

The project registered `materialgraph.org`, configured the apex and `www`
names directly to the production EC2 host, and deployed one trusted certificate
covering both names. Nginx now redirects HTTP to HTTPS, rejects TLS 1.0 and 1.1,
serves TLS 1.2 and 1.3, returns a one-year HSTS policy, and omits its version.
Automated renewal is enabled and a simulated renewal succeeded. Independent
public health checks and complete parsed material, screening, and discovery
responses passed without scientific change. See
[`../remediation/verification/MG-SEC-005.md`](../remediation/verification/MG-SEC-005.md).
