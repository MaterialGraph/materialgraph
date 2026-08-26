# MG-IA-014 Change Impact — Canonical Downstream Stability Evidence

## Status

Verified locally: 20 focused tests, 68 adjacent tests, 663 full-suite tests,
Ruff, and Git whitespace validation passed.

## Before

Similarity converted `is_stable` and `energy_above_hull` into one canonical,
energy-primary stability contribution. Recommendation inherited that complete
similarity score without reapplying stability. Discovery then added another
20 points whenever the raw imported flag was true and narrated the candidate
as dataset-stable. Substitution independently added 0.05 and used the same raw
flag in its explanation. Both downstream paths could therefore contradict the
energy-primary policy, and discovery double-counted inherited evidence.

## After

Discovery accepts the recommendation score as the complete inherited score and
does not add or narrate a second raw-flag stability signal. Substitution now
uses `StabilityEvidencePolicy` and scales its canonical similarity contribution
into the existing bounded substitution rank range by dividing it by 400.
Substitution responses disclose the canonical band, evidence basis,
completeness, source consistency, and exact rank contribution. Explanations use
the policy reason and explicitly report inconsistent sources.

## Impact

- Discovery scoring: **Corrected** — inherited stability is counted once.
- Discovery explanations: **Corrected** — raw imported flags no longer produce
  an independent stability claim.
- Substitution scoring: **Corrected** — energy above hull is primary and the
  imported flag is only incomplete fallback evidence.
- Substitution explanations: **Corrected** — narrative and numeric contribution
  share the same evidence assessment.
- Contradictory sources: **Disclosed** — a stable flag cannot override unstable
  energy evidence and the inconsistency is reported.
- Fallback evidence: **Down-weighted** — a positive stable flag without energy
  evidence contributes 0.025 rather than the former unconditional 0.05.
- Stable energy evidence: **Weight preserved** — the canonical 20-point
  contribution scales to the existing 0.05 substitution maximum.
- Near-stable and metastable evidence: **Represented** — canonical graded
  contributions scale to 0.0375 and 0.025 respectively.
- Substitution API contract: **Additive** — five stability-evidence fields are
  added to each substitute candidate.
- Database schema and stored data: **No change**.
- Query count and asymptotic work: **No change**; assessment is constant work
  per already-loaded candidate.

## Compatibility note

Substitution rank scores may intentionally decrease for fallback-only evidence
or raw flags contradicted by energy evidence. This is the required scientific
correction, not a backward-compatible numeric preservation guarantee.
