# Literature Case Study 01 — PR #44 qualification records

This folder holds the **post-freeze qualification records** for PR #44
(objective-aware bounded admission for Objective Explore). It is separate from
`../evidence/`, which contains the frozen Case Study 01 record and the frozen
pre-fix multi-objective baseline. Nothing in `../evidence/` was modified.

These are engineering qualification records. They show what MaterialGraph
returned under stated conditions; they are **not** scientific validation of any
material, synthesis route or property.

All files are stored byte-exact (`-text` in `.gitattributes`). Verify with
`SHA256SUMS.txt` in each subfolder.

## Contents

| Folder | Registered execution | What it records |
|---|---|---|
| `local-2026-10-08/` | 2026-10-08 ≈18:06–18:08 UTC, local PostgreSQL | Harness reproduction of the frozen pre-fix baseline on `main` (pre-fix code), then post-fix capture on the PR #44 branch, on two datasets |
| `production-2026-10-09/` | 2026-10-09 ≈03:30–03:55 UTC, production | Production deployment qualification of commit `0c86179`; outcome **CONDITIONAL PASS** — see `MG-LCS01-PRODUCTION-QUALIFICATION-PR44.md` |

## `local-2026-10-08/`

Tool: `tools/capture_qualification.py`. It reads the six registered requests from
`../evidence/diagnostics/MG-LCS01-PRE-FIX-MULTI-OBJECTIVE-QUALIFICATION.json`
(read-only), calls `ResearchObjectiveExplorationService.explore()` with the real
request schemas and the original projection, runs every case twice
(determinism), and writes only outside the repository. Each JSON records git
HEAD, working-tree changes, import path and a credential-masked database target.

| Dataset (local database) | Pre-fix reproduction | Post-fix |
|---|---|---|
| `materialgraph_test` — the database the frozen baseline was captured on | **6/6 cases byte-match the frozen baseline**, deterministic (code `b183993`, clean) | Q1–Q3, Q6 unchanged; Q4 same candidates via direct chains; Q5 same results, narrower search |
| `materialgraph_test_mg_de_007` — larger dataset that reproduces the failure *mode*; **not** production identities; provenance not yet documented | Used as its own pre-fix reference | CS01 request (Q3) 0/5 → 5/5 Na; Q4 Strict empty → 5 Na; Q6 still Li-only |

The pre-fix reproduction runs used `main` at `b183993` (no PR #44 code). The
post-fix runs used the PR #44 branch with its five changed files uncommitted on
top of `b183993` (recorded in each file's `working_tree_changes`); that content
is identical to the merged commit `0c86179`.

## `production-2026-10-09/`

| Item | Detail |
|---|---|
| Report | `MG-LCS01-PRODUCTION-QUALIFICATION-PR44.md` |
| Deployed commit | `0c86179792020cfa52491cf444acddc17b63fe8a` (previous: `5ccdb92f7…`) |
| Database identity | `neondb`, host fingerprint `74bb531fabe3`, Alembic `c8f3a2d7e901` |
| `pre-deploy-20261009T034415Z/` | Frozen CS01 request (byte-identical response to the frozen record) and Q4 Strict, before deployment |
| `post-deploy-20261009T034841Z/` | Same two requests after deployment |
| `gate-e-20261009T035427Z/` | Default-off `/objective/chains` check, 3× latency/determinism runs per request |
| `tools/` | Capture scripts used (`capture_production_explore.ps1`, `gate_e_checks.ps1`, `gate_b_dataset_identity.py`) |

`cs01_frozen_response.json` in the capture folders is a copy of
`../evidence/case01_objective_response.json` made at capture time for
side-by-side comparison; its SHA-256 matches the frozen file.

**Deliberately not committed:** production `openapi.json` captures (the API is
behind pilot authentication); copies of `DEPLOYMENT.md` and systemd/Nginx unit
files (available in the repository at `0c86179`); and an incomplete capture
folder `pre-deploy-20261009T034357Z` (aborted by HTTP 401 before any
Objective Explore request was sent). No credentials were captured: request
headers were never saved and Basic Auth was passed to `curl` via stdin.

## Verify

```powershell
Get-ChildItem <subfolder> -Recurse -File | Where-Object Name -ne 'SHA256SUMS.txt' |
  Get-FileHash -Algorithm SHA256 | ForEach-Object { '{0}  {1}' -f $_.Hash.ToLower(), $_.Path.Substring((Resolve-Path <subfolder>).Path.Length + 1) }
```

Compare the output with that subfolder's `SHA256SUMS.txt`.
