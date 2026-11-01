SRQ-01 PR-A, part 2: formula-correspondence report

Objective-aware Objective Explore responses now carry the R7.1 formula_correspondence report, and every frozen request keeps its exact bytes. It’s on srq-01-pr-a2 in two commits, not pushed:

Commit 1, aafca6e (tests only): baselines of today’s objective-aware responses, captured before any app change.
Commit 2, 510c2c4: the integration.

The full suite passes, the 7 strict xfails are unchanged, and no existing snapshot was regenerated.

Files changed
File	Change
app/schemas/research_objective_exploration.py	R7.1 models; formula_correspondence: FormulaCorrespondenceReport | None = None on ResearchObjectiveExplorationResponse
app/services/research/formula_correspondence_report.py (new)	Report builder, composition loader, R5 MP-ID sort key, limitation strings
app/services/research/objective_exploration_service.py	is_objective_aware() (section 4.0); adds the report after the response is otherwise complete
tests/api/test_objective_aware_golden.py + tests/fixtures/golden/srq01_pra/	Commit-1 baselines, plus the full new responses under full/
tests/services/research/test_formula_correspondence_report.py (new)	Requirement tests
tests/services/research/test_objective_coverage.py	Minimal adjustment to an existing test, explained below

app/schemas/discovery.py and every shared Discovery schema are unchanged. Admission, traversal, ranking, scoring, ordering and truncation are untouched: the report only reads the chains and ranked candidates that were already returned.

How the key is absent on frozen requests
The field defaults to None, and a model_serializer(mode="wrap") on the response drops the key whenever it’s None, so it’s absent, not null.
The service sets it only when is_objective_aware(request): at least one preferred element, or Strict with at least one avoided element.
OpenAPI still documents the field as an optional FormulaCorrespondenceReport.
Proven by: all 31 PR-0 golden cases pass byte for byte; an explicit test checks that the string formula_correspondence doesn’t appear in 5 frozen responses; and an 8-case scope matrix for is_objective_aware.
Query strategy
One SELECT id, mp_id, raw_data['composition'] … WHERE id IN (…) covers every involved material: the request source, every material in the returned chains, and every ranked candidate. There’s no per-material loop; a test counts exactly one statement.
Every stored value passes through normalise_stored_composition; a ValueError makes it unusable (None).
Tests mapped to the requirements
Requirement	Tests
Frozen requests: key absent	test_frozen_requests_carry_no_key_at_all (5 cases); test_objective_aware_scope (8); PR-0 golden suite unchanged (31 cases)
Objective-aware: response minus the key identical to commit 1	test_response_without_the_report_matches_the_pre_integration_baseline (3). It strips the key, re-serializes like Starlette, and compares with the baseline bytes. It also checks the served bytes directly: they must equal the baseline with only ,"formula_correspondence":… appended. test_full_objective_aware_response_bytes_match_golden (3) freezes the full responses
Report always present and shaped per R7.1	test_objective_aware_requests_always_carry_the_report (4): flags false, expansions == [], every formula_group == [], count equals list length, limitations; test_schema_literals_match_the_classifier
Guard: no side without an alkali	test_no_entry_has_a_side_without_alkali (4 live requests, checked against stored compositions); test_pairs_that_are_not_one_alkali_replacements_are_omitted (same alkali; LiMnO₂ → MgMn₂O₄; MgMn₂O₄ → NaMnO₂)
None versus not_evaluated	test_unusable_composition_is_reported_only_where_it_was_examined; test_not_evaluated_ids_are_ordered_by_numeric_mp_id
Normalisation before classification	test_every_classified_composition_was_normalised (4): spies on both functions; every non-None classifier input is an object normalise_stored_composition returned
Bounded queries	test_compositions_load_in_one_query
Case Study 01 content and the NaFePO₄ rule	test_case_study_01_report_on_reference_data; test_nafepo4_is_exact_against_lifepo4_whenever_ranked
Wording	test_report_strings_use_no_forbidden_wording (section 3 list plus the neutral-alkali patterns); test_limitations_state_sections_2_3_and_2_5; the existing app-wide S-5 scan passes
What Case Study 01 returns on the reference data

The request is source #5, limit 10.

source_correspondence: one entry. Rank 5, material #10 NaFePO₄ (mp-19226), exact_alkali_replacement, Li→Na, formula_group: [].
transitions: 10 entries, all not_exact_replacement / ratios_differ. They run from each of mp-19017, mp-26003, mp-25977, mp-27007 and mp-19294 to each of mp-19028 [Na₃Fe(PO₄)₂] and mp-556540 [Na₃Fe₃(PO₄)₄]. NaFePO₄ isn’t in any returned chain at limit 10, so it appears only in source_correspondence.
not_evaluated_material_ids: empty.

The other two requests:

Strict Avoid Li: source_correspondence again holds NaFePO₄ as exact, and transitions includes the one-step mp-19017 → mp-19226 as exact_alkali_replacement.
Q6 on #28: both lists are empty, because no alkali-changing pair is returned.
Results
Full backend suite: 1421 passed, 1 skipped, 7 xfailed, with no XPASS. The 7 xfails are the same H1/H2 permutation tests as before.
ruff check app tests passes, and gitleaks passed on both commits.
Commits: aafca6e (baseline) and 510c2c4 (integration).
Tests ran against mgpra1-pg (127.0.0.1:55434), which is still running.
Ambiguities and how I resolved them
“Appears only in not_evaluated_material_ids” versus R7.1’s “not_evaluated entries are always serialized”.
An unusable material in an alkali-changing transition yields a serialized not_evaluated entry in transitions, as R7.1 requires, and is listed in the IDs.
As a ranked candidate, it appears only in the IDs, never in source_correspondence.
The test asserts exactly this split.
Whether a transition with an unusable composition is alkali-changing. Stored composition can’t answer that, so I use the transition’s recorded element sets (shared, removed and introduced elements) with the step 2 rule.
If the pair would be compared, it’s reported as not_evaluated and the material is listed.
Otherwise it’s omitted and the material counts as never examined.
This matters only for unusable compositions; with usable ones, the classifier decides from stored composition alone.
The source-EFA check counts as “examined” for every ranked candidate. So an unusable ranked candidate, or an unusable request source, is always listed, as R7.1’s population rule says.
R5 ordering of missing MP IDs. Missing and non-numeric IDs follow every numeric ID, ordered by string, with a missing ID treated as the empty string, then by local ID. The spec doesn’t say where a missing ID sorts relative to a non-numeric one.
ExpansionEfaCounts.excluded stays list[dict], exactly as R7.1 gives it. I didn’t invent typed field names ahead of PR-B.
Pydantic writes tolerance as 1e-6, while json.dumps writes 1e-06. That’s why the byte check on served responses uses an exact prefix comparison rather than re-serializing the whole response. The stripped-response comparison you asked for is unaffected, because the stripped data contains no such float.
Two existing tests broke on test doubles.
test_objective_explore_routes_admission_policies_by_mode passes a partial objective. I made is_objective_aware read missing terms as not requested, following the precedent objective_coverage already sets. That test is unmodified.
test_explore_adds_coverage_without_changing_existing_fields builds the service without a database and asserts objective_coverage is the last key. I stubbed the report builder there, set db = None, and updated the key-order assertion so formula_correspondence follows objective_coverage; every earlier field is still checked unchanged. That’s the only existing test I edited.