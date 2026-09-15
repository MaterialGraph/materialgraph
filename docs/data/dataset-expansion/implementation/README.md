# MG-DE Implementation Records

| Finding | Record | Status |
|---|---|---|
| MG-DE-001 | [Manifest-first resumable import](MG-DE-001.md) | Verified and closed |
| MG-DE-002 | [Dataset provenance and refresh semantics](MG-DE-002.md) | Verified and closed |
| MG-DE-003 | [Scale-sensitive request-path narrowing](MG-DE-003.md) | Ready for independent PostgreSQL verification |

Each approved change must receive a focused record describing:

- finding and acceptance criteria addressed;
- baseline and resulting commits;
- schema, application, script, test, documentation, and operational effects;
- migration and rollback behavior;
- focused and complete validation;
- scientific regression evidence;
- environment-specific evidence still outstanding;
- whether production synchronization, migration, or restart is required.

Implementation records do not close findings by themselves. Closure requires
the evidence specified in the corresponding finding.
