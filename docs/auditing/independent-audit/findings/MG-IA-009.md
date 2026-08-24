# MG-IA-009 — Unknown composition is persisted and computed as equal composition

- Classification: scientific correctness and evidence-honesty defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Evidence

When structured composition is absent, `resolve_import_fractions()` returns `1.0` for every unique element. The importer stores these values in `MaterialElement.fraction`. Criticality uses them as quantitative weights and publicly reports them as fractions; quality consumes the resulting criticality score. Tests explicitly preserve this fallback.

Affected files/functions: `composition_service.py:resolve_import_fractions`, `import_service.py:_link_elements`, `material_element.py:MaterialElement.fraction`, `criticality_service.py:_build_criticality_response`, and `quality_service.py`.

## Expected versus actual

Membership-only data should remain distinguishable from quantitative composition. Instead, unknown stoichiometry becomes an affirmative equal-weight assumption. Four elements produce four `1.0` fractions totaling `4.0`.

## Impact

Composition-weighted scores use invented equal weights, fraction-labelled outputs can exceed one, and downstream consumers cannot distinguish structured composition from membership-only legacy data.

## Tests

Structured normalization tests are strong. Missing tests cover evidence status, downstream refusal/fallback disclosure, and legacy-row migration.

## Reproduction and caller trace

Import a manual/legacy candidate with four element symbols and empty `composition_fractions`; observe four stored `1.0` values and the equal-weight criticality result. The path is explicitly exercised by composition and import tests and reaches quality through criticality.

## Remediation scope

Separate membership from quantitative composition, store composition evidence status, prevent undisclosed weighted computation on unknown composition, and identify/migrate legacy rows.
