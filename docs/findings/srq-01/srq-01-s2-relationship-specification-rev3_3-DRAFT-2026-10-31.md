# SRQ-01 — S2 Relationship Specification, revision 3.3 (DRAFT for review)

| Field | Value |
|---|---|
| Date | 2026-10-31 |
| Status | **DRAFT rev 3.3 — working specification for PR-0; PR-A and PR-B not approved.** |
| Baseline | S1 finding record, `docs/findings/srq-01/` (PR #93, `f22c6f1`); production `release-2` (`c8c6ed9`) |
| Scope | Objective Investigation (`POST /api/v1/materials/{id}/discovery/objective/explore`) |
| Supersedes | S2 draft rev 3.2 (same date) |
| Code mapped | `main` at `41e852b` (S2.0 read-only mapping report) |

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
| `exact_alkali_replacement` | — | "Exact formula analog: Li replaced by Na; all other element ratios unchanged. Structure not assessed." |
| `not_exact_replacement` | `ratios_differ` | "Different alkali metal; element ratios differ." |
| | `non_alkali_elements_differ` | "Different alkali metal; the materials contain different other elements." |
| | `replacement_alkali_in_source` | "Not compared as a one-alkali replacement: the source already contains Na." |
| | `replaced_alkali_in_candidate` | "Not compared as a one-alkali replacement: the candidate still contains Li." |
| | `multiple_alkali_changes` | "More than one alkali metal changes; not a one-alkali replacement." |
| `not_evaluated` | `formula_unparsed` | "Formula correspondence not evaluated." |

Reason codes are evaluated in the table order above; the first that applies is reported, so wording never asserts more than the comparison showed. In particular, `ratios_differ` is reported only when the alkali conditions hold and the other elements match, and the substituted ratios were compared and found unequal.

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
4. **General step.** Fill remaining slots in the existing order, with the R5 tie-break.

Within each step, EFA groups are ordered by the numeric MP ID of their representative (R3). **Output order** is the admission order defined by these steps; the current re-sort into family order is removed on the objective path. Because breadth-first queue order follows admission order, chains generated may change; this is expected and covered by AC5 and AC8. Steps 1–2 precede step 3, so preferred-element diversity is never displaced by extra EFAs. With the bound in 2.4, single-alkali sources can never exceed the EFA budget; two-alkali sources can, and the excess is reported as overflow. No slot is guaranteed for the general step.

**Overflow reporting.** Any eligible EFA group not admitted (cap reached or budget reached) is listed in search metadata with its formula, member MP IDs, the expansion at which it was excluded, and the reason (`cap` or `efa_budget`).

### R3 — Formula groups separate membership from record identity
- EFA records are grouped by reduced formula. Each group occupies **one** admission slot.
- Exactly one **representative** record per group is traversed and scored. Its scores use **its own record data** (energy above hull, material quality, neighbours). They are reported as that record's scores, never as the group's.
- The representative is the record with the lowest numeric MP ID: a documented convention, **not** a scientific preference.
- Other members are disclosed with their MP IDs and their own energy above hull, labelled "Same formula; not traversed or scored; structure not distinguished."
- No text, score or label presents members as scientifically equivalent to the representative.
- Expected effect (from S2.0, to be confirmed by AC11): family pools are built from element sets, so records sharing a formula should have the same candidate neighbourhood. Representative choice is then expected to affect mainly the chain usefulness score's material-quality component (stability evidence), not traversal. The objective rule score does not use energy above hull.

### R4 — Reserved preferred slots
As defined in R2 steps 1–2. A preferred element served by an EFA group receives no additional reserved slot at that expansion.

### R5 — Stable ordering (addresses H1 and H2 separately)
Within the objective path, every ordering that currently falls back to local database ID uses the numeric MP ID instead: (a) admission ordering, and (b) ordering of equally scored ranked chains and candidates. Each is changed and tested independently.

- **Where:** only on objective-aware Objective Explore requests (4.0): the `chain_service` objective-aware branch and `objective_exploration_service._rank_candidates_from_chains`. `objective_service._rank_chains` is shared with frozen endpoints, so the MP-ID tie-break must be applied only when called for an objective-aware explore request (e.g. by an explicit parameter defaulting to current behaviour). `family_service` ordering is **not** changed (D3).
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

class CandidateSourceCorrespondence(BaseModel):  # one per ranked candidate that is a source EFA
    candidate_rank: int                          # 1-based position in `ranked_candidates`
    material_id: int
    correspondence: FormulaCorrespondence
    formula_group: list[FormulaGroupMember]

class ExpansionEfaCounts(BaseModel):
    expanded_material_id: int
    groups_found: int; groups_admitted: int
    excluded: list[dict]                         # formula, member mp_ids, reason: "cap" | "efa_budget"

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
- On frozen requests (4.0) the key is **absent**, not `null`, so their bytes are unchanged. Never emitted by any other endpoint.
- **Availability flags.** The report carries `formula_grouping_available: bool` and `admission_reporting_available: bool`. Both are `false` in PR-A, where every `formula_group` is an empty list and `expansions` is an empty list. PR-B sets them to `true` when R3 grouping and R2 admission reporting exist. An empty list with a `false` flag means "not yet reported", never "no members" or "nothing excluded". The UI must not display group or admission information while the flag is `false`.
- **`not_evaluated_material_ids`.** The unique material IDs whose stored composition was actually examined during the request (for per-edge classification of an alkali-changing pair, or for the source-EFA check of a ranked candidate) and could not be normalised. Each ID appears once; the list is ordered by the R5 MP-ID key. Materials never examined, including those outside the reachable pool (2.5), are **not** listed. A companion `not_evaluated_count` equals the list length.
- `transitions` lists only alkali-changing transitions; other transitions are omitted, not marked.
- `not_evaluated` entries are always serialized, never dropped.
- Field names are final once PR-A merges; later changes require a new `contract_version`.
- In PR-A, `expansions` is present with empty lists; PR-B populates it.

### R8 — Preserved behaviour
Frozen requests (4.0) produce byte-identical responses, as defined by the PR-0 golden suite. Existing fields keep their meaning; all API changes are additive. Relationship-type weights are unchanged (D5).

## 5. Acceptance criteria

| ID | Criterion | Evidence |
|---|---|---|
| AC1 | Unit tests for every row of the 2.2 table, including the retained-K EFA and every reason code; reduction (Li₂Fe₂P₂O₈ ≡ LiFePO₄); malformed formula → `not_evaluated` | Tests written and failing before implementation |
| AC2 | Case Study 01 (S1 request, limit 5): a NaFePO₄ group is returned as a one-step `exact_alkali_replacement` from LiFePO₄, appears in the top five and lists all members; Na₃Fe(PO₄)₂ is `not_exact_replacement` / `ratios_differ` | Production-equivalent capture compared with S1 baseline |
| AC3 | H1: permuting local IDs in a test database does not change admitted candidates (compared by MP ID, class and reason) | Controlled test |
| AC4 | H2: permuting local IDs does not change the order of equally scored candidates | Controlled test, separate from AC3 |
| AC5 | Anti-overfitting: frozen multi-objective baseline (including Q6) re-run; every difference listed and explained; no objective-specific exception exists | Before/after artifact |
| AC6 | All PR-0 golden cases, including Strict with an empty objective, pass unchanged without regeneration; shared schemas unchanged; the new field appears only on objective-aware Objective Explore responses and is absent (not null) elsewhere | Characterization tests added in PR-0, passing unchanged through PR-A and PR-B; schema serialization tests for presence and absence |
| AC7 | Balanced, Strict and Exploratory semantics unchanged; an EFA introducing an avoided element is rejected before admission | Mode tests |
| AC8 | (a) No change to scoring functions, formulas or weights (code diff). (b) Scores identical for every material and chain whose scoring inputs are identical in baseline and new results. (c) Every other score difference enumerated with its cause | Score diff artifact on frozen baselines |
| AC9 | All new user-facing text reviewed against 2.3, section 3 wording and the forbidden list | Copy review in the PR |
| AC10 | Case Study 01 latency not materially worse than baseline (~10 s) | Timed production qualification |
| AC11 | **Gate.** Representative sensitivity: in a test environment, Case Study 01 is run once with each NaFePO₄ group member forced as representative; differences in traversal, candidates and scores are recorded and reviewed before PR-B merges | Sensitivity artifact; test-only mechanism not exposed in the API |
| AC14 | For every qualification objective, reachability of each EFA the dataset holds for that source is checked first; results report classified vs unreachable separately | Reachability table in each qualification record |
| AC13 | EFA identity uses stored composition only; materials without usable composition are `not_evaluated` and counted in search metadata | Unit tests; dataset coverage count recorded before PR-A |
| AC12 | Admission sequence: tests for (i) EFA serving a preferred element, (ii) preferred element without EFA, (iii) EFA groups exceeding budget, (iv) cap reached during step 3, each verifying overflow reporting | Unit tests |

For Q6 (LiMnO₂, Avoid Li, Prefer Na), the result is observed, not targeted; whether a Na–Mn–O EFA exists in the dataset is recorded before the run. Issue 3's diagnosis stays separate.

**AC2 is empirical, not guaranteed.** R6 keeps scoring unchanged, so admission priority and the tie rule cannot guarantee that an EFA reaches the top five if other candidates legitimately score higher. For the frozen Case Study 01 baseline, NaFePO₄ scored 115.0, tied with the candidates it should precede, so the tie rule is expected to suffice if its score stays comparable. If AC2 fails, the cause is investigated and recorded; no objective-specific exception is added and scoring is not changed within this correction.

**AC11 is a binding gate.** PR-B may not merge until AC11 has been run and reviewed. If representative choice materially changes traversal, candidates or scores, D2 must be revised and re-reviewed first.

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
| D7 | EFA budget per expansion | 4 groups. This limits formula-analog admission while reserving capacity for other admission categories where eligible candidates exist. It admits every EFA group of a single-alkali source; two-alkali sources may exceed it (overflow reported). It does **not** guarantee a general-exploration slot; preferred-element reservations keep priority under R2. |

## 7. Implementation sequence (each step separately approved)

1. **S2.0, read-only mapping** — done at `41e852b`; reconciled in this revision.
2. **Local data checks (owner, no code change)** — confirm all production-dataset MP IDs match `^mp-\d+$`; identify the fourth NaFePO₄ record; count records with usable stored composition (AC13).
3. **PR-0, characterization tests only** — byte-identical no-objective golden tests and a local-ID permutation harness for AC3/AC4. No behaviour change.
4. **PR-A, classification only** — rule, the R7.1 contract (`transitions`, `source_correspondence`, empty `expansions`), disclosure text, tests (AC1, AC6, AC9, AC13). Results otherwise identical.
5. **PR-B, admission and ordering** — R2–R6 with tests first (AC3, AC4, AC7, AC8, AC11, AC12).
6. **S4 qualification** — frozen captures before and after, AC2, AC5, AC10 on production-equivalent data, and a production qualification record under `docs/findings/srq-01/`.

## 8. Out of scope

Structure import and polymorph distinction; oxidation-state computation in the application; scoring weight changes; raising the per-material cap; dataset growth; the reserved-slot backfill decision (Issue 6); Q6 downstream diagnosis (Issue 3); ML-based ranking.
