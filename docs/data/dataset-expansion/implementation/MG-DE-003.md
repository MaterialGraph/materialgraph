# MG-DE-003 Implementation Record

**Baseline:** `bfbe6afd50738c6fe3533c10937a8c8fcaad3de3`
**Status:** Ready for independent PostgreSQL verification
**Production synchronization authorized:** No

## Implemented boundary

- Candidate screening applies stable and maximum-energy hard constraints in
  SQL before loading the eligible material set. The existing Python predicate
  remains in place as a defensive equivalence check.
- Substitution analysis uses material-element membership to load only
  candidates with at least one element in common with the source. Candidates
  excluded by this query necessarily have zero Jaccard similarity and were
  already discarded after full loading.
- Discovery graph construction loads composition for the start material and
  extends its cache only for candidates returned by the existing bounded
  frontier. Materials with no composition are cached as empty to prevent
  repeated queries.
- Material-family discovery preselects candidates through the union of the
  existing strong relationship prerequisites, then retains the existing Python
  classifier, explanation builder, and deterministic ordering.

## Scientific compatibility

The scoring equations, evidence tiers, relationship labels, explanation text,
ranking keys, graph depth, branching limits, and returned schemas are unchanged.
The SQL predicates remove only records that the existing deterministic Python
logic rejects or constrain hard eligibility earlier in the same request.

No arbitrary material cap or index is introduced. Whether another staged cap
or index is scientifically and operationally justified depends on the
representative PostgreSQL evidence governed by MG-DE-004.

## Verification required

1. Confirm runtime and migration URLs identify `materialgraph_test`.
2. Run focused screening, substitution, graph-builder, family, API, scenario,
   sensitivity, pathway, and configuration tests against PostgreSQL.
3. Confirm the family SQL prefilter returns the same strong relationships as
   exhaustive classification on the curated dataset.
4. Confirm substitution candidates all share a source element and graph
   composition queries remain within the bounded frontier.
5. Run the complete suite, Ruff, automation-pin check, dependency-contract
   check, and `git diff --check`.
6. Compare representative complete JSON responses before any production
   synchronization.

## Operational effects

There is no migration, dependency, Nginx, systemd, environment, source-import,
or database-content change. Application service code changes would require a
later approved EC2 synchronization and restart, but neither is authorized by
this implementation record.

## Isolated implementation validation

- Python compilation passed for application and test sources.
- Twelve database-independent screening and substitution tests passed.
- A disposable SQLite fixture exercised the new screening eligibility query,
  substitution overlap subquery, and material-family strong-predicate union;
  the expected scopes and deterministic family ordering matched.
- Focused Ruff, automation-pin, dependency-contract, and `git diff --check`
  checks passed.
- The isolated workspace has no prepared PostgreSQL scientific fixture, so the
  authoritative focused and complete suites remain required externally.

## Rollback

Before production use, rollback is a Git decision. No database downgrade or
data restoration is required. If later deployed, restore the previously
accepted application commit and restart the service under a separately approved
rollback procedure.
