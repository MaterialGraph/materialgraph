SRQ-01 PR-B1: deterministic ordering on objective-aware requests

Objective-aware Objective Explore requests now break ties by numeric MP ID instead of local database ID. All seven PR-0 xfails genuinely pass, and their markers are removed. The frozen golden suite passes without regeneration. It’s on srq-01-pr-b1 in two commits, not pushed:

6a6e138: code and tests.
672039e: the deliberate srq01_pra snapshot regeneration.

On the reference data, NaFePO₄ (mp-19226) moves from rank 5 to rank 1 in Case Study 01.

Files changed
File	Change
app/services/discovery/chain_service.py	Flag objective_aware_ordering, threaded get_discovery_chains → _build_chains → _get_next_candidates and added to the admission cache key. With the flag on, the objective branch sorts eligible candidates by (-shared element count, MP-ID key) before the unchanged reservation and fill; the admitted list keeps that order
app/services/research/objective_service.py	generate_chains_for_objective forwards the flag and a new chain_tie_key=None; _rank_chains(..., chain_tie_key=None) sorts by (-score, tie key) only when given one
app/services/research/objective_exploration_service.py	Sets both from is_objective_aware; chain_tie_key (MP-ID keys over the chain’s materials, source included); ranked candidates sort by (-score, not source analog, MP-ID key)
app/services/research/formula_correspondence_report.py	source_efa_material_ids(): one composition query, classification results only
tests/support/id_permutation.py	Optional setup hook that adds rows inside the rolled-back transaction before permuting; existing callers behave as before
Tests	Permutation tests extended; two test doubles of generate_chains_for_objective given the new parameters; one Case Study 01 characterization updated (see below)

How frozen callers stay on the default

explore passes the two new arguments only when is_objective_aware(request) is true. Frozen explore requests make exactly the same call as before, which matters for Strict with an empty objective, since it shares the admission branch.
The Discovery Chains route, /objective/chains and scientific pathways never pass them.
family_service, the legacy admission path, shared schemas, and every score formula and weight are unchanged.
The S-3 guard passes: there’s no alkali_substitution in the explore service.
The 7 PR-0 xfails

All 7 now pass, and the markers were removed one by one after each showed as a genuine strict XPASS:

H1 admission for cs01_source5_balanced and q6_source28_balanced;
H2 candidate order for cs01, q6 and strict;
H2 chain order for q6 and strict.

New tests

AC3: a synthetic Strict case with 8 eligible candidates for 6 slots. Three synthetic Na–Fe–P–O records are added inside the permutation transaction and permuted along with the rest. It’s invariant across every permutation, and a guard test confirms the cap really binds.
AC4: Case Study 01 chain order, plus the synthetic case.
Fallback: a test that fails if any objective-aware ordering key comes from a non-numeric MP ID. It records zero such keys on all three requests.

Proof the tests discriminate: with only the app/ changes stashed, the synthetic H1 case and the Case Study 01 candidate-order and chain-order tests fail against the old code.

srq01_pra regeneration
Full snapshots were rewritten with the switch.
All three baselines (Q6 changes too this time) were re-derived with the same derivation. Before writing anything, it was checked to reproduce all three committed baselines from the committed full snapshots.

What changed: only ranked_candidates, chains, objective_coverage and formula_correspondence. search_metadata is unchanged in all three cases.

Case	Ranked candidates	Chains
Case Study 01	Same 9, reordered within ties	Different selection at limit 10: the tied 117.25 group now expands from mp-19028 and mp-19226 instead of mp-556540 and the Li phosphates. 9 added, 9 dropped, 1 kept
Q6	Same 4, reordered	3 tied 59.45 chains swapped at the limit boundary (via mp-530177 instead of mp-691115)
Strict Avoid Li	Same 5, reordered	One tied 82.0 chain swapped at the limit boundary

AC8b: every ranked material (9, 4, 5) and every chain present in both versions (1, 7, 9) keeps the same score and score breakdown.

Case Study 01 on the reference data
	Order
Before	mp-19028, mp-556540, mp-761065, mp-752506, mp-19226, then mp-26003, mp-25977, mp-27007, mp-19294
After	mp-19226, mp-19028, mp-556540, mp-752506, mp-761065, then mp-19294, mp-25977, mp-26003, mp-27007
The first five are all tied at 117.25; the last four at 77.25.
NaFePO₄ is now rank 1: source analog first among equal scores, then MP ID.
The one-step LiFePO₄ → NaFePO₄ chain is now among the returned chains.
So test_case_study_01_report_on_reference_data needed updating: its returned alkali steps went from ten ratios_differ pairs to mp-19017 → mp-19028 (ratios_differ) and mp-19017 → mp-19226 (exact).
Results
Full backend suite: 1453 passed, 1 skipped, 0 xfailed.
Frozen golden: all 34 srq01_pr0 tests pass with no snapshot changed.
ruff check app tests passes, and gitleaks passed on both commits.
Commits: 6a6e138 (code and tests) and 672039e (snapshots).
Test database: a new disposable container, mgprb1-pg (127.0.0.1:55435), is still running.
Open questions
Case Study 01 chain-set change. It changed the most, because MP-ID admission now expands NaFePO₄ and mp-19028 rather than mp-556540. That’s expected under R5, but it’s the largest objective-aware change so far. Worth noting in the AC5 before/after record.
Import direction. chain_service (discovery layer) now imports mp_id_sort_key from the research report module. It works and creates no cycle, but the key may belong in a neutral module when PR-B2 adds more shared logic.
Repeated composition query. The source-analog tie key loads compositions separately from the report’s own query: two bounded queries per objective-aware request. PR-B2’s one-query-per-request composition load (D11) can serve both.
Ranked-candidate reasons. These also change where the returned chain set changed, as they’re built from chains. AC8b covers scores only, so this is noted rather than asserted.