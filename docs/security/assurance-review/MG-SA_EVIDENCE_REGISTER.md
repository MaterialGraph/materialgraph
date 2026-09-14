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
