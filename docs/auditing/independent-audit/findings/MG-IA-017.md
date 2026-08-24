# MG-IA-017 — Pathway quality summary mishandles unknown risk

- Classification: missing-evidence correctness and runtime-reliability defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/services/research/scientific_pathway_analysis_service.py`
- `app/services/material/quality_service.py`
- `app/schemas/research_objective_exploration.py`
- scientific-pathways endpoint

## Exact evidence

`MaterialQualityService` intentionally returns `risk_score = None` when risk evidence is unknown. `ScientificPathwayAnalysisService._quality_summary` passes every quality record to `max` with `key=lambda item: item.get("risk_score", 0.0)`. The default does not apply when the key exists with value `None`.

Python cannot order `None` against another `None` or a float during `max`. Normal pathway opportunities contain at least two material-quality records. If a path contains unknown risk evidence, summary construction can therefore raise `TypeError`. If only one unknown record were supplied directly, it would be labelled `highest_risk_material` despite having no numeric risk evidence.

## Expected versus actual

Unknown risk should remain unknown and be excluded from numeric highest-risk selection, with coverage or unavailability exposed. It currently causes a runtime failure in multi-record summaries or an unsupported highest-risk label in a single-record summary.

## Impact

The scientific-pathways endpoint can fail precisely when evidence is incomplete, contradicting the system's first-class unknown-evidence policy. Even without failure, identifying an unknown material as highest risk would overstate the evidence basis.

## Reproduction

Call `_quality_summary` with two material records and quality records whose `risk_score` values are `None`, or with one `None` and one float. Python raises a comparison `TypeError` while evaluating `max`. A single `None` record returns that material as highest risk.

## Caller trace

`analyze` builds every pathway opportunity through `_build_opportunity`, which always calls `_quality_summary` after bulk quality prefetch. The FastAPI `/materials/{material_id}/research/scientific-pathways` route directly returns this analysis.

## Tests

The pathway-analysis tests have not yet been supplied. Missing regression coverage should include all-known, mixed-known/unknown, all-unknown, and no-quality cases and assert both response serialization and scientifically honest highest-risk semantics.

## Recommended remediation scope

Select highest risk only from records with `risk_known` and a finite numeric `risk_score`; return `None` when no eligible record exists. Consider exposing risk coverage in `QualitySummary`. Add focused unit tests and an endpoint regression test with incomplete evidence.
