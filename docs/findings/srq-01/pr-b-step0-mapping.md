SRQ-01 PR-B, step 0: read-only code mapping

Mapped on main at c123e49 (tag release-3). Nothing was changed: no files, branches or databases, and no production access.

chain_service.py, family_service.py, objective_service.py and transition_validator.py are unchanged since the S2.0 mapping at 41e852b, so those line numbers still hold.

The thing to settle first is a spec conflict. R2 says overflow is "listed in search metadata", but R7.1 freezes DiscoverySearchMetadata. Overflow can only go into formula_correspondence.expansions (open question 1).

Q1. Where the R2 sequence replaces today's admission, and how to gate it

Where. Replace the objective branch of DiscoveryChainService._get_next_candidates (app/services/discovery/chain_service.py L293–452). Keep its eligibility filter and hard-Avoid (L358–388), and replace three parts:

the reservation pass (L390–419);
the fill pass (L421–425);
the re-sort into family order (L427–431).

The four steps become preferred EFA → preferred reservation → remaining EFA (budget 4) → general fill, with output in admission order. _record_admission_counts (L445–451) still records eligible versus admitted. The legacy path (L333–356) is not touched.

Gating. Gate on an explicit flag, not on the branch taken.

Strict with an empty objective already enters this branch (hard_avoid_admission is true at L334) but is frozen (section 4.0, golden objective_explore_{5,28}_strict_no_objective).
So add a parameter that defaults to off, for example formula_aware_admission: bool = False, and thread it through:
ResearchObjectiveExplorationService.explore (L34–43; set from is_objective_aware, L113–124);
ResearchObjectiveService.generate_chains_for_objective (L16–35);
DiscoveryChainService.get_discovery_chains (L40–53);
_build_chains (L112–122, and the call at L161–168);
_get_next_candidates.
Every frozen caller relies on the default: the Discovery Chains route (discovery.py L83–99), /objective/chains (L102–118) and scientific pathways (scientific_pathway_analysis_service.py L35).

Q2. Per-edge EFA compositions at admission time, and the cache key

Compositions without a per-candidate query. Three options:

(a) Recommended: one query per request for every stored composition, normalised with normalise_stored_composition. This mirrors _get_material_elements_map (L562–585), which already loads the whole material_elements table once per request. Keep it in a dict on the service instance; 1,727 rows in production.
(b) Lazy per expansion: one IN (…) query for the family pool IDs not loaded yet, using load_compositions (formula_correspondence_report.py L54–75). The query count is bounded by the number of distinct expansions (6 in CS01).
(c) Reuse search_service._CACHE (CompositionIndexCache, L390): not recommended. Its fingerprint is (count, max(id)) (L322–329). The permutation harness keeps both values the same, so the cache would serve fractions keyed by stale IDs within one test process (see Q9).

Classification is then classify_formula_correspondence(fractions[expanding_id], fractions[candidate_id]) for each eligible candidate, a pure in-memory call.

Cache key. The key at L313–319 is (material_id, avoid, prefer, hard_avoid, prefer_allocation), scoped to one service instance per request. Add the new flag. Per-edge classification depends only on the pair, and the introduced-Avoid pre-check depends on avoid, which is already in the key. So no other component is needed, and the per-material cache (spec 2.2) stays valid.

Q3. Introduced-Avoid pre-check for EFA candidates before the cap

DiscoveryTransitionValidator._violates_avoid_elements (transition_validator.py L132–150) is a pure function of (from_elements, to_elements, avoid_elements). It's the same check validate_transition applies after admission (L57–62), using the same element-record evidence.

In the objective branch, elements_map is already in scope (used at L374–376). The service already holds self.transition_validator (L28).
So, for EFA candidates only and before steps 1 and 3, call self.transition_validator._violates_avoid_elements(from_elements=elements_map[material_id], to_elements=elements_map[candidate_id], avoid_elements=normalized_avoid_elements).
reject_introduced_avoided reaches _build_chains (L121) but not _get_next_candidates. It must be threaded through (and added to the cache key) so the pre-check honours the mode policy. Today every mode sets it to true.
Consider making _violates_avoid_elements public, or wrapping it, rather than calling a private method across classes.

Q4. How candidate identity flows (formula groups, R3)

Flow today

family_service builds related-material dicts with material_id, mp_id, formulas, relationships and shared_elements (L96–114), sorted by (-len(shared_elements), material_id) (L186–191).
_get_next_candidates returns a subset of those dicts.
_build_chains turns each into a chain node through _candidate_to_node (L598–610: material_id, mp_id, pretty_formula, formula) and a transition through _build_transition (L454–486).
Ranked candidates come from chain nodes in _rank_candidates_from_chains (objective_exploration_service.py L167–239; identity at L192–201).
The report reads the returned chains and ranked candidates (formula_correspondence_report.py L146–221).

Choosing the representative. In _get_next_candidates, after per-edge classification: group EFA records by reduced composition (fractions equal within TAU), pick the representative (lowest numeric MP ID; mp_id_sort_key is in the report module, L46–51), and admit only the representative's dict into candidates. Non-representatives never become nodes, so traversal and scoring use the representative's own record (R3).

Attaching members. Record each group per expansion in an admission store beside _admission_counts (L255–291), for example _efa_groups[cache_key]. Carry it out of the chain service as a separate key on the get_discovery_chains result, not inside search_metadata (open question 1). generate_chains_for_objective passes it through to explore, and build_formula_correspondence_report fills formula_group (today [] at L202) and expansions.

Member energy_above_hull comes from one bulk query, or from the composition query in Q2 extended with that column.

Q5. MP-ID ordering points, objective-aware only

| Ordering | Insertion point | How it stays off for frozen requests |
|---|---|---|
| Admission (R5a) | _get_next_candidates objective branch: re-sort eligible_candidates (built L368–388) by (-len(shared_elements), mp_id_sort_key) before the R2 steps. family_service stays unchanged (D3) | The Q1 flag |
| Ranked-candidate ties (R5b, R6) | The sorted(..., key=score) in _rank_candidates_from_chains (L235–239): key (-score, not source_efa, mp_id_sort_key). The source-EFA set comes from the per-request compositions (Q2) | A parameter from explore, set only when objective-aware. The S-3 guard forbids any mention of alkali_substitution in this file, so key it on classification results, as R7.2 already does |
| Chain ties (R5b) | ResearchObjectiveService._rank_chains (objective_service.py L183–212; sort at L207–210): add chain_tie_key=None. When set, sort by (-score, tuple of mp_id_sort_key over chain materials) | Thread through generate_chains_for_objective (L16–24) with default None. /objective/chains and scientific pathways never pass it |
| Truncation (R5) | Already follows the sort: eligible_chains[:limit] (explore L65) and candidates[:limit] (L72). The Strict final filter (L46–50) keeps order | Nothing extra |

Once admission and chain ties use MP-ID keys, breadth-first generation order no longer decides anything.

Q6. The 7 strict xfails (tests/services/research/test_srq01_id_permutation.py)

All run at limit 20 and compare by MP ID; the marker is LOCAL_ID_DEPENDENCE, L34.

| Test | What it needs to pass |
|---|---|
| test_h1_admitted_candidates_do_not_depend_on_local_ids[cs01_source5_balanced], [q6_source28_balanced] (L156–164) | MP-ID admission ordering (Q5, admission row). Reservation and fill would then pick the same MP IDs under any permutation. The R2 sequence isn't required for this |
| test_h2_equally_scored_candidates_keep_their_order[cs01 / q6 / strict] (L178–180) | The ranked-candidate tie key (Q5). The precondition test (L170–174) already shows the sets are invariant |
| test_h2_equally_scored_chains_keep_their_order[q6 / strict] (L189–191) | The chain tie key in _rank_chains. For Strict this also decides which tied chains survive the cut to 20 |

Each marker is removed deliberately in the PR that fixes it. AC3 adds a synthetic Strict case with more than 6 eligible candidates; AC4 adds a Case Study 01 chain-order test once H1 is fixed.

Q7. AC11: forcing each NaFePO₄ record as representative

Mechanism. Make representative selection a single module-level function, for example choose_representative(members) -> member, defaulting to the lowest numeric MP ID. The AC11 harness monkeypatches it to return a given MP ID. Nothing is exposed in the API, a request or the configuration.

Data. The CI reference fixture has only one NaFePO₄ (#10, mp-19226), so AC11 can't run there as-is. Two options:

(a) Production-equivalent local database (materialgraph_test_mg_de_007, 4 NaFePO₄ records), run through ResearchObjectiveExplorationService in a rolled-back transaction, with the artifact recorded under docs/findings/srq-01/. This is the AC11 gate.
(b) Synthetic copies of #10 with distinct MP IDs and energies, inserted inside a rolled-back transaction like the permutation harness. That gives a CI-runnable regression test, not the gate.

Q8. Report fields to switch on

| Field | Today | PR-B |
|---|---|---|
| expansions | [] (report L215) | One ExpansionEfaCounts per expansion, from the admission store (Q4) |
| excluded | list[dict] (schema L229) | Type it, for example ExcludedEfaGroup(formula, member_mp_ids, reason: Literal["cap", "efa_budget"]); the expansion is the parent's expanded_material_id. The JSON keys are new, but the OpenAPI schema changes from object to model: see open question 2 on contract_version |
| formula_group | [] (L202), FormulaGroupMember (schema L210) | Members with traversed=True only for the representative |
| formula_grouping_available, admission_reporting_available | False (L216–217) | Set each to True in the PR that implements it, never before (R7.1: false means "not yet reported") |

Q9. Risks and a proposed split

Risks

Frozen bytes. Strict with an empty objective shares the objective branch, so the Q1 flag is mandatory. The legacy path, family_service, the default _rank_chains, and the Discovery Chains, /objective/chains and scientific-pathways callers must not change. The 31 PR-0 golden cases enforce this.
Objective-aware snapshots. srq01_pra will legitimately change in candidates, chains and scores. test_response_without_the_report_matches_the_pre_integration_baseline (test_objective_aware_golden.py L83) assumes only reasons and the report differ, so it has to be retired or re-baselined deliberately. Pair each regeneration with an AC5/AC8 diff artifact; the reasons-only derivation used so far no longer applies.
S-3 guard. It forbids alkali_substitution in objective_exploration_service.py and scoring_service.py, and allows exactly one normalisation line in path_ranking_service.py and edge_intelligence_service.py. Key all EFA logic on classifier results. chain_service.py isn't guarded, but keying on classifications is cleaner there too.
S-5 wording. Any new user-facing string must pass the neutral-alkali scan. Reason codes like cap and efa_budget are API values.
Composition cache. Reusing CompositionIndexCache would serve stale fractions inside the permutation harness (Q2c).
Performance (AC10). Classifying every eligible candidate per expansion (CS01: about 5,000 considered in total) is pure dict work. The cost is the composition load, one query per request under Q2a.
Overflow location. DiscoverySearchMetadata is shared and frozen, and its schema would silently drop extra keys anyway. Overflow must travel by a side channel to expansions.

Proposed split (each separately testable; frozen golden unchanged throughout):

| PR | Scope | Tests |
|---|---|---|
| PR-B1: ordering | Q1 flag plumbing; MP-ID admission tie key (no R2 steps yet); ranked-candidate tie key (source EFA first, then MP ID); _rank_chains tie parameter | All 7 xfails turn into passes, markers removed; synthetic Strict H1 case with more than 6 eligible (AC3); CS01 chain-order H2 (AC4); deliberate srq01_pra regeneration with an order-only diff |
| PR-B2: formula groups | Composition load (Q2a); per-edge EFA at admission; grouping and representative (choose_representative); formula_group and its flag | AC11 harness (synthetic in CI, plus the production-equivalent gate run before merge); grouping unit tests |
| PR-B3: admission sequence | R2 four steps; EFA budget 4; introduced-Avoid pre-check (Q3); expansions with typed excluded and its flag | AC7 and AC12 (i)–(iv); overflow reporting; AC5/AC8 diff artifact |

After these, S4 (spec section 7, step 6): AC2 at limits 5 and 10, AC5, AC8, AC10 and AC14 on production-equivalent data.

Open questions

1. Where overflow lives. R2 says "listed in search metadata", but R7.1 freezes DiscoverySearchMetadata and defines expansions[].excluded. Confirm formula_correspondence.expansions as the only location.
2. Typing excluded. Is replacing list[dict] with a typed model a contract change needing contract_version "2", or is it allowed because the field has only ever been empty?
3. Which formula string identifies a group. pretty_formula of the representative, or a canonical reduced formula derived from stored composition (which would need a formatter without pymatgen)?
4. formula_group scope for source EFAs. For a ranked source EFA reached at hop 2 through a non-EFA edge, there's no admission group. Should formula_group list every record with the same reduced composition in the reachable pool, only the members of the admission group it came from, or stay empty?
5. Chain tie key. R5 says "numeric MP ID" for chains. Is the tuple of MP-ID keys along the chain's materials (lexicographic) the intended definition?
6. R2 ordering with no EFA present. Should admission order within the general step be (-shared_count, MP ID), keeping today's shared-element priority, or MP ID only?
7. Composition source. Q2a (one query per request) versus Q2b (lazy per expansion): pick one before PR-B2. The process cache (Q2c) is ruled out.
8. AC11 data. The gate needs the production-equivalent database, which has 4 NaFePO₄ records, because CI has one. Confirm the gate is a local run with a recorded artifact, plus a synthetic CI regression test.

(Decisions on these questions are recorded in SRQ-01 S2 rev 3.11.)
