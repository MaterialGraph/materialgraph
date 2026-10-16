# Objective coverage contract (Objective Explore, contract version 1)

Status: **approved 2026-10-16** (decisions D1–D3, open points O1–O4).
Issues: #52 (objective-coverage summary) and #55 (per-chain avoided-element disclosure; shares this computation).
Implementation: `app/utils/chemical_formula.py` (`parse_formula_elements_strict`), `app/services/research/objective_coverage.py`, `app/schemas/research_objective_exploration.py` (`ObjectiveCoverage`), one call in `ResearchObjectiveExplorationService.explore()`.

Coverage describes what the **returned** results contain. It is not a scientific conclusion, does not establish suitability, synthesis feasibility or performance, and there is deliberately no overall "satisfied" status. It is independent of the Scientific Pathway Analysis `ObjectiveSatisfaction` model, which has different semantics.

## 0. Approved decisions
- D1: element presence from a strict formula parse; missing, empty or unparseable formulas are **Not evaluated**, never absent. Traversal and ranking unchanged; a MaterialElement membership cross-check is future work.
- D2: material unit = **returned ranked materials** (not "final candidates"); pathway unit = **returned chains, excluding the source material**, stated in the response.
- D3: additive `objective_coverage` on the Objective Explore response only; backend computes, frontend only renders.
- O1 field/enum names as below; O2 Avoid vocabulary `present` / `not_observed` / `not_evaluated`; O3 `chain_avoidance` included; O4 Strict wording as in §6.

## 1. Scope and non-goals
- Endpoint: `POST /api/v1/materials/{id}/discovery/objective/explore` only.
- Additive response field `objective_coverage`. All existing fields, values and ordering unchanged.
- **Not changed:** traversal, PR #44 admission/allocation, expansion limit, scoring, candidate ordering, chain selection, `extract_elements`/`contains_element`, Objective Chains API, Scientific Pathway Analysis.
- Coverage is computed **after** the existing response is assembled, from `ranked_candidates`, `chains`, `objective`, `mode`, `material_id`, `base_formula` and the full ranked pool size. It is a pure function (no DB access).

## 2. Element evaluation (D1)
- New strict parser `parse_formula_elements_strict(formula) -> frozenset[str] | None` (new function; existing helpers untouched).
- Accepts: element symbols from `ELEMENT_SYMBOLS`, integer/decimal counts, balanced parentheses. The whole string must be consumed.
- Returns **None (Not evaluated)** for: missing, empty/whitespace, unknown symbols (e.g. `Xx`), lowercase starts, unbalanced parentheses, unsupported characters (e.g. hydrate dot `·`, brackets, charges), or no symbols.
- Formula source: ranked material → `ranked_candidates[i].formula`; chain material → `formula`, falling back to `pretty_formula` only when `formula` is empty (same precedence as the existing Strict response filter).
- An element is reported **absent only if the formula was evaluated**. Uncertain → Not evaluated, never absent.
- Known limitation (documented): ranking uses the permissive regex; where the strict parser rejects a formula the ranking may still have scored it. A MaterialElement membership cross-check is a separate future issue.

## 3. Units and denominators
| Section | Unit | Denominator |
|---|---|---|
| Preferred elements | **returned ranked materials** (`ranked_candidates` after `limit`) | `returned_ranked_material_count` |
| Avoided elements — materials | returned ranked materials | same |
| Avoided elements — pathways | **returned chains** (`chains`), evaluating every material **except the source** (index 0) | `returned_chain_count` |

- Ranked materials need not be chain endpoints and may appear in no returned chain (CS01: 3 of 5). No candidate count is ever equated with a chain count.
- A chain counts as **containing** element E if any evaluated non-source material contains E (certain presence, even if another material is not evaluated). It counts as **not containing** only if every non-source material was evaluated and none contains E. Otherwise it is **not evaluated** for E.
- `ranked_material_pool_count` (all ranked materials before `limit`) is reported so the UI can say "5 returned of N ranked".

## 4. Status vocabulary
- Prefer: `represented` (≥1 evaluated material contains it) · `not_represented` (evaluated > 0, none contains it) · `not_evaluated` (evaluated = 0, incl. empty results).
- Avoid (materials and chains): `present` · `not_observed` · `not_evaluated`. Avoid never uses "represented" and absence is never called satisfied, suitable or proof.
- `coverage_complete = (not_evaluated_count == 0)`. When false, the UI must show both the observed count and the not-evaluated count; denominators are never silently reduced.
- No overall "satisfied" status exists.

## 5. Schema (`app/schemas/research_objective_exploration.py`; counts are validated `>= 0`)
```python
PreferStatus = Literal["represented", "not_represented", "not_evaluated"]
AvoidStatus = Literal["present", "not_observed", "not_evaluated"]

class PreferredElementCoverage(BaseModel):
    element: str
    unit: Literal["returned_ranked_materials"] = "returned_ranked_materials"
    containing_count: int; evaluated_count: int; not_evaluated_count: int; total_count: int
    status: PreferStatus; coverage_complete: bool

class AvoidedElementMaterialCoverage(BaseModel):
    element: str
    unit: Literal["returned_ranked_materials"] = "returned_ranked_materials"
    containing_count: int; evaluated_count: int; not_evaluated_count: int; total_count: int
    status: AvoidStatus; coverage_complete: bool

class AvoidedElementChainCoverage(BaseModel):
    element: str
    unit: Literal["returned_chains_excluding_source"] = "returned_chains_excluding_source"
    containing_chain_count: int; evaluated_chain_count: int; not_evaluated_chain_count: int; total_chain_count: int
    chain_positions: list[int]          # 1-based positions in `chains`
    status: AvoidStatus; coverage_complete: bool

class ChainMaterialAvoidance(BaseModel):
    material_id: int
    chain_material_index: int           # index within chain.materials (>= 1)
    role: Literal["intermediate", "final"]
    avoided_elements: list[str]         # in request order

class ChainAvoidanceDetail(BaseModel):  # one per returned chain, same order as `chains` (#55)
    chain_position: int
    materials_with_avoided_elements: list[ChainMaterialAvoidance]
    not_evaluated_material_ids: list[int]

class SourceMaterialDisclosure(BaseModel):
    material_id: int
    excluded_from_counts: Literal[True] = True
    avoided_elements_present: list[str] | None   # None = source formula not evaluated

class ObjectiveCoverage(BaseModel):
    contract_version: Literal["1"] = "1"
    scope: Literal["returned_results_only"] = "returned_results_only"
    element_evaluation_basis: Literal["formula_symbols_strict_parse"] = "formula_symbols_strict_parse"
    returned_ranked_material_count: int; ranked_material_pool_count: int; returned_chain_count: int
    preferred_elements: list[PreferredElementCoverage]                 # request order
    avoided_elements_in_ranked_materials: list[AvoidedElementMaterialCoverage]
    avoided_elements_in_returned_chains: list[AvoidedElementChainCoverage]
    chain_avoidance: list[ChainAvoidanceDetail]
    source_material: SourceMaterialDisclosure
    terms_not_evaluated: list[Literal["preserve_elements", "target_family"]]  # only if requested
    mode: Literal["balanced", "exploratory", "strict"]
    avoid_policy_explanation: str
    limitations: list[str]

# ResearchObjectiveExplorationResponse gains:  objective_coverage: ObjectiveCoverage
```

## 6. Backend-owned text
- Balanced: "Avoid is a soft preference in Balanced mode. Returned ranked materials or composition chains may still contain avoided elements."
- Exploratory: "Avoid is a soft preference in Exploratory mode, with a smaller score penalty than Balanced. Returned ranked materials or composition chains may still contain avoided elements."
- Strict: "Strict mode excludes materials containing avoided elements during search, using recorded element membership; materials without membership records are also excluded. It then removes returned chains in which any material other than the source contains an avoided element, read from formula symbols. The source material is exempt." *(verified against `chain_service.py` admission and `objective_exploration_service.py` response filter on b0fb07d)*
- Limitations (always): "Counts describe only the returned results, not the full dataset or all possible materials." · "Element presence is read from reported formulas; it does not establish stability, synthesis feasibility or performance." · "Ranked materials are not necessarily chain endpoints and may not appear in any returned chain." · "Pathway counts exclude the source material." Plus, when `result_truncated` or `search_truncated`: "Results were limited; coverage may differ for unreturned results."
- Frontend renders these strings and the counts; it does not parse formulas or derive statuses.

## 7. Golden acceptance case (frozen production CS01)
Fixture `tests/fixtures/objective_coverage/cs01_production_post_deploy_response.json`: byte-exact **copy** of `docs/product/literature-case-study-01/qualification/production-2026-10-09/post-deploy-20261009T034841Z/cs01_response.json` (SHA-256 `0ae32ba28607714224d07d5ed609c7195337a2c6d16fa68b50c3f9767ea473ac`, identical to the qualification `SHA256SUMS.txt`; frozen evidence untouched; `.gitattributes` keeps it byte-exact). Expected coverage:

| Term | Unit | Result | Status |
|---|---|---|---|
| Prefer Na | ranked materials | 5 of 5 evaluated | represented |
| Prefer K | ranked materials | 0 of 5 evaluated | not_represented |
| Avoid Li | ranked materials | 0 of 5 evaluated | not_observed |
| Avoid Co | ranked materials | 0 of 5 evaluated | not_observed |
| Avoid Li | returned chains excl. source | 3 of 5 (positions 3, 4, 5; materials 1, 2, 3, role intermediate) | present |
| Avoid Co | returned chains excl. source | 0 of 5 | not_observed |
| Source LiFePO₄ (ID 5) | — | contains Li; excluded from counts | — |

All counts complete (no Not evaluated). All 29 distinct formulas in the reference dataset and Case Study 01 evidence parse with the strict parser and agree with `extract_elements`.

## 8. Contract tests
Implemented in `tests/services/research/test_objective_coverage.py`, `tests/utils/test_chemical_formula_strict.py` and `tests/api/test_research_objective_exploration_api.py`:
1. Golden CS01 (above), from fixture; no live data.
2. Empty results (0 ranked, 0 chains) → all `not_evaluated`, totals 0.
3. Missing/empty formula on a ranked material → counted in `not_evaluated_count`, never absent.
4. Unparseable formulas (`Xx2O`, `LiFe(PO4`, `Fe2O3·H2O`, `li2O`) → not evaluated.
5. Multiple preferred elements; multiple avoided elements; request order preserved.
6. Multiple chains per material and same endpoint in several chains → chain counts per chain, material counts per material.
7. Chain with one unevaluable material and one Li material → `present`; chain with one unevaluable material and no Li → `not_evaluated`.
8. Source contains avoided element → excluded, disclosed.
9. Strict vs Balanced vs Exploratory explanations; Strict chain Avoid count 0 for evaluated chains.
10. Tied ranked scores → coverage identical under permutation of tied items.
11. Truncation flags → limitation sentence present; pool count > returned count.
12. No Avoid/Prefer → empty sections, no statuses invented; Preserve/family requested → listed in `terms_not_evaluated`.
13. API test: field present, schema-valid and internally consistent with `ranked_candidates`/`chains` of the same response; Strict reports no avoided element in returned chains. Byte-identity of all pre-existing fields is verified during release qualification by comparing pre- and post-change captures of the same requests on the test database.
14. Parser unit tests incl. `Co` vs `CO`, decimals, nested parentheses.

