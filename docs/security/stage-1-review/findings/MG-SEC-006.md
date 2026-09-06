# MG-SEC-006 — Production Database Connection Is Unencrypted

## Status

Retired after deployment revalidation on 2026-09-06.

## Assessment

- Severity: **High**
- Confidence: **High**
- Affected component: production EC2-to-Neon database transport
- Application evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Deployment configuration only; repository
  reconciliation pending**

## Revalidation disposition

The original conclusion is not supported by end-to-end client evidence. The
`pg_stat_ssl` result below described the Neon proxy's backend session rather
than the EC2 client's TLS session. Both deployed client paths required TLS,
negotiated TLS 1.2 or newer, rejected plaintext, and successfully completed
certificate and hostname validation.

The identifier is retained for audit history but is no longer an actionable
security finding. The narrower certificate-validation hardening was completed
by changing both deployed URLs from `sslmode=require` to
`sslmode=verify-full`, while retaining `channel_binding=require`.

## Original exact evidence

A read-only query executed through MaterialGraph's deployed SQLAlchemy engine
reported:

- `pg_stat_ssl.ssl=false`;
- TLS version is null;
- cipher is null.

The separately configured Alembic connection reported the same proxy-side
session properties. The inspection originally interpreted both results as
client transport evidence.

The query did not print or record the connection URL, database name, role name,
or credential values.

## Original threat scenario

A network-positioned attacker between EC2 and Neon can observe or tamper with
database authentication and application traffic. Exposure of the database
credential can permit direct access using the role's broad privileges, while
modified query results can undermine stored scientific data and deterministic
outputs.

## Current safeguards

- The database credential is stored outside source control.
- The previously exposed credential was rotated and removed from current Git
  history.
- Gitleaks scans history and staged changes.
- Neon is reached through a configured connection string rather than a public
  database service hosted on the EC2 instance.

## Original missing safeguards

- TLS-required database connection policy.
- Certificate validation policy appropriate for the Neon endpoint.
- Startup or deployment verification that fails when the session is not using
  TLS.
- Regression evidence that requires encrypted production and migration
  connections.

## Revalidation evidence

- Runtime and migration URLs both target Neon and explicitly required TLS and
  SCRAM channel binding before remediation.
- Independent client probes succeeded over TLS 1.2 or newer for both paths.
- `sslmode=disable` failed for both paths.
- `sslmode=verify-full` succeeded for both paths.
- After deployment hardening, direct runtime and migration connections
  succeeded with `sslmode=verify-full` and `channel_binding=require`.
- MaterialGraph restarted successfully and returned HTTP `200` from `/health`.
- The isolated backup service completed a verified nine-table logical backup
  using the migration connection.
- No URL, password, role name, database name, or credential value was recorded.

Complete redacted evidence and the classification rationale are maintained in
[`../remediation/verification/MG-SEC-006.md`](../remediation/verification/MG-SEC-006.md).

## Original recommended remediation

Require TLS with certificate validation in the production and migration
database connection configuration. Fail closed when the deployed connection
cannot establish an authenticated encrypted session.

## Original verification requirements

- Client-side transport inspection confirms TLS for application and migration
  sessions; proxy-side `pg_stat_ssl` is not treated as end-to-end evidence.
- A modern TLS version and negotiated cipher are present.
- A connection that cannot validate the expected server certificate fails.
- Application startup, migrations, and representative scientific endpoints
  continue to work.
- Database URLs and credentials never appear in logs or test output.
