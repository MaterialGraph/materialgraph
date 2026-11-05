# MaterialGraph — SRQ-01 S4 qualification and Release 4 runbook: `main` 50dd3ed (DRAFT rev 2, not approved)

Scope: SRQ-01 PR-B — deterministic MP-ID ordering (PR-B1, #104/#105), exact-analog formula groups (PR-B2, #106), four-step admission sequence and per-expansion reporting (PR-B3, #107), review follow-up (#108). Objective-aware Objective Explore requests only.
Target: `main` = `50dd3eda31bbb1930dcc2782e3ec777af3c35244`. Before: Release 3, `bf0e702f88615d6de7f3cb62bfe225902c4fe0b1` (backend detached; frontend `releases/bf0e702…`).
**Backend-only release.** `git diff --stat release-3 50dd3ed -- frontend` is empty: no frontend build, upload or symlink switch. Runtime diff: 6 files under `app/` (ordering, schema, chain service, report, explore service, objective service); no change to `alembic/`, `pyproject.toml`, `requirements-production.*`, `materialgraph.service`, `materialgraph.nginx`.
Status: **awaiting explicit approval.** Nothing below has been executed on production.

Rev 2 (review): (1) preconditions, dependency checks and the switch run as one `set -euo pipefail` script (`deploy_r4.sh`) that re-verifies the reviewed target commit and the backend-only diff immediately before switching; (2) dependency checks run **before** checkout, and any failure after checkout but before restart restores the Release 3 checkout automatically, so the running service is never restarted onto an unverified tree; (3) the direct LiFePO₄ → NaFePO₄ result is machine-verified against the response contract (chain, exact classification, four-record group with one traversed member, admitted source expansion); (4) evidence directory created with mode 700, and pre-deployment captures copied off the server before the switch.

## Part 1 — S4 evidence already obtained (local)

### 1.1 Tests and gates
- Backend suite on `50dd3ed`-equivalent code: 1,473 passed, 1 skipped; ruff clean; CI green on every PR.
- AC3/AC4: all seven PR-0 local-ID permutation tests pass (PR-B1). AC11 passed at PR-B2 (two flaws found and fixed) and re-passed after PR-B3. AC7/AC12 admission tests pass.
- Frozen golden suite (`srq01_pr0`) byte-identical throughout PR-B.

### 1.2 Attribution on the production-equivalent database (`materialgraph_test_mg_de_007`, 1,727 materials)
Method: `s4_attribution.py`; the same five requests at four commits via git worktrees — r3 `bf0e702`, b1 `e76a7b1`, b2 `baef466`, b3 `50dd3ed`. Evidence: `s4-attribution.md` and per-commit responses.

| Request | Release 3 (r3) | After PR-B1 | After PR-B2 | After PR-B3 |
|---|---|---|---|---|
| Case Study 01, limit 5 | NaFePO₄ rank 5; no direct chain | rank 1 (tie order) | metadata only (15 grouped duplicates leave the eligible pool) | **direct LiFePO₄ → NaFePO₄ chain**; group of four records |
| Case Study 01, limit 10 | rank 5; no direct chain | rank 1 | metadata only | direct chain; group of four; mp-556984 enters at rank 7 |
| Strict Avoid Li, limit 10 | rank 5 and a second NaFePO₄ record at rank 7 | rank 1, one record | group of four reported | no change |
| Q6 (LiMnO₂, Avoid Li, Prefer Na) | Li-containing materials only (27.25) | a Li-free Na material (mp-16381) at rank 1, 67.25 | metadata only | a different Li-free Na material (mp-17967) at rank 1, 67.25; fewer expansions (6 → 5) |
| Frozen Avoid-only | — | — | — | **byte-identical at all four commits** |

Findings:
- **No candidate score and no chain score changed** for any material or chain present at consecutive commits (AC8b), in every request.
- Every change is attributable to one PR: B1 (tie order; which equally ranked candidates are admitted and returned), B2 (grouped duplicates removed from eligibility), B3 (exact analogs admitted first; downstream chains through NaFePO₄).
- **The original S1 failure is corrected on production-equivalent data:** NaFePO₄ ranks first and is admitted directly from LiFePO₄ at both Case Study 01 limits.
- Q6 now returns Li-free sodium materials at the top; the identity of the top material depends on admission (B1 vs B3). Recorded for the Issue 3 diagnosis; not an SRQ-01 acceptance criterion.
- Production differs from this database in some scores (Release 3 production ranks NaFe₃P₃O₁₃ above the 115 group), so production expectations below are stated as checks, not exact copies.

## Part 2 — Production expectations (gate)

| Request | Hard rules (FAIL stops the release) | Expected and checked (deviation → stop and assess) |
|---|---|---|
| Frozen Avoid-only; Discovery Chains material 5 | Byte-identical pre/post | — |
| Case Study 01, limits 5 and 10 | No score change for any material or chain present pre and post; both report flags true; expansions present; **direct result verified**: a returned chain is exactly mp-19017 → mp-19226, its step is classified `exact_alkali_replacement` in the report, NaFePO₄'s `formula_group` is exactly the four records with only mp-19226 traversed, and the source expansion reports at least one admitted exact-analog group | NaFePO₄ (mp-19226) in the top five at limit 5 (rank 1, or 2 behind a higher-scoring material) |
| Strict Avoid Li, limit 10 | Score rules; flags; expansions | NaFePO₄ rank 1; group of four |
| Q6, limit 10 | Score rules; flags; expansions | Changes listed and compared with the local attribution |
| All | HTTP 200 for every capture | Latency comparable to Release 3 (CS01 ~8–13 s) |

Comparison script `compare_release_r4.py`, SHA-256 `daf7ebbf50c1a2583c1fdb31dbb359e440db121ed9b703eea5dd3bc7395d8acf`. Built-in dry run (`selftest`) on the S1 production capture, 13/13: accepts order/selection changes and a verified direct chain; rejects a changed candidate score, a changed chain score, a false grouping flag, empty expansions, a missing NaFePO₄ group, a missing direct chain, a non-exact direct step, an incomplete group, a source expansion with no admitted group, and a one-byte frozen change. A real-data dry run compares the local attribution captures r3 → b3 (Case Study 01, both limits) with all flags and must PASS.

Deployment script `deploy_r4.sh`, SHA-256 `cc27b3bcaee5436b33c43045b2bcf7e7c1cd4202894f31d6105d3cd2879022e9`. Transfer unmodified (do not open and save on Windows; CRLF line endings would break it) and verify the hash on the server.

## Part 3 — Runbook

### 3.1 Pre-deployment (read-only)
1. CI on the `main` push of 50dd3ed: `gh run list --repo MaterialGraph/materialgraph --commit 50dd3eda31bbb1930dcc2782e3ec777af3c35244 --json name,conclusion,event,databaseId` → all success; record IDs.
2. Server state: `git -C /opt/materialgraph rev-parse HEAD` (expect `bf0e702…`, detached); `git -C /opt/materialgraph status --porcelain --untracked-files=no` (empty); `systemctl is-active materialgraph`; `curl -sS http://127.0.0.1:8000/health`; `df -h /opt /tmp`.
3. `install -d -m 700 /tmp/mg-r4`. Pre captures in `/tmp/mg-r4` via `127.0.0.1:8000`, each with `curl -sS --fail-with-body … -w "%{http_code} %{time_total}"` (HTTP 200 gate): `cs01_l5`, `cs01_l10` (S1 request bodies from `docs/findings/srq-01/`), `strict` (Avoid Li, Strict, limit 10), `q6` (source 28, Avoid Li, Prefer Na, Balanced, limit 10), `frozen` (Avoid Li only, Balanced, limit 5) and `GET /api/v1/materials/5/discovery/chains` → `pre_*.json`. Record SHA-256.
4. `scp` `compare_release_r4.py` and `deploy_r4.sh` to `/tmp/mg-r4`; verify both hashes above.
5. Copy the pre captures off the server (`scp -r` to `C:\mg-validation\release4\pre`) and record their hashes locally **before** the switch.

### 3.2 Backend switch (approval required)
```bash
bash /tmp/mg-r4/deploy_r4.sh
```
The script (`set -euo pipefail`): fetches; stops unless the checkout is detached at Release 3 with clean tracked files, the target resolves to exactly the reviewed commit and descends from Release 3, and no dependency, migration, unit, Nginx or frontend file differs; runs `pip check` and the dependency contract **before** checkout; switches; re-verifies HEAD and the clean tree, restoring the Release 3 checkout automatically if either fails; only then restarts and checks `is-active` and `/health`. Expected final line: `DEPLOYED 50dd3ed… at <UTC>`. No migration, no dependency install, no frontend or Nginx change. If the service fails after restart, use 3.5.

### 3.3 Verification gate (read-only)
Repeat 3.1.3 with prefix `post_`; all captures HTTP 200. Then:
```bash
cd /tmp/mg-r4
python3 compare_release_r4.py frozen pre_frozen.json post_frozen.json
cmp pre_chains.json post_chains.json && echo "chains IDENTICAL"
python3 compare_release_r4.py aware pre_cs01_l5.json  post_cs01_l5.json  --expect-nafepo4-group --expect-direct-nafepo4
python3 compare_release_r4.py aware pre_cs01_l10.json post_cs01_l10.json --expect-nafepo4-group --expect-direct-nafepo4
python3 compare_release_r4.py aware pre_strict.json   post_strict.json   --expect-nafepo4-group
python3 compare_release_r4.py aware pre_q6.json       post_q6.json
sha256sum post_*.json
```
Every line must print PASS (or `chains IDENTICAL`), and the expected checks in Part 2 must hold or be explained before the release is accepted.

### 3.4 Browser smoke (authenticated)
Hard refresh `/?material=5`. Case Study 01 limit 5: NaFePO₄ card with the exact-analog note; returned chain "LiFePO₄ → NaFePO₄" labelled "Exact formula analog". Strict: NaFePO₄ rank 1. Frozen Avoid-only: no Formula correspondence panel. Dossier, comparison, refresh, shared URL work; no console errors; unauthenticated request still 401; `journalctl -u materialgraph --since <restart>` free of errors.

### 3.5 Rollback (pre-staged)
`git -C /opt/materialgraph switch --detach bf0e702f88615d6de7f3cb62bfe225902c4fe0b1` then `sudo systemctl restart materialgraph`. No migration to reverse; frontend unchanged. Triggers: any hard-rule FAIL; frozen difference; unexplained expected-check deviation; errors; latency regression; availability or security regression. Preserve `/tmp/mg-r4` and journal logs first.

### 3.6 After deployment
Qualification record with hashes, run IDs, timestamps, gate output and screenshots; copy `/tmp/mg-r4` off the server; tag `release-4` on 50dd3ed; commit evidence under `docs/findings/srq-01/release-4/`.
