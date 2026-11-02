# MaterialGraph — Release 3 production qualification record: `main` bf0e702 (2026-11-02)

Status: **DEPLOYED and qualified** (approved by Jithin: "approve Release 3 deployment").
Scope: SRQ-01 PR-A — formula-correspondence classification and display on objective-aware Objective Explore requests (classifier, backend `formula_correspondence` report, frontend display, wording consistency with the S-5 neutral-alkali rule, objective-aware reasons per R7.2). Specification: SRQ-01 S2 rev 3.10. Runbook: `release-3-deployment-plan-bf0e702-DRAFT-rev4`. PR-B (admission and ordering) is not part of this release.

## Versions
| Component | Before | After |
|---|---|---|
| Backend `/opt/materialgraph` (detached) | `c8c6ed938ce8b38588f006e785fa93387b97d221` (Release 2) | `bf0e702f88615d6de7f3cb62bfe225902c4fe0b1` |
| Frontend `current` | `releases/c8c6ed938ce8b38588f006e785fa93387b97d221` | `releases/bf0e702f88615d6de7f3cb62bfe225902c4fe0b1` |
| Frontend assets | (Release 2) | `index-RQRDUiF5.js`, `index-COXlTBnX.css` |

Rollback targets retained: frontend symlink text `releases/c8c6ed938ce8b38588f006e785fa93387b97d221`; backend `c8c6ed9…` (`git switch --detach`). No migration to reverse.

## Pre-deployment evidence
- CI on `main` push of bf0e702: Dependency Security `41324891763`, Backend Tests `41324891641`, Secret Scan `41324891646`, all success.
- Local qualification: backend 1,437 passed, 1 skipped, 7 xfailed (H1/H2 permutation tests, no XPASS); all 31 PR-0 golden cases byte-identical; `srq01_pra` objective-aware snapshots differ from the pre-PR-A baseline only in R7.2 reasons and the appended report; frontend 126/126; AC13 data check 1,727/1,727 usable compositions; local visual check on `materialgraph_test_mg_de_007`.
- Runtime diff `release-2..bf0e702`: 4 backend files (`app/schemas/research_objective_exploration.py`, `app/services/material/formula_correspondence.py`, `app/services/research/formula_correspondence_report.py`, `app/services/research/objective_exploration_service.py`) and frontend sources; frontend `package.json`/lock dev-only bumps. No change to `alembic/`, `pyproject.toml`, `requirements-production.*`, `materialgraph.service`, `materialgraph.nginx`. (`release-2` is an annotated tag; `release-2^{commit}` = `c8c6ed9`.)
- Comparison script `compare_release.py` SHA-256 `08ee1a078b81f885986727024d690cc3b3d24e0900dfcf9dd48da6fcae490ce9`, verified on the PC and on the server; dry run `selftest_compare_release.py` (`2d83bd6b…75f2`) on the S1 production capture: 12/12 cases as expected (accepts the R7.2 change; rejects changed candidate identity, ranking, score, chain order, chain material, search metadata, objective coverage, an unrelated reason, a missing report, and a one-byte frozen change).
- Frontend package: clean `git archive` export of bf0e702 outside OneDrive; `npm ci` (0 vulnerabilities), `npm test` 126/126, `npm run build`; `frontend-bf0e702.tgz` SHA-256 `728a09e1785972d80882e7f2496c8c063653d011924ccd84dd9211f92ce18ed5` (verified on the server before unpacking; contents `index.html` and the two assets only).
- Server before: detached at `c8c6ed9`; tracked files clean (untracked `.venv-prev-51b618e` only); service active; `/health` ok; disk 2.7 GB free (82% used).

## Execution log (UTC, 2026-11-02)
| Time | Phase | Result |
|---|---|---|
| before 05:01 | 1.3 Pre-deployment captures (`/tmp/mg-r3`, evidence `MG-R3-PRE`) | All HTTP 200. `pre_cs01_l5` `2b5a7cf2…7c1d` and `pre_cs01_l10` `8a51eb32…7854` byte-identical to the S1 production captures of 2026-10-31 (data unchanged); `pre_strict` `16d0b6fd…45dc`; `pre_frozen` `8f93af66…1bb9`; `pre_chains` `caceed86…b075` |
| 05:01:08 | 3a Guarded preconditions | `ALL PRECONDITIONS PASSED` (detached, HEAD = c8c6ed9, tracked clean, ancestor, target present) |
| 05:01:56 | 3b `git switch --detach bf0e702`, verification, restart | HEAD bf0e702; only `?? .venv-prev-51b618e`; `pip check` OK; `dependency_contract_valid=true`, `installed_environment_matches_lock=true`; active and `/health` ok by 05:01:59 |
| after 05:02 | 4 Backend verification gate (evidence `MG-R3-POST`) | **PASSED** (below) |
| ~05:04 | 5a Package transfer | SHA-256 matched |
| 05:05:26 | 5b Stage, verify, atomic switch | `index.html` → RQRDUiF5.js / COXlTBnX.css; `staged-link-ok`, `index-ok`; `current` → `releases/bf0e702…`; no `current.new` left |
| 05:06:03 | 6a Server smoke | Unauthenticated homepage and asset 401 (Basic Auth enforced); `/health` ok; no service errors since restart; Nginx error log empty |
| after | 6b Browser smoke | Passed (below) |

## Phase 4 — backend verification gate
| Capture | HTTP | Time | Post SHA-256 | Comparison |
|---|---|---|---|---|
| CS01 limit 5 | 200 | 10.2 s | `ba6c75b1…a20a` | **PASS** (aware) |
| CS01 limit 10 | 200 | 8.7 s | `fac0a93d…a770` | **PASS** (aware) |
| Strict, Avoid Li, limit 10 | 200 | 7.6 s | `a9a98b9a…3ed5c` | **PASS** (aware) |
| Balanced, Avoid Li only, limit 5 (frozen) | 200 | 6.8 s | `8f93af66…1bb9` | **PASS** (byte-identical) |
| Discovery Chains, material 5 (frozen) | 200 | 4.5 s | `caceed86…b075` | **IDENTICAL** |

"Aware" PASS means: post = pre with `formula_correspondence` appended as the last key; candidate identity, ranking, scores, chains, search metadata and objective coverage identical; reasons differ only by the R7.2 replacement of "…with relationship type different alkali metal (composition not compared)." with "…containing a step classified as …"; no remaining "composition not compared".

Report content on production:
- CS01 limit 5: `source_correspondence` empty (NaFePO₄ not in the top five, as expected before PR-B); 5 transitions `not_exact_replacement/ratios_differ`; flags false; nothing not evaluated.
- CS01 limit 10: NaFePO₄ mp-19226 (material 10) at rank 6 `exact_alkali_replacement`; 10 transitions `ratios_differ`.
- Strict Avoid Li: two source analogs — NaFePO₄ mp-1192859 (material 384, rank 2) and mp-19226 (material 10, rank 7); 9 transitions `ratios_differ`, 1 `exact_alkali_replacement`.

## Phase 6b — browser smoke (authenticated, screenshots by Jithin)
- CS01 limit 5: results unchanged from Release 2 ("5 of 26 generated chains"; NaFe₃P₃O₁₃ 117.25, then Na₃Fe(PO₄)₂, Na₃Fe₃(PO₄)₄, Na₉Fe₃P₈O₂₉, NaFeP₂O₇ at 115; Li present in chains 3, 4, 5). Formula correspondence panel present; every alkali step "Different alkali metal (not an exact formula analog)" / "Element ratios differ."; reasons use "containing a step classified as …"; no "composition not compared".
- CS01 limit 10: results unchanged ("10 of 26"; Na 6/10; Li 4/10 in chains 3–6). NaFePO₄ at rank 6 shows "Exact formula analog of LiFePO₄: alkali metal Li → Na; all other element ratios unchanged. This compares formulas with the starting material directly, independently of the returned chains. Structure not assessed." alongside "Returned chain: 10" (the indirect path recorded in S1).
- Strict Avoid Li: "10 of 42"; NaFePO₄ mp-1192859 at rank 2 with the exact-analog note; NaFe₃P₃O₁₃ reasons list both a "ratios differ" step and an "exact formula analog" step, worded as steps in its chains, not as a property of NaFe₃P₃O₁₃.
- Frozen Balanced Avoid Li only: no Formula correspondence panel; page as in Release 2.
- Dossier, comparison, refresh and shared URL work; no browser console errors.

## Notes
- One pre-deployment CS01 limit-5 run took 13.4 s; all post-deployment runs were 4.5–10.2 s, in line with Release 2.
- Strict shows two NaFePO₄ records as source analogs. This is correct per R7.1 (distinct MP IDs remain distinct materials) and is the situation PR-B's formula grouping (R3) will present more compactly.
- Server captures in `/tmp/mg-r3` are temporary; copy them off the server and commit them as evidence in a separate docs PR.

## Follow-ups (separate)
- Tag `release-3` on bf0e702.
- PR-B (admission and ordering), with the AC11 representative-sensitivity gate before merge; S4 production qualification at limits 5 and 10 after PR-B.
- "Not validated" badge wording (open presentation item; collect pilot feedback).
- Avoid-only requests return only Li-containing materials (frozen legacy behaviour; post-SRQ-01 candidate).
- Server disk at 82%: approved cleanup of retained venvs (`.venv-prev-51b618e` and older) and wheel directories.
- Move the SSH private key out of the repository folder and OneDrive; consider rotating the key pair.
