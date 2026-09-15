# MG-DE-001: Import lifecycle is not expandable or resumable

**Status:** Closed
**Priority:** First implementation wave
**Initial expansion blocker:** Yes

## Observation

The Materials Project import entry point uses five hard-coded chemical systems
and requests a single 25-record chunk for each. The import service processes the
result in one transaction and performs repeated per-record identity and element
lookups. It has no manifest-only mode, deterministic multi-page traversal,
checkpoint, resume, or chunk reconciliation.

## Impact

A larger import cannot presently demonstrate that its source scope was
completely traversed or that an interrupted run can resume without repeating
ambiguous work. One failing record can also roll back an unnecessarily broad
unit of work.

## Required outcome

- configurable, validated source scope;
- deterministic pagination and ordering;
- immutable import manifest and dry-run mode;
- documented chunk and transaction boundary;
- bulk identity and element lookup;
- checkpoint and safe resume;
- bounded retry and rejection behavior;
- final source/import/database reconciliation.

## Acceptance evidence

Automated tests and a representative test-database run must demonstrate clean
import, identical rerun, controlled interruption, resume, failed-chunk behavior,
and reconciled counts. No production import is required to close the
implementation portion of this finding.

## Implementation checkpoint

The repository now contains deterministic source paging, a bounded manifest
builder, atomic chunk application, checkpoint/resume behavior, bulk per-chunk
identity lookup, sanitized rejection records, and final identity/count
reconciliation. See the [implementation record](../implementation/MG-DE-001.md).

The repository now includes a composed PostgreSQL lifecycle test covering a
first committed chunk, controlled interruption before the second chunk,
checkpoint inspection, resume, final identity reconciliation, and a clean
idempotent rerun.

## Closure

Independent execution against the guarded `materialgraph_test` PostgreSQL
database passed at commit
`6dfe67d817b8ac848bb41d2783e27c7ed6b27d27`. The test demonstrated a committed
first chunk, a controlled interruption before the next chunk, checkpoint value
2, resumed completion, reconciliation of all three manifest identities, and a
fresh-checkpoint rerun with zero imports and three deterministic skips.

The focused import suite reported 67 passed; the complete suite reported 860
passed and 1 skipped. Ruff, automation-pin, dependency-contract, and diff checks
passed. GitHub Dependency Security run 11 and Secret Scan run 97 passed for the
same commit.

This closes the import-lifecycle defect only. It does not authorize production
import or close MG-DE-002, MG-DE-003, or MG-DE-004.
