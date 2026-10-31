SRQ-01 PR-0, part 2: Strict golden cases and local-ID permutation harness

Committed on srq-01-pr0-part2 as 0364d3b; tests only, not pushed. The harness confirms both hypotheses on the reference data: which candidates get admitted (H1) and how tied results are ordered (H2) both depend on local IDs today. Strict mode is the one exception for H1.

Permutation method, seeds, integrity and isolation
Utility: tests/support/id_permutation.py, with permuted_reference_session(seed).
It isn’t named test_*.py, so pytest doesn’t collect it as a test module.
Each permutation maps the 28 reference IDs onto the same 28 IDs.
Seeds:
"baseline" is the identity.
"reversed" maps 1↔28, 2↔27 and so on: the strongest reordering.
Integers 1, 2 and 3 seed random.Random(seed).shuffle, so results are reproducible.
Foreign-key integrity:
The foreign keys referencing materials.id are read from the catalog: material_elements, material_applications, material_source_records and material_import_events. No other column refers to materials.
The harness drops those keys, remaps IDs in two passes through an offset range (so no intermediate value collides with an ID in use), then re-adds each key with its original definition. Re-adding makes PostgreSQL re-validate every reference.
A harness test checks that every material keeps the same element symbols by MP ID, and that its ID maps exactly as the permutation says.
Isolation from the golden IDs 1–28:
Everything, DDL included, runs in one outer transaction on one connection and is rolled back; nothing is committed.
After rollback, the context manager re-reads the ID-to-MP-ID pairs on a fresh connection and fails if any pairing changed.
Running the permutation tests and then the golden suite in one process passes (43 passed, 7 xfailed).
The requests are run directly through ResearchObjectiveExplorationService on the permuted session, not over HTTP.
New golden snapshots

MATERIALGRAPH_REGENERATE_GOLDEN=srq01_pr0 -k strict_no_objective wrote only these two files. All 29 existing snapshots are byte-unchanged.

Snapshot	Request
objective_explore_5_strict_no_objective.json	POST /materials/5/discovery/objective/explore: mode strict, empty avoid/prefer/preserve, no family, max_hops 2, limit 10
objective_explore_28_strict_no_objective.json	The same request on source 28
H1 and H2 per request

All three requests are objective-aware and use limit 20. Each is compared by MP ID against the baseline under the reversed, 1, 2 and 3 permutations.

Case Study 01 style on #5 (Avoid Li, Co; Prefer Na, K; preserve Fe, P, O; phosphate; Balanced)

H1: depends on local IDs, under every permutation. Examples:
Reversed: expanding mp-26003 admits {mp-19226, mp-752506} in place of {mp-19028, mp-556540}. NaFePO₄ (mp-19226) gets its own expansion, and mp-556540 is no longer expanded.
Seed 1: at mp-19028 and mp-556540, {mp-26003, mp-25977} are replaced by {mp-19294, mp-27007}.
H2: depends on local IDs. The candidate set and scores are identical under every permutation; only the order within ties changes.
Baseline tie at 117.25: [mp-19028, mp-556540, mp-761065, mp-752506, mp-19226]. Reversed: [mp-19226, mp-752506, mp-761065, mp-556540, mp-19028].
The tie at 77.25 [mp-26003, mp-25977, mp-27007, mp-19294] reorders the same way.
Its chain set changes because of H1, so chain order isn’t tested here as a separate H2 observation.

Avoid Li + Prefer Na on #28 (Balanced)

H1: depends on local IDs. At mp-754656 and the four Li–Mn–O materials:
Baseline admits {mp-27569, mp-558376}.
Reversed and seed 2 admit {mp-18957, mp-770618}.
Seed 1 admits {mp-27510, mp-755874}.
Seed 3 admits {mp-1003638, mp-18957}.
H2: depends on local IDs. The tie at 27.25 is [mp-18988, mp-691115, mp-530177, mp-1272804] in the baseline and [mp-1272804, mp-530177, mp-691115, mp-18988] reversed. The chain set and scores are identical, but chain order differs (ties of 4 at 61.95 and 12 at 59.45).

Strict, Avoid Li on #5

H1: no dependence observed. Only five Na candidates are eligible at each expansion, which is below the cap of 6, so there’s no competition for slots.
H2: depends on local IDs. The tie at 52.25 is [mp-19028, mp-556540, mp-761065, mp-752506, mp-19226] in the baseline and its exact reverse under the reversed permutation. The returned chains also differ, because which tied chains survive the cut to 20 depends on order.
Strict xfail tests

All seven are xfail(strict=True, raises=AssertionError). Each fails today, and turns into an XPASS error once PR-B fixes the dependence, so the marker then has to be removed deliberately.

Test	Detects
test_h1_admitted_candidates_do_not_depend_on_local_ids[cs01_source5_balanced]	Admitted MP-ID sets per expansion changing with local IDs (AC3)
…[q6_source28_balanced]	The same, for the Q6-style request
test_h2_equally_scored_candidates_keep_their_order[cs01 / q6 / strict] (3 tests)	Order of equally scored ranked candidates changing with local IDs (AC4)
test_h2_equally_scored_chains_keep_their_order[q6 / strict] (2 tests)	Order and truncation of equally scored chains changing with local IDs

These permutation tests pass normally today:

the two harness checks (the permutation is bijective and seed-stable; foreign keys hold and IDs are restored);
H1 for Strict, with no dependence observed;
a precondition test showing ranked candidate sets and scores are permutation-invariant for all three requests, so the H2 failures are purely about order.

No frozen path is tested under permutation.

Results
Full backend suite: 1325 passed, 1 skipped, 7 xfailed (the skip is the POSIX-only test on Windows).
ruff check passes, and gitleaks passed on the commit.
Commit: 0364d3b on srq-01-pr0-part2, not pushed.
Test database: mgpr0-pg (127.0.0.1:55433) is still running; I’ll leave it until you ask for it to be removed.
Open questions
Weak Strict H1 result. It shows no dependence only because the fixture has five eligible candidates, under the cap. Is a larger fixture, or a synthetic family, needed for a test that can catch Strict H1 dependence?
Chain truncation. For Strict, the H2 chain test detects which tied chains survive the cut to 20, not only their order. Does R5’s “ordering of equally scored chains” also cover selection at the truncation boundary?
Case Study 01 chain order. No independent H2 test exists for it, because its chain set depends on H1. After PR-B fixes H1, should a CS01 chain-order H2 test be added?
Fixed limit. The harness uses limit 20 to see as much as possible. The same dependence exists at limits 5 and 10, but isn’t tested separately.
PostgreSQL only. The harness drops and re-adds foreign keys and rolls back DDL, which works because PostgreSQL rolls back DDL inside a transaction. It assumes the CI database stays PostgreSQL.