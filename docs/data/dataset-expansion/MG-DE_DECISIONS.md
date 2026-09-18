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
| MG-DE-D-011 | Use 48 exact oxide, phosphate, sulfide, and silicate systems with an explicit 0.1 eV/atom energy-above-hull ceiling as the first real-source pilot | Exercises established substitution and family behavior across relevant mobile ions and transition metals without claiming domain-wide coverage | Superseded after the bounded first execution reached 3,000 records before Na traversal |
| MG-DE-D-012 | End MG-DE-005 at an immutable, offline-inspected manifest | Separates live-source discovery and legal/scientific review from all database mutation | Approved |
| MG-DE-D-013 | Require local PostgreSQL qualification and isolated Neon qualification before any production canary | Production uses Neon, but the live database must not be the first real-data test environment | Approved |
| MG-DE-D-014 | Preserve all 48 chemical systems and reduce the MG-DE-005 energy-above-hull ceiling to 0.05 eV/atom | Offline sensitivity retained 1,455 of the truncated 3,000 records, leaving material-count headroom for the 15 unvisited Na systems without weakening completeness or database-write gates | Verified by complete 1,727-record acquisition |
| MG-DE-D-015 | Accept the complete version 3 manifest only as input to MG-DE-006 scientific cohort review | Technical qualification establishes provenance and coverage, not scientific representativeness or authorization to import | Approved |
| MG-DE-D-016 | Separate deterministic cohort measurements from the MG-DE-006 scientific suitability decision | Integrity and distribution facts can be automated; usefulness and accepted imbalance must remain explicit reviewed judgment against the stated scope | Approved |

Proposed decisions become approved only through a reviewed repository change.
