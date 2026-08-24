# Documentation-to-Implementation Evidence

## Batch 1 — root README and project-direction document

Reviewed the complete root `README.md` and `docs/architecture/what_should_be_materialgraph.md` against the independently inspected implementation, routes, configuration, tests, and current audit evidence. References in these documents to the earlier 94-finding audit were not used as an independent-audit checklist or reconciliation source.

## Root README

### Confirmed inconsistencies

- The current-capability list presents PostgreSQL-backed graph-job routes as available, while the versioned router deliberately does not mount them and API/OpenAPI tests assert their absence (`MG-IA-023`).
- The Quick Start runs Alembic, Materials Project import, and Uvicorn without first configuring required `DATABASE_URL` and import-required `MATERIALS_PROJECT_API_KEY` (`MG-IA-024`).

### Positive checks

- Discovery is explicitly defined as deterministic computational exploration rather than experimental discovery, novelty, synthesis feasibility, or validated performance.
- Structural preservation, transformation feasibility, physical performance, and scientific correctness are explicitly disclaimed.
- Determinism is conditioned on input, source-data, configuration, software, and ordering versions and is not presented as scientific validity.
- Unknown evidence is not described as favorable evidence; internal support is separated from external validation.
- Implemented and future scientific knowledge/evidence layers are generally distinguished.
- The validation table clearly states that literature case studies, independent researcher review, DFT cross-validation, and experimental validation are incomplete.
- Technology-stack claims align with the supplied implementation and deployment context.

The README's package/capability label `v1.9.6` remains within `OBS-001` pending the canonical versioning policy. Its reference to the prior 94-finding register is historical project status, not evidence used during this independent pass.

## `what_should_be_materialgraph.md`

### Confirmed inconsistency

The objective-semantics section says current execution forwards only the first avoid and first prefer element. Current objective, chain, ranking, and exploration services propagate and iterate full collections (`MG-IA-025`).

### Positive checks

- The document is explicitly a direction/principles artifact rather than an implemented feature list.
- Future physical modeling, external compute, private research context, polyglot compute, validation-priority intelligence, and staged commercialization are consistently marked as future directions or gated proposals.
- It distinguishes shared canonical knowledge from researcher objectives and private context.
- It treats search-space construction as scientifically meaningful and distinguishes bounded production safety from exhaustive scientific coverage.
- It distinguishes composition overlap from structural preservation and prevents repeated downstream reuse from becoming independent evidence.
- It separates internal deterministic support, external evidence, readiness, numerical convergence, model validity, and experimental agreement.
- It preserves genuine ties, unknown evidence, uncertainty, provenance, and researcher authority.
- It frames the Research Cycle as a hypothesis requiring representative researcher validation, not a universal scientific workflow.

Specific reference-case formulas and numeric scores were not independently reproduced in this workspace and are therefore not treated as verified current-output evidence. They remain documentation claims pending a pinned database snapshot and captured execution record.

## Disposition

Three documentation defects are confirmed (`MG-IA-023`–`MG-IA-025`). The broader scientific direction is notably conservative and aligned with the project's stated honesty and researcher-in-the-loop principles. Additional architecture, research, guide, deployment, roadmap, and technical-notes documents remain to be compared before documentation closure.
