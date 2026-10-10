# MG-LCS01 — Production Deployment Qualification: PR #44

**Outcome: CONDITIONAL PASS**
Deployed behaviour matches the acceptance criteria for Objective Explore. The GitHub Actions deployment preconditions for the deployed SHA succeeded (§2). The outcome is conditional on the documented limitations (§9) and on archiving the evidence (§8).

| Field | Value |
|---|---|
| Change qualified | PR #44 — objective-aware bounded admission for Objective Explore |
| Deployed commit | `0c86179792020cfa52491cf444acddc17b63fe8a` (merge of PR #44; head of `origin/main` at qualification time) |
| Previous production commit (rollback point) | `5ccdb92f7b8e64383b1e988c43c0dcf7f1fdb0a3` (merge of PR #38, deployed 2026-10-04) |
| Qualification window (UTC) | 2026-10-09 ≈03:30 – 03:55 |
| Environment | AWS EC2 `materialgraph-api` (ap-south-1), Nginx → Uvicorn `127.0.0.1:8000`, systemd `materialgraph.service` |
| Database | Neon PostgreSQL, `db_name=neondb`, host fingerprint `74bb531fabe3` (SHA-256 prefix), `ENVIRONMENT=production`, Alembic `c8f3a2d7e901` |
| Frozen evidence relied on | `docs/product/literature-case-study-01/evidence/` (PR #41) — unmodified |
| Scientific status | Engineering qualification only. API results are **not** experimental or literature validation of any material. |

---

## 1. Gate A — Deployment state before change

| Check | Observation |
|---|---|
| Production checkout | `/opt/materialgraph`, branch `main`, HEAD `5ccdb92f7…`, working tree clean |
| PR #44 merge object on server | absent; traversal code on disk: 0 occurrences |
| Running code vs disk | last checkout move 2026-10-04 19:25:34 UTC; service start 19:26:48 UTC → running code = `5ccdb92` |
| systemd unit | installed unit identical to repository `materialgraph.service` |
| Health | local 200, public 200 |

**Conclusion:** PR #44 was not deployed. Production ran the exact pre-fix code from which Case Study 01 was frozen.

## 2. Gate C — Deployment scope and preconditions

Commits deployed (`5ccdb92..0c86179`, first-parent): #41 (evidence docs), #42 (pre-commit hook), #43 (security test), #44 (traversal).
18 files: `app/` 3 (traversal only), `docs/` 9, `tests/` 3, `.githooks/` 2, `.gitattributes` 1.

Deployment-sensitive files changed: **none** (no Alembic migration, dependency lock, `pyproject.toml`, systemd/Nginx/journald units, or `app/core`). `alembic upgrade head` was therefore not required and not run.

| Precondition (`docs/guide/DEPLOYMENT.md`) | Status |
|---|---|
| `Dependency Security` workflow succeeded for deployed SHA | **Succeeded:** run #199, commit `0c86179`, branch `main`, push event, 2026-10-08 18:16 UTC (11:46 PM IST), duration 1 m 40 s |
| `Secret Scan` workflow succeeded for deployed SHA | **Succeeded:** run #282, commit `0c86179`, branch `main`, push event, 2026-10-08 18:16 UTC (11:46 PM IST), duration 9 s |
| Workflow evidence checked before deploying | **Process deviation:** both runs completed ≈9.5 h *before* deployment (03:47 UTC 2026-10-09), but were confirmed and recorded only after it (2026-10-10). Run-level conclusions were checked; individual job steps were not opened. Durations are consistent with earlier fully executed runs (Dependency Security 1 m 30 s – 1 m 51 s; Secret Scan 9 – 48 s), which indicates the jobs ran rather than being skipped. |
| Explicit deployment approval recorded | **Process deviation:** deployment executed before the written approval step in this qualification; recorded for transparency. |

## 3. Gate B — Production dataset identity (read-only)

| Check | Production | Frozen CS01 diagnostic |
|---|---|---|
| Materials / without element rows | 1,727 / **0** | — |
| Material 5 | `mp-19017`, LiFePO₄ | same |
| `EXPANSION_LIMIT` | 6 | same |
| Family size (source 5) | 839 | same |
| First 6 admitted (legacy order) | 1, 2, 3, 4, 198, 199 — **6/6 contain Li** | same |
| First Na candidates | positions 148–152 → IDs 6, 7, 8, 9, 10 | 148/149 |
| First K candidates | position 698 (ID 213, K₂Fe₄O₇); 13 K members in family | not recorded |

**Conclusion:** production reproduces the Case Study 01 failure conditions exactly. Because no material lacks element membership, the approved Strict fail-closed refinement has **no effect on the current production dataset**.

## 4. Deployment record

Executed per `DEPLOYMENT.md` *Common Operations*, pinned to the exact SHA:

- `git merge --ff-only 0c86179…` at 2026-10-09 **03:47:16 UTC** (fast-forward)
- hash-locked `pip install` + `pip check` + editable install: `dependency_contract_valid=true`, `installed_environment_matches_lock=true`
- `systemctl restart materialgraph` → start **03:47:23 UTC**, `NRestarts=0`, active/running
- Post-deploy: HEAD `0c86179…`, clean tree, traversal code present (8 occurrences), local 200, public 200

Rollback (not used): `git switch --detach 5ccdb92f7…` → restart → health check. No dependency or schema changes to reverse.

## 5. Gate D — Production behaviour, frozen requests

Route (from production `/openapi.json`): `POST /api/v1/materials/5/discovery/objective/explore`, via Nginx with pilot Basic Auth.
Requests: Case Study 01 = `case01_objective_request.json` byte-for-byte from `origin/main`; Q4 Strict = `registered_request` of Q4 in `MG-LCS01-PRE-FIX-MULTI-OBJECTIVE-QUALIFICATION.json`.

### 5.1 Case Study 01 (LiFePO₄; Avoid Li, Co; Prefer Na, K; Preserve Fe, P, O; phosphate; Balanced)

| | Frozen (2026-10-06) | Pre-deploy (03:44:15Z) | **Post-deploy (03:48:41Z)** |
|---|---|---|---|
| HTTP / size | 200 / 12,362 B | 200 / 12,362 B, **byte-identical to frozen** | 200 / 17,245 B |
| Ranked candidates (id: formula, score) | 198 LiFeP₂O₇ 77.25; 199 LiFeP₂O₇ 77.25; 1 LiFe(PO₃)₃ 75.0; 2 LiFe(PO₃)₄ 75.0; 3 LiFe₂P₃O₁₀ 75.0 | identical | **70 NaFe₃P₃O₁₃ 127.25; 6 Na₃Fe(PO₄)₂ 125.0; 7 Na₃Fe₃(PO₄)₄ 125.0; 8 Na₉Fe₃P₈O₂₉ 125.0; 9 NaFeP₂O₇ 125.0** |
| Na / Li / Co / K (by formula) | 0 / 5 / 0 / 0 | 0 / 5 / 0 / 0 | **5 / 0 / 0 / 0** |
| Returned chains | [5,198] [5,199] [5,1] [5,2] [5,3] | identical | [5,6] [5,6,70] [5,1,6] [5,2,6] [5,3,6] |
| expanded states / generated chains | 7 / 36 | 7 / 36 | 6 / 26 |
| `search_truncated` / `result_truncated` / `scientific_completeness_guaranteed` | false / true / false | same | false / true / false |

Observations:
- **Three of five returned chains pass through Li-containing intermediates** (IDs 1, 2, 3) before reaching a Li-free Na candidate. This is expected Balanced behaviour (Avoid is a soft penalty; `hard_rejection_scope: none`) and must be explained to researchers reading chains.
- **No K-containing candidate ranks in the top 5.** The response does not expose whether a K reservation occurred (first K at family position 698); no claim is made either way.
- Candidate 70 (reached via 6) did not appear in the local `mg_de_007` qualification; this reflects dataset differences, not a contradiction.

### 5.2 Q4 Strict (LiFePO₄; Avoid Li; Prefer Na; Preserve Fe, P, O; phosphate; Strict)

| | Pre-deploy | **Post-deploy** |
|---|---|---|
| HTTP / size | 200 / 1,457 B | 200 / 12,565 B |
| Ranked candidates | **none** | **6, 7, 8, 9, 10** (Na₃Fe(PO₄)₂, Na₃Fe₃(PO₄)₄, Na₉Fe₃P₈O₂₉, NaFeP₂O₇, NaFePO₄), all 125.0 |
| Na / Li | 0 / 0 | **5 / 0** |
| Chains | none | [5,6] [5,7] [5,8] [5,9] [5,10] (all one-hop, Li-free) |
| expanded / generated / returned | 7 / 36 / 0 | 7 / 42 / 5 |

Matches the local post-fix qualification on `materialgraph_test_mg_de_007` (same IDs, same one-hop chains).

## 6. Gate E — Regression and operational checks

| Check | Result |
|---|---|
| Default-off caller: `POST …/objective/chains` with CS01 objective | 200; chain ends 198, 199, 1, 2, 3 (0/5 Na, 5/5 Li); metadata identical to frozen (7 / 36). **Legacy behaviour unchanged; new admission policies not active outside Objective Explore.** |
| Determinism | CS01: 4/4 runs identical candidates; Q4: 4/4 identical |
| Latency CS01 (client, via Nginx) | pre 8.23 s (n=1); post 10.39, 8.73, 8.51, 9.61 s (mean ≈ 9.3 s) |
| Latency Q4 | pre 7.25 s (n=1); post 7.60, 7.29, 7.32, 7.74 s (mean ≈ 7.5 s) |
| Budget | application deadline 20 s; Nginx expensive timeout 25 s → post-deploy CS01 ≈ 47–52 % of application deadline |
| Server: source-node admission time (material 5) | 0.62–1.12 s (retained log lines) |
| Service errors/exceptions since deploy | 0 (in retained journal) |
| Strict fail-closed exclusions logged | 0 (consistent with 0 materials lacking element rows) |
| Missing-element-membership behaviour | **Not exercisable in production** (no such materials); covered by unit tests only |

**Observability limitation:** the service journal is rate-limited (200 records / 30 s) and per-request chain logging exceeds it; only 4 of ≥9 post-deploy material-5 timing lines were retained. Error absence and timing attribution are therefore partial. The ≈1 s mean CS01 latency increase cannot be split between the new admission code and database/scoring time from available evidence.

## 7. Comparison with local qualification

| | Local (`materialgraph_test_mg_de_007`) | Production |
|---|---|---|
| CS01 pre-fix | Li-family 1, 2, 3, 4, 2722 | Li-family 198, 199, 1, 2, 3 (= frozen) |
| CS01 post-fix | Na 6, 7, 8, 9, 10 | Na 70, 6, 7, 8, 9 |
| Q4 Strict pre → post | empty → Na 6–10 | empty → Na 6–10 |

Production, not `mg_de_007`, is the dataset matching the frozen Case Study 01 identities.

## 8. Conditions on this outcome

1. ~~Record the GitHub Actions results for `0c86179`.~~ **Satisfied 2026-10-10:** Dependency Security #199 and Secret Scan #282 both succeeded (§2).
2. Preserve this report and the capture artifacts (§10) through a separate documentation PR; do not modify frozen Case Study 01 files.

## 9. Known limitations (unchanged by PR #44)

1. LiMnO₂ → Na (Q6) remains Li-only; cause is downstream of bounded admission.
2. Reserved preferred slots that dead-end are not backfilled; search can narrow (CS01: 36 → 26 chains).
3. Objective Chains API and Scientific Pathway Analysis use legacy admission (**confirmed in production**, §6).
4. Balanced mode may route through, and may return, avoided-element materials (soft penalty) — observed in CS01 chains.
5. Per-step cap metadata and objective-satisfaction UI summary not implemented.
6. Full pytest suite is not run in CI; test evidence (967 passed, 1 skipped) is local.
7. Journal rate limiting reduces operational observability (§6).

## 10. Evidence artifacts

Local: `C:\MaterialGraph-Backups\prod-qualification-pr44\`

| Folder | Contents |
|---|---|
| `pre-deploy-20261009T034415Z\` | requests, response headers/payloads (CS01, Q4), frozen CS01 response copy, `openapi.json`, `summary.txt` |
| `post-deploy-20261009T034841Z\` | same set, post-deploy |
| `gate-e-20261009T035427Z\` | legacy `/objective/chains` request/response, 6 latency/determinism responses, `summary.txt` |
| repository files exported | `DEPLOYMENT.md`, systemd/Nginx unit copies |

Generate a SHA-256 manifest before archiving (see accompanying instructions).
