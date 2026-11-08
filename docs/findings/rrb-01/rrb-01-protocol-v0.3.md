# RRB-01: Retrospective Substitution Retrieval Benchmark — Pre-registration v0.3 (DRAFT)

Nov 5, 2026 · @Jithin Mathews

## Status and scope

RRB-01 measures how well frozen release-4 retrieves an independently documented substitute composition, given a parent material and an explicitly specified substitution objective, compared with deterministic baselines. This is draft v0.3. It is registered in two stages, a protocol lock and an evaluation lock, each an immutable Git reference (section: Freeze sequence); the evaluation lock is the execution-ready registration.

**Study type.** RRB-01 is a founder-extracted, externally sourced retrieval evaluation without independent eligibility verification. No independent reviewer has been recruited, and none is assumed.

| Item | Frozen value |
| --- | --- |
| System | release-4 = main 50dd3ed (tagged); backend-only on top of release-3 (bf0e702) |
| Dataset | 1,727 materials, Materials Project release 2026.04.13 |
| Endpoint | Objective Explore |
| Changes permitted | None to code, data, config or defaults for the life of the benchmark |

**Primary claim (narrow).** Given a parent material and an explicitly specified substitution objective, how effectively does frozen release-4 retrieve the independently documented target composition compared with deterministic baseline methods?

**What it does not claim.** It is not a temporal prediction test: the snapshot already contains the targets and there is no time-gated view. It does not establish independent candidate identification, scientific usefulness, structural correctness or synthesizability. Formula Hit@k is a mechanical retrieval proxy, not a relevance judgment.

**Open items held untouched until RRB-01 reports:** representative vs criticality spec decision; Issue 3 (Q6, LiMnO2); "Not validated" badge wording.

## Research questions

Q1 is the single primary question; everything else is secondary or diagnostic and cannot rescue a primary outcome.

| ID | Question | Role |
| --- | --- | --- |
| Q1 | Positional Formula Hit@5 of release-4, balanced mode, informed arm (Avoid + Prefer), on the direct-composition-eligible cohort (E) | Primary |
| Q1b | The same metric on all covered, objective-expressible cases (E + I), with I also reported alone | Secondary |
| Q2 | Paired difference in Hit@5 between release-4 and baselines B1, B2, B3 in the informed arm | Secondary |
| Q3 | Positional Formula Hit@5 in the balanced avoid-only arm, and its paired difference from the informed arm | Secondary |
| Q4 | Coverage: what fraction of the literature source cohort is in the dataset and objective-expressible | Secondary |
| Q5 | Which stage each miss is attributable to, where the response permits; duplicate-formula rate in responses | Diagnostic |
| Q6 | Strict avoid-only Hit@5 | Exploratory |

**Interpreting Q3.** In balanced mode, supplying Prefer both adds a hint and switches the request onto the SRQ-01 objective-aware admission path (objective\_exploration\_service.py, lines 149–159). The informed minus avoid-only difference therefore measures what a researcher gains by specifying Prefer under default mode, path switch included. It does not isolate the value of the hint.

**Interpreting Q6.** Strict avoid-only does enter the objective-aware path, including remaining exact-analog group admission (chain\_service.py), but strict also changes avoidance behavior. It is a partial decomposition only and is never substituted into the primary arm.

## Case cohort

Cases come from one or two published review articles on battery electrode substitution, named in this document before extraction begins. Every qualifying pair in those sources is extracted; none is hand-picked.

**Source (selected).** Two open-access reviews: Hwang, Myung & Sun (2017), *Sodium-ion batteries: present and future*, Chem. Soc. Rev. 46, 3529–3614, DOI 10.1039/c6cs00776g; and Noerochim, Suwarno, Idris & Dipojono (2021), *Recent Development of Nickel-Rich and Cobalt-Free Cathode Materials for Lithium-Ion Batteries*, Batteries 7, 84, DOI 10.3390/batteries7040084. Muralidharan et al. (2022) was considered but not selected because access to the journal article's full text could not be established; its OSTI chapter version was not substituted.

**Selection rationale.** Both sources were chosen on documented extractability under the explicit-pair rule, without running any pair through MaterialGraph. Hwang states explicit Li→Na links sparsely, in prose only; its more frequent explicit relationships are Na-internal partial substitutions. Noerochim frames Co replacement explicitly in prose with fixed compositions, but its pairs concentrate in a few primary studies. Noerochim's summary table lists individual materials with their modification and performance; it names no parent for any row, so it cannot establish pairs, its rows are never paired with one another by inference, and it is used only to locate supporting prose. The two reviews offer different chemistry contexts, not a guaranteed balanced cohort: qualifying pairs may be sparse, concentrated in a few primary studies, or ineligible under the frozen objective semantics, and the cohort is expected to be dominated by within-family substitutions; this is stated in advance and is not corrected after extraction by adding sources or selecting examples. Source selection is closed unless an objective access or extraction failure arises.

**Extraction.** Jithin performs the extraction from both frozen sources, recording every inclusion and exclusion decision with its source location, the source's stated relationship, and the cited primary study. Both sources are open access, so any reader can check each decision against the original text.

**No independent eligibility verification.** Eligibility decisions are not verified by an independent reviewer. The study is never described as independently validated, and AI agreement is never presented as scientific independence.

**Rule-reproducibility check (pre-registered).** A second automated application of the locked rules, run after the protocol lock and before the evaluation lock. It tests whether the rules are precise enough to reproduce; it is not independent scientific verification.

1. Jithin completes the founder extraction from both sources, recording every inclusion and exclusion decision with its source location.
2. A fresh AI session receives only the locked extraction rules, the two source documents and the required output schema. It receives neither the founder extraction nor any previous discussion.
3. Both outputs are preserved unchanged before comparison, with model identification, configuration, prompts and execution date recorded.
4. The comparison covers exact directed parent–target pairs, inclusion and exclusion decisions and relationship classifications. Agreement and every disagreement are reported, including omissions and additional proposed pairs.
5. Disagreements are resolved against the original literature using the locked rules, with every adjudication and its rationale recorded. A disagreement the rules cannot resolve is marked ambiguous; the criteria are not silently changed.

The original founder extraction is preserved unchanged after adjudication, so the final case list does not conceal how much judgment was needed to build it. Any change to a locked extraction rule is a protocol amendment, logged as a deviation, not a clarification.

**Post-hoc human audit (optional).** A later audit of eligibility decisions by a domain researcher is permitted. It is labelled post-hoc and reported separately; it does not change the pre-registered results.

**Order of operations.** First enumerate every literature pair in the sources (the source cohort). Only then classify each pair against the dataset. Dataset membership is never an extraction criterion, so Q4's denominator is unbiased.

**Explicit-pair requirement.** A pair is extracted only when the source text, a table or a caption explicitly relates the target composition to a named parent composition as its substitute or analog. A material presented only as a broad technology alternative, for example a cobalt-free cathode discussed alongside cobalt-containing cathodes in general, does not form a pair. The extractor never supplies a parent the source does not name.

**Relationship characterization.** Each extracted pair records how the source itself characterizes the relationship, as one of: formula or structural analog; proposed replacement; experimentally evaluated substitute. The label is taken from the source's wording, with the supporting location recorded. Labels are never merged into a single validity claim, and a named formula analog is not treated as a demonstrated functional substitute. The label is reported as a descriptive stratum and does not change eligibility or the primary denominator.

**Source identity.** A journal article and any chapter, preprint or report version of the same work are separate potential sources. Substituting one for another requires its own recorded source-selection decision.

**Qualifying relationship types (provisional).** Two types qualify, each recorded and reported as its own stratum:

1. Cross-chemistry analog: the source names a parent and a target in different chemistries (for example, a Li compound and its Na analog) and states the analog or substitution relationship.
2. Within-family composition substitution: the source names a parent composition and a target in which one or more elements are explicitly replaced, partially or fully.

A synthesis route alone, such as a material obtained by ion exchange from a precursor, does not qualify unless the source independently describes a substitution or analog relationship. Direction follows the source's explicit parent-to-target description.

**Composition rules (provisional).**

| Composition type | Rule |
| --- | --- |
| Fixed integer formula | Include |
| Fixed fractional formula | Include; keep the published formula in the audit record and normalize with exact rational arithmetic, never floating point |
| Fixed doped composition | Include if both parent and target compositions are explicitly named |
| Formula with an unresolved variable | Exclude from scored cases; count in the source cohort |
| Variable formula with a stated value | Include only if that value is explicitly tied to the documented relationship |
| Material family without a specific composition | Exclude from scored cases; count in the source cohort |

**Stoichiometry-only substitutions.** A substitution that changes coefficients without changing the element set yields empty Avoid and Prefer and is classified N under the frozen objective semantics. No objective is invented to make it testable, so broadening relationship types does not guarantee a larger scored cohort.

**Spatially heterogeneous materials.** Core–shell, concentration-gradient and other spatially heterogeneous materials are excluded as benchmark endpoints when their defining composition cannot be represented by a single homogeneous formula. The exclusion applies to the material, not the study: a separate, explicit substitution between two homogeneous compositions documented in the same study can qualify on its own.

**Morphology and surface modifications.** Comparisons involving only coatings, particle size, crystallinity, single-crystal versus polycrystalline structure or synthesis method, with the underlying composition unchanged, do not form pairs. A composition substitution accompanied by a morphology change can qualify if the source explicitly identifies the compositional relationship; the morphology change is recorded as a confounding characteristic and is never read as evidence that the substitution caused a reported performance difference.

**Directed pairs only.** A comparison among alternative dopants or compositions does not establish a pair unless the source identifies which composition replaces or modifies which parent.

**Evidence-source record.** For each extracted pair, the audit trail records the cited primary-study identifier (DOI or reference number in the source) where the review relays another study's result.

### Extraction output schema (draft, to be fixed at protocol lock)

Both the founder and the AI extraction write one JSON Lines file each, UTF-8, one record per line, with the same schema version. Extractors record compositions exactly as published; a deterministic script, not the extractor, performs normalization.

**Raw preservation.** Both raw extraction files are preserved unchanged, transcription mistakes included. Normalization writes to separate fields; a composition the script cannot parse or normalize is logged as a normalization failure with the raw string, never silently corrected.

**Frozen source snapshots.** Extraction uses the publisher PDF of each source, saved with its SHA-256 recorded. Locations refer to these files only.

| Source | File | SHA-256 |
| --- | --- | --- |
| Hwang 2017 | Sodium-ion batteries\_ present and future - c6cs00776g.pdf | 6832B1BCFF445AED9CD7AC31E955CE9473EB8EF7A0ECD63FCBD874DB91799243 |
| Noerochim 2021 | batteries-07-00084-v2.pdf | 8D8991D441AD6AA43AFA98602411A685F40974980921E30BCD96D394F16B3292 |

**What creates a record.** A record is created for every statement, table row or caption that does either of the following: (a) places two specific compositions, or a composition and a material family, in a substitution, replacement, analog, doping or comparison context; or (b) presents a single specific composition as replacing, substituting for or serving as an analog of an unnamed parent or a general class (for example, "cobalt-containing cathodes"). Type (b) records are always `exclude` with reason `no_named_parent`. Included and excluded candidates are both recorded, so exclusions can be compared between extractions.

| Field | Content | Filled by |
| --- | --- | --- |
| schema\_version | Fixed string, e.g. `rrb01-extract-1` | Extractor |
| extractor | `founder` or `ai` | Extractor |
| record\_id | `<source>-<page>-<n>`, n counting records on that page in reading order | Extractor |
| source | `HWA17` or `NOE21` | Extractor |
| location | Page, section number, and paragraph ordinal within the page, or table/figure number and row | Extractor |
| evidence | The relating sentence or row, quoted, at most 40 words | Extractor |
| cited\_primary\_study | Reference number and DOI the source cites for the statement, or `none` if the review's own statement | Extractor |
| parent\_as\_published | Parent composition exactly as printed, or `null` if the source names none | Extractor |
| target\_as\_published | Target composition exactly as printed | Extractor |
| composition\_type | One of: `fixed_integer`, `fixed_fractional`, `fixed_doped`, `unresolved_variable`, `variable_with_stated_value`, `family_no_composition`, `spatially_heterogeneous` (for parent and target separately) | Extractor |
| direction\_basis | The words establishing which composition replaces or modifies which | Extractor |
| relationship\_type | `cross_chemistry_analog` or `within_family_substitution` | Extractor |
| characterization | `formula_or_structural_analog`, `proposed_replacement` or `experimentally_evaluated_substitute` | Extractor |
| confounders | List, e.g. `morphology_change`, `coating`; empty if none | Extractor |
| decision | `include`, `exclude` or `ambiguous` | Extractor |
| exclusion\_reason | One of: `no_named_parent`, `not_directed`, `synthesis_route_only`, `morphology_or_surface_only`, `spatially_heterogeneous`, `unresolved_variable`, `family_no_composition`; `null` unless decision is `exclude` | Extractor |
| ambiguity\_note | Which rule could not decide the record, and why; `null` unless decision is `ambiguous` | Extractor |
| parent\_normalized, target\_normalized | Reduced formulas by exact rational arithmetic | Script |

**Comparison keys.** Included pairs match on source, normalized parent and normalized target, direction-sensitive. Excluded and ambiguous records match on source, location (page plus paragraph, table or figure position) and the published compositions. Two records that cannot be matched unambiguously, for example several distinct comparisons of the same compositions on one page, are reported as unmatched rather than forced into agreement. Unmatched records on either side are reported as omissions or additional proposals.

**Duplicates.** Each occurrence keeps its own record and its own decision. Occurrences of the same normalized directed pair, at several locations or in both sources, collapse into one benchmark case, which qualifies if at least one occurrence is `include`. An occurrence that does not itself meet the rules (for example a mutual comparison without direction, recorded as `exclude`, `not_directed`) never becomes qualifying evidence because another occurrence qualifies; the case's audit trail lists every occurrence with its decision.

**Ambiguous after adjudication.** Records still ambiguous after adjudication are excluded from the scored cohort and counted by source.

**Complete enumeration.** All unique qualifying directed pairs from the two frozen sources are retained, regardless of cohort size. The 20–40 range is a planning estimate only, not a sampling target or cap. No sampling or selection based on dataset coverage, relationship type or benchmark results is permitted. If the full cohort cannot be processed, the evaluation is reported as incomplete rather than substituting an unregistered subset.

**Development exclusions.** LiFePO4 → NaFePO4 (Case Study 01, used to develop SRQ-01) and Li3Fe2(PO4)3 → Na3Fe2(PO4)3 (observed during release-4 qualification) are excluded from the primary cohort. If they appear in the sources they stay in the coverage count, and are reported separately as development cases.

**Objective derivation (mechanical).** For each pair, Avoid = elements in the parent absent from the target; Prefer = elements in the target absent from the parent. No hand-tuning.

**Parent record resolution (pre-registered convention).** When a parent formula matches several dataset records, the request uses the record with the lowest numeric MP-ID, consistent with release-4's formula-group representative rule and with pre-check 2b. If several records share the same numeric MP-ID, ties are resolved by the full MP-ID string and then by local material ID, ascending. The complete ordered match list and the selected parent ID are recorded before any benchmark request is executed. This is a selection convention, not a claim that the chosen record is scientifically representative of every structure sharing that formula.

**Empty Avoid with non-empty Prefer.** Such cases, for example partial substitutions where the parent's element is reduced rather than removed, remain eligible under the E/I rules and stay in the informed-arm cohort and coverage reporting unchanged. They are excluded only from the balanced avoid-only arm and from paired informed vs avoid-only comparisons, because their avoid-only request would carry an empty objective. The excluded count and the resulting avoid-only denominator are reported explicitly.

### Classification layers

Records first pass a pre-classification gate: only records with decision `include` reach classification. Records excluded at extraction (including unresolved-variable formulas, material families and spatially heterogeneous materials) and records left ambiguous receive status P and are never forced into N or X. N, X, E and I are then mutually exclusive and assigned by script, in the precedence order shown, so their fractions of the qualifying pairs sum to 100%. A and H are recorded from the runs and are diagnostic only: they never remove a case from the primary denominator.

**Denominators.** Three counts are reported separately: source records (every extraction record, including repeated mentions), P records by exclusion reason, and unique qualifying directed pairs after deduplication. Coverage statistics for N, X, E and I use unique qualifying directed pairs only, so repeated mentions of one relationship cannot inflate them.

| Precedence | Layer | Meaning | Assigned |
| --- | --- | --- | --- |
| 1 | N | Not objective-expressible: parent and target share the same element set, so Avoid and Prefer are both empty; assigned regardless of dataset coverage | Before runs, by script |
| 2 | X | Objective-expressible, but parent or target formula absent from the dataset | Before runs, by script |
| 3 | E | Objective-expressible, both present, at least 3 shared elements | Before runs, by script |
| 4 | I | Objective-expressible, both present, fewer than 3 shared elements | Before runs, by script |
| — | A | Target formula group observed in admission evidence | From run responses, where exposed |
| — | H | Target returned within the requested cutoff | From run responses |

**Dataset coverage, reported separately.** For every source pair, N included, record whether the parent and the target are each present in the dataset. This keeps coverage information that N's precedence would otherwise hide.

**Primary cohort: the direct-composition-eligible cohort** = E minus development exclusions. It is not described as the reachable cohort: E is a composition rule, not proof that release-4 can reach the target. I cases are run in every arm and reported alone and pooled with E (Q1b), so the headline cannot hide performance on harder relationships. No zero-hit outcome is asserted for I, because multi-hop chains may reach targets through intermediates. An I-stratum hit triggers investigation and is reported, not discarded. N and X cases appear only in the coverage report.

**Code-derived reachability.** Whether a valid path exists under frozen graph semantics may be established by code reading for selected cases and labelled as derived. No parallel traversal implementation is built.

## Run conditions

Every request states its mode, both limits and the full objective explicitly; nothing relies on server defaults, so a default change would surface as a deviation.

| Arm | Mode | Avoid | Prefer | Role |
| --- | --- | --- | --- | --- |
| Informed | balanced | derived | derived | Primary |
| Avoid-only | balanced | derived | empty | Secondary |
| Strict avoid-only | strict | derived | empty | Exploratory |

**Frozen request fields.** `mode`, `request.limit` (response slice, schema range 1–20), `objective.limit` (passed to chain generation), Avoid, Prefer, parent identifier. `request.limit` = 5 for primary runs. `objective.limit` = *the value the frozen release-4 frontend actually submits, determined by code inspection, not by results, and sent explicitly in every request*. Each request is stored as canonical JSON with its SHA-256 hash.

**Determining `objective.limit`.** If the frozen frontend sends a fixed value, that exact value is used. If it omits the field and relies on a backend default, the frozen backend default is inspected and its effective value sent explicitly. If the frontend derives `objective.limit` from `request.limit`, that coupling is preserved and both values are recorded for each configuration; the protocol never overrides the coupling to make an equivalence check pass.

**Determination (pre-check 1, static inspection of 50dd3ed).** Case C: on the normal form path the frontend sends `objective.limit` = `request.limit`, so the primary configuration is `request.limit` = 5, `objective.limit` = 5. A comparison-link entry path can carry a different recorded value; it is not the default product path and is not used. On this endpoint `objective.limit` does not reach traversal or slicing; it appears only in the response, as `search_metadata.requested_result_limit` and in the echoed objective. `request.limit` alone determines how many chains and candidates are returned.

**Pinned request fields.** Every benchmark request sends all fields the frontend sends, with frontend defaults unless the arm says otherwise: `objective.avoid_elements` and `objective.prefer_elements` (as derived per arm), `objective.preserve_elements` = \[\], `objective.target_family` = null, `objective.max_hops` = 2, `objective.limit` = `request.limit`, `objective.prefer_lower_criticality` = true, `objective.require_stable_materials` = false, `mode` per arm, `limit` per configuration.

**Frozen-system observation (not a benchmark failure).** `search_metadata.requested_result_limit` reports `objective.limit`, while the returned-result cap is `request.limit`. The two can disagree only when the values differ, which the normal frontend path never does. Release-4 is not changed for RRB-01; the observation is recorded for later review.

**Limit equivalence.** On the frozen release-4 Objective Explore endpoint, static code inspection establishes that `objective.limit` does not control search, admission, ranking or result slicing when the ranked/search pool is enabled. The normal frontend couples `objective.limit` to `request.limit`. Requests with (`request.limit`, `objective.limit`) of (5, 5) and (10, 10) are therefore treated as the same search procedure with different response limits, subject to empirical verification on both development cases. This refinement was made before the protocol lock from code evidence alone; no development-case retrieval result informed it.

**Canonical comparison rules (frozen from pre-check 2a before any development-case response is seen).** Two comparisons answer two questions and use different rules. A field is never excluded merely because it differs; complete raw responses are always preserved.

1. **Repeatability (same request executed twice).** The complete canonical response is compared, including coverage, metadata and scientific summaries. Static inspection found no timestamp, ID or random field in the response, so any difference is a finding.
2. **Limit equivalence ((5, 5) versus (10, 10)).**
   - Exact agreement required: the first five `ranked_candidates` (IDs, formulas, scores, reasons, warnings); the first five `chains` (paths, transitions, scores, explanations); the limit-independent search diagnostics (expansion counts, candidate and admission counts, `search_truncated`, `ranked_material_pool_count`, `formula_correspondence.expansions` and formula groups); and all policy and objective fields other than `objective.limit`.
   - Expected differences allowed: `objective.limit` and `search_metadata.requested_result_limit`; returned counts and `result_truncated`; the number of records in the returned candidate and chain arrays; coverage summaries and formula-correspondence summaries computed over the returned slice; the truncation string in `objective_coverage.limitations` only when `search_truncated` is identical.
   - For slice summaries, per-position entries are compared across responses wherever their meaning is directly comparable (`chain_avoidance` and `formula_correspondence.transitions` at chain position ≤ 5, `source_correspondence` at candidate rank ≤ 5). Aggregate values computed over the whole returned slice are not required to match the other response; instead each is recomputed from its own response's slice and checked for internal consistency.

If both development cases pass, Formula Hit@10 and unique-formula Hit@5 may be reported as secondary metrics derived from the ten-result responses. If either fails, the ten-result response is treated as a separate configuration, and no equivalence-dependent metric is reported as comparable to the primary configuration.

**Environment.** Runs use read-only requests against production release-4. A local instance is allowed only if it runs 50dd3ed against a copy of the production database with identical local IDs (not a re-import), because tie order on non-objective-aware requests, including the balanced avoid-only arm, follows local `material_id` order; it must also reproduce the Case Study 01 production capture on canonical scientific output. Captures are stored compactly and archived off the server (server disk at 82%).

**Reproducibility.** Every request is run twice. Two checks are recorded separately:

1. Raw reproducibility: identical response bytes, or identical canonical serialization with non-semantic fields (timestamps, request IDs) listed in advance and removed.
2. Scientific reproducibility: identical formula groups, ranks, labels, chain paths and explanations.

A scientific-output difference marks the case as a reproducibility failure. It is reported in the results and not resolved by rerunning until it passes. Raw-only differences are recorded but do not affect the case.

## Baselines

All baselines are deterministic offline scripts over a frozen export of the same 1,727-material snapshot, committed before any run. Each baseline receives only the information MaterialGraph receives in that arm.

| Baseline | Rule | Informed arm | Avoid-only arm |
| --- | --- | --- | --- |
| B0 Random | Exact expected hit probability under uniform ranking of the eligible pool, computed analytically | Yes | Yes |
| B1 Element filter | Eligible pool, ordered by lowest MP ID per formula group | Yes | Yes |
| B2 Composition substitution | Enumerated element substitutions on the parsed parent composition, looked up in the dataset (full rule below) | Yes | Not applicable |
| B3 Composition similarity | Eligible pool ranked by element-set Jaccard similarity to the parent, tie broken by lowest MP ID | Yes | Yes |

**Common rules.**

- Eligible pool (B0, B1, B3): dataset materials containing no Avoid element and, in the informed arm, every Prefer element. The parent's own formula is excluded.
- Unit of ranking: baselines rank reduced-formula groups, each represented by its lowest-MP-ID record, so a baseline never repeats a formula. Release-4 is scored on its returned records as they come, duplicates included (see Metrics). This difference is disclosed in the results and tested by the duplicate sensitivity analysis.
- Every baseline is scored at the same five-position budget as release-4.
- If the target formula is not in a baseline's candidate list, that baseline's hit for the case is 0.
- B0 uses the probability that the single target group falls in the top k of n eligible groups under uniform ranking: min(k, n)/n, or 0 when the target is ineligible.

**B2 full rule.**

1. Sort Avoid (A) and Prefer (P) alphabetically by element symbol.
2. Enumerate every assignment mapping each element of A to one element of P, repeats allowed, giving |P|^|A| assignments. Order them lexicographically by the tuple of assigned symbols, following A's sorted order.
3. For each assignment, replace each avoided element by its assigned element at the avoided element's coefficient. If the assigned element is already present, from the parent or from another replacement, the coefficients add.
4. Reduce each result to its reduced formula. Keep the first occurrence of any duplicate formula.
5. Keep only formulas present in the dataset. No Prefer-completeness filter is applied, since every Avoid element has already been replaced.
6. The ranked list is the surviving formulas in enumeration order. A list shorter than five leaves the remaining positions empty.

**Why B2 has no avoid-only form.** Without Prefer there is no replacement element. Choosing one (for example, all alkalis) would give the baseline knowledge MaterialGraph does not receive.

**Expected B2 tie (a hypothesis, not an assumption).** In the informed arm on exact-analog cases, release-4 is expected to match B2, because SRQ-01's exact admission is a structured form of the same substitution. This expectation is not built into any analysis step or label. If observed, a tie means release-4 equals trivial substitution on those cases, and any added value must be shown through ranking, grouping or criticality evidence. If not observed, the difference is reported and investigated like any other result.

**B4 dropped.** Release-4 has no objective-blind mode in Objective Explore, and an empty-objective request is not a clean equivalent.

## Metrics

The primary metric is positional Formula Hit@5: the target's reduced formula appears among the first five candidate records release-4 returns, in response order. Duplicate records of one formula each occupy a position; no deduplication is applied, so the metric scores the ranking a user actually sees.

| Metric | Definition | Role |
| --- | --- | --- |
| Positional Formula Hit@5 | Target reduced formula among the first 5 returned records, duplicates occupying positions | Primary |
| Hit@5 on E + I | Positional Formula Hit@5 pooled over all covered, objective-expressible cases | Secondary |
| Unique-formula Hit@5 | Target among the first 5 distinct formulas of the limit-10 response; only if limit equivalence holds | Secondary |
| Target rank | Position of the first record of the target formula; misses recorded as "not returned" | Secondary |
| Reciprocal rank | 1/rank, miss = 0 | Secondary |
| Formula Hit@1 | Target in position 1 | Secondary |
| Formula Hit@10 | Target in top 10 records; only if limit equivalence holds | Secondary |
| Exact-label agreement | Target labelled exact when it is an exact formula analog of the parent | Secondary |
| Coverage fractions | Share of the source cohort in N, X, E and I | Secondary |
| Duplicate rate | Share of returned top-5 positions occupied by a repeated formula | Diagnostic |
| Miss location | For misses: the last stage the target formula group is shown to reach (stages below) | Diagnostic |
| Reproducibility rate | Share of cases passing raw and scientific checks | Integrity |

Within a five-record response, deduplicating cannot change whether the target is present. Unique-formula Hit@5 therefore needs the longer limit-10 response, and is dropped if the limit-equivalence check fails.

If a ten-result response contains fewer than five distinct formulas, unique-formula Hit@5 is interpreted as retrieval within the available ten-record window, not as evidence that no further distinct formula exists beyond it.

A ten-result request can return fewer than ten candidates (pre-check 2b: six and seven in the avoid-only arm), so the actual returned count is reported alongside every Hit@10 and unique-formula Hit@5 value. A target absent from the returned candidates is a miss under the retrieval metric, not evidence that the target is scientifically unsuitable.

**Miss-location stages.** For each miss, record which of these the frozen response establishes, each as yes, no or unknown:

1. Target formula group observed in admission evidence, at any expansion step.
2. Target formula group present in the eligible candidate pool before ranking.
3. Target formula present in the returned top five.

Where the response cannot establish a stage, it is recorded as unknown. A miss is never attributed to rejection or low ranking by inference.

**Recorded per hit.** The MP ID returned for the target group, step depth in the chain, and the representative record. A formula hit does not establish the correct polymorph; NaFePO4, for example, has a four-record group whose records may represent different structures.

**Rank is reported, not just hit.** In Case Study 01, NaFePO4 sat at rank 5 of 5, so Hit@5 is boundary-sensitive.

**Not measured.** There is no precision on non-target results, because no ground truth exists for them. Other returned materials are neither false positives nor discoveries.

## Analysis and interpretation

Each comparison is labelled better, worse or inconclusive by whether a paired 95% interval on the Hit@5 difference excludes zero. At 20–40 cases, inconclusive is the most likely outcome and is a reportable result.

**Main analysis (Q1, Q2).** Report release-4 positional Formula Hit@5 with a 95% Wilson interval. For B1, B2 and B3, report the paired difference in Hit@5, the discordant counts (release-4 hit only; baseline hit only), and a 95% interval from Newcombe's hybrid score method for paired proportions (method 10). That method includes the within-case correlation term; an interval built from two independent Wilson intervals is not used. B0 yields probabilities, not binary hits, so it gets no paired interval: report observed release-4 hits against summed B0 expected hits, descriptively.

**Small or empty cohort.** No minimum cohort size invalidates the study; poor coverage is itself a finding, reported under Q4.

- If E contains zero cases after exclusions, Q1 and Q2 are reported as not estimable. Q1b, Q3 and Q4 are still reported where their cohorts are non-empty.
- If E is small, observed hits and intervals are reported as they are, with an explicit statement that the comparisons have little discriminating power.
- Cases are never added, eligibility is never relaxed, and the denominator is never changed in response to the observed cohort size.

**Pre-registered labels.**

| Label | Rule |
| --- | --- |
| Better | Lower bound of the paired 95% interval above 0 |
| Worse | Upper bound of the paired 95% interval below 0 |
| Inconclusive | Interval includes 0 |

No "similar" or equivalence label is used. With this sample size, any defensible equivalence margin would be too wide to be informative. An inconclusive result is never described as showing no difference.

**Multiplicity.** The three baseline comparisons are reported side by side with unadjusted intervals, labelled as a family. The labels are not family-wise controlled and are never presented as controlled evidence of superiority. No single comparison is promoted after the fact. The B2 tie is a pre-stated expectation, not a test.

**Duplicate sensitivity.** Labels are determined by positional Hit@5, which penalises release-4 for duplicate formulas that baselines cannot produce. If unique-formula Hit@5 is available, the comparisons are repeated on it and any label change is reported. The positional label stands.

**Secondary arms (Q3, Q6).** Same paired method for informed vs balanced avoid-only, interpreted as described under Research questions. Strict avoid-only is reported descriptively only.

**Exact tests.** Exact McNemar p-values may be reported alongside, labelled exploratory. They do not determine any label.

**Family sensitivity (shared-element family proxy).** Each scored directed pair gets a family key F(P, T): the alphabetically sorted set of elements present in both the normalized parent and the normalized target, ignoring stoichiometry. Within each analysis cohort, cases are ordered by their earliest qualifying occurrence (source: Hwang, then Noerochim; then page; then record\_id), and the first case per family key is retained. Selection is done separately per cohort: the primary analysis selects from E after development exclusions, and the E + I analysis selects from E + I, so an I case never displaces an E case from the primary sensitivity analysis. The key is a formula-derived dependence proxy, not a structural or crystallographic family: it cannot distinguish different frameworks with identical element sets. The analysis is a sensitivity check, not a conservative bound; reducing cases can move the observed hit rate in either direction.

**Evidence-source concentration (descriptive).** Report the number of distinct primary studies behind the cohort and the share of cases contributed by the most frequent ones. This addresses evidence-source dependence, which the family sensitivity analysis does not; it is descriptive and determines no label.

**Reporting commitment.** All outcomes, including worse and inconclusive, are published in docs/findings/rrb-01/. The analysis script is committed before runs and executed unmodified.

## Pre-freeze checks, freeze sequence and deviations

Registration happens in two locks: the rules are frozen before any case is extracted, and every case-dependent artifact is frozen before any confirmatory case is run.

### Pre-freeze checks (development cases only)

These use only LiFePO4 → NaFePO4 and Li3Fe2(PO4)3 → Na3Fe2(PO4)3, so the benchmark cohort stays unseen.

- [x] Limit equivalence: passed for both development cases and both arms, in both passes; all 12 rules passed in every comparison (pre-check 2b, 2026-11-06).
- [x] Repeatability: passed; all 16 pinned requests and both historical requests byte-identical on the second run.
- [x] Explicit-field acceptance: passed; all 18 requests HTTP 200 with objective and mode echoed; both historical runs byte-identical to the 2026-11-05 production capture (8b88ed92…).
- [x] Environment equivalence: not applicable; all requests ran against production.

**Pre-check record.**

| Item | Result |
| --- | --- |
| Server code | /opt/materialgraph HEAD = 50dd3eda31bbb1930dcc2782e3ec777af3c35244; no tracked modifications; one untracked leftover virtual environment (`.venv-prev-51b618e`) |
| Backend process | PID 403316, started Thu Nov 5 12:58:17 2026; unchanged before and after the run, so no restart during pre-check 2b |
| Virtual environment | Backend runs from `.venv-ebe10b1`; \`git diff ebe10b1 50dd3ed\` over pyproject.toml and all requirements\* files (including requirements-production.in and .lock) is empty, so dependency specifications are identical; this does not prove the installed packages are identical |
| DC2 parent | 14 records match Li3Fe2(PO4)3; lowest numeric MP-ID mp-6373 (material\_id 1038) used |
| Requests | 1 lookup GET and 18 explore POSTs, all HTTP 200 on first attempt, no retries |
| Procedural deviation | One unapproved GET /health tunnel probe before the matrix; connection reset, no HTTP response reached the API |
| Checker validation | Three deliberately altered values in a copied response were all detected |
| Evidence | C:\\mg-validation\\rrb01-precheck2b-2026-11-06\\ (manifest, raw requests and responses, reports, scripts); to be committed with the protocol |

DC1 historical used the captured Case Study 01 field set; DC1 and DC2 pinned used the benchmark field set; the two were never compared. Avoid-only pools were smaller than 10 candidates (DC1: 6, DC2: 7), so ten-result windows in that arm can hold fewer than ten candidates.

### Freeze sequence

1. **Protocol lock.** Fill every *to be fixed* item in this document except those that depend on the case list. This freezes source selection, extraction criteria, objective derivation, eligibility definitions, baseline specifications, metrics, analysis rules and the rule-reproducibility procedure. Commit to docs/findings/rrb-01/, tag `rrb-01-protocol-lock`, and push to a remote for an external timestamp. An OSF registration is optional.
2. Founder extraction of the source cohort, preserved unchanged.
3. Rule-reproducibility check: fresh AI extraction, preserved comparison, adjudication against the literature, ambiguous cases marked. Then deduplicate the adjudicated qualifying pairs and classify N/X/E/I by script on that list, before the evaluation lock.
4. **Evaluation lock.** Commit the preserved founder extraction, the AI extraction, the adjudication record, the final case list with source references and resolved MP IDs, the request generator, the baseline implementations and the analysis script. Tag `rrb-01-evaluation-lock` and push. The case list need not be public before evaluation, but its SHA-256 hash is recorded in the tag message so it cannot change unnoticed. This is the execution-ready registration.
5. Run all arms twice per request. Store captures and reproducibility results.
6. Run the analysis script unmodified. Commit results and the deviation log.

Any rule change between the two locks is a protocol amendment, logged as a deviation with its reason.

### Deviations

Every departure from this document is logged with date, what changed, why, and which results it affects. Cases may be excluded after freeze only for pre-listed reasons: a request error, or a dataset-resolution mistake found before that case is run. Any other exclusion is a deviation, and the analysis is reported both with and without it.

## Threats to validity and known limitations

The largest threat is that the primary arm hands the system part of the answer through Prefer; the claim is scoped to explicitly specified objectives for that reason.

| Threat | Mitigation or statement |
| --- | --- |
| Hint leakage via Prefer | Primary claim limited to specified objectives; balanced avoid-only reported as secondary |
| Development leakage | Two development pairs excluded from the primary cohort |
| Developer selection bias | Cases from named open-access reviews, full extraction with source locations, pre-registered rule-reproducibility check; no independent eligibility verification, stated |
| Fame bias | Well-known substitutes are more likely to appear in reviews and in MP; hits say little about novel cases |
| Snapshot contains targets | Not a temporal prediction test; stated in scope |
| Small, correlated sample | Interval-based labels, inconclusive expected, one-per-family sensitivity |
| Formula-level matching | Hit@k is a retrieval proxy; no polymorph or structural claim |
| Mode-dependent admission | Arms held at balanced mode; arm difference interpreted as Prefer plus path switch |

**Release-4 limitations, stated as possible causes of misses rather than excuses:**

- Formula-level only: no structure, oxidation states or synthesizability.
- Formula grouping is per step, not global.
- Analogs sharing fewer than 3 elements with the parent are not reachable by direct comparison (e.g. LiMnO2 → NaMnO2); multi-hop reach is not ruled out.
- The lowest-MP-ID representative can be a record without criticality evidence, which can lower a target's rank.
- Dataset of 1,727 materials limits coverage, reported under Q4.

## Deferred scope and open items before freeze

All design items are resolved; one housekeeping item remains before the protocol lock; two studies are deliberately out of scope.

**Deferred to later studies.**

- Pre-SRQ-01 ablation: needs a second environment and build, and would not establish scientific usefulness.
- Scientific relevance review: a blinded expert assessment of whether returned records support the substitution. It needs domain reviewers and is kept separate, never merged with Formula Hit@k into a composite score.

**Open before freeze.**

- [x] Name the review article(s) used as the case source. Resolved: Hwang 2017 and Noerochim 2021.
- [x] Rule for large cohorts. Resolved: complete enumeration, no cap.
- [x] `objective.limit`. Resolved: case C, equal to `request.limit` on the normal path; limit equivalence confirmed at runtime by pre-check 2b.
- [x] Material family for the sensitivity analysis. Resolved: shared-element family proxy, selected per cohort.
- [x] Extraction output schema. Resolved; both source snapshots hashed.
- [x] Pre-freeze checks on development cases. Passed (pre-check 2b, 2026-11-06); see the pre-check record.
- [ ] Before tagging (dependency-file comparison done: specifications identical): commit this document, the pre-check evidence and both source PDFs; verify each committed blob matches its working-tree file and each PDF's SHA-256 matches the recorded value; then tag and push rrb-01-protocol-lock.
