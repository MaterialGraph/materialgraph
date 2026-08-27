# MG-IA-007 Change Impact — Selected Risk-Profile Attribution

## Status

Verified locally: 37 focused and downstream tests, 719 full-suite tests, Ruff,
and Git whitespace validation passed.

## Before

Computed material-risk results exposed scores and a generic latest-profile
selection label but omitted the identity, year, and persisted source of the
rows that supplied those numbers. Criticality exposed year only. Quality,
screening, sensitivity, substitution, and research-quality contracts retained
methodology and coverage metadata without selected-source attribution.

## After

Material-risk and criticality results identify the selected persisted profile
per element using profile ID, year, and source. Both responses also provide
stable aggregate lists of selected profile IDs, years, and sources.

The aggregate attribution is propagated through risk signals into quality,
candidate screening, sensitivity analysis, substitution analysis, and typed
research-quality evidence. Unknown evidence uses explicit empty lists.

## Impact

- Provenance: **Corrected** — numeric risk and criticality evidence identifies
  the stored profiles that supplied it.
- Multi-source visibility: **Added** — mixed datasets and years are visible in
  computed and downstream outputs.
- Reproducibility: **Improved** — profile identities can be cross-checked
  against persisted rows.
- Scientific scoring: **Unchanged** — selection, dimensions, aggregation,
  weighting, rounding, and ranking are unaffected.
- Evidence completeness: **Unchanged** — attribution does not upgrade partial
  or unknown evidence.
- API compatibility: **Additive** — existing fields retain their meaning;
  provenance fields are added.
- Database schema and stored data: **No change**.

## Scope decision

Per-element attribution preserves the exact profile-to-element mapping in the
primary computed outputs. Downstream decision outputs carry compact aggregate
summaries because they consume material-level risk or quality signals rather
than individual profile rows.

