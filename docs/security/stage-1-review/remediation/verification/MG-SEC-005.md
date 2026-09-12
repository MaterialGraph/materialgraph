# MG-SEC-005 Verification — Public HTTPS Transport

## Status

Verified on 2026-09-12. All sixteen acceptance criteria passed.

Baseline: `602538d5d439a90230a67ea0425fc376a54972b9`.

## Acceptance criteria

| # | Criterion | Status |
|---:|---|---|
| 1 | Apex and `www` DNS names resolve directly to the approved EC2 IPv4 address | Pass |
| 2 | One trusted certificate covers `materialgraph.org` and `www.materialgraph.org` | Pass |
| 3 | Certificate validity dates and Let's Encrypt issuer are present | Pass |
| 4 | Nginx configuration validation succeeds | Pass |
| 5 | Nginx listens publicly on ports 80 and 443 | Pass |
| 6 | Apex HTTP requests redirect permanently to the same HTTPS path | Pass |
| 7 | `www` HTTP requests redirect permanently to the same HTTPS path | Pass |
| 8 | Apex HTTPS health returns HTTP `200` | Pass |
| 9 | `www` HTTPS health returns HTTP `200` | Pass |
| 10 | TLS 1.0 and TLS 1.1 handshakes are rejected | Pass |
| 11 | TLS 1.2 and TLS 1.3 handshakes succeed | Pass |
| 12 | HSTS is consistently returned with a one-year maximum age | Pass |
| 13 | The response server header omits the Nginx version | Pass |
| 14 | Certbot renewal timer is enabled and active and a dry run succeeds | Pass |
| 15 | Material, screening, and discovery responses match complete parsed pre-change JSON exactly | Pass |
| 16 | MaterialGraph, Nginx, and the backup timer remain active | Pass |

## Repository evidence

- `materialgraph.nginx` preserves loopback proxying, defines only TLS 1.2/1.3
  through Certbot's maintained options, redirects plaintext traffic, applies
  HSTS, and suppresses version disclosure.
- The deployment guide documents certificate issuance, installation of the
  reviewed final site, validation, renewal testing, rollback, and monitoring.
- Certificate paths are configuration references only; no certificate private
  key or registration contact data is tracked.

## Production evidence

- Public DNS checks from EC2 and an independent Windows client resolved both
  hostnames to the approved EC2 IPv4 address.
- Let's Encrypt issued one certificate whose subject alternative names are
  `materialgraph.org` and `www.materialgraph.org`; its observed validity was
  2026-09-12 through 2026-12-11.
- Nginx validation succeeded and listeners were present on ports 80 and 443.
- Independent public checks returned `301` from HTTP with the original health
  path preserved and returned HTTP `200` over HTTPS for both names.
- OpenSSL probes rejected TLS 1.0 and 1.1 and accepted TLS 1.2 and 1.3.
- Repeated requests consistently returned
  `Strict-Transport-Security: max-age=31536000`; the server header was reduced
  to `nginx` without a version.
- `certbot.timer` was enabled and active. `certbot renew --dry-run` successfully
  simulated renewal for both certificate names.
- Complete parsed JSON for a material read, screening request, and discovery
  request matched the pre-change captures exactly.
- MaterialGraph, Nginx, and the verified-backup timer remained active.

## Operational note

The first header check used an HTTP `HEAD` request against a GET-only health
route and correctly received `405`; a GET request returned `200`. Immediately
after reload, one observation retained the prior versioned server header while
another had the new settings. Process inspection confirmed one systemd-managed
master and its current workers, and five repeated requests consistently
returned HSTS. No manual process termination was required.

## Conclusion

Public scientific traffic is authenticated and encrypted, plaintext requests
are redirected before proxying, obsolete TLS versions are rejected, renewal is
exercised, and deterministic scientific behavior is unchanged. `MG-SEC-005`
is Verified.
