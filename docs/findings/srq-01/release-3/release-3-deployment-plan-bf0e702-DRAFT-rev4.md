# MaterialGraph — Release 3 controlled deployment plan: `main` bf0e702 (DRAFT rev 4, not approved)

Scope: SRQ-01 PR-A — formula-correspondence classification and display, objective-aware Objective Explore only. Classifier (PR-A1), backend `formula_correspondence` report (PR-A2), frontend display (PR-A3, polish, ranked-card wording fix #101), wording consistency (S-5 compliance, objective-aware reasons, spec rev 3.9/3.10). Also on `main` since Release 2: PR-0 characterization tests (#94, #95), S1 finding record (#93), frontend dev-tool dependency bumps (#84 undici, #85 vitest).
Target: `main` = `bf0e702` (`bf0e702f88615d6de7f3cb62bfe225902c4fe0b1`).
Before: Release 2, expected backend `c8c6ed9` (verify in 1.2). Note: `git rev-parse release-2` returns `e2617f6…`; if `release-2` is an annotated tag this is the tag object, and `git rev-parse release-2^{commit}` should give `c8c6ed9…`. Verify locally before approval.
Status: **awaiting explicit deployment approval.** Nothing below has been executed. PR-B is not part of this release.

Rev 4 (review + preflight 1.3): Git preconditions run as one guarded block that also asserts the detached state; every capture uses `curl --fail-with-body` and an explicit HTTP 200 gate precedes any comparison. Pre-deployment captures (2026-11-02, all HTTP 200): `pre_cs01_l5.json` `2b5a7cf2…7c1d` and `pre_cs01_l10.json` `8a51eb32…7854` are byte-identical to the S1 production captures of 2026-10-31, so production data is unchanged for Case Study 01; `pre_strict.json` `16d0b6fd…45dc`; `pre_frozen.json` `8f93af66…1bb9`. Discovery Chains path: `GET /api/v1/materials/{material_id}/discovery/chains`.

Rev 3 (preflight 1.2): production checkout is **detached** at `c8c6ed9`, with one untracked rollback venv (`.venv-prev-51b618e`); section 3 now uses a detached switch to the exact commit, and the clean-tree check ignores untracked files. CI for the bf0e702 push: Dependency Security `41324891763`, Backend Tests `41324891641`, Secret Scan `41324891646`, all success. Frontend rollback target (symlink text): `releases/c8c6ed938ce8b38588f006e785fa93387b97d221`. Disk: 2.7 GB free (82% used) — sufficient for this release; cleanup of retained venvs is a separate, approved task.

Rev 2 (review): (A) explicit Git preconditions before the backend fast-forward; (B) frontend rollback restores the original symlink text, and the staged symlink is verified before the switch; (C) comparison script pinned by SHA-256, rules stated, dry run recorded; disk check covers evidence.

## 0. Qualification evidence already obtained
| Gate | Result |
|---|---|
| Backend suite (local, CI-style DB) | 1,437 passed, 1 skipped, 7 xfailed (H1/H2 permutation tests, no XPASS); ruff and gitleaks pass |
| Frozen behaviour | All 31 PR-0 golden cases byte-identical (no-objective, Discovery Chains, `/objective/chains`, scientific pathways, families, candidates, graph endpoints, Avoid-only Explore, Strict empty objective) |
| Objective-aware behaviour | `srq01_pra` snapshots: only `ranked_candidates[*].reasons` changed (R7.2), plus the appended `formula_correspondence`; scores, ranks, chains, metadata, coverage and key order identical |
| Frontend | `npm test` 126/126; `npm run build` clean |
| Data (AC13, local full dataset) | 1,727/1,727 stored compositions usable; 0 element mismatches; LiFePO₄ → all four NaFePO₄ records exact, Na₃Fe(PO₄)₂ not |
| Local visual check (`materialgraph_test_mg_de_007`) | CS01 limits 5 and 10, Strict, frozen Avoid-only displayed as specified; wording fix #101 re-checked |
| CI on PRs | Green on each PR (record run IDs for the `main` push of bf0e702 in 1.1) |

Runtime diff `release-2..bf0e702` (verified locally):
- Backend, 4 files: `app/schemas/research_objective_exploration.py`, `app/services/material/formula_correspondence.py` (new), `app/services/research/formula_correspondence_report.py` (new), `app/services/research/objective_exploration_service.py`.
- **No change** to `alembic/`, `pyproject.toml`, `requirements-production.lock`, `requirements-production.in`, `materialgraph.service`, `materialgraph.nginx` → no migration, no dependency install, no unit or Nginx change.
- Frontend: `src/objective/FormulaCorrespondence.tsx` (new), `ObjectiveInvestigation.tsx`, `contract.ts`, `style.css` (1 line), tests. `package.json` / `package-lock.json`: dev-only bumps (vitest, undici via jsdom); the production bundle was byte-unchanged by those merges (asset names unchanged at the time).

What users will see: on objective-aware requests (any preferred element, or Strict with an avoided element), a "Formula correspondence" panel, class labels on alkali chain steps, an exact-formula-analog note on qualifying ranked cards, and reasons that say a chain "contains a step classified as …". Frozen requests look exactly as before. **Ranking is unchanged**: at limit 5, NaFePO₄ is still not in the CS01 top five; that is expected until PR-B (AC2 is a PR-B criterion).

## 1. Pre-deployment checks (read-only)
1. CI on `main` push of bf0e702: `gh run list --repo MaterialGraph/materialgraph --commit bf0e702f88615d6de7f3cb62bfe225902c4fe0b1 --json name,conclusion,event,databaseId` → Backend Tests, Dependency Security, Secret Scan all `success`; record run IDs.
2. Server state (record every output):
   ```bash
   git -C /opt/materialgraph rev-parse HEAD                    # expect c8c6ed9…  → backend rollback target
   git -C /opt/materialgraph symbolic-ref -q --short HEAD      # branch name, or nothing if detached
   git -C /opt/materialgraph status --short                    # must be empty
   readlink /var/www/materialgraph/current                     # symlink TEXT → frontend rollback target
   readlink -f /var/www/materialgraph/current                  # resolved directory (for the record)
   systemctl is-active materialgraph
   curl -sS http://127.0.0.1:8000/health
   df -h /opt /var/www /tmp                                    # room for the new release, retained rollback release and /tmp/mg-r3 evidence
   ```
3. Pre-deployment captures on the server (new evidence `MG-R3-PRE-<UTC>`), all via `127.0.0.1:8000`, saved under `/tmp/mg-r3`:
   ```bash
   mkdir -p /tmp/mg-r3 && cd /opt/materialgraph && git fetch origin
   C=bf0e702f88615d6de7f3cb62bfe225902c4fe0b1
   git show $C:docs/findings/srq-01/request.json          > /tmp/mg-r3/cs01_l5.json
   git show $C:docs/findings/srq-01/request-limit10.json  > /tmp/mg-r3/cs01_l10.json
   cd /tmp/mg-r3
   printf '%s' '{"objective":{"avoid_elements":["Li"],"prefer_elements":[],"preserve_elements":[],"target_family":null,"max_hops":2,"limit":10,"prefer_lower_criticality":true,"require_stable_materials":false},"mode":"strict","limit":10}' > strict.json
   printf '%s' '{"objective":{"avoid_elements":["Li"],"prefer_elements":[],"preserve_elements":[],"target_family":null,"max_hops":2,"limit":5,"prefer_lower_criticality":true,"require_stable_materials":false},"mode":"balanced","limit":5}' > frozen.json
   for f in cs01_l5 cs01_l10 strict frozen; do
     curl -sS --fail-with-body -X POST http://127.0.0.1:8000/api/v1/materials/5/discovery/objective/explore \
       -H 'Content-Type: application/json' --data-binary @$f.json -o pre_$f.json \
       -w "$f %{http_code} %{size_download} %{time_total}\n" || echo "STOP: $f failed"
   done
   sha256sum pre_*.json
   git -C /opt/materialgraph show $C:docs/findings/srq-01/cs01-response.json | sha256sum   # S1 limit-5 capture: 2b5a7cf2…
   ```
   Frozen Discovery Chains capture (same URL, method and parameters before and after; no query parameters):
   ```bash
   curl -sS --fail-with-body http://127.0.0.1:8000/api/v1/materials/5/discovery/chains -o pre_chains.json \
     -w "chains %{http_code} %{size_download} %{time_total}\n" || echo "STOP: chains failed"
   ```
   Gate: every capture line must show HTTP `200`; any other status or a STOP line ends the preflight.
   Observation, not a gate: if `pre_cs01_l5.json` equals the S1 capture hash, production data is unchanged for this query since 2026-10-31.
4. Copy `compare_release.py` to `/tmp/mg-r3/` with `scp` and verify `sha256sum compare_release.py` = `08ee1a078b81f885986727024d690cc3b3d24e0900dfcf9dd48da6fcae490ce9`. Any other hash: stop.
   Comparison rules (stdlib only, read-only, never writes files):
   - `frozen PRE POST`: PASS only if the two files are byte-identical.
   - `aware PRE POST`: PASS only if PRE has no `formula_correspondence`; POST has it as the last key; all other top-level keys are identical and in the same order; every field except `ranked_candidates[*].reasons` is identical (candidate identity, ranking, scores, chains and their order, search metadata, objective coverage, policies); and each candidate's reasons are identical once the old alkali reason ("…with relationship type different alkali metal (composition not compared).") is removed from PRE and reasons starting "Appears in an eligible composition chain containing a step classified as " are removed from POST. Any remaining "composition not compared" in POST reasons fails.
   Dry run (`selftest_compare_release.py`, SHA-256 `2d83bd6b55a06c8e401f0f51fdf5e8ed7132a77403c3bfea6c3fc2538ccc75f2`) on the S1 production capture `docs/findings/srq-01/cs01-response.json`: accepts the expected R7.2 change; rejects changed candidate identity, swapped candidate ranking, changed score, swapped chain order, changed chain material, changed search metadata, changed objective coverage, an unrelated added reason, a missing report, and a one-byte change to a frozen response (12/12 cases as expected). Re-run locally before approval and record the output.
5. Frontend artifact on the PC: clean export of bf0e702, `npm ci`, `npm test` (126), `npm run build`; record `dist/assets` names; `tar -czf frontend-bf0e702.tgz -C dist .`; record SHA-256.

## 2. Order and rationale
Backend first, then frontend. Both orders are compatible: the Release 2 frontend ignores `formula_correspondence` (it will show the new reason wording in the reasons list, which is accurate on its own); the new frontend renders exactly as before when the key is absent. Backend first means the new UI never meets the old backend.

## 3. Backend deployment (approval required)
Preconditions, as one guarded block (never use `git reset --hard`). Production is detached at Release 2, so the switch is a detached checkout of the exact target commit. Do not continue unless the last line prints `ALL PRECONDITIONS PASSED`:
```bash
cd /opt/materialgraph && git fetch origin &&
EXPECTED=c8c6ed938ce8b38588f006e785fa93387b97d221 &&
TARGET=bf0e702f88615d6de7f3cb62bfe225902c4fe0b1 &&
! git symbolic-ref -q HEAD >/dev/null &&
test "$(git rev-parse HEAD)" = "$EXPECTED" &&
test -z "$(git status --porcelain --untracked-files=no)" &&
git merge-base --is-ancestor HEAD "$TARGET" &&
git cat-file -e "$TARGET^{commit}" &&
echo "ALL PRECONDITIONS PASSED"
```
Untracked rollback venvs (`.venv-prev-*`) are expected and unaffected.

```bash
cd /opt/materialgraph
umask 022
git switch --detach bf0e702f88615d6de7f3cb62bfe225902c4fe0b1
git rev-parse HEAD                                            # expect bf0e702…
source .venv/bin/activate
python -m pip check
python scripts/check_dependency_contract.py --check-installed  # lock unchanged; verify only
sudo systemctl restart materialgraph
systemctl is-active materialgraph
curl -sS http://127.0.0.1:8000/health
```
No `alembic upgrade`, no dependency install.

## 4. Backend production checks (read-only, before frontend switch)
Repeat the 1.3 captures with prefix `post_` (same files, URLs and `--fail-with-body`). **Gate: all five post captures HTTP 200**; otherwise stop and assess rollback. Then:
```bash
cd /tmp/mg-r3
python3 compare_release.py frozen pre_frozen.json post_frozen.json
cmp pre_chains.json post_chains.json && echo chains IDENTICAL
python3 compare_release.py aware pre_cs01_l5.json  post_cs01_l5.json
python3 compare_release.py aware pre_cs01_l10.json post_cs01_l10.json
python3 compare_release.py aware pre_strict.json   post_strict.json
sha256sum post_*.json
```
Pass criteria:
- Frozen responses byte-identical.
- Each objective-aware comparison prints `PASS`: identical apart from the R7.2 reason strings and the appended report.
- Expected report content (from S1 and local checks; any difference is investigated, not assumed): CS01 limit 5 — `source_correspondence` empty (NaFePO₄ not in the top five), alkali transitions to Na₃Fe(PO₄)₂-type materials `not_exact_replacement/ratios_differ`; CS01 limit 10 — NaFePO₄ (mp-19226) listed as `exact_alkali_replacement`; flags `false`; `not_evaluated_material_ids` empty.
- Latency comparable to Release 2 (~10 s for CS01; AC10).

## 5. Frontend release (approval required)
```bash
# server, after scp to /tmp and sha256 check:
R=bf0e702f88615d6de7f3cb62bfe225902c4fe0b1
sudo mkdir /var/www/materialgraph/releases/$R
sudo tar -xzf /tmp/frontend-bf0e702.tgz -C /var/www/materialgraph/releases/$R
sudo chown -R root:root /var/www/materialgraph/releases/$R
sudo find /var/www/materialgraph/releases/$R -type d -exec chmod 755 {} + -o -type f -exec chmod 644 {} +
sudo ln -sfn releases/$R /var/www/materialgraph/current.new
# verify the staged link before switching; stop if either check fails
test "$(readlink -f /var/www/materialgraph/current.new)" = "/var/www/materialgraph/releases/$R" && echo staged-link-ok
test -f /var/www/materialgraph/current.new/index.html && echo index-ok
sudo mv -T /var/www/materialgraph/current.new /var/www/materialgraph/current
readlink /var/www/materialgraph/current          # expect releases/<R>
readlink -f /var/www/materialgraph/current
```
No Nginx change or reload.

## 6. Production smoke (authenticated browser + server)
- Basic Auth still enforced (unauthenticated `https://materialgraph.org/` → 401).
- `/?material=5` loads the new asset names.
- CS01 limit 5 (Balanced): "Formula correspondence" panel present; alkali steps read "Different alkali metal (not an exact formula analog)" / "Element ratios differ."; no "composition not compared" in steps or reasons.
- CS01 limit 10: NaFePO₄ card shows "Exact formula analog of LiFePO₄: alkali metal Li → Na; … independently of the returned chains. Structure not assessed."
- Strict Avoid Li: any direct LiFePO₄ → NaFePO₄ step reads "Exact formula analog".
- Frozen: Balanced, Avoid Li only, no Prefer → no Formula correspondence panel; page as in Release 2.
- Dossier, comparison, refresh and shared URL work; no console errors; `/health` ok; `journalctl -u materialgraph --since <deploy time>` and Nginx error log free of errors.

## 7. Rollback (pre-staged)
- Frontend: restore the **original symlink text** recorded in 1.2 (`readlink`, not `readlink -f`), verify, then switch:
  ```bash
  sudo ln -sfn '<symlink text from 1.2>' /var/www/materialgraph/current.new
  readlink -f /var/www/materialgraph/current.new     # must equal the resolved directory recorded in 1.2
  sudo mv -T /var/www/materialgraph/current.new /var/www/materialgraph/current
  ```
- Backend: `git -C /opt/materialgraph switch --detach <HEAD recorded in 1.2>` then `sudo systemctl restart materialgraph`. No migration to reverse; no `git reset --hard`. The checkout stays detached, as it is at Release 2.
- Triggers: any frozen response differs; objective-aware content other than R7.2 reasons differs; wording that overclaims (structure, mechanism, "replac…"); API errors; latency regression; SPA load, refresh or comparison broken; security or availability regression. Preserve journal logs and `/tmp/mg-r3` captures before rolling back.

## 8. After deployment
- Qualification record `release-3-production-qualification-bf0e702-<date>.md` with SHAs, run IDs, timestamps, capture hashes and smoke screenshots; copy `/tmp/mg-r3` captures off the server before `/tmp` is cleared.
- Tag `release-3` on bf0e702 after qualification passes.
- Remaining, separate: PR-B (AC11 gate before merge) and S4 production qualification at limits 5 and 10 after PR-B; "Not validated" badge wording (open presentation item); Avoid-only returns only Li materials (post-SRQ-01 follow-up); moving the local repo out of OneDrive.
