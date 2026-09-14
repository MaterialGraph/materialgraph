# MG-DE Decision Register

| ID | Decision | Rationale | Status |
|---|---|---|---|
| MG-DE-D-001 | Use the `MG-DE-*` namespace under `docs/data/dataset-expansion/` | Keeps dataset engineering distinct from closed security and audit history | Approved |
| MG-DE-D-002 | Use approximately 1,000 representative materials as the first scale target | Large enough to expose density and query behavior while remaining operationally bounded | Approved |
| MG-DE-D-003 | Do not import into production during readiness or implementation discovery | Production data changes require completed gates and explicit authorization | Approved |
| MG-DE-D-004 | Preserve current curated materials as a deterministic regression cohort | Expansion must not silently alter established scientific behavior | Approved |
| MG-DE-D-005 | Treat source records, normalized records, and derived intelligence as distinct evidence layers | Supports provenance, reproducibility, and honest uncertainty | Proposed |
| MG-DE-D-006 | Prefer measured SQL narrowing over speculative indexing | Indexes should follow representative query plans | Proposed |
| MG-DE-D-007 | Use a manifest-first, resumable, chunked import lifecycle | Makes scope, reruns, failures, and reconciliation inspectable | Proposed |
| MG-DE-D-008 | Require explicit refresh and conflict semantics before updating existing materials | `mp_id` duplicate skipping alone cannot establish dataset correctness | Proposed |

Proposed decisions become approved only through a reviewed repository change.
