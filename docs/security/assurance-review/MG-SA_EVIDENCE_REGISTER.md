# MG-SA Evidence Register

**Assessment date:** 2026-09-14

| ID | Layer | Evidence | Independently reproduced result | Limit |
|---|---|---|---|---|
| `MG-SA-E-001` | Bundle | Complete-history authoritative artifact | `git bundle verify` passed; bundle `main` and `HEAD` equal the checkpoint | Does not prove production identity |
| `MG-SA-E-002` | Repository | Isolated checkout and worktree | Exact SHA; clean at assessment start; no submodules or symlinks | Review cleanliness is not production cleanliness |
| `MG-SA-E-003` | Records | Complete `docs/security` tree and linked deployment guide | Read completely; eleven Verified findings and retired `MG-SEC-006` reconciled | Historical production commands were not rerun |
| `MG-SA-E-004` | Tests | Focused security/configuration suite | `91 passed`, one Starlette deprecation warning | Disposable SQLite table supports the non-integration subset; not the claimed complete suite |
| `MG-SA-E-005` | Static validation | Automation pins and dependency contract | Both validators returned `*_valid=true` | Validates repository contract, not deployed state |
| `MG-SA-E-006` | Static validation | Ruff, whitespace, and worktree | Ruff passed; `git diff --check` passed; checkout remained clean | Not a scientific integration test |
| `MG-SA-E-007` | GitHub | Secret Scan run `34773420976`, job `103767055988` | Success for exact SHA; pinned Gitleaks ran with no network and reported no leaks | A successful scan cannot prove no secret exists in every external location |
| `MG-SA-E-008` | GitHub | Dependency Security run `34773420986`, job `103767055465` | Success for exact SHA; contract valid, clean environment, `pip check`, installed-lock reconciliation, and `pip-audit` zero known vulnerabilities | Snapshot result; future advisories can change |
| `MG-SA-E-009` | GitHub governance | Branch and ruleset APIs | `main` unprotected; no applicable ruleset; no required status checks | Repository Actions policy endpoint was unavailable through the connector |
| `MG-SA-E-010` | Application | Admission classifier and mounted routes | Classifier has five exact POSTs and discovery/research regex; six material-intelligence route families are outside it | Runtime cost was analyzed, not load-tested |
| `MG-SA-E-011` | Application | Deadline middleware interaction | Same classifier controls deadline; behavioral test confirms slot retention after timeout | Only classified routes benefit |
| `MG-SA-E-012` | Nginx | Committed proxy configuration | Expensive locations mirror application allowlist; the only connection zone is keyed by client address | Effective production configuration pending |
| `MG-SA-E-013` | Backup | Script, units, runbook, and tests | Consistent snapshot, checksum, upload size/encryption checks, retention lifecycle, isolated restore process | Current S3 objects, timer runs, and role state pending |
| `MG-SA-E-014` | Scientific behavior | Historical full-JSON comparisons and current unit suite | Records consistently describe exact parsed JSON comparisons, not shallow key checks | Baseline responses were not reproduced without approved production/data access |
| `MG-SA-E-015` | Tests | Complete-suite invocation in the isolated review environment | `747 passed, 72 failed, 5 skipped`; failures were missing seeded materials/relationships (`404`, empty candidates, or empty graph results) | Environment has no PostgreSQL service or prepared `materialgraph_test`; this is not an authoritative complete-suite result |
| `MG-SA-E-016` | `MG-SA-001` repository remediation | Application classifier and Nginx material-route regex | Neighbor, similarity, neighborhood, criticality, and recommendation paths now receive the same admission/deadline/proxy class as discovery and research | Repository evidence; effective production result is recorded separately |
| `MG-SA-E-017` | `MG-SA-001` policy tests | Mounted FastAPI route inventory, independent cost policy, application/Nginx parity, alternate material-ID spellings, and path-specific overload/deadline behavior | Focused admission, deadline, and configuration suite passes; Ruff and `git diff --check` pass | Repository-focused evidence; authoritative and production results are recorded separately |
| `MG-SA-E-018` | `MG-SA-001` Nginx semantics | Primary `ngx_http_limit_conn_module` documentation | Confirms `$server_name` aggregate key pattern, multiple simultaneous limits, and inheritance only when the current level has no `limit_conn` directive | Repository semantic evidence; deployed syntax and effective configuration are recorded separately |
| `MG-SA-E-019` | `MG-SA-001` scientific regression | Complete canonical JSON from all six newly covered endpoints at the original implementation and remediation checkout using the same fixture | Byte-equivalent canonical output; both SHA-256 values were `571981c82166b6df1da16972f732c66262aca4ca869a881963d1aa322a28380b` | Isolated fixture evidence; production comparison is recorded separately |
| `MG-SA-E-020` | `MG-SA-001` complete-suite attempt | Full `pytest -q` collection in the isolated remediation environment | `809 passed, 27 failed, 5 skipped`; all failures depended on canonical seeded scientific data absent from the fixture; no changed security/configuration test failed | Environment limitation superseded for closure by the authoritative `MG-SA-E-021` result |
| `MG-SA-E-021` | Maintainer validation | Prepared PostgreSQL `materialgraph_test`, focused tests, complete suite, validators, Ruff, and whitespace | Admission/deadline/configuration `59 passed`; DB timeout `5 passed`; complete suite `840 passed, 1 skipped`; all validators and Ruff passed; worktree clean at `9a7fb111...` | Maintainer-executed local evidence |
| `MG-SA-E-022` | GitHub | Exact remediation commit workflow runs | Secret Scan run `34809206809`, job `103866966275`, and Dependency Security run `34809206835`, job `103866966991`, completed successfully on attempt one; substantive steps were not skipped | Successful commit evidence; enforcement limitation subsequently qualified and closed through `MG-SA-002` |
| `MG-SA-E-023` | Production identity and activation | Commit, clean worktree, Nginx candidate, application restart, Nginx reload, services, timers, and health | Production clean at `9a7fb111...`; tracked/active Nginx SHA-256 `475298c...`; syntax passed; application and Nginx active; backup and monitor timers active; health `200` | Direct operator evidence; no load test performed |
| `MG-SA-E-024` | Production route and proxy policy | Direct classifier check and effective Nginx directives | Six corrected route families plus `+5` classified expensive; effective configuration contained the site zone, three aggregate directives, and two expensive client directives | Aggregate cap was not deliberately saturated |
| `MG-SA-E-025` | Production scientific regression | Six complete before/after parsed responses plus raw hashes and sizes | Criticality, neighborhood, neighbors, recommendations, scenario recommendations, and similarity matched exactly; alternate `+5` response matched canonical material 5 | Current production dataset and request set only |
| `MG-SA-E-026` | Production bounded bypass probe | Eight sequential invalid-ID recommendation requests | Five application `422` and three proxy `429`; proxy classification active; health remained `200` | Proves route/rate classification, not 20-connection aggregate saturation |
| `MG-SA-E-027` | `MG-SA-002` repository remediation | Live dependency policy, deployment guide, finding, and cumulative assurance records | Automated audit and protected-branch enforcement are distinguished; exact-SHA successful Dependency Security and Secret Scan runs are a documented manual deployment precondition | Repository implementation evidence; acceptance limitations superseded by `MG-SA-E-028` through `MG-SA-E-030` |
| `MG-SA-E-028` | Maintainer validation | Prepared PostgreSQL `materialgraph_test`, focused configuration suite, complete suite, validators, Ruff, whitespace, and worktree | Configuration `32 passed`; complete suite `841 passed, 1 skipped`; validators and Ruff passed; diff/worktree clean at `7786aa95...` | Maintainer-executed local evidence |
| `MG-SA-E-029` | GitHub governance | Fresh repository Settings screenshots after remediation integration | Repository had no rulesets and no classic branch protection; therefore no required status checks applied to `main` | Operator-supplied settings evidence; confirms the documented manual boundary rather than an enforced gate |
| `MG-SA-E-030` | GitHub | Exact remediation commit workflow runs and job steps | Secret Scan run `34831604742`, job `103935983896`, and Dependency Security run `34831604715`, job `103935983504`, passed on attempt one for `7786aa95...`; every substantive scan, pin, contract, audit, clean-build, `pip check`, and reconciliation step succeeded | Successful exact-commit evidence; future commits still require their own run evidence |

## Primary technical references

- Nginx documents that limit counters operate per value of the key used to
  define the shared zone:
  <https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html>.
- Nginx documents per-key leaky-bucket request limiting and burst behavior:
  <https://nginx.org/en/docs/http/ngx_http_limit_req_module.html>.
- Nginx documents that `$host` prefers the request-line host, then the `Host`
  header, then the matching server name:
  <https://nginx.org/en/docs/http/ngx_http_core_module.html#var_host>.
- PostgreSQL documents statement and lock timeout semantics:
  <https://www.postgresql.org/docs/current/runtime-config-client.html>.
- GitHub documents that required checks prevent merging only when configured on
  a protected branch or ruleset:
  <https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches>.
- GitHub documents that Actions checks can be skipped through commit messages:
  <https://docs.github.com/en/pull-requests/reference/status-checks#skipping-and-requesting-checks-for-individual-commits>.
- GitHub documents full-length Action SHA pinning as the immutable reference:
  <https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions>.

## Pending minimum production evidence

No item below was requested from or executed against production during the
assessment phase:

- deployed commit and worktree state;
- effective Nginx configuration, syntax result, listeners, and network exposure;
- effective systemd identity/sandbox and environment-file metadata;
- certificate chain, protocol behavior, HSTS, and renewal state;
- redacted DB client TLS, role grants, and effective timeout evidence;
- backup/monitor timers, recent bounded results, S3 retention metadata,
  journald limits, filesystem use, and alert state;
- active dependency reconciliation and vulnerability audit;
- health and a small bounded set of negative requests; and
- deployment/rollback evidence without restart or mutation.
