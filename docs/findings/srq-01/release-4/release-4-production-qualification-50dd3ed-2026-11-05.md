# MaterialGraph — Release 4 production qualification record: `main` 50dd3ed (2026-11-05)

Status: **DEPLOYED and qualified** (approved by Jithin: "approve Release 4 deployment"). This record is also the SRQ-01 **S4** qualification.
Scope: SRQ-01 PR-B — deterministic MP-ID ordering (PR-B1, #104/#105), exact-analog formula groups (PR-B2, #106), four-step admission sequence with per-expansion reporting (PR-B3, #107), review follow-up (#108). Objective-aware Objective Explore requests only. Backend-only release. Specification: SRQ-01 S2 rev 3.13. Runbook: `release-4-s4-plan-and-runbook-50dd3ed-DRAFT-rev2`.

## Versions
| Component | Before | After |
|---|---|---|
| Backend `/opt/materialgraph` (detached) | `bf0e702f88615d6de7f3cb62bfe225902c4fe0b1` (Release 3) | `50dd3eda31bbb1930dcc2782e3ec777af3c35244` |
| Frontend `current` | `releases/bf0e702…` | unchanged (no frontend diff) |

Rollback target retained: `git switch --detach bf0e702…` and restart. No migration to reverse.

## Pre-deployment evidence
- CI on `main` push of 50dd3ed: Backend Tests `41853854225`, Dependency Security `41853854235`, Secret Scan `41853854237`, all success.
- Local qualification: backend 1,473 passed, 1 skipped; AC3/AC4 (seven permutation tests) pass; AC11 passed at PR-B2 (two flaws found and fixed) and after PR-B3; AC7/AC12 pass; frozen golden suite unchanged throughout.
- **Local S4 attribution** (production-equivalent database, four commits r3/b1/b2/b3 via worktrees, `s4_attribution.py`): every change attributed to one PR; no candidate or chain score changed between consecutive commits; frozen Avoid-only byte-identical at all four commits; Case Study 01 at both limits: NaFePO₄ rank 5 → 1 (B1), grouped duplicates leave eligibility (B2), direct LiFePO₄ → NaFePO₄ chain with a four-record group (B3).
- Scripts: `compare_release_r4.py` SHA-256 `daf7ebbf50c1a2583c1fdb31dbb359e440db121ed9b703eea5dd3bc7395d8acf` (self-test 13/13; real-data dry run r3 → b3 PASS at both Case Study 01 limits); `deploy_r4.sh` SHA-256 `cc27b3bcaee5436b33c43045b2bcf7e7c1cd4202894f31d6105d3cd2879022e9`. Both verified on the server. Implementation checked for the rollback window (pre-restart only; no success line after a failed restart or health check) and exact chain/step matching of the direct-result check.
- Server before: detached at `bf0e702`; tracked files clean; active; healthy; 2.7 GB free (82%); evidence directory `/tmp/mg-r4` mode 700.
- Pre-deployment captures (all HTTP 200), copied to the PC before the switch with matching hashes: `pre_cs01_l5` `ba6c75b1…`, `pre_cs01_l10` `fac0a93d…`, `pre_strict` `a9a98b9a…`, `pre_frozen` `8f93af66…`, `pre_chains` `caceed86…` — **identical to the Release 3 post-deployment captures of 2026-11-02** (production unchanged since); `pre_q6` `fe2e87ce…` (first capture).

## Execution (UTC, 2026-11-05)
`bash /tmp/mg-r4/deploy_r4.sh`: `pip check` OK; `dependency_contract_valid=true`, `installed_environment_matches_lock=true`; `ALL PRECONDITIONS PASSED`; switched to 50dd3ed; restart **12:58:17Z**; `active`; health ok; `DEPLOYED 50dd3ed… at 12:58:21Z`.

## Verification gate (all HTTP 200)
| Capture | Time | Post SHA-256 | Result |
|---|---|---|---|
| Frozen Avoid-only | 6.9 s | `8f93af66…` | **PASS** (byte-identical) |
| Discovery Chains, material 5 | 4.9 s | `caceed86…` | **IDENTICAL** |
| Case Study 01, limit 5 | 10.6 s | `8b88ed92…` | **PASS** incl. direct-result check |
| Case Study 01, limit 10 | 9.3 s | `1916b4be…` | **PASS** incl. direct-result check |
| Strict Avoid Li, limit 10 | 7.4 s | `e12295e2…` | **PASS** (group check) |
| Q6 (LiMnO₂), limit 10 | 7.9 s | `f15e1806…` | **PASS** |

Direct-result check (machine-verified from the response contract at both Case Study 01 limits): a returned chain is exactly mp-19017 → mp-19226; its step is `exact_alkali_replacement`; NaFePO₄'s `formula_group` is exactly mp-19226, mp-746030, mp-753672, mp-1192859 with only mp-19226 traversed; the source expansion reports an admitted exact-analog group. No score changed for any material or chain present before and after.

### Expected-check deviation, assessed
The runbook expected NaFePO₄ at rank 1–2 in Case Study 01 and rank 1 in Strict. On production it is **rank 5 in both** (115 and 50), behind four sodium iron phosphates (mp-18493, mp-18774, mp-554409, mp-556984) scoring 117.25 / 52.25. The 2.25 difference is the lower-criticality contribution from production quality evidence, which those materials receive and mp-19226 does not; locally all leading candidates scored equally, so tie order placed NaFePO₄ first. Scores are unchanged by PR-B (AC8b), NaFePO₄ leads every material it ties with, and it is within the top five at limit 5 (AC2). **Assessment: a prediction error in the runbook, not a release defect; no rollback.**

### Production finding (not visible locally)
In Release 3's Strict results, NaFePO₄ record mp-1192859 scored 52.25 while mp-19226 scored 50.0: production criticality evidence differs between records of the same formula. The representative rule (lowest MP ID) selected the record without the criticality contribution. AC11 could not reveal this because local quality data is uniform. Not a gate failure; recorded for a separate specification decision on whether representative selection should consider evidence completeness (current rule is deliberately a convention).

### Other observations
- Case Study 01 also returns a second exact-analog step on production: **Li₃Fe₂(PO₄)₃ (mp-6373) → Na₃Fe₂(PO₄)₃ (mp-556984)**, labelled "Exact formula analog".
- NaFe₃P₃O₁₃ (mp-1040459), Release 3's rank 1, is no longer in the candidate pool (admission change attributed to PR-B1 locally).
- Q6 returns a Li-free sodium material, mp-17967, at rank 1 (67.25), matching the local attribution; kept as evidence for the separate Issue 3 diagnosis, not as proof it is resolved.

## Smoke (server and authenticated browser)
- Unauthenticated request 401 (Basic Auth enforced); `/health` ok; no service errors in the journal since the restart.
- Case Study 01 limit 5: chain 1 "LiFePO₄ → NaFePO₄" labelled "Exact formula analog" ("Alkali metal Li → Na; all other element ratios unchanged"); NaFePO₄ card at rank 5 with the exact-analog note.
- Strict Avoid Li: "10 of 42", no lithium in results, Formula correspondence panel present, NaFePO₄ with note (rank 5, direct chain 5).
- Frozen Balanced Avoid-only: no Formula correspondence panel; page as in Release 3.
- Dossier, comparison and refresh work; no browser console errors.

## Follow-ups (separate)
- Tag `release-4` on 50dd3ed; commit this record and evidence under `docs/findings/srq-01/release-4/`.
- Specification decision: representative selection and criticality-evidence differences between same-formula records (production finding above).
- Issue 3 (Q6) diagnosis, using the attribution and production evidence.
- "Not validated" badge wording (open presentation item).
- Server disk at 82%: approved cleanup of retained environments.
- Scientific Benchmark Protocol against this frozen, qualified release.
