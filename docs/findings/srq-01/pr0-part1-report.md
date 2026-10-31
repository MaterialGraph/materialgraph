SRQ-01 PR-0, part 1: no-objective golden tests

The golden tests are committed on srq-01-pr0-characterization as 1b64bdc. They are tests only: the commit touches nothing outside tests/, and it is not pushed. The full suite passes, and I have not started part 2.

Paths covered and why

Each of these reads the shared family_service ordering without the objective-aware admission branch:

Path	Why it’s covered	Sources
GET /discovery/chains (Discovery Chains API)	Named in AC6; always uses the legacy admission path	5, 10, 28, and 5 with avoid_element=Li&prefer_element=Na&limit=10
POST /discovery/objective/explore, Balanced or Exploratory with no preferred elements	Takes the legacy path: objective_aware_prefer_allocation needs a preferred element, and hard-Avoid is off	Balanced 5, 10, 28; Exploratory 5; Avoid-only CS01-style (Avoid Li, Co, preserve Fe/P/O, phosphate) on 5; Exploratory Avoid Li on 28
POST /discovery/objective/chains	ResearchObjectiveService is always called with the default flags, so legacy admission	5, 10, 28 (empty objective)
POST /research/scientific-pathways	Built on generate_chains_for_objective	5, 28 (empty objective)
GET /families	Serves the family ordering directly	5, 10, 28
GET /discovery/candidates	DiscoveryCandidateService uses the family results	5, 10, 28
GET /discovery/graph, /subgraph, /path, /communities/connected, /communities/modularity	DiscoveryGraphBuilder uses the family results (graph_builder.py L549)	graph 5 and 28; subgraph 5; path 5→10, 5→7, 28→25; connected 5; modularity 5 and 28

The path 5→10 returns path_found: false: NaFePO₄ isn’t reachable from LiFePO₄ within the bounded graph. I froze that outcome deliberately, and added 5→7 and 28→25 as reachable paths.

Found but not covered

Strict mode with no preferred elements. Hard-Avoid admission is on even when Avoid is empty, so it already runs the objective-aware branch. That’s the path later PRs will change, so it isn’t a frozen path.
Objective Explore with preferred elements. This is the target of the change.
/neighbors, /similar, /recommendations, /neighborhood. None of them refers to family_service or the graph builder, either directly or through the services I traced.
Snapshot files and fixture data
29 files under tests/fixtures/golden/srq01_pr0/, one per case, named after the case (for example objective_explore_5_balanced_avoid_only.json). Together they’re about 760 KB; the two scientific-pathways files are about 186 KB each.
The exact request for each case is in the CASES table in tests/api/test_no_objective_golden.py. Objective requests use max_hops 2, limit 10.
Fixture data is the CI reference dataset (scripts.reference_test_data load, 28 curated materials), loaded the same way as CI: alembic upgrade head, then the three seed scripts and the reference load.
The three sources are LiFePO₄ (mp-19017, #5), NaFePO₄ (mp-19226, #10) and LiMnO₂ (mp-754656, #28, the Q6 source).
How determinism is ensured
The test compares the raw response.content with the snapshot, byte for byte.
tests/fixtures/golden/.gitattributes sets * -text, and a test asserts that no snapshot contains \r. Every committed blob matches its working file.
I scanned the snapshots for timestamps and for time, date, duration, UUID or job fields; there are none.
IDs and ordering come from the fixed reference dataset, which always loads with IDs 1–28.
Floats are serialised exactly as served. The scores are deterministic sums and roundings on fixed inputs.
The suite passed in fresh processes with PYTHONHASHSEED = 0, 1, 4242, 7 and random, so set-iteration order has no effect.
Negative check: I changed one MP ID in a snapshot. The test failed and named the path ($.chains[4].materials[1].mp_id); I then restored the file.
Two extra tests fail on any orphaned or missing snapshot, and on any line-ending conversion.
How to regenerate
MATERIALGRAPH_REGENERATE_GOLDEN=srq01_pr0 python -m pytest tests/api/test_no_objective_golden.py

Regeneration is off by default; only that exact value turns it on. Each rewritten case then fails with “snapshot written…”, so a regeneration run can never pass silently. Afterwards, review the diff and rerun without the variable. Add -k <case> to rewrite only selected cases.

Results
Golden module: 32 passed (29 snapshot cases plus 3 guards).
Full backend suite: 1314 passed, 1 skipped, 1 warning (the skip is the POSIX-only test on Windows). That’s 1282 before, plus 32 new.
ruff check passes, and gitleaks passed on the commit.
Test database: a new disposable container, mgpr0-pg (postgres:17.11, 127.0.0.1:55433, materialgraph_test_ci). It’s still running, and I’ll leave it until you ask for it to be removed.
Open questions
R5 versus R8 conflict. R5 changes tie-breaking in objective_service._rank_chains. That function also serves POST /objective/chains and scientific pathways when there’s no objective, and those are frozen here under R8. Today ties fall back to local-ID order, so an MP-ID tie-break there would break those snapshots unless PR-B adds MP-ID ordering only on the explore path. The spec should state which applies.
Strict with an empty objective. It already takes the objective-aware branch, so I didn’t freeze it. Should it count as a “no-objective request” under R8?
Snapshot scope. Snapshots freeze whole responses, including fields unrelated to SRQ-01 (quality, criticality and risk values). Any later change to seeds or the reference data will need a deliberate regeneration, which is intended but adds upkeep.
Test isolation. The golden tests rely on the reference dataset being unchanged when they run. Every test that commits to the database already cleans up after itself, and the tests pass in collection order, but an independent check in a randomised order (no plugin for that is installed) was not run.