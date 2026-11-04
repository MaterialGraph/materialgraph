# SRQ-01 — S2 Relationship Specification, revision 3.12 (DRAFT for review)

| Field | Value |
|---|---|
| Date | 2026-11-04 |
| Status | **DRAFT rev 3.12 — PR-B1 (#104, #105) and PR-B2 (#106) merged, not deployed; PR-B3 implemented, under review. Production remains on release-3 until PR-B1–B3 are qualified together (S4).** |
| Baseline | S1 finding record, `docs/findings/srq-01/` (PR #93, `f22c6f1`); production `release-2` (`c8c6ed9`) |
| Scope | Objective Investigation (`POST /api/v1/materials/{id}/discovery/objective/explore`) |
| Supersedes | S2 draft rev 3.11 (2026-11-03) |
| Code mapped | `main` at `41e852b` (S2.0) and `c123e49` (PR-B step 0, `pr-b-step0-mapping.md`) |

## Changes from revision 3.11 (PR-B2 AC11 findings, PR-B3 implementation, review)

| Topic | Rule |
|---|---|
| Representative slot (AC11 finding 1) | The representative takes the admission position of the group's earliest member. Which record represents a group never decides whether the group gets a slot (R3) |
| Admitted groups only (AC11 finding 2) | Groups are formed before the expansion cap; only groups whose representative is admitted are kept and reported (R3, D12) |
| Per-step grouping boundary | Grouping applies at each expansion relative to the expanding material. It does **not** guarantee one ranked candidate per formula across an investigation: another record with the same formula can reach the results through a step where it is not an exact analog of the expanding material (most visible when a non-default representative is forced). No global deduplication is applied; the UI must not imply it (R3) |
| Introduced-Avoid pre-check (PR-B3) | An exact-analog group whose representative would introduce an avoided element gets no priority in steps 1 and 3; it remains an ordinary candidate for step 4 and is not listed as excluded (R2) |
| Output order (PR-B3) | Admitted candidates are returned in admission-sequence order (R2) |
| Excluded reason (PR-B3) | A prioritised group not admitted is `efa_budget` if four exact-analog groups were admitted at that expansion, otherwise `cap` (R2, R7.1) |
| Expansion reporting (PR-B3) | `expansions` lists every objective-aware expansion in expansion order, including those with no exact-analog groups; `admission_reporting_available` is `true`; a limitation states that exact analogs are prioritised during exploration without any score change (R7.1) |
| S4 qualification | See section 7 step 6 |

## Changes from revision 3.10 (PR-B step 0 mapping and review)

| Topic | Decision |
|---|---|
| Overflow location (R2 said "search metadata", contradicting the frozen shared schema) | Overflow is reported only in `formula_correspondence.expansions[].excluded`; `DiscoverySearchMetadata` is unchanged (R2) |
| Typing `excluded` | Typed model replaces `list[dict]` within `contract_version` "1": the field has only ever been served empty with `admission_reporting_available: false`, which the contract defines as "not yet reported" (R7.1) |
| Group identity | Groups are keyed by normalised stored composition (fractions equal within TAU); the representative's `pretty_formula` is used for display only, never as a key (R3) |
| `formula_group` scope | Only members of an actual admission group. A source EFA not reached through an admission group has an empty `formula_group`; with the flag `true` this means "not reached through an admission group", never "no other records with this formula" (R3, R7.1) |
| Chain tie key | Lexicographic tuple of numeric MP-ID keys over the chain's ordered materials, source included (R5) |
| General-step ordering | `(-shared element count, MP-ID key)`: MP ID resolves ties only; shared-element priority is unchanged (R2) |
| Composition loading | One bulk query per request, request-scoped; the process-wide composition cache is not used (D11) |
| AC11 data and interpretation | Gate is a local run on the production-equivalent database (4 NaFePO₄ records) with a recorded artifact, plus a synthetic CI regression test. The gate records which outputs change for each representative choice and why; it does not require identical results (AC11) |
| Seven PR-0 xfails | Expected to pass after PR-B1, not required at any cost: any test still failing stays xfail with a documented reason; no permutation test is weakened (AC3, AC4) |
| MP-ID fallback | The unique index on `materials.mp_id` makes duplicates impossible, and all 1,727 production IDs match `^mp-\d+$`, so the local-ID last resort is unreachable on current data; a test must fail if it is ever used for an objective-aware ordering decision (R5) |
| Objective-aware gating | New behaviour is gated by an explicit parameter set from `is_objective_aware`, defaulting off for every frozen caller, because Strict with an empty objective shares the internal admission branch (4.0) |
| PR-B split | B1 ordering; B2 formula groups (AC11 gate); B3 admission sequence (section 7) |

## Changes from revision 3.9

| Review issue | Change |
|---|---|
| R8 and section 7 still said PR-A leaves results identical and all API changes are additive, which contradicts R7.2 | Compatibility contract restated precisely (R8, section 7 step 4) |
| "Not validated" badge beside "Exact formula analog" may read as a contradiction | Recorded as an open presentation item (R8 note); handled as a separate UI change applying to all chain steps, not within SRQ-01 classification |

## Changes from revision 3.8 (PR-A part 3, local visual check, wording consistency)

| Finding | Change |
|---|---|
| Section 3 wording ("Li replaced by Na", "one-alkali replacement") violates the project's existing neutral-alkali wording rule (S-5), which forbids any form of "replac…" in user-facing text; the frontend had no S-5 test | Section 3 user-facing wording rewritten ("alkali metal Li → Na", "single alkali-metal change"). The frontend test suite now enforces the S-5 pattern as well as the section 3 forbidden list. Internal identifiers (`exact_alkali_replacement`, reason codes) are API values and unchanged |
| The ranked-card note said "it is not a returned chain step", which is false when the analog is also in a returned chain (seen in Strict, chain 5) | Note reads "This compares formulas with the starting material directly, independently of the returned chains." |
| Backend reasons still said "different alkali metal (composition not compared)" on compared steps | On objective-aware requests, reasons for classified steps read "Appears in an eligible composition chain containing a step classified as <label>." Unclassified steps and all frozen requests keep existing wording. See R7.2 |
| Reasons describe every step leading to a candidate, so an exact-analog step can appear in a later candidate's reasons | Reason sentence states that the chain *contains a step* so classified; it makes no claim about the candidate itself |
| S-3 guard forbids any mention of `alkali_substitution` in `objective_exploration_service.py` | Reason selection is keyed on the classification lookup, not the transition type; the guard is unchanged |
| Two "not a single alkali-metal change" reasons cannot name the element (the backend does not supply it for those cases) | UI wording names no element for these reasons; they cannot occur on current data |
| Local visual check (2026-11-01, `materialgraph_test_mg_de_007`) | Case Study 01 (limits 5 and 10), Strict Avoid Li, and a frozen Avoid-only request displayed as specified. Not a substitute for S4 production qualification |

Recorded observations, not changed here: the "Not validated" badge appears beside "Exact formula analog" on steps (it refers to structural preservation and mechanism; existing hint explains it); Avoid-only requests return only Li-containing materials because no reserved slots apply (frozen legacy behaviour; candidate follow-up after SRQ-01).

## Changes from revision 3.7 (PR-A part 2 resolutions)

PR-A part 2 (`aafca6e` baseline, `510c2c4` integration) resolved the following points; they are recorded here as required behaviour.

| Point | Rule |
|---|---|
| Applicability of a transition whose composition is unusable | Decided from the transition's recorded element sets using the step 2 rule. If the pair would be compared, it is reported in `transitions` as `not_evaluated` / `formula_unparsed` and the material is listed in `not_evaluated_material_ids`; otherwise it is omitted and not counted as examined |
| Unusable ranked candidate or request source | Always counted as examined by the source-EFA check: listed in `not_evaluated_material_ids`, never in `source_correspondence` |
| R5 key for missing vs non-numeric MP IDs | Numeric IDs first; then missing and non-numeric IDs by string, a missing ID treated as the empty string; then local ID |
| Partial objectives in `is_objective_aware` | Missing objective terms are read as not requested, following the `objective_coverage` precedent |
| Key position | `formula_correspondence` is serialized after `objective_coverage`; on objective-aware requests the served bytes equal the pre-integration baseline with only this key appended |
| `ExpansionEfaCounts.excluded` | Remains `list[dict]` in contract version 1 until PR-B defines its entries; PR-B must type it before `admission_reporting_available` becomes `true`; since the list is always empty until then, typing it does not change any served response, and no `contract_version` change is needed unless an existing non-empty shape changes |

## Changes from revision 3.6 (PR-A part 1 findings)

| Finding | Change |
|---|---|
| A source or candidate with no alkali reached steps 5–6 and got reason codes whose wording does not fit (FePO₄ → NaFePO₄ reported as "candidate still contains Li") | Step 2 extended: if either side has no alkali, no classification is produced. Such pairs are alkali insertion or removal, not replacement, and today's pool rules never place them in `alkali_substitution` transitions |
| Empty composition mappings | Step 1 treats an empty mapping as unusable |
| Step 8 renormalisation | Implementation renormalises after substitution, so non-normalised inputs are handled; recorded as required behaviour |
| Input validation | Classifier trusts `normalise_stored_composition` output; it does not re-validate symbols or amounts |
| Module location | `app/services/material/formula_correspondence.py`, beside `compositions_equal`, to avoid a domain → services dependency |

## Changes from revision 3.5

| Issue | Change |
|---|---|
| Absence from `source_correspondence` could be read as an unperformed comparison | Rule added: only positive source EFAs are listed; meaning of absence defined (R7.1) |
| Section 3 said reason codes are checked "in table order", which contradicted the `ratios_differ` precondition | Replaced by an explicit classification algorithm (section 3) |

## Changes from revision 3.4 (AC13 measurement and S4 scope)

AC13 was measured on 2026-11-01 against the full local dataset (`materialgraph_test_mg_de_007`, 1,727 materials), using the application's own `normalise_stored_composition` and `compositions_equal`. Record: `srq-01-s2-ac13-composition-check-2026-11-01.md`.

| Finding | Change |
|---|---|
| 1,727 of 1,727 stored compositions are usable; 0 failures | AC13 baseline recorded; `not_evaluated` is expected to be rare and arises only from malformed future data |
| Stored-composition elements match `material_elements` for all 1,727 records | Classification basis (stored composition) and candidate-pool basis (element records) agree on current data; PR-A adds a test asserting this for fixtures (AC13) |
| No record contains more than one alkali; no Rb or Cs records | Reason codes `replacement_alkali_in_source`, `replaced_alkali_in_candidate` and `multiple_alkali_changes` cannot occur on current data and are covered by unit tests only. At most 2 EFA groups per source exist today (Li, Na, K), so the D7 budget of 4 is not reached in practice; AC12 overflow tests use synthetic data |
| Rule sanity check on real data: LiFePO₄ (Li→Na) equals all four NaFePO₄ records and not Na₃Fe(PO₄)₂ | Consistent with AC2 expectations |
| Harness used limit 20 and the service layer | S4 runs Case Study 01 at limits 5 and 10 through the HTTP endpoint (AC2) |
| Rev 3.4 status line still read "rev 3.3" | Corrected |

## Changes from revision 3.3 (PR-0 part 2 findings)

PR-0 part 2 (`0364d3b`) confirmed H1 and H2 on the reference data with a local-ID permutation harness: seven strict-xfail invariance tests fail today. Under a reversed permutation, the Case Study 01-style request admits NaFePO₄ (mp-19226) where the baseline does not.

| Finding | Change |
|---|---|
| Tied-chain order decides which chains survive the result limit | R5 explicitly covers selection at the truncation boundary |
| Strict H1 not testable on the reference data (5 eligible candidates, below the cap) | PR-B adds a synthetic case with more than 6 eligible Strict candidates (AC3) |
| No independent Case Study 01 chain-order H2 test, because its chain set depends on H1 | PR-B adds it once H1 is fixed (AC4) |
| Harness relies on transactional DDL | Recorded: the harness assumes a PostgreSQL test database |

## Changes from revision 3.2

| Review issue | Change |
|---|---|
| Strict with an empty objective would gain new behaviour | Frozen; a golden case is added in PR-0 part 2 (4.0, AC6) |
| PR-A cannot truthfully report formula groups | Availability flags added; `formula_group` is empty until PR-B (R7.1) |
| `not_evaluated_material_ids` population undefined | Population, deduplication and ordering defined; unreachable materials excluded (R7.1) |

## Changes from revision 3.1 (PR-0 part 1 findings)

| Finding | Change |
|---|---|
| `objective_service._rank_chains` also serves `/objective/chains` and scientific pathways, frozen under R8 | R5 tie-breaking applies only on objective-aware Objective Explore requests (new 4.0, R5) |
| Objective Explore requests without preferred elements (and hard-Avoid off) take the legacy path and are frozen | New field and all R2–R6 behaviour limited to objective-aware requests; legacy requests omit the field entirely (4.0, R7.1) |
| Strict with an empty objective already uses the objective-aware branch | Classified as objective-aware, in scope of change (4.0) |
| Frozen paths now enumerated by golden tests | R8 and AC6 reference the PR-0 golden suite as the definition of preserved behaviour |

## Changes from revision 3

| Review issue | Change |
|---|---|
| Reachability limits EFA value; Q6 not interpretable without it | Qualification must report "classified" and "unreachable under existing rules" separately; reachability is checked before Q6 is interpreted (2.5, AC5, AC14) |
| R6 "EFA relationship to the source" ambiguous vs per-edge EFA | R6 defines a separate, path-independent **source EFA** classification used only for presentation order (R6) |
| PR-A response contract unspecified | New R7.1 defines an additive, objective-only response object; shared Discovery schemas are not changed (R7.1, AC6) |

## Changes from revision 2.1 (reconciliation with S2.0)

| S2.0 finding | Change |
|---|---|
| Objective path uses element sets only; strict count parsing exists only in search (pymatgen) or as stored-composition fractions | 2.1 redefined on normalised stored-composition fractions with the existing tolerance; no formula-regex or request-path pymatgen use (D8) |
| Admission is cached per expanding material | EFA is defined per edge (expanding material → candidate), not relative to the root source (2.2) |
| A pair enters the pool only with ≥3 shared elements | New 2.5: EFA applies only to pairs already reachable; reachability extension is a separate decision (D9) |
| Introduced-Avoid rejection runs after the cap | R2 corrected: EFA candidates are pre-checked for introduced-Avoid; general behaviour unchanged and recorded as a separate issue (D10) |
| Multi-element "covered" rule in reservations | R2 step 1 adopts the same covered rule; step 2 serves only uncovered elements |
| Admission output is re-sorted into family order | R2 defines output order by the admission sequence; resulting breadth-first changes are expected and covered by AC5/AC8 |
| ID ordering lives in shared `family_service` | R5 places ordering in the objective-path services only (D3 confirmed) |
| MP ID strings do not sort numerically | R5 defines numeric parsing and fallback |
| Family pools come from element sets | R3 notes the expected limited effect of representative choice; AC11 remains a gate |
| No byte-identical no-objective test exists | New PR-0 adds characterization tests before any behaviour change (AC6, section 7) |
| A new transition type would fall into the 0.5 plausibility branch | D1 (additive field) confirmed |

## Changes from revision 2

| Review issue | Change |
|---|---|
| AC11 was informational | AC11 is now a binding decision gate before PR-B merges (section 5). |
| D7 rationale overstated | D7 no longer claims a guaranteed general-exploration slot; multi-alkali sources may have more than four EFA groups (section 6). |
| AC2 implied a guarantee | AC2 stated as an empirical acceptance criterion; failure triggers investigation, not exceptions or scoring changes (section 5). |

## Changes from revision 1

| Review issue | Change |
|---|---|
| 1. EFA admission could exhaust the cap | R2 rewritten as an explicit four-step admission sequence with an EFA budget, preferred-element diversity before extra EFAs, and reporting of EFA groups excluded by the cap (R2, D7). Section 2.4 shows the number of EFA groups is structurally bounded. |
| 2. Representative selection not neutral downstream | R3 separates formula-group membership from record identity: only the representative is traversed and scored, as itself; other members are disclosed but not scored or attributed. New AC11 measures representative sensitivity. |
| 3. R6 and AC8 inconsistent | Distinguishes unchanged scoring algorithms and weights (required everywhere) from unchanged numerical scores (required only where all inputs are identical); other differences must be enumerated with their cause (R6, AC8). |
| 4. Classification edge cases | Retained additional alkalis made explicit (2.2, examples). `composition_differs` replaced by `not_exact_replacement` with a reason code; wording only asserts the demonstrated reason (section 3, AC1). |

S2.0 (read-only code mapping) may be approved independently of this specification (section 7).

## 1. Problem statement

S1 showed that MaterialGraph cannot tell an exact Li→Na formula analog (LiFePO₄ → NaFePO₄) apart from a sodium compound with different stoichiometry (LiFePO₄ → Na₃Fe(PO₄)₂). Both are currently `alkali_substitution` transitions based on element overlap, both receive the same objective rule score, and admission and tie ordering follow local database IDs (S1 hypotheses H1 and H2).

The goal is to make MaterialGraph **recognise a precisely defined formula-level relationship, distinguish it from looser composition relationships, and report the distinction without overclaiming**, while ensuring arbitrary database ordering does not decide which relationships researchers see. Returning NaFePO₄ for Case Study 01 is a consequence to be verified, not the design target.

## 2. Definitions

### 2.1 Reduced composition

A material's composition is its stored element amounts, normalised to fractions summing to 1 (existing `normalise_stored_composition`). Two compositions are equal when every element fraction matches within the existing tolerance (`compositions_equal`, TAU = 1e-6). Normalisation makes scaled formulas equal automatically: Li₂Fe₂P₂O₈ and LiFePO₄ compare equal.

Formula-string regex extraction is never used for EFA, and pymatgen is not imported on the request path (D8). A material whose stored composition is missing or excluded by normalisation is `not_evaluated`.

### 2.2 Exact alkali formula analog (EFA)

Let the alkali set be **{Li, Na, K, Rb, Cs}**. Material C is an **exact alkali formula analog** of material S if and only if there exist alkali metals A ≠ B such that:

1. S contains A, and S does **not** contain B;
2. C contains B, and C does **not** contain A;
3. replacing A with B in S's composition (moving A's amount to B), then normalising, gives a composition equal to C's under 2.1.

All other elements, **including any other alkali metals**, must be present in identical ratios. Exactly one alkali is replaced per relationship. A source containing Li and K can therefore have a Li→Na EFA that retains K (LiKX → NaKX); this is intentional.

**EFA is evaluated per edge**: S is the material being expanded and C its candidate, at every hop. It is not evaluated relative to the root source. This matches the existing per-material admission cache, and keeps the classification a property of the pair (R1).

| Source → Candidate | EFA? | Reason code if not |
|---|---|---|
| LiFePO₄ → NaFePO₄ | Yes | — |
| LiCoO₂ → NaCoO₂ | Yes | — |
| Li₂FeSiO₄ → Na₂FeSiO₄ | Yes | — |
| LiKX → NaKX (K retained) | Yes | — |
| LiFePO₄ → Na₃Fe(PO₄)₂ | No | `ratios_differ` |
| LiFePO₄ → NaFeP₂O₇ | No | `ratios_differ` |
| LiFePO₄ → Na₂FePO₄F | No | `non_alkali_elements_differ` |
| LiNaX → Na₂X | No | `replacement_alkali_in_source` |
| LiFePO₄ → LiNaFe₂(PO₄)₂ | No | `replaced_alkali_in_candidate` |
| LiKX → NaRbX | No | `multiple_alkali_changes` |

### 2.3 What an EFA does and does not establish

An EFA establishes **only** that two reduced formulas correspond under one alkali replacement. It does **not** establish the same crystal structure or framework (the dataset holds no structure data), actual oxidation states, synthesizability, stability, electrochemical behaviour, or that a substitution reaction is possible. Distinct Materials Project IDs with the same reduced formula remain distinct materials.

### 2.4 EFA groups per source are structurally bounded

For a given source and a given pair (A, B), rule 3 determines exactly one reduced formula. So the number of distinct EFA formulas (groups) for a source is at most the number of valid (A, B) pairs:

- source with one alkali: at most **4** groups;
- source with two alkalis: at most **6** groups (2 choices of A × 3 choices of B not in S).

Many records may share one formula (four NaFePO₄ records exist), which is why grouping (R3) matters more than the group count.

### 2.5 Reachability (existing relationship rules unchanged)

Today a pair becomes an `alkali_substitution` candidate only when both materials contain an alkali, their alkali sets differ, and they share at least 3 elements (`MIN_SHARED_ELEMENTS`). Only element sets are compared.

In this correction, EFA classification and priority apply **only to pairs that existing rules already place in the candidate pool**. Pool membership rules are unchanged. Consequence: EFAs sharing fewer than 3 elements are not reachable. Examples: LiCoO₂ → NaCoO₂ and LiMnO₂ → NaMnO₂ each share only 2 elements. They are still classified correctly by the rule function (AC1), but cannot appear in results.

Whether to extend reachability is a separate decision (D9). For Q6 (LiMnO₂), this may be relevant to Issue 3, but that is a hypothesis for the Issue 3 diagnosis, not a conclusion.

This is a **product limitation** and must be disclosed as such. Every qualification report distinguishes:

- EFA relationships **classified** when a pair was evaluated; and
- EFA relationships **unreachable** because existing candidate-generation rules never place the pair in the pool.

No objective result (Q6 in particular) is treated as evidence that EFA admission works or fails until reachability for that source has been checked (AC14).

## 3. Relationship classification

Every alkali-changing relationship returned by Objective Investigation carries one formula-correspondence class and, where applicable, a reason code:

| Class | Reason codes | Required UI wording (draft) |
|---|---|---|
| `exact_alkali_replacement` | — | Step: "Exact formula analog" — "Alkali metal Li → Na; all other element ratios unchanged." Ranked card: "Exact formula analog of LiFePO₄: alkali metal Li → Na; all other element ratios unchanged. This compares formulas with the starting material directly, independently of the returned chains. Structure not assessed." |
| `not_exact_replacement` | `ratios_differ` | "Different alkali metal (not an exact formula analog)" — "Element ratios differ." |
| | `non_alkali_elements_differ` | "… — The materials contain different other elements." |
| | `replacement_alkali_in_source` | "… — Not a single alkali-metal change: the material before this step already contains the new alkali metal." |
| | `replaced_alkali_in_candidate` | "… — Not a single alkali-metal change: the material after this step still contains the original alkali metal." |
| | `multiple_alkali_changes` | "… — More than one alkali metal differs." |
| `not_evaluated` | `formula_unparsed` | "Different alkali metal (formula correspondence not evaluated)" — "Stored composition could not be compared." Ranked card: "Formula correspondence not evaluated." |

All user-facing wording must pass the section 3 forbidden list **and** the S-5 neutral-alkali pattern (no form of "replac…", "mechanism", "substitution candidate", and the other S-5 terms).

**Classification algorithm.** For source S and candidate C, with alkali sets alk(S) and alk(C) over {Li, Na, K, Rb, Cs}:

1. If either stored composition is unusable (missing, or an empty mapping): `not_evaluated` / `formula_unparsed`.
2. If alk(S) = alk(C), or alk(S) or alk(C) is empty: not a one-alkali replacement pair; no classification is produced.
3. Let removed = alk(S) − alk(C) and added = alk(C) − alk(S).
4. If removed or added has more than one element: `multiple_alkali_changes`.
5. Else if removed is empty (an alkali is added while every source alkali remains): `replaced_alkali_in_candidate`.
6. Else if added is empty (an alkali is removed and the remaining alkali was already in the source): `replacement_alkali_in_source`.
7. Otherwise removed = {A} and added = {B}. If the non-alkali-replaced element sets differ (S without A vs C without B): `non_alkali_elements_differ`.
8. Otherwise substitute A→B in S's fractions, renormalise, and compare with C using `compositions_equal`: equal → `exact_alkali_replacement`; unequal → `ratios_differ`.

The classifier trusts its inputs to come from `normalise_stored_composition`; it does not re-validate symbols or amounts.

`replaced_from` and `replaced_to` are set to A and B in steps 7–8, and are `null` otherwise. Each code is reported only when its step is reached, so wording never asserts more than the comparison showed.

`structural_correspondence` is reserved and never emitted in this correction. Other relationship types (e.g. `family_expansion`) are unchanged. Forbidden wording for any class: "validated", "same structure", "equivalent", "drop-in", "substitution mechanism".

## 4. Behaviour requirements

### 4.0 Scope: objective-aware vs frozen requests

A request is **objective-aware** if it is an Objective Explore request with at least one preferred element, or a Strict-mode Objective Explore request with at least one avoided element. Every other request is **frozen**: the Discovery Chains API, `/objective/chains`, scientific pathways, families, candidates, graph endpoints, Objective Explore requests with no preferred elements outside Strict, and **Strict requests with neither avoided nor preferred elements**.

Strict with an empty objective already runs the objective-aware admission branch today. It is frozen in its current behaviour, branch included: new behaviour is gated on the objective-aware definition above, not on the code branch taken.

R2–R7 apply to objective-aware Objective Explore requests only. Frozen requests must produce byte-identical responses, as enforced by the PR-0 golden suite (`tests/api/test_no_objective_golden.py`, 29 cases).

Consequence, disclosed as a limitation: EFA labels and MP-ID ordering are not available on frozen requests in this correction, including Balanced or Exploratory Objective Explore with Avoid only. Extending them is a later decision with a new contract version.

### R1 — Classification is objective-independent
The class and reason are properties of the formula pair alone.

### R2 — Admission sequence at each expansion (addresses SRQ-02, H1)
The per-material cap remains **6**. Constraint handling, as mapped:

- Strict hard-Avoid already excludes candidates before the cap; unchanged.
- Introduced-Avoid rejection currently happens **after** admission, at transition validation, so rejected candidates can occupy slots. In this correction, **EFA candidates only** are checked for introduced avoided elements before steps 1 and 3, so an EFA that would be rejected never uses an EFA slot. General-step behaviour is unchanged; the post-cap slot waste is recorded as a separate issue (D10).

Eligible candidates are then admitted in this order, stopping when 6 slots are filled:

1. **Preferred EFA step.** For each preferred element in the existing alphabetical order, if it is not yet covered, admit the first eligible EFA group containing it. Using the existing covered rule, a group containing several preferred elements covers all of them.
2. **Preferred reservation step.** For each preferred element still uncovered, apply the existing reservation behaviour (first eligible candidate in the R5 order, covered rule, no backfill; Issue 6 remains separate).
3. **Remaining EFA step.** Admit other eligible EFA groups until the total number of admitted EFA groups at this expansion reaches the **EFA budget of 4** (D7).
4. **General step.** Fill remaining slots ordered by `(-shared element count, MP-ID key)`: today's shared-element priority, with the MP ID replacing local ID as the tie-break.

Within each step, EFA groups are ordered by the numeric MP ID of their representative (R3). **Output order** is the admission order defined by these steps; the current re-sort into family order is removed on the objective path. Because breadth-first queue order follows admission order, chains generated may change; this is expected and covered by AC5 and AC8. Steps 1–2 precede step 3, so preferred-element diversity is never displaced by extra EFAs. With the bound in 2.4, single-alkali sources can never exceed the EFA budget; two-alkali sources can, and the excess is reported as overflow. No slot is guaranteed for the general step.

**Overflow reporting.** Any eligible EFA group not admitted (cap reached or budget reached) is listed in `formula_correspondence.expansions[].excluded` (never in the shared, frozen `search_metadata`) with its display formula, member MP IDs, the expansion at which it was excluded, and the reason (`cap` or `efa_budget`).

### R3 — Formula groups separate membership from record identity
- EFA records are grouped by **normalised stored composition** (fractions equal within TAU, as in 2.1). Each group occupies **one** admission slot. The representative's `pretty_formula` is the group's display label only, never its key.
- Exactly one **representative** record per group is traversed and scored. Its scores use **its own record data** (energy above hull, material quality, neighbours). They are reported as that record's scores, never as the group's.
- The representative is the record with the lowest numeric MP ID, chosen by a single function (`choose_representative`): a reproducibility convention, **not** a scientific preference. User-facing text where groups are shown must say so.
- Other members are disclosed with their MP IDs and their own energy above hull, labelled "Same formula; not traversed or scored; structure not distinguished."
- No text, score or label presents members as scientifically equivalent to the representative.
- `formula_group` lists only members of the admission group a candidate came from. A source EFA reached through a non-EFA step has an empty `formula_group`; once `formula_grouping_available` is `true`, the report limitations state that an empty group means "not reached through an admission group", not "no other records with this formula".
- Expected effect (from S2.0, to be confirmed by AC11): family pools are built from element sets, so records sharing a formula should have the same candidate neighbourhood. Representative choice is then expected to affect mainly the chain usefulness score's material-quality component (stability evidence), not traversal. The objective rule score does not use energy above hull.

### R4 — Reserved preferred slots
As defined in R2 steps 1–2. A preferred element served by an EFA group receives no additional reserved slot at that expansion.

### R5 — Stable ordering (addresses H1 and H2 separately)
Within the objective path, every ordering that currently falls back to local database ID uses the numeric MP ID instead: (a) admission ordering, and (b) ordering of equally scored ranked chains and candidates. Each is changed and tested independently.

- **Where:** only on objective-aware Objective Explore requests (4.0): the `chain_service` objective-aware branch and `objective_exploration_service._rank_candidates_from_chains`. `objective_service._rank_chains` is shared with frozen endpoints, so the MP-ID tie-break must be applied only when called for an objective-aware explore request (e.g. by an explicit parameter defaulting to current behaviour). `family_service` ordering is **not** changed (D3).
- **Truncation:** because results are cut to the request limit after sorting, the R5 order also decides *which* equally scored chains and candidates are returned at the limit boundary. R5 covers that selection, not only display order.
- **Chain tie key:** the lexicographic tuple of MP-ID keys over the chain's ordered materials, source included.
- **Fallback reachability:** `materials.mp_id` has a unique index and all production IDs match the pattern, so the local-ID last resort below is unreachable on current data; a test must fail if any objective-aware ordering decision uses it.
- **MP-ID key:** parse `^mp-(\d+)$` to an integer. Records with a missing or non-matching MP ID sort after all numeric IDs, by MP ID string, then by local ID as a last, documented fallback.

### R6 — Scoring algorithms unchanged; presentation order documented
- Scoring **algorithms, formulas and weights** are unchanged; no scoring constant or function changes in this correction.
- Numerical scores may still change where their **inputs** change (for example a different admitted path or a different bottleneck material). Such changes are legitimate only if enumerated with their cause (AC8).
- Among candidates with equal objective rule scores, presentation order is: **source EFA** first, then numeric MP ID. This is an ordering rule, not a claim that an EFA is a better material.
- **Source EFA (definition):** a ranked candidate whose composition is an exact alkali replacement (2.2) of the **original request's source material**, regardless of the path by which it was reached. It is computed separately from per-edge classification, and it does not alter traversal eligibility, admission or scoring.
- Per-edge EFA (2.2) labels transitions and drives admission (R2). Source EFA labels ranked candidates and drives tie presentation only. A candidate reached through an EFA edge at hop 2 is not a source EFA unless it independently meets 2.2 against the source.

### R7 — Disclosure
Each classified transition and each source EFA states its class, reason, the replaced alkali (A→B) where defined, group members (R3) and the limitation in 2.3. Counts per expansion of EFA groups found, admitted and excluded (with reasons, per R2) are reported. All of this uses the contract in R7.1.

### R7.1 — Response contract (additive, objective-only)

Shared schemas in `app/schemas/discovery.py` (`DiscoveryChainTransition`, `DiscoveryChain`, `DiscoverySearchMetadata`) are **not changed**, because they are also served by the Discovery Chains API and no-objective requests. Following the existing `objective_coverage` pattern, `ResearchObjectiveExplorationResponse` gains one new top-level field:

```python
CorrespondenceClass = Literal["exact_alkali_replacement", "not_exact_replacement", "not_evaluated"]
CorrespondenceReason = Literal["ratios_differ", "non_alkali_elements_differ",
    "replacement_alkali_in_source", "replaced_alkali_in_candidate",
    "multiple_alkali_changes", "formula_unparsed"]

class FormulaCorrespondence(BaseModel):
    correspondence_class: CorrespondenceClass
    reason: CorrespondenceReason | None          # None only for exact_alkali_replacement
    replaced_from: str | None                    # e.g. "Li"; None when not a single replacement
    replaced_to: str | None                      # e.g. "Na"

class TransitionCorrespondence(BaseModel):       # one per alkali-changing transition
    chain_position: int                          # 1-based position in `chains`
    transition_index: int                        # 0-based index in chain.transitions
    from_material_id: int; to_material_id: int
    correspondence: FormulaCorrespondence

class FormulaGroupMember(BaseModel):
    material_id: int; mp_id: str | None
    energy_above_hull: float | None
    traversed: bool                              # True only for the representative

class CandidateSourceCorrespondence(BaseModel):  # only ranked candidates that ARE source EFAs (see rules)
    candidate_rank: int                          # 1-based position in `ranked_candidates`
    material_id: int
    correspondence: FormulaCorrespondence
    formula_group: list[FormulaGroupMember]

class ExpansionEfaCounts(BaseModel):
    expanded_material_id: int
    groups_found: int; groups_admitted: int
    excluded: list[ExcludedEfaGroup]             # PR-B3; was list[dict], always served empty while the flag was false

# class ExcludedEfaGroup(BaseModel):
#     display_formula: str; member_mp_ids: list[str]; reason: Literal["cap", "efa_budget"]

class FormulaCorrespondenceReport(BaseModel):
    contract_version: Literal["1"] = "1"
    basis: Literal["stored_composition_fractions"] = "stored_composition_fractions"
    tolerance: float = 1e-6
    transitions: list[TransitionCorrespondence]
    source_correspondence: list[CandidateSourceCorrespondence]
    expansions: list[ExpansionEfaCounts]
    formula_grouping_available: bool             # False in PR-A
    admission_reporting_available: bool          # False in PR-A
    not_evaluated_material_ids: list[int]        # population defined in rules below
    not_evaluated_count: int
    limitations: list[str]                       # includes 2.3 and 2.5 statements

# ResearchObjectiveExplorationResponse gains: formula_correspondence: FormulaCorrespondenceReport
```

Rules:
- Emitted on every **objective-aware** Objective Explore response (always present there, possibly with empty lists).
- **`source_correspondence` lists only ranked candidates positively classified as `exact_alkali_replacement` against the original source.** Other ranked candidates are omitted; the list is not a complete classification of all ranked candidates. A ranked candidate that is absent from `source_correspondence` and absent from `not_evaluated_material_ids` was compared and is not a source EFA. A candidate listed in `not_evaluated_material_ids` could not be compared.
- On frozen requests (4.0) the key is **absent**, not `null`, so their bytes are unchanged. Never emitted by any other endpoint.
- **Availability flags.** The report carries `formula_grouping_available: bool` and `admission_reporting_available: bool`. Both are `false` in PR-A, where every `formula_group` is an empty list and `expansions` is an empty list. PR-B sets them to `true` when R3 grouping and R2 admission reporting exist. An empty list with a `false` flag means "not yet reported", never "no members" or "nothing excluded". The UI must not display group or admission information while the flag is `false`.
- **`not_evaluated_material_ids`.** The unique material IDs whose stored composition was actually examined during the request (for per-edge classification of an alkali-changing pair, or for the source-EFA check of a ranked candidate) and could not be normalised. Each ID appears once; the list is ordered by the R5 MP-ID key. Materials never examined, including those outside the reachable pool (2.5), are **not** listed. A companion `not_evaluated_count` equals the list length.
- `transitions` lists only alkali-changing transitions; other transitions are omitted, not marked.
- `not_evaluated` entries are always serialized, never dropped.
- Field names are final once PR-A merges; later changes require a new `contract_version`.
- In PR-A, `expansions` is present with empty lists; PR-B populates it.

### R7.2 — Reasons wording on objective-aware requests

On objective-aware Objective Explore requests, each alkali-changing step in the eligible chains is classified per edge (same rules as the report's `transitions`) before candidate reasons are built. For a classified step the reason reads "Appears in an eligible composition chain containing a step classified as <label>.", where <label> is "exact formula analog (alkali metal A → B; all other element ratios unchanged)", "different alkali metal (element ratios differ)", "different alkali metal (other elements differ)", "different alkali metal (not a single alkali-metal change)" or "different alkali metal (formula correspondence not evaluated)". Unclassified steps keep "…with relationship type <label>." Frozen requests are unchanged. Scores, ranking, ordering and truncation are unaffected.

The objective-aware snapshots under `srq01_pra/` were deliberately updated for this (commits `f6bd646`, `3326e51`): full snapshots regenerated; pre-integration baselines derived as the full snapshot up to the appended `formula_correspondence` key; structural diff confirmed that only `ranked_candidates[*].reasons` changed. The original PR-A2 proof that the report changed nothing else remains recorded at `aafca6e`.

### R8 — Preserved behaviour
Compatibility contract after PR-A:

- **Frozen requests (4.0):** byte-identical responses, as defined by the PR-0 golden suite.
- **Objective-aware requests:** candidate identity, chain identity, scores, ranking, ordering and truncation are preserved. Candidate `reasons` strings may change, and only as defined in R7.2.
- **`formula_correspondence`:** additive, present only on objective-aware requests.
- Existing fields otherwise keep their meaning. Relationship-type weights are unchanged (D5).

Open presentation item (not part of this contract): the existing "Not validated" badge on chain steps refers to structural preservation and mechanism, and can read as contradicting "Exact formula analog". Any relabelling applies to every chain step consistently and is reviewed as a separate UI change.

## 5. Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| AC1 | Unit tests for every row of the 2.2 table, including the retained-K EFA and every reason code; reduction (Li₂Fe₂P₂O₈ ≡ LiFePO₄); malformed formula → `not_evaluated` | Tests written and failing before implementation |
| AC2 | Case Study 01 (S1 request) at **limits 5 and 10**, through the HTTP endpoint: a NaFePO₄ group is returned as a one-step `exact_alkali_replacement` from LiFePO₄, appears in the top five at limit 5, and lists all members once grouping is available; Na₃Fe(PO₄)₂ is `not_exact_replacement` / `ratios_differ` | Production-equivalent HTTP captures compared with the S1 baseline responses |
| AC3 | H1: permuting local IDs in a test database does not change admitted candidates (compared by MP ID, class and reason) | PR-0 strict-xfail tests turn into passes (markers removed deliberately); PR-B adds a synthetic Strict case with more than 6 eligible candidates |
| AC4 | H2: permuting local IDs does not change the order, or truncation-boundary selection, of equally scored candidates and chains | PR-0 strict-xfail tests turn into passes; PR-B adds a Case Study 01 chain-order test once H1 is fixed |
| AC5 | Anti-overfitting: frozen multi-objective baseline (including Q6) re-run; every difference listed and explained; no objective-specific exception exists | Before/after artifact |
| AC6 | All PR-0 golden cases, including Strict with an empty objective, pass unchanged without regeneration; shared schemas unchanged; the new field appears only on objective-aware Objective Explore responses and is absent (not null) elsewhere | Characterization tests added in PR-0, passing unchanged through PR-A and PR-B; schema serialization tests for presence and absence |
| AC7 | Balanced, Strict and Exploratory semantics unchanged; an EFA introducing an avoided element is rejected before admission | Mode tests |
| AC8 | (a) No change to scoring functions, formulas or weights (code diff). (b) Scores identical for every material and chain whose scoring inputs are identical in baseline and new results. (c) Every other score difference enumerated with its cause | Score diff artifact on frozen baselines |
| AC9 | All new user-facing text reviewed against 2.3, section 3 wording and the forbidden list | Copy review in the PR |
| AC10 | Case Study 01 latency not materially worse than baseline (~10 s) | Timed production qualification |
| AC11 | **Gate (PR-B2).** Representative sensitivity: on the production-equivalent local database, Case Study 01 is run once with each NaFePO₄ record forced as representative (test-only monkeypatch of `choose_representative`, nothing exposed in the API); every difference in traversal, candidates, chains and scores is recorded with its cause. A synthetic CI test covers the mechanism | Sensitivity artifact under `docs/findings/srq-01/`, reviewed before PR-B2 merges |
| AC14 | For every qualification objective, reachability of each EFA the dataset holds for that source is checked first; results report classified vs unreachable separately | Reachability table in each qualification record |
| AC13 | EFA identity uses stored composition only; materials without usable composition are `not_evaluated` and counted in the report; stored-composition elements match `material_elements` for test fixtures | Unit tests; baseline measured 2026-11-01: 1,727/1,727 usable, 0 element mismatches |
| AC12 | Admission sequence: tests for (i) EFA serving a preferred element, (ii) preferred element without EFA, (iii) EFA groups exceeding budget, (iv) cap reached during step 3, each verifying overflow reporting | Unit tests |

For Q6 (LiMnO₂, Avoid Li, Prefer Na), the result is observed, not targeted; whether a Na–Mn–O EFA exists in the dataset is recorded before the run. Issue 3's diagnosis stays separate.

**AC2 is empirical, not guaranteed.** R6 keeps scoring unchanged, so admission priority and the tie rule cannot guarantee that an EFA reaches the top five if other candidates legitimately score higher. For the frozen Case Study 01 baseline, NaFePO₄ scored 115.0, tied with the candidates it should precede, so the tie rule is expected to suffice if its score stays comparable. If AC2 fails, the cause is investigated and recorded; no objective-specific exception is added and scoring is not changed within this correction.

**AC11 is a binding gate.** PR-B2 may not merge until AC11 has been run and reviewed. Identical results are **not** required: the four NaFePO₄ records have different stability evidence, so chain usefulness scores and possibly traversal may legitimately differ. The gate passes when every difference is recorded, explained and reviewed. If a representative choice changes outcomes in a way that cannot be explained, D2 is revised and re-reviewed before merge.

**AC3/AC4 expectation.** The seven PR-0 strict xfails are expected to pass after PR-B1. Any that still fail remain xfail with a documented reason; no permutation test is weakened to pass.

## 6. Decisions for review

| ID | Question | Recommendation |
|---|---|---|
| D1 | New transition type vs additive field | Additive `formula_correspondence` (class + reason) on alkali-changing transitions; keep `alkali_substitution` as the type. Confirmed by S2.0: a new type would hit the 0.5 plausibility branch and eight special cases |
| D2 | Representative per formula group | Lowest numeric MP ID, documented convention; revisit if AC11 shows material sensitivity, and once structure data exists |
| D3 | Scope of MP-ID ordering (R5) | Objective path only, implemented in objective-path services, not `family_service`; global ordering as a separate issue |
| D4 | Tie presentation (R6) | EFA first among equal scores, then MP ID; no scoring change |
| D5 | `not_exact_replacement` keeps 17/20 relationship-type weighting | Unchanged here; separate issue, since weight changes alter scoring |
| D6 | Alkali set | {Li, Na, K, Rb, Cs}; H and Fr excluded |
| D8 | Composition source for EFA | Stored composition via `normalise_stored_composition` and `compositions_equal`; not formula regex, not request-path pymatgen |
| D9 | Extend reachability to EFAs sharing fewer than 3 elements | Out of scope here; separate issue, since it changes pool membership for all relationships |
| D10 | Introduced-Avoid rejection after the cap (general candidates) | Unchanged here; separate issue. EFAs are pre-checked (R2) |
| D11 | Composition source during admission | One bulk, request-scoped query of stored compositions, normalised with `normalise_stored_composition`; the process-wide composition cache is not used (its fingerprint does not detect ID permutations) |
| D12 | `formula_group` scope | Admission-group members only; empty for source EFAs not reached through an admission group, with that meaning stated in the limitations |
| D7 | EFA budget per expansion | 4 groups. This limits formula-analog admission while reserving capacity for other admission categories where eligible candidates exist. It admits every EFA group of a single-alkali source; two-alkali sources may exceed it (overflow reported). On current data no source has more than 2 EFA groups, so the budget is exercised only by synthetic tests. It does **not** guarantee a general-exploration slot; preferred-element reservations keep priority under R2. |

## 7. Implementation sequence (each step separately approved)

1. **S2.0, read-only mapping** — done at `41e852b`; reconciled in this revision.
2. **Local data checks (owner, no code change)** — confirm all production-dataset MP IDs match `^mp-\d+$`; identify the fourth NaFePO₄ record; count records with usable stored composition (AC13).
3. **PR-0, characterization tests only** — byte-identical no-objective golden tests and a local-ID permutation harness for AC3/AC4. No behaviour change.
4. **PR-A, classification only** — rule, the R7.1 contract (`transitions`, `source_correspondence`, empty `expansions`), disclosure text, tests (AC1, AC6, AC9, AC13). Candidate sets, chains, scores, ranking, ordering and truncation unchanged; objective-aware `reasons` change only per R7.2 (added after PR-A3).
5. **PR-B, in three separately approved PRs** (frozen golden cases unchanged throughout; objective-aware snapshot changes regenerated deliberately with a diff artifact each time):
   - **PR-B1, ordering:** objective-aware gating parameter; MP-ID tie key in admission (no R2 steps yet); ranked-candidate ties (source EFA first, then MP ID); chain tie key in `_rank_chains` via a parameter that frozen callers never pass. Tests: PR-0 xfails (AC3, AC4), synthetic Strict H1 case with more than 6 eligible candidates, Case Study 01 chain-order test, fallback-unreachable test.
   - **PR-B2, formula groups:** request-scoped composition load (D11); per-edge EFA at admission; grouping and `choose_representative`; `formula_group` and `formula_grouping_available`. Gate: AC11.
   - **PR-B3, admission sequence:** R2 four steps; EFA budget 4; introduced-Avoid pre-check for EFAs; typed `expansions`/`excluded` and `admission_reporting_available`. Tests: AC7, AC12, AC5/AC8 diff artifact.
6. **S4 qualification** (after PR-B1–B3, before release). Production and production-equivalent results are recorded and labelled separately; direct LiFePO₄ → NaFePO₄ admission is verified at Case Study 01 limits 5 and 10; candidate identities, scores and returned chains are inspected, not only whether NaFePO₄ appears; every change from release-3 is attributed to ordering (B1), grouping (B2) or admission (B3); frozen behaviour is verified byte-identical. Original text: — frozen captures before and after, AC2, AC5, AC10 on production-equivalent data, and a production qualification record under `docs/findings/srq-01/`.

## 8. Out of scope

Structure import and polymorph distinction; oxidation-state computation in the application; scoring weight changes; raising the per-material cap; dataset growth; the reserved-slot backfill decision (Issue 6); Q6 downstream diagnosis (Issue 3); ML-based ranking.
