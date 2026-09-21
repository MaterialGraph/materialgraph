# Material Explorer contract review — 2026-09-21

Baseline: clean `main` at `158b19314`. Reviewed `MATERIALGRAPH_FRONTEND_UX_DESIGN.md`, `FRONTEND_ARCHITECTURE.md`, `FRONTEND_IMPLEMENTATION_ROADMAP.md`, `API_SCREEN_MAPPING.md`, `system_architecture.md`, `research_architecture.md`, and `scientific_principles.md` against registered routes and response schemas.

| Planned UX / architecture | Implemented backend contract | Milestone decision |
|---|---|---|
| Search by formula and source ID | `GET /api/v1/materials` is ID-ordered pagination (`limit` ≤ 100, `offset`); no server search | Filter loaded pages, allow direct numeric-ID lookup, disclose the boundary. |
| Evidence-backed property inspection, field provenance and coverage | `GET /api/v1/materials/{id}/detail` includes source, scalar properties and elements; no field provenance, evidence state, or coverage | Show source identity and raw nullable fields; explain missing provenance. Do not label inferred versus observed without evidence. |
| Candidate rank groups, partial status and reproducibility metadata | `GET /api/v1/materials/{id}/discovery/candidates` returns ordered candidates, score breakdown, explanations, warnings, soft constraint policy; no status, rank groups, coverage, dataset/methodology versions, or completeness flag | Preserve backend order; label position as “Item”, show warnings and limitations; no invented ties, status, coverage, or versions. |
| `discovery_path` vocabulary | The candidates response supplies encoded relationship labels, not ordered material/transition identities | Display these as backend relationship signals; do not depict them as a validated material transformation path. |
| Objective builder with strict constraints | Candidate endpoint accepts at most one avoid and one prefer element and both are soft; `POST /discovery/objective/explore` is a different contract | Bound this milestone to optional soft element preferences; defer objective builder and hard-constraint UX. |
| Full research workflow, methodology, saved investigation | These are later milestones or future contracts | Keep this as a read-only entry workflow, without saved-state claims. |
| Domain extensibility | Current core and documents distinguish generic reasoning from domain scientific validation | No battery-specific assumptions or defaults. |

The product docs remain a target specification; this bounded implementation exposes current gaps rather than changing backend semantics. Follow-up backend work should specify property-level provenance, version/completeness metadata, pagination search, and rank semantics before implementing the broader roadmap's status/tie/coverage UI.

The candidate `explanation` is currently a single backend-authored prose field. Some entries combine multiple composition heuristics and validation caveats into long semicolon-separated sentences. The explorer separates its existing sentences and clauses visually without rewriting claims; a future backend contract should expose distinct structured reasons, cautions, and evidence references so the UI can present a concise summary without parsing prose.
