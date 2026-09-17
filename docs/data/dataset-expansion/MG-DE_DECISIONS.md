# MG-DE Decision Register

| ID | Decision | Rationale | Status |
|---|---|---|---|
| MG-DE-D-001 | Use the `MG-DE-*` namespace under `docs/data/dataset-expansion/` | Keeps dataset engineering distinct from closed security and audit history | Approved |
| MG-DE-D-002 | Use approximately 1,000 representative materials as the first scale target | Large enough to expose density and query behavior while remaining operationally bounded | Approved |
| MG-DE-D-003 | Do not import into production during readiness or implementation discovery | Production data changes require completed gates and explicit authorization | Approved |
| MG-DE-D-004 | Preserve current curated materials as a deterministic regression cohort | Expansion must not silently alter established scientific behavior | Approved |
| MG-DE-D-005 | Treat source records, normalized records, and derived intelligence as distinct evidence layers | Supports provenance, reproducibility, and honest uncertainty | Approved |
| MG-DE-D-006 | Prefer measured SQL narrowing over speculative indexing | Indexes should follow representative query plans | Approved |
| MG-DE-D-007 | Use a manifest-first, resumable, chunked import lifecycle | Makes scope, reruns, failures, and reconciliation inspectable | Verified |
| MG-DE-D-008 | Require explicit refresh and conflict semantics before updating existing materials | `mp_id` duplicate skipping alone cannot establish dataset correctness | Implemented; verification pending |
| MG-DE-D-009 | Treat retirement as an inactive provenance state, not automatic material deletion | Preserves audit history and avoids destructive deletion before publication semantics are measured | Approved |
| MG-DE-D-010 | Qualify scale only in a disposable PostgreSQL database dedicated to MG-DE-004 | Prevents synthetic records and benchmark state from contaminating shared test or production data | Approved |
| MG-DE-D-011 | Use 48 exact oxide, phosphate, sulfide, and silicate systems with an explicit 0.1 eV/atom energy-above-hull ceiling as the first real-source pilot | Exercises established substitution and family behavior across relevant mobile ions and transition metals without claiming domain-wide coverage | Proposed for MG-DE-005 execution |
| MG-DE-D-012 | End MG-DE-005 at an immutable, offline-inspected manifest | Separates live-source discovery and legal/scientific review from all database mutation | Approved |
| MG-DE-D-013 | Require local PostgreSQL qualification and isolated Neon qualification before any production canary | Production uses Neon, but the live database must not be the first real-data test environment | Approved |

Proposed decisions become approved only through a reviewed repository change.
