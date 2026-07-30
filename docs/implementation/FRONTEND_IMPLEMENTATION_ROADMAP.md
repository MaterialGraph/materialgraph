# MaterialGraph Frontend Implementation Roadmap

**Version:** 0.1  
**Status:** Planning

## Milestone 0 — Contract readiness

Before React implementation:

- standardize computation status payloads;
- define rank-group fields;
- define evidence-state vocabulary;
- expose coverage metadata;
- expose provenance links or embedded provenance;
- expose dataset and methodology versions;
- define stable investigation identifiers.

## Milestone 1 — Trust and identity baseline

### Deliverables

- application shell;
- public home page;
- material search;
- material workspace;
- methodology page;
- provenance interactions;
- loading, missing, and error states.

### Exit criteria

- property source available within two interactions;
- missing values distinct from zero;
- observed and inferred values visually distinct;
- canonical material lookup works end to end.

## Milestone 2 — Core investigation cycle

### Deliverables

- objective builder;
- objective validation;
- candidate results;
- tied-rank blocks;
- coverage badges;
- evidence panel;
- partial-computation banners.

### Exit criteria

- LiFePO4 sodium/phosphate reference investigation completes;
- tied candidates remain tied;
- partial search and partial evidence are independently visible;
- score contributions and penalties are inspectable.

## Milestone 3 — Comparison and pathways

### Deliverables

- candidate comparison matrix;
- direct pathway view;
- multi-hop explorer;
- transition evidence drawer;
- accessible ordered-path fallback;
- graph performance controls.

### Exit criteria

- transition acceptance or rejection is inspectable;
- graph encodings have legends;
- alternative and tied paths preserve backend semantics;
- max-depth boundaries remain visible.

## Milestone 4 — Versioned investigations

### Deliverables

- authentication;
- save investigation;
- reopen investigation;
- objective refinement;
- rerun as new version;
- history and version comparison;
- notes and decision records.

### Exit criteria

- historical results remain reproducible;
- dataset or methodology updates create new versions;
- notes never overwrite scientific evidence.

## Milestone 5 — Collaboration and institutions

### Deliverables

- sharing;
- comments and review;
- team workspaces;
- roles and permissions;
- exports and citations;
- audit history.

### Exit criteria

- private investigations remain private;
- shared versions are stable;
- authorship and review actions are auditable;
- institutional permissions do not obscure individual contribution.

## Implementation Sequence

```text
Contract review
    ↓
Low-fidelity wireframes
    ↓
Component specifications
    ↓
Screen implementation
    ↓
Scientific UX review
    ↓
Accessibility and responsive review
    ↓
API integration tests
    ↓
Documentation update
```
