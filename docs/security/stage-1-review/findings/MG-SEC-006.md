# MG-SEC-006 — Production Database Connection Is Unencrypted

## Status

Open.

## Assessment

- Severity: **High**
- Confidence: **High**
- Affected component: production EC2-to-Neon database transport
- Application evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Not resolved**

## Exact evidence

A read-only query executed through MaterialGraph's deployed SQLAlchemy engine
reported:

- `pg_stat_ssl.ssl=false`;
- TLS version is null;
- cipher is null.

The separately configured Alembic connection reports the same unencrypted
session properties. Both production database paths are affected.

The query did not print or record the connection URL, database name, role name,
or credential values.

## Threat scenario

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

## Missing safeguards

- TLS-required database connection policy.
- Certificate validation policy appropriate for the Neon endpoint.
- Startup or deployment verification that fails when the session is not using
  TLS.
- Regression evidence that requires encrypted production and migration
  connections.

## Recommended remediation

Require TLS with certificate validation in the production and migration
database connection configuration. Fail closed when the deployed connection
cannot establish an authenticated encrypted session.

## Verification requirements

- `pg_stat_ssl` reports `ssl=true` for the application and migration sessions.
- A modern TLS version and negotiated cipher are present.
- A connection that cannot validate the expected server certificate fails.
- Application startup, migrations, and representative scientific endpoints
  continue to work.
- Database URLs and credentials never appear in logs or test output.
