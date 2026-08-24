# MG-IA-014 — Downstream discovery and substitution bypass canonical stability evidence

- Classification: cross-service scientific-consistency and scoring defect
- Priority: P2
- Confidence: high
- Disposition: confirmed

## Affected files and components

- `app/services/material/stability_evidence_policy.py`
- similarity and recommendation services
- `app/services/discovery/scoring_service.py`
- `app/services/discovery/candidate_service.py`
- `app/services/discovery/explanation_service.py`
- `app/services/substitution_analysis_service.py`
- related scoring and service tests

## Exact evidence

Similarity computes one stability contribution through `StabilityEvidencePolicy`, using energy above hull as the primary signal and disclosing source inconsistency. Recommendation explicitly inherits that contribution without reapplying it.

Discovery then takes the recommendation score and adds another 20-point `STABILITY_BONUS` whenever raw `candidate["is_stable"]` is true. For consistent stable evidence, the same stability fact contributes once inside similarity/recommendation and again in discovery. For inconsistent evidence such as `is_stable=True` with high energy above hull, similarity correctly gives no stability contribution but discovery restores a favorable bonus from the contradicted raw flag.

Substitution analysis independently adds `0.05` and explains `Stable candidate` based only on raw `material.is_stable`, without consulting the canonical policy or energy evidence.

## Expected versus actual

Services sharing stability semantics should use the canonical evidence policy, preserve its energy-primary decision and uncertainty, and avoid counting an inherited contribution again. Current downstream scoring bypasses that policy and can double-count or contradict it.

## Impact

Candidate rankings and explanations can favor materials because of duplicated or inconsistent stability evidence. Identical material evidence is interpreted differently across similarity, recommendation, discovery, and substitution endpoints.

## Reproduction

Pass a recommendation candidate with a similarity-derived stability contribution of 20 and `is_stable=True` into `score_recommendation_candidate`; discovery adds another 20. Then use `is_stable=True` with an energy value assessed as unstable by the canonical policy; discovery and substitution still grant their raw-flag bonuses.

## Tests

Recommendation tests explicitly verify that stability is not reapplied after similarity. Discovery scoring tests protect criticality non-duplication but have no equivalent stability regression. Substitution tests assert the raw-flag bonus but do not exercise inconsistent energy/flag evidence.

## Recommended remediation scope

Propagate the canonical stability evidence object or disclosed contribution into downstream services, define whether any additional discovery-level stability term is scientifically distinct, prevent duplicate contribution, and add parity tests for consistent, inconsistent, fallback, and unavailable evidence.
