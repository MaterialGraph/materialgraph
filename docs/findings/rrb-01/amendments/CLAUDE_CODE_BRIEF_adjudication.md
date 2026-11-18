# Claude Code brief: RRB-01 adjudication (AMD-002), one batch per task

Send this brief once per batch, changing only BATCH and ROWS:
- Batch 1: ADJ-001 to ADJ-025
- Batch 2: ADJ-026 to ADJ-050
- Batch 3: ADJ-051 to ADJ-075
- Batch 4: ADJ-076 to ADJ-093

---

TASK: RRB-01 adjudication, BATCH <n>, rows <ADJ-xxx> to <ADJ-yyy>

Context
- You are adjudicating records produced by two AI extraction runs against two review
  articles. Work ONLY from these files in the repository:
  - docs/findings/rrb-01/ai-extraction-package/ai_extraction_rules.md (the rules)
  - docs/findings/rrb-01/sources/Sodium-ion batteries_ present and future - c6cs00776g.pdf (source HWA17)
  - docs/findings/rrb-01/sources/batteries-07-00084-v2.pdf (source NOE21)
  - docs/findings/rrb-01/comparison/adjudication.xlsx (the rows; read only)
- Page numbers in record IDs are PDF page indices (first page of the file = 1).
- Do not read any other file in docs/findings/rrb-01 (no run logs, amendments,
  protocol rationale, or previous discussions). Do not use the internet.
- Do not modify adjudication.xlsx, the run files, or anything else in the repository
  except the output file below.

Output file
- docs/findings/rrb-01/comparison/adjudication_ai.xlsx. If it does not exist (batch 1),
  create it as an exact copy of adjudication.xlsx. Fill ONLY these columns, ONLY for the
  rows in this batch: founder_decision, founder_exclusion_reason, audit_result,
  error_type, rule_applied, reason, assistance_used. Do not change any other cell.

For each row, read the cited page and answer four checks
1. Is the evidence quote on the cited page? (Ignore differences in whitespace, line breaks,
   end-of-line hyphenation, ligatures and subscript rendering.)
2. Do the recorded compositions appear in that passage as published?
3. Does the passage explicitly link the two compositions (e.g. "replaced by",
   "substituted", "instead of", "analog of", "doped with") and state which is the original?
4. Is either composition a variable, placeholder, family, or spatially heterogeneous material?
For rows with both a Run A and a Run B record, check each record's quote.

Decisions
- category unmatched_a / unmatched_b / normalization_failure:
  - founder_decision = include only if a parent is named, checks 1–3 are yes and check 4 is no.
  - founder_decision = exclude only when the text clearly shows one condition; put the reason
    in founder_exclusion_reason using exactly one of: no_named_parent, not_directed,
    synthesis_route_only, morphology_or_surface_only, spatially_heterogeneous,
    unresolved_variable, family_no_composition.
  - Otherwise founder_decision = ambiguous. If the quote is not on the cited page:
    ambiguous, and name any other page where you found it.
- category audit_joint_include:
  - audit_result = confirmed if checks 1–3 are yes and check 4 is no for the pair.
  - Otherwise audit_result = error; error_type = one of evidence_not_found,
    composition_mismatch, no_explicit_direction, variable_or_family, other; and set
    founder_decision to the corrected decision.
- Every row: rule_applied = the rule from ai_extraction_rules.md that decided it;
  reason = "p.<n>: check1 <yes/no>; check2 <yes/no>; check3 <yes/no>; check4 <yes/no>; <one
  short sentence>"; assistance_used = "performed by AI: <your model identifier>".
- Do not guess. When the text does not settle a row, use ambiguous.

Report (in this conversation)
- Your model identifier.
- For this batch: counts of include / exclude / ambiguous, confirmed / error, and every
  row where the quote was not found on the cited page.
- The SHA-256 of adjudication_ai.xlsx after saving.

STOP after the report. Do not start the next batch.
