# Service File Inventory Evidence

## Purpose

This ledger accounts for the supplied `app/services/` modules during the independent audit closure pass. A matched file is syntax-compiled and compared byte-for-byte with the version already traced through its callers, schemas, routes, and supplied tests. A changed file requires a fresh vertical review.

## Batch 1

| Service | Verification | Existing audit disposition |
|---|---|---|
| `candidate_comparison_service.py` | Compiles; exact match | Reviewed in Stack 06; deterministic tie preservation and missing-versus-filtered semantics confirmed. |
| `candidate_screening_service.py` | Compiles; exact match | Reviewed in Stack 02; deterministic ranking confirmed; participates in `MG-IA-010` baseline comparison and `OBS-010` pool-scaling review. |
| `graph_job_service.py` | Compiles; exact match | Reviewed in Stack 05; safe claim/terminal primitives confirmed; lifecycle evidence remains `OBS-016`. |
| `scenario_policy.py` | Compiles; exact match | Reviewed in Stacks 03 and 07; numeric explanations reconcile; heuristic risk semantics remain `OBS-011`. |
| `scenario_ranking_service.py` | Compiles; exact match | Reviewed in Stack 07; request-boundary defect remains `MG-IA-019`. |
| `sensitivity_analysis_service.py` | Compiles; exact match | Reviewed in Stack 02; aggregation inconsistency remains `MG-IA-010`. |
| `substitution_analysis_service.py` | Compiles; exact match | Reviewed in Stacks 02 and 04; stability-policy divergence remains part of `MG-IA-014`. |

No implementation delta, new finding, or new observation was established by Batch 1. The service inventory remains open for additional files.
