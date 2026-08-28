# MG-SEC-007 — Application Database Role Has Administrative Capabilities

## Status

Open.

## Assessment

- Severity: **High**
- Confidence: **High**
- Affected component: Neon role and production application credential boundary
- Application evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Not resolved**

## Exact evidence

A read-only query executed through MaterialGraph's deployed SQLAlchemy engine
reported that the application role:

- is not a PostgreSQL superuser;
- can create roles;
- can create databases;
- can log in;
- has replication capability;
- can bypass row-level security.

The deployed environment defines different runtime and migration URLs, but
both connections authenticate as the same role. The runtime role can create
databases, connect, and create temporary objects. It also has `SELECT`,
`INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `REFERENCES`, and `TRIGGER` across all
nine inspected `public` tables. No explicit usage grants were returned.

The confirmed attributes and grants exceed the current runtime application's
needs. The URL distinction provides pooled/direct connection selection but no
credential or privilege separation.

## Threat scenario

An attacker who obtains code execution in MaterialGraph or steals its database
credential can use administrative role capabilities beyond application CRUD.
The attacker may create persistent principals or databases, bypass future RLS
policies, access replication capabilities, or broaden the impact of database
compromise.

## Current safeguards

- The role is not a PostgreSQL superuser.
- The credential is external to source control.
- Gitleaks and credential-rotation procedures are established.
- Current prototype data is public, and multi-tenant private data is not yet
  implemented.

## Missing safeguards

- Dedicated least-privilege runtime role.
- Separation between runtime and migration/administration credentials.
- Removal of role creation, database creation, replication, and RLS-bypass
  capabilities from the application identity.
- Documented schema/table/sequence grants required by runtime operations.
- Privilege-regression and deployment verification.

## Recommended remediation

Create a dedicated runtime role limited to the database objects and operations
required by MaterialGraph. Use a separate, non-runtime credential for Alembic
migrations and administrative work. Rotate the application credential after
the role boundary is established.

## Verification requirements

- Runtime role attributes show no role creation, database creation,
  replication, RLS-bypass, or superuser capability.
- Runtime grants are limited to required schemas, tables, sequences, and
  operations.
- Migration commands use a separate authorized role.
- Application startup and representative reads/writes continue to work.
- Scientific outputs and deterministic ordering remain unchanged.
