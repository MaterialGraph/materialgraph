# Stack 03 Evidence — Relationships, Neighborhoods, and Recommendations

## Scope

Reviewed material query, family, neighbor, neighborhood, similarity, recommendation, and scenario-policy services; family, neighbor, neighborhood, similarity, recommendation, and common schemas; family and material-intelligence routes; and the supplied service/API tests.

All supplied Python files compiled successfully.

## Vertical traces

### Family relationships

Candidates are selected through overlapping element membership and classified with composition-level heuristics. Returned records explicitly use `relationship_basis="composition_heuristic"`, set `structural_family_validated` false, and disclaim unvalidated structural frameworks and substitution mechanisms. Results sort by shared-element count and then material ID. Tests protect the scientific qualifications and deterministic tie-breaker.

The endpoint has no result limit and overlap candidates are loaded in full. Whether this is materially unsafe at the intended dataset scale remains `OBS-010` pending measurements and policy evidence.

### Neighbors and neighborhoods

Neighbors are generated from all shared-element and shared-application association rows. Complete score ties lack a final material-ID key. Bounded neighborhood membership consumes this order, and tied edges also lack stable endpoint tie-breakers (`MG-IA-012`).

The neighborhood node limit filters response membership but does not stop excluded nodes from being queued and expanded. Supplied tests explicitly require the opposite and are contradicted by the implementation (`MG-IA-011`).

### Similarity and recommendations

Similarity scores shared elements, shared applications, and a single stability-evidence contribution. It bulk-loads criticality, distinguishes unknown deltas, declares its ranking policy, and resolves complete ties by material ID. Recommendations inherit rather than reapply stability, optionally apply a symmetric criticality-delta adjustment, explain numeric versus contextual contributions, score the complete similarity pool, and use a stable final ID key. Supplied tests protect these properties.

Full-pool scoring before the API limit is explicit and test-protected, so it is not classified as hidden preselection. Its scaling implications remain part of `OBS-010`.

### Scenario policy

Scenario ranking applies a fixed formula-membership adjustment for the named supply-risk element plus fixed avoid/prefer rules. Reasons reconcile to the net score delta, chemical symbols are route-validated, and tests cover positive, negative, neutral, and combined adjustments.

The named supply-risk multiplier does not use stored risk evidence or composition fraction. Its scientific interpretation remains `OBS-011` until the intended heuristic-versus-quantitative contract is established.

## Test-quality assessment

The neighborhood suite contains strong intended-contract tests for bounded expansion, but the supplied implementation cannot satisfy the two call-bound assertions. Its determinism test repeats an identical preordered fixture and therefore does not exercise tied-order permutations. Neighbor API coverage checks existence and response shape only.

Similarity and recommendation tests directly verify complete-pool scoring, evidence treatment, explanations, and stable tie-breaking. Family tests protect both deterministic order and careful scientific language. Scenario tests verify arithmetic consistency within the policy but do not establish external scientific calibration.

## Negative findings

No defect was confirmed in family scientific labeling, similarity criticality handling, recommendation stability accounting, recommendation explanations, scenario arithmetic, or the supplied schema inheritance. The complete-pool policies were not classified as defects solely because they may be expensive.

## Execution limitation

The exact repository checkout and test environment are unavailable. The neighborhood test contradiction is directly reproducible from the supplied mock fixture and control flow, but pytest was not executed here. Repository-scale performance observations remain unconfirmed pending runtime evidence.
