# Task

Two review articles are attached as PDF files:

- HWA17: Hwang, Myung & Sun (2017), "Sodium-ion batteries: present and future", Chem. Soc. Rev. 46, 3529–3614.
- NOE21: Noerochim, Suwarno, Idris & Dipojono (2021), "Recent Development of Nickel-Rich and Cobalt-Free Cathode Materials for Lithium-Ion Batteries", Batteries 7, 84.

The attached file "ai_extraction_rules.md" contains a fixed set of extraction rules.
Apply those rules exactly as written to every page of both PDFs. Use only the two PDFs
and the rules; do not use other knowledge, other sources or the internet.

# Output format

Produce one CSV file (UTF-8, comma-separated, every value enclosed in double quotes,
first row = header). The header row must be exactly:

"record_id","source","location","evidence","cited_primary_study","parent_as_published","target_as_published","parent_composition_type","target_composition_type","direction_basis","relationship_type","characterization","confounders","decision","exclusion_reason","ambiguity_note"

One row per record, covering both sources. Formatting conventions for this CSV:

- An empty value means null: write "".
- `parent_composition_type` and `target_composition_type` are the two parts of the
  rules' `composition_type` field.
- `confounders`: tokens separated by ";" with no spaces, or "" if none.
- Page numbers in `record_id` and `location` use the page number of the PDF file itself, counting the first page of the file as 1 (not the journal's printed page numbers).
- Do not add the fields schema_version, extractor, parent_normalized or target_normalized;
  they are filled in later by software.
- Allowed values:
  - source: HWA17, NOE21
  - parent_composition_type / target_composition_type: family_no_composition, fixed_doped, fixed_fractional, fixed_integer, spatially_heterogeneous, unresolved_variable, variable_with_stated_value
  - relationship_type: cross_chemistry_analog, within_family_substitution
  - characterization: experimentally_evaluated_substitute, formula_or_structural_analog, proposed_replacement
  - decision: ambiguous, exclude, include
  - exclusion_reason: family_no_composition, morphology_or_surface_only, no_named_parent, not_directed, spatially_heterogeneous, synthesis_route_only, unresolved_variable

If the full CSV does not fit in one reply, stop at the end of a complete row and
continue from the next row when asked to continue, without repeating the header or
any row.
