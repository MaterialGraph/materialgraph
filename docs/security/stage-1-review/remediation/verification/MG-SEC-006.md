# MG-SEC-006 Revalidation — Database Transport

## Status

Retired after deployment revalidation on 2026-09-06. The original finding was
not supported by end-to-end client evidence. Proportionate certificate and
hostname validation hardening was also completed and verified.

## Scope

- production runtime database connection;
- production migration and backup connection;
- EC2-to-Neon client transport;
- deployed configuration only, without recording connection URLs or secrets.

## Classification correction

The inspection queried `pg_stat_ssl` through Neon and received `ssl=false` with
null TLS version and cipher. That view represented the observed backend
connection after Neon's proxy boundary, not the TLS state of the originating
EC2 client. It was therefore insufficient evidence for the original conclusion
that MaterialGraph sent database traffic in plaintext.

Direct client evidence established that both production paths already:

- required TLS through `sslmode=require`;
- required SCRAM channel binding through `channel_binding=require`;
- negotiated TLS 1.2 or newer; and
- rejected an explicit plaintext connection attempt.

The original High-severity threat scenario was therefore not present. The
identifier is retired rather than marked Verified, because remediation did not
resolve the alleged plaintext condition; revalidation disproved it.

## Proportionate hardening

PostgreSQL distinguishes encrypted `require` mode from `verify-full`, which
also validates the certificate chain and requested server hostname. Both
deployed connection paths successfully passed a `verify-full` probe, so their
configuration was changed to `sslmode=verify-full` without adding a paid
service, certificate, key-management system, or infrastructure component.
`channel_binding=require` was retained.

## Redacted verification evidence

| Check | Result |
|---|---|
| Runtime connection succeeded | Pass |
| Runtime client TLS active | Pass |
| Runtime TLS 1.2 or newer | Pass |
| Runtime plaintext attempt rejected | Pass |
| Runtime `verify-full` probe | Pass |
| Migration connection succeeded | Pass |
| Migration client TLS active | Pass |
| Migration TLS 1.2 or newer | Pass |
| Migration plaintext attempt rejected | Pass |
| Migration `verify-full` probe | Pass |
| Deployed runtime URL uses `verify-full` | Pass |
| Deployed migration URL uses `verify-full` | Pass |
| Both URLs retain required channel binding | Pass |
| Production restart and health check | Pass (`HTTP 200`) |
| Verified backup under hardened migration path | Pass (9 tables; explicit Ubuntu CA bundle) |
| Daily backup timer remained active and enabled | Pass |
| Temporary protected configuration copy removed | Pass |

The first health request immediately after restart returned `502`; a repeat
returned `200`. The systemd journal showed a clean shutdown, successful startup
one second later, and no database or TLS error. This was classified as a
startup-readiness race and is not evidence of transport failure.

## Follow-up source correction

Post-reconciliation source inspection found that `database_environment()` in
the backup helper forced `PGSSLMODE=require`, independently of the migration
URL. The recorded backup therefore proved encrypted connectivity and backup
integrity, but did not prove certificate and hostname validation. The helper
has been changed to enforce `verify-full` and required channel binding even if
an input URL requests weaker settings. Testing inside the systemd isolation
showed that implicit CA discovery and `sslrootcert=system` failed, while the
readable Ubuntu CA bundle at `/etc/ssl/certs/ca-certificates.crt` succeeded.
The helper now supplies that explicit CA bundle to psycopg and `pg_dump`. A
deployed run completed successfully on 2026-09-06, verified a nine-table
archive, and left the application healthy and backup timer active.

## Secret-handling evidence

- Connection strings and passwords were not printed.
- Verification output contained only booleans and non-secret protocol
  properties.
- The deployment environment file remained outside source control.
- The temporary owner-readable rollback copy was removed after verification.

## Disposition

`MG-SEC-006` remains Retired because the original plaintext conclusion was
disproved. The original record remains available for traceability and the
`verify-full` changes are retained as verified defense-in-depth hardening.

## Authoritative references

- [PostgreSQL SSL support and protection by mode](https://www.postgresql.org/docs/current/libpq-ssl.html)
- [PostgreSQL connection parameters](https://www.postgresql.org/docs/current/libpq-connect.html)
- [Neon secure connection guidance](https://neon.com/docs/connect/connect-securely)
