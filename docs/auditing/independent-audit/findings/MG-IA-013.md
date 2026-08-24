# MG-IA-013 — Scenario API accepts nonexistent chemical element symbols

- Classification: API validation and scientific-input defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/utils/chemical_formula.py`
- scenario-recommendation route in `app/api/v1/routes/material_neighbors.py`
- `app/domain/periodic_table.py`
- scenario API tests

## Exact evidence

The scenario route rejects an element only when `is_valid_element_symbol` returns false. That helper checks only the regular-expression shape `^[A-Z][a-z]?$`; it does not check the authoritative 118-symbol set. Direct evaluation returns true for nonexistent symbols including `Xx` and `Qz`.

In contrast, discovery routes use `normalize_element_symbol`, which rejects values absent from `ELEMENT_SYMBOLS`. The scenario endpoint can therefore accept scientifically invalid inputs that equivalent discovery filters reject.

## Expected versus actual

An API parameter described and validated as a chemical element symbol should accept only canonical periodic-table symbols. The current scenario route accepts any one- or two-letter value with matching capitalization.

## Impact

Invalid scenarios can return successful, apparently meaningful results. Because no candidate formula contains a nonexistent element, the named supply-risk adjustment silently becomes neutral, which can mislead callers and creates inconsistent validation across APIs.

## Reproduction

Call the scenario-recommendation endpoint with `element=Xx`. Route validation passes because `is_valid_element_symbol("Xx")` is true. The policy evaluates candidates without a matching exposure instead of returning HTTP 422.

## Tests

Periodic-table tests protect rejection through `normalize_element_symbol`, but scenario API tests cover valid, missing, and length-invalid inputs only. They do not exercise well-shaped nonexistent symbols.

## Recommended remediation scope

Use the canonical periodic-table normalizer for all public element parameters, return a consistent structured 422 response, and add cross-route tests for lowercase normalization, whitespace policy, and nonexistent one- and two-letter symbols.
