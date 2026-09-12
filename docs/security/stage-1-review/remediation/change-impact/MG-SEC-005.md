# MG-SEC-005 Change Impact — Public HTTPS Transport

## Status

Completed and verified on 2026-09-12.

Repository and deployment baseline:
`602538d5d439a90230a67ea0425fc376a54972b9`.

## Baseline

- `materialgraph.org` was registered for the project and configured with
  DNS-only records for the apex and `www` hostnames.
- Both names resolved directly to the existing EC2 IPv4 address.
- Nginx listened publicly only on port 80 and proxied plaintext requests to
  loopback-bound Uvicorn.
- EC2 already permitted inbound TCP 443, but no process listened there.

## Approved scope

1. Issue one publicly trusted certificate covering `materialgraph.org` and
   `www.materialgraph.org`.
2. Serve both names over HTTPS through Nginx while retaining loopback-only
   Uvicorn.
3. Redirect every HTTP request to the same host, path, and query over HTTPS.
4. Reject TLS 1.0 and 1.1 while accepting TLS 1.2 and 1.3.
5. Enable one-year HSTS without `includeSubDomains` or preload.
6. Hide the Nginx version and retain a repository-controlled final site file.
7. Enable and exercise automated certificate renewal.
8. Compare complete parsed scientific responses before and after the change.

## Expected impact

- Public research objectives and results are encrypted and authenticated in
  transit.
- Existing HTTP clients receive a permanent redirect rather than plaintext
  proxied scientific content.
- API payloads, ordering, scores, explanations, and database behavior remain
  unchanged.
- Let's Encrypt and Certbot add no paid infrastructure service.

## Rollout and rollback

1. Preserve the active Nginx site and global configuration as root-owned mode
   `600` rollback files.
2. Capture representative material, screening, and discovery JSON over HTTP.
3. Confirm both DNS names resolve directly to the EC2 address and return
   healthy HTTP responses.
4. Install Certbot's Nginx integration and request both certificate names.
5. Validate Nginx before every reload and require HTTPS health from an
   independent public client.
6. On failure, restore the saved site and global configuration, validate it,
   reload Nginx, and confirm HTTP health.
7. Remove rollback and response captures only after the reviewed repository
   configuration is deployed and final verification is recorded.

## Non-goals and residual boundaries

- Cloudflare remains DNS-only during this verification. Proxying, WAF rules,
  and CDN behavior are separate changes.
- HSTS does not include subdomains and is not submitted for browser preload.
- This remediation does not add rate limits, request deadlines, body-size
  limits, or authentication; those remain separately tracked findings or
  future scope.
- Certificate private keys and domain-registration contact data are never
  copied into the repository or evidence.
