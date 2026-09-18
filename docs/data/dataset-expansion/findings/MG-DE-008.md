# MG-DE-008: Real data lacks isolated Neon qualification

**Status:** Open; planning safeguards implemented
**Production blocker:** Yes

## Finding

The exact approved cohort passed disposable local PostgreSQL qualification, but
remote managed-service behavior remains unproven. Direct and pooled connection
roles, network-sensitive endpoint performance, recovery after remote disconnect,
provider resource use, cost ceilings, and isolated cleanup require evidence.

## Acceptance criteria

- offline target validation passes against explicit production identifiers;
- provider evidence proves a dedicated non-production resource;
- direct migration and pooled runtime behavior pass with strong TLS;
- exact import, curated preservation, idempotency, and both recovery modes pass;
- all representative endpoints complete with comparable remote measurements;
- provider resource use remains within the reviewed contract;
- identity/formula crowding evidence remains intact;
- the qualification resource is deleted and absence is independently verified;
- no production resource is written or modified.

## Current resolution state

The repository now provides a fail-closed offline contract validator and a
reviewed execution/evidence design. No Neon resource was created, no network
connection was made, and no database write was authorized by this change.
