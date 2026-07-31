# MaterialGraph Change Impact History

This document is the concise chronological record of externally meaningful
scientific, scoring, explanation, and API behavior changes made through the
MaterialGraph audit.

It does not contain root-cause analysis, file-level implementation details,
complete tests, or full production responses. Those belong in
`MATERIALGRAPH_AUDIT_RESOLUTION.md`. The canonical finding status remains in
`MaterialGraph_Architecture_Implementation_Audit_v2_Regenerated.md`.

`Production verified` means the listed behavior was observed on the deployed
version for the recorded request and dataset. It does not imply exhaustive
edge-case coverage or independent scientific validation.

## Impact legend

- **Scientific result:** computed scientific values or conclusions changed.
- **Ranking:** candidate or pathway order may change.
- **API contract:** response fields or serialized values changed.
- **Data migration:** stored data required recalculation or backfill.

---

## Composition-aware criticality weighting

Related findings: MG-AUD-001  
Release reference: v1.9.7  
Status: Production verified

### Before

Material criticality treated constituent elements without correct
stoichiometric weighting.

### After

Criticality uses composition-aware weighting. For the reference material
LiFePO4, criticality changed from `36.5` to `32.0`, and the reference pathway's
scientific usefulness changed from `94.95` to `95.65`.

### Impact

- Scientific result: **Yes**
- Ranking: **Potentially**, where corrected values distinguish candidates
- API contract: **No**
- Data migration: **Yes**

---

## Unknown criticality remains unknown

Related findings: MG-AUD-002  
Release reference: v1.9.8  
Status: Production verified

### Before

Missing criticality evidence could be treated like favorable zero criticality
and contribute a quality advantage.

### After

Unknown criticality remains `null` and receives no favorable quality bonus.
Known-material values and the LiFePO4 reference workflow are unchanged.

### Impact

- Scientific result: **Yes**, for materials with incomplete evidence
- Ranking: **Potentially**, for affected materials
- API contract: **No**
- Data migration: **No**

---

## Unknown risk preserved during candidate screening

Related findings: MG-AUD-003  
Release reference: v1.9.9  
Status: Production verified

### Before

Candidate screening and comparison could collapse unknown risk into a
favorable numeric value.

### After

Unknown risk remains unknown throughout screening and comparison. Candidate
responses expose risk-evidence metadata, and bulk loading avoids repeated
per-material lookups.

### Impact

- Scientific result: **Yes**, for candidates with unknown risk
- Ranking: **Potentially**, for affected candidates
- API contract: **Additive metadata only**
- Data migration: **No**

---

## Exact chemical-element membership

Related findings: MG-AUD-004  
Release reference: v1.9.10  
Status: Production verified

### Before

Some discovery logic used raw formula substring matching, which could confuse
symbols such as `N` and `Na`, `S` and `Si`, or `C` and `Ca`.

### After

Candidate scoring, chain filtering, warnings, and research-objective logic use
structured or parsed chemical-element membership.

### Impact

- Scientific result: **Yes**, for ambiguous element symbols
- Ranking: **Potentially**, for affected objectives
- API contract: **No**
- Data migration: **No**

---

## Qualified framework-preservation provenance

Related findings: MG-AUD-005  
Release reference: v1.9.11  
Status: Production verified

### Before

Shared elements could be described as framework preservation without exposing
the limits of the underlying evidence.

### After

Discovery and research outputs distinguish shared-element continuity from
validated structural preservation. They expose `shared_elements`,
`preservation_basis: "element_overlap"`, and
`structural_preservation_validated: false`. The existing
`preserved_framework` field remains as a compatibility alias.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Additive metadata; compatibility field retained**
- Data migration: **No**

---

## Reconciled discovery-score provenance

Related findings: MG-AUD-006  
Release reference: v1.9.12  
Status: Production verified

### Before

Candidate merging could combine score breakdowns from competing sources, so a
displayed breakdown did not always describe the final score.

### After

The winning source's score and breakdown remain together while contextual
discovery evidence is aggregated. For every candidate:

```text
sum(score_breakdown) = discovery_score
```

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **No**
- Data migration: **No**

---

## Source-diversity bonus based on distinct sources

Related findings: MG-AUD-007  
Release reference: v1.9.13  
Status: Production verified

### Before

Repeated encounters and previously aggregated scores could inflate the
source-diversity contribution.

### After

The bonus uses distinct discovery source types: one source receives `0`, two
receive `10`, and three receive `20`. Base-score provenance is kept separate
from the diversity bonus so the bonus is applied once.

### Impact

- Scientific result: **Yes**, where prior source accounting was inflated
- Ranking: **Potentially**, for affected candidates
- API contract: **No**
- Data migration: **No**

---

## Complete evidence required for favorable risk-quality bonuses

Related findings: MG-AUD-008  
Release reference: v1.9.14  
Status: Production verified

### Before

A calculable risk score based on incomplete material-element coverage could
still qualify for a favorable risk-quality bonus.

### After

Low- and medium-risk quality bonuses require complete constituent-element risk
evidence. Partial evidence remains visible but is not treated as favorable.
The LiFePO4 and inspected Na-phosphate reference materials had complete
coverage and therefore retained their results.

### Impact

- Scientific result: **Yes**, for incomplete-evidence materials
- Ranking: **Potentially**, across quality-dependent graph and pathway ranking
- API contract: **No**
- Data migration: **No**

---

## Exact community element membership

Related findings: MG-AUD-049  
Release reference: v1.9.14 development cycle  
Status: Production verified

### Before

Graph community summaries could count elements using formula substrings.

### After

Community analytics use exact element membership, preventing false matches
between short and longer chemical symbols.

### Impact

- Scientific result: **Yes**, for ambiguous symbols in community summaries
- Ranking: **No**
- API contract: **No**
- Data migration: **No**

---

## Multi-element research objectives

Related findings: MG-AUD-009  
Release reference: v1.9.15  
Status: Production verified

### Before

Objective alignment could evaluate only the first avoided and preferred
element even when several were requested.

### After

Every requested avoided and preferred element contributes to deterministic
objective evaluation. Responses expose matched and unmatched elements,
coverage percentages, and completion status. Single-element behavior remains
unchanged; multi-element objectives may now receive different scores.

### Impact

- Scientific result: **Yes**, for multi-element objectives
- Ranking: **Potentially**, for multi-element objectives
- API contract: **Additive objective-satisfaction metadata**
- Data migration: **No**

---

## Path-wide and endpoint-specific objective satisfaction

Related findings: MG-AUD-050  
Release reference: v1.9.16  
Status: Production verified

### Before

Path-wide transition events could be interpreted as proof that the final
material satisfied the same objective.

### After

Research responses distinguish objective events anywhere along a path from the
composition of the final endpoint. Endpoint matched and unmatched elements,
coverage, status, and interpretation are exposed separately.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Additive endpoint-evaluation fields**
- Data migration: **No**

---

## Stable pathway identity for tied pathways

Related findings: MG-AUD-051  
Release reference: v1.9.17  
Status: Production verified within pathway-identity scope

### Before

Comparative research could use rank as pathway identity, causing distinct tied
pathways to be conflated.

### After

Each pathway exposes a stable `pathway_id`, `position`, and `rank`.
Comparative summaries and element aggregation reference pathway identity while
preserving competition ranking and valid ties.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Additive pathway identity fields**
- Data migration: **No**

---

## Canonical criticality comparison terminology

Related findings: MG-AUD-036  
Release reference: v1.9.18  
Status: Production verified

### Before

The `criticality_direction` field used risk-oriented values even though it was
derived from `criticality_score`.

### After

Serialized values use `LOWER_CRITICALITY`, `HIGHER_CRITICALITY`,
`SAME_CRITICALITY`, and `UNKNOWN`. Numeric deltas, bonuses, ranking, and
human-readable explanations are unchanged.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **Yes; serialized enum values changed**
- Data migration: **No**

---

## Direction-aware scenario explanations

Related findings: MG-AUD-052  
Release reference: Post-v1.9.18  
Status: Production verified

### Before

Scenario explanations could describe a positive adjustment as a negative
penalty or display a signed penalty inconsistently.

### After

Positive deltas are described as bonuses, negative deltas as penalties using
their absolute magnitude, and zero as no adjustment. The invariant is:

```text
scenario_delta = scenario_score - recommendation_score
```

Numeric scores, weights, ranking, and response fields are unchanged.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **No; human-readable wording only**
- Data migration: **No**

---

## Correct discovery base-score selection and deterministic ties

Related findings: MG-AUD-053  
Release reference: Post-v1.9.18  
Status: Production verified

### Before

A stronger incoming source could be rejected when an earlier candidate's
displayed score appeared larger only because it already included a diversity
bonus. Exact-score ordering also lacked an explicit stable tie-breaker.

### After

Source merging compares base score with base score. Results remain sorted by
descending `discovery_score`, with ascending `material_id` used only for exact
ties. Valid equal-evidence scores, including the family-only `125.0` ties, are
preserved.

### Impact

- Scientific result: **Yes**, when the wrong base source previously won
- Ranking: **Yes**, for affected merges and deterministic exact ties
- API contract: **No**
- Data migration: **No**

---

## Evidence-calibrated phosphate and oxide explanations

Related findings: MG-AUD-011  
Date: 2026-07-22  
Status: Production verified

### Before

Researcher-facing explanations used phrases such as `shares phosphate
framework`, `shares oxide chemistry`, and path wording that could imply
validated structural preservation from elemental overlap alone.

### After

Explanations now state the evidence and its limit:

- both materials contain phosphorus and oxygen; structural framework
  similarity is not validated;
- both materials contain oxygen; oxide structure similarity is not validated;
- paths retain shared elemental overlap; structural preservation is not
  validated.

Compatibility fields such as `preserved_framework` remain available and are
qualified by element-overlap provenance.

### Impact

- Scientific result: **No**
- Ranking: **No**
- API contract: **No; human-readable wording only**
- Data migration: **No**

---

## Evidence-calibrated transition classifications

Related findings: MG-AUD-012  
Date: 2026-07-22  
Release reference: Post-v1.9.18  
Status: Production verified; replacement branches covered by automated tests

### Before

Element overlap or an evidence-free validator fallback could be serialized as
`framework_preserving`, implying stronger structural evidence than the system
possessed.

### After

Qualifying elemental-overlap transitions use `shared_element_continuity`.
The validator's evidence-free final fallback uses `candidate_transition`.
Compatibility evidence fields remain available and structural validation
continues to be reported as false.

### Impact

- Scientific result: **No; terminology now matches evidence strength**
- Ranking: **No; existing numeric weights were retained**
- API contract: **Yes; affected serialized transition values changed**
- Data migration: **No**

---

## Shared-element continuity scoring semantics

Related findings: MG-AUD-013  
Date: 2026-07-22  
Release reference: Post-v1.9.18  
Status: Resolved; production verified 2026-07-23

### Before

The path-ranking score breakdown exposed `framework_preservation`, although
the dimension was computed from shared-element overlap rather than independent
bonding, structure-matching, or crystallographic evidence.

### After

The score dimension is `shared_element_continuity`. Research evidence,
pathway analysis, comparative explanations, and provenance use the same term
and explicitly state that structural preservation is not validated. Existing
continuity weights and valid final scores are retained.

Regression checks also confirmed that one-hop path efficiency remains `10.0`
and empty paths receive `0.0` efficiency. Local objective exploration for
material 5 returned `shared_element_continuity: 30` with the expected total
score of `95.65`.

Production verification on 2026-07-23 confirmed the same score breakdown and
total. The response exposed `preservation_basis: element_overlap`,
`structural_preservation_validated: false`, and no
`framework_preservation` score field or unsupported structural-preservation
claim.

### Impact

- Scientific result: **No; the evidence label is now scientifically qualified**
- Ranking: **No; final weights and valid rankings are unchanged**
- API contract: **Yes; one score-breakdown key changed**
- Data migration: **No**

---

## Contributor-aware recommendation explanations

Related findings: MG-AUD-037  
Date: 2026-07-23  
Release reference: Post-v1.9.18  
Status: Resolved; production verified 2026-07-23

### Before

Recommendation reasons mixed scoring contributors with contextual comparisons.
Criticality could be mentioned even when its preference was disabled, shared
elements and applications were not identified as the basis of the similarity
score, and the low-energy-above-hull contribution was omitted from the reason.

### After

Recommendation reasons now distinguish:

- the similarity score and its shared-element/shared-application basis;
- active score contributors, including stability, qualifying low energy above
  hull, and criticality when lower criticality is preferred;
- non-scoring criticality comparison under `context` when the preference is
  disabled; and
- the final recommendation score.

Local checks confirmed that a similarity score of `130.0`, stability bonus of
`10`, and low-energy bonus of `5` produce `145.0` when criticality preference is
disabled. With the preference enabled, the applicable criticality adjustment
is also reflected in both the score and explanation.

Production verification on 2026-07-23 passed for both
`prefer_lower_criticality=true` and `false` using material 5. Active
contributors reconciled with returned scores, while criticality was retained
only as context when the preference was disabled.

### Impact

- Scientific result: **No**
- Ranking: **No; scoring policy and numeric calculations are unchanged**
- API contract: **No; human-readable wording only**
- Data migration: **No**

---

## Path-wide shared-element continuity

Related findings: MG-AUD-014  
Date: 2026-07-23  
Release reference: Post-v1.9.18  
Status: Resolved; production verified 2026-07-23

### Before

Research-objective preservation could be satisfied by the union of elements
shared by different transitions. Scientific pathway analysis also read only
the compatibility field `preserved_framework`, ignored authoritative
`shared_elements`, and could omit transitions without evidence.

### After

Required preservation is evaluated from the intersection of shared-element
evidence across every transition. `shared_elements` is authoritative whenever
present, including when explicitly empty; `preserved_framework` is used only
when the primary field is absent. Every transition participates in the
intersection, and an empty path does not establish preservation.

Twenty-six focused research-service tests and the full regression suite passed.
A local two-hop objective response correctly reported:

``` text
{Fe, O, P} ∩ {Fe, Na, O, P} = {Fe, O, P}
```

The chain explanation consequently reported `Fe-O-P shared-element
continuity`; regression coverage separately confirmed that union-only evidence
is rejected.

### Impact

- Scientific result: **Yes; invalid union-only preservation is rejected**
- Ranking: **Potentially; paths failing continuous preservation may be filtered or evaluated differently**
- API contract: **No; existing fields retain their shape**
- Data migration: **No**

---

## Endpoint-based discovery path objective alignment

Related findings: MG-AUD-015  
Date: 2026-07-24  
Release reference: Post-v1.9.18  
Status: Resolved; development endpoint verified 2026-07-24

### Before

Discovery path ranking unioned removed and introduced elements across every
transition. A path could therefore earn objective-alignment credit when an
avoided element was removed and later reintroduced, or when a preferred
element was introduced and later removed, even though the final material did
not satisfy the objective. Usefulness explanations also described accumulated
transition events without distinguishing final endpoint composition.

### After

Objective alignment is determined from the final material's exact element
composition:

- structured endpoint `elements` are authoritative whenever the field is
  present, including when explicitly empty;
- otherwise, endpoint `formula` or `pretty_formula` is evaluated with the
  canonical chemical-formula parser;
- missing endpoint composition earns no objective credit;
- avoid and prefer objectives retain their established proportional scoring,
  with each side contributing at most `12.5`; and
- transition events remain available as pathway evidence but no longer prove
  endpoint satisfaction.

Usefulness explanations now separately report events that occur during the
path and objective outcomes at the endpoint. They also state when endpoint
composition is unavailable. Discovery transition separators were standardized
from the Unicode arrow to ASCII `->` to prevent mojibake in terminal-rendered
API responses.

Regression coverage includes endpoint reversals, partial and complete
multi-element objectives, missing endpoint evidence, structured-element
precedence, and explanation semantics. The full test suite passed.

Development verification of:

``` text
LiFePO4 -> Na3Fe3(PO4)4
```

returned:

- `objective_alignment: 25.0`;
- `scientific_usefulness_score: 99.47`;
- path-event explanations for removing Li and introducing Na; and
- endpoint explanations confirming that Li is excluded and Na is present.

### Impact

- Scientific result: **Yes; endpoint objective credit now reflects the final material**
- Ranking: **Potentially; paths with reversed or incomplete endpoint outcomes can score lower**
- API contract: **No structural change; numeric results and human-readable wording may change**
- Data migration: **No**

---

## Canonical risk-profile scale and provenance

Related findings: MG-AUD-055  
Date: 2026-07-27  
Release reference: Post-v1.9.18  
Status: Resolved; production verified 2026-07-27

### Before

Risk-profile seeds used incompatible scales under indistinguishable metadata.
Eight element profiles used `1–10`, while nickel used `0–1`, making stored
scientific evidence dependent on seed execution order.

### After

One idempotent canonical seed uses a `1–10` scale and versioned provenance:
`materialgraph_canonical_risk_profile_v1`. Nickel now uses canonical values
`5, 6, 4, 7, 6` for abundance, supply risk, toxicity, recyclability, and
geopolitical risk.

Local PostgreSQL and production Neon were updated in place. Each run reported
`Created: 0, Updated: 9`; uniqueness checks found no duplicate
`(element_id, year)` rows.

### Impact

- Scientific result: **Yes, for nickel-containing materials**
- Ranking: **Potentially, where corrected nickel evidence affects scoring**
- API contract: **No**
- Data migration: **Yes**

---

## Beneficial abundance direction in criticality

Related findings: MG-AUD-064  
Date: 2026-07-27  
Release reference: Post-v1.9.18  
Status: Resolved; production verified 2026-07-27

### Before

Raw abundance was averaged as though a higher value represented greater risk.
More abundant elements could therefore increase criticality. Null abundance
or recyclability could also cause arithmetic failure.

### After

Criticality internally uses `10 - abundance_score`, matching the declared
beneficial direction, while API responses retain raw abundance values. Null
dimensions remain excluded, and an all-null profile remains unknown.

For production LiFePO4, element criticality scores are now Li `56`, P `38`,
Fe `10`, and O `6`. Stoichiometric weighting produces material criticality
`18.29`, replacing the former production value `32.0`.

### Impact

- Scientific result: **Yes**
- Ranking: **Potentially, wherever criticality contributes**
- API contract: **No structural change; numeric values may change**
- Data migration: **No calculation migration; related seed data updated under MG-AUD-055**

---

## Evidence-aware similarity tie ordering

Related findings: MG-AUD-062  
Date: 2026-07-27  
Release reference: Post-v1.9.18  
Status: Resolved; test-verified 2026-07-27

### Before

Within an equal-similarity group, missing criticality evidence could receive a
favorable tie position. Public null values were preserved, but the internal
ordering still treated uncertainty as advantageous.

### After

Similarity score remains primary. Equal-similarity candidates with known
criticality evidence now precede candidates with unknown evidence. Unknown
criticality and delta values remain null, and complete ties remain
deterministic.

Focused tests and the full regression suite passed. Development endpoint
responses verified normal known-criticality ordering and general regression
behavior. Because the available development records did not include an
equal-similarity known-versus-unknown pair, controlled automated fixtures
provide direct verification of the corrected branch.

### Impact

- Scientific result: **Yes; missing criticality is no longer favorable**
- Ranking: **Yes, for equal-similarity candidates with different evidence availability**
- API contract: **No structural change; ordering may change**
- Data migration: **No**

---

## Evidence-aware candidate screening and comparison

Related findings: MG-AUD-065  
Date: 2026-07-27  
Release reference: Post-v1.9.18  
Status: Resolved; test-verified 2026-07-27

### Before

Unknown material risk produced no calculable risk penalty and could therefore
rank ahead of known-risk evidence through the numeric screening score. Pairwise
comparison inherited the same favorable-uncertainty behavior.

### After

Screening and comparison share an evidence-aware deterministic decision key.
Known risk evidence precedes unknown risk before the remaining score and risk
dimensions are considered. Unknown risk stays null, receives no fabricated
penalty, and is never described as low risk. Complete-key equality remains an
explicit, request-order-independent tie.

Focused screening and comparison tests and the full regression suite passed.
Normal development endpoints remained operational. Controlled automated
fixtures directly verify the otherwise-equivalent known-versus-unknown branch,
which was not present in the normal development dataset.

### Impact

- Scientific result: **Yes; missing risk evidence is no longer rewarded**
- Ranking: **Yes; screening order and comparison winners can change**
- API contract: **No structural change; ordering and reasons may change**
- Data migration: **No**

---

## Nullable risk in scenario ranking and sensitivity analysis

Related findings: MG-AUD-066, MG-AUD-067  
Date: 2026-07-28  
Release reference: Post-v1.9.18  
Status: Resolved; test-verified 2026-07-28

### Before

Scenario ranking compared nullable material risk directly with numeric
thresholds, so an unknown value could raise a `TypeError`. Sensitivity analysis
multiplied a nullable baseline risk by scenario multipliers, causing the same
class of failure. A zero fallback would have incorrectly represented missing
evidence as measured zero risk.

### After

Scenario ranking preserves `material_risk_score: null` and explains that
aggregate risk is unknown without assigning a low, moderate, or high label.
Sensitivity analysis preserves `baseline_material_risk_score: null`, reports
`sensitivity_level: "UNKNOWN"`, and returns `adjusted_score: null` and
`score_delta: null` for risk-derived scenarios.

Focused scenario-ranking and sensitivity-analysis tests passed. The related
candidate-screening, scenario-ranking, and sensitivity-analysis regression
tests also passed, while known-risk behavior remained unchanged.

This change is limited to nullable-risk correctness. The existing scenario
definitions are unchanged; element-specific scenario adjustment and distinct
supply-risk versus geopolitical calculations remain tracked by `MG-AUD-068`
and `MG-AUD-069`.

### Impact

- Scientific result: **Yes; unknown risk now propagates explicitly instead of becoming a failure or fabricated zero**
- Ranking: **No intended change for materials with known risk**
- API contract: **No breaking structural change; unknown derived sensitivity values are nullable and use `UNKNOWN` classification**
- Data migration: **No**

---

## Element-specific scenario policy and dimension-specific sensitivity

Related findings: MG-AUD-068, MG-AUD-069  
Date: 2026-07-28  
Release reference: Post-v1.9.18  
Status: Resolved; test-verified 2026-07-28

### Before

Scenario-policy evaluation multiplied the entire recommendation score by the
supply-risk multiplier, regardless of whether the candidate contained the
named element. A multiplier above `1.0` could therefore reward increased risk.

Sensitivity analysis applied supply-risk and geopolitical-risk scenario names
to identical calculations over the same aggregate material-risk score. The
underlying dimension-specific evidence was not used.

### After

Supply-risk policy adjustment applies only to candidates containing the named
element. Increased exposure produces a fixed-weight, auditable penalty;
unaffected candidates receive no supply-risk adjustment. Existing avoid- and
prefer-element adjustments remain independent.

Sensitivity analysis derives separate supply-risk and geopolitical-risk
baselines from their corresponding element-level evidence. Each scenario
adjusts only its named dimension and reports the dimension, baseline component,
and adjusted component. Partial missing evidence remains local to the affected
dimension, while completely unavailable evidence retains
`sensitivity_level: "UNKNOWN"` and nullable derived values.

Focused scenario-policy and sensitivity-analysis tests passed. The related
scenario-ranking and candidate-screening regression tests also passed.

### Impact

- Scientific result: **Yes; scenario outputs now reflect the named element and risk dimension**
- Ranking: **Yes; scenario scores can change because increased risk is penalized only for exposed candidates**
- API contract: **Additive sensitivity fields; existing aggregate baseline retained**
- Data migration: **No**

---

## Evidence-aware substitution risk ranking

Related finding: MG-AUD-070  
Date: 2026-07-28  
Release reference: Post-v1.9.18  
Status: Resolved; test-verified 2026-07-28; endpoint regression-verified with
known-risk data

### Before

Substitution analysis consumed the legacy numeric risk API, so missing risk
evidence became `0.0`. The rank formula then gave that fabricated zero the
maximum low-risk contribution and could describe an unknown-risk candidate as
lower risk.

### After

Source and candidate risk values remain nullable. Unknown risk receives no
low-risk contribution, known evidence is ordered before unknown evidence, and
material ID breaks otherwise equal ties deterministically. The response now
reports risk-known state, evidence coverage and completeness, and unknown-risk
elements. Explanations identify unavailable evidence without calling it low
risk.

Focused substitution tests covered nullable evidence, score construction,
known-before-unknown ordering, deterministic ties, metadata, and explanations.
Related screening, comparison, and material-risk regressions passed.

The development endpoint check confirmed serialization, known-risk ranking,
explanation consistency, and deterministic equal-score ordering. Because the
available records all had complete risk evidence, the unknown-risk endpoint
branch remains directly verified by controlled automated tests rather than a
production fixture.

### Impact

- Scientific result: **Yes; missing risk evidence is no longer represented as minimum risk**
- Ranking: **Yes; known-evidence candidates precede unknown-evidence candidates**
- API contract: **Additive evidence fields and nullable source/candidate risk scores**
- Data migration: **No**

---

## Hop-bounded chain enumeration and weighted path state

Related findings: MG-AUD-074, MG-AUD-075  
Date: 2026-07-28  
Release reference: Post-v1.9.18  
Status: Resolved; full-suite test-verified 2026-07-28; MG-AUD-074 development
endpoint-verified

### Before

Discovery-chain enumeration returned a chain only when its length exactly
equaled `max_hops`. Valid shorter chains, dead ends, and prefixes with no valid
continuation were omitted.

Weighted shortest-path search stored one best cost per material. Under a hop
bound, a cheap deep arrival could suppress a costlier shallower arrival even
when only the shallower state retained enough hop capacity to reach the target.

### After

`max_hops` is now an inclusive upper bound. Every valid non-zero-hop chain is
retained, while only chains below the bound are expanded further. The source
alone is not returned, and the hop ceiling remains strict.

Weighted search stores costs per `(material_id, depth)` and applies a
depth-aware stale-state check. Different arrivals at the same material retain
their distinct future feasibility.

Focused tests covered shorter and maximum-depth chains, dead ends, invalid or
cyclic continuations, hop-ceiling enforcement, and the controlled
deep-versus-shallow weighted-search failure mode. The full suite passed.

A development chain request with `max_hops=2` and `limit=20` returned five
one-hop and fifteen two-hop chains, with no result beyond two hops and with
internally consistent material/transition counts and endpoints. The specialized
weighted-state condition remains directly verified by its targeted fixture
rather than by incidental endpoint topology.

### Impact

- Scientific result: **Yes; valid bounded pathways are no longer omitted**
- Ranking: **Yes; newly retained shorter paths can rank higher, and corrected weighted search can select a previously pruned route**
- API contract: **No structural change; result contents and ordering can change**
- Data migration: **No**

---

## Canonically validated and bounded K-best traversal

Related findings: MG-AUD-077, MG-AUD-079, MG-AUD-080  
Date: 2026-07-28  
Release reference: Post-v1.9.18  
Status: Resolved; full-suite test-verified 2026-07-28

### Before

K-best search consumed raw discovery-candidate adjacency rather than the
canonical transition validator. It could therefore return an edge rejected by
the canonical graph and reconstruct different transition metadata.

Material metadata was found through a graph-wide first match by target ID, so
a multiply reachable material could receive evidence from the wrong incoming
edge.

Simple-path enumeration explored and ranked every reachable path before
applying `k`. The declared internal path limit was unused, and no independent
processed-state budget protected sparse or unreachable searches.

### After

Adjacency now admits only canonically validated transitions and carries each
accepted transition into K-best path construction. Material metadata is
resolved from the actual `(source, target)` edge traversed by the path.

Enumeration accepts at most 100 target-reaching paths and processes at most
1,000 search states before ranking. `search_truncated` reports when either
budget stops the search. `total_path_count` records valid paths evaluated
within the bounded search; it is not an exhaustive count when truncated.
`path_count` remains the number returned after applying `k`.

Focused tests covered invalid-edge exclusion, path-specific metadata, both
computational budgets, bounded ranking calls, deterministic ordering, result
limiting, simple paths, and hop limits. The full regression suite passed.
K-best has no current public route or research-service consumer, so no endpoint
or public-schema change was required.

### Impact

- Scientific result: **Yes; invalid transitions and wrong-edge evidence are excluded**
- Ranking: **No formula change; very large searches rank only the explicitly bounded evaluated set**
- Performance: **Yes; enumeration and ranking now have enforceable path and state budgets**
- API contract: **No public change; internal service metadata adds `search_truncated` and clarifies count semantics**
- Data migration: **No**

---

## Edge-intelligence score differentiation

Related finding: MG-AUD-076  
Date: 2026-07-31  
Release reference: Post-v1.9.18  
Status: Resolved; full-suite test-verified 2026-07-31

### Before

Edge scoring multiplied scientific plausibility by 100 and then added
framework-continuity and elemental-exchange bonuses before clamping the result
to 100. High-plausibility transitions could therefore reach or exceed the
maximum without the additional evidence, causing scientifically different
edges to collapse to the same score.

### After

Scientific plausibility contributes at most 80 points. The remaining 20 points
are reserved for the existing evidence signals: P–O continuity, oxygen
continuity, and a removed-and-introduced element exchange. The score remains
bounded to `0–100`, but each intended component can now affect the result.

Focused regression coverage demonstrates that alkali-substitution edges with
full, partial, and baseline evidence score `100.0`, `85.0`, and `80.0`,
respectively. Updated edge-intelligence tests and the full regression suite
passed. K-best and path-ranking formulas were not changed because they do not
consume `edge_score`.

### Impact

- Scientific result: **Yes; edge evidence distinctions are now preserved**
- Ranking: **Graph-edge score ordering can change; K-best/path ranking is unchanged**
- API contract: **No structural change; numeric `edge_score` values can change**
- Data migration: **No**