# MaterialGraph Frontend and UX Design Specification

**Version:** 0.1  
**Status:** Initial Architecture Specification  
**Scope:** Researcher-facing web application  
**Owner:** MaterialGraph

---

## 1. Purpose

This document defines how researchers interact with MaterialGraph before frontend implementation begins. It is the canonical product and interaction specification for the researcher-facing application.

The frontend is not a visual wrapper around APIs. It is the interface through which MaterialGraph communicates scientific identity, evidence, uncertainty, ranking semantics, graph relationships, pathways, and reproducibility.

The frontend must preserve the meaning of backend outputs. It may clarify information, but it must never strengthen, simplify, reorder, or visually exaggerate a scientific claim beyond the available evidence.

### 1.1 Objectives

The specification exists to:

- translate the MaterialGraph Research Cycle into a coherent interface;
- prevent isolated endpoint-driven screens;
- preserve scientific semantics across all views;
- make uncertainty, coverage, provenance, and limitations visible;
- identify missing backend contracts before React implementation;
- define screen responsibilities, state ownership, and API behavior;
- provide implementation-ready acceptance criteria.

### 1.2 Non-goals

This version does not define final branding, visual artwork, marketing copy, or production pixel specifications. It defines structure, behavior, semantics, and engineering constraints.

---

## 2. Product Vision

MaterialGraph should feel like a continuous scientific investigation workspace, not a database browser and not a collection of disconnected tools.

> MaterialGraph helps a researcher move from a scientific question to an evidence-backed material decision through a continuous, explainable, and iterative workflow.

The product should help users:

- begin with a research need, known material, domain research template, or
  already explicit scientific objective;
- formalize an incomplete problem without hiding introduced assumptions;
- define explicit constraints and preferences;
- inspect ranked and explainable alternatives;
- evaluate coverage and uncertainty;
- explore relationships and multi-hop pathways;
- compare candidates without false precision;
- save and refine investigations;
- collaborate without weakening reproducibility.

---

## 2. Core Design Philosophy

### 3.1 Scientific honesty before visual simplicity

The interface must not hide complexity when that complexity materially affects interpretation. Simplification is acceptable only when it preserves scientific meaning.

### 3.2 Research workflow before page hierarchy

Screens are stages within an investigation. Navigation and state must preserve context as users move between materials, candidates, evidence, pathways, and comparisons.

### 3.3 Explainability by default

Every recommendation, score component, property value, transition, and pathway must expose an explanation or provenance route where available.

### 3.4 Progressive disclosure

The first view should support rapid comprehension. Deeper reasoning, provenance, transformations, and caveats must remain inspectable without leaving the investigation.

### 3.5 Deterministic interaction

The same backend result and the same user state should produce the same visible scientific ordering and meaning. The frontend must not create hidden heuristics that alter scientific interpretation.

### 3.6 Unknown remains unknown

Missing, unavailable, inferred, estimated, and conflicting values must remain distinguishable. Unknown values must never be silently converted to zero, neutral, or complete.

### 3.7 Visual restraint

Color, size, position, line weight, animation, and ordering must not imply scientific superiority, confidence, feasibility, or causality unless backed by a defined field.

### 3.8 Workflow familiarity before novelty

The interface should fit recognizable scientific research practice before introducing new interaction patterns. MaterialGraph may make a workflow more connected, explicit, reproducible, or inspectable, but it must not create unfamiliar procedural steps merely to make the product appear distinctive.

Distinctiveness should come from how effectively the interface exposes research context, graph relationships, objective-sensitive reasoning, evidence, provenance, uncertainty, and investigation continuity. It should not come from forcing researchers into a novel process that conflicts with established scientific methods.

Where domain workflows differ, the interface should support a stable common investigation framework with domain-specific information and actions rather than pretend that every materials-science task has identical requirements.

A researcher-facing workflow should be treated as provisional until representative researchers or case studies confirm that it reflects a real task. If researcher testing reveals that the page flow conflicts with scientifically appropriate practice, the workflow should be revised rather than expecting the researcher to adapt to the application.

### 3.9 Domain-aware entry without hidden domain policy

The interface should support domain-specific vocabulary and research templates without encoding domain-specific scientific assumptions as invisible frontend behavior.

Where a validated domain extension or cross-domain context is active, the UI should make its identity, version, applicability, and important assumptions inspectable. Domain templates may provide familiar starting points, but researchers must be able to inspect and modify template-derived assumptions before execution.

A domain template is a versioned scientific artifact when it encodes objective defaults, constraints, proxies, validation requirements, or applicability conditions. It must not be treated as an unversioned convenience preset.

---

## 3. MaterialGraph Research Cycle

The user experience follows a continuous cycle:

```text
Research Need / Scientific Question
        ↓
Formalize Problem and Starting Context
        ↓
Define / Confirm Explicit Research Objective
        ↓
Generate Explainable Candidates
        ↓
Inspect Supporting Evidence
        ↓
Explore Relationships and Pathways
        ↓
Compare Alternatives
        ↓
Save Investigation
        ↓
Collaborate and Review
        ↓
Refine Objective
        ↺
```

### 4.1 Begin from research need or explicit context

The user may begin from a scientific question, known material, material family,
application context, prior investigation, domain research template, or an already
explicit objective. A precise objective should not be forced through an
unnecessary formalization wizard.

### 4.2 Formalize problem and define research objective

Where needed, the interface helps translate the research need into explicit hard
constraints, soft constraints, preferences, preservation requirements, target
context, unknown-handling policy, exploration bounds, and exploration policy.

Any assumption, proxy, or default introduced by a domain template or context must
be visible and editable before execution. If active extensions or contexts create
an explicit conflict, the UI must surface the conflict and require researcher
resolution rather than silently choosing a priority.

### 4.3 Generate candidates

MaterialGraph returns valid candidates with explicit ranking semantics, tie groups, score contributions, penalties, and coverage information.

### 4.4 Inspect evidence

The researcher inspects source data, normalization, inference rules, confidence, uncertainty, and limitations.

### 4.5 Explore pathways

The user studies graph relationships, direct substitutions, multi-hop transitions, alternative paths, and transition-level explanations.

### 4.6 Compare alternatives

Candidates are compared using observed, calculated, inferred, unavailable, and conflicting values without collapsing these states into a single number.

### 4.7 Save investigation

The objective, dataset snapshot, methodology version, results, selected candidates, pathways, notes, and decisions are stored together.

### 4.8 Collaborate

Researchers review, comment, cite, export, and share versioned investigations according to permission rules.

### 4.9 Refine objective

A saved investigation may be cloned or revised. Re-execution creates a new version rather than silently replacing prior results.

### 4.10 Design gate

Every frontend capability should improve at least one stage of the Research Cycle. Features that do not improve the cycle require explicit justification.

The Research Cycle itself is also subject to validation. Before a major workflow is treated as stable, the design should be checked against representative researcher practice and should identify:

- which existing scientific step the interaction supports;
- what friction or information loss MaterialGraph reduces;
- which established external method or tool remains authoritative;
- what provenance and investigation context must survive the transition;
- which domain-specific differences require an extension rather than a universal UI assumption.

---

## 4. Scientific UX Invariants

These rules are mandatory across all screens and components.

### 5.1 Tied rankings remain tied

The UI must never manufacture ranking precision. Equal scientific usefulness or equal backend rank values must be rendered as a tied-rank block.

```text
Rank 1 — Tied candidates
├── NaFePO4 — 94.95
├── Na3Fe(PO4)2 — 94.95
└── Na3Fe3(PO4)4 — 94.95
```

Secondary ordering is permitted only for navigation and must be labeled as non-scientific ordering.

### 5.2 Coverage accompanies every score

A numeric score cannot appear as if it represents complete characterization. The interface must display coverage and missing inputs near the score.

```text
Scientific usefulness: 94.95
Coverage: Partial — 8 of 11 expected inputs
Missing: synthesis evidence, temperature range, experimental stability
```

Canonical coverage labels:

- Complete coverage
- Partial coverage
- Inferred coverage
- Unknown coverage
- Conflicting evidence

### 5.3 Provenance is locally inspectable

Every supported property, score component, transition, and evidence item must provide an expandable inspection chain:

```text
Data source
    ↓
Raw value
    ↓
Normalization or transformation
    ↓
Rule or inference
    ↓
Score contribution or displayed conclusion
    ↓
Confidence, uncertainty, and limitations
```

Where provenance is unavailable, the UI must say so explicitly.

### 5.4 Partial computation is not application failure

A bounded computation that returns valid results is a successful request with incomplete scientific scope. It must not be shown as a generic error.

### 5.5 Missing does not equal zero

The UI must distinguish:

- zero;
- unknown;
- unavailable;
- not applicable;
- not requested;
- calculation failed.

### 5.6 Rejected candidates remain explainable

When technically and computationally feasible, excluded candidates should expose the hard constraint or validation rule that caused rejection.

### 5.7 Backend semantics are authoritative

The frontend may format values, but it must not:

- recompute scientific rank;
- reorder tied groups as if they were distinct ranks;
- reinterpret confidence;
- hide penalties;
- convert partial evidence into complete evidence;
- infer causality from correlation or graph adjacency.

### 5.8 Claim boundaries remain visible

The interface must distinguish:

- discovery opportunity;
- computational recommendation;
- evidence-supported candidate;
- experimentally validated material;
- production-ready material.

---

## 5. Target Users

### 6.1 Materials researcher

**Goals:** investigate alternatives, inspect evidence, generate hypotheses, compare candidates.  
**Needs:** transparent methodology, reproducibility, provenance, exportable results.

### 6.2 Battery engineer

**Goals:** identify cathode, anode, electrolyte, or substitution opportunities under practical constraints.  
**Needs:** composition preservation, criticality, stability, pathway plausibility, comparison.

### 6.3 Graduate student

**Goals:** explore material families, learn relationships, prepare research proposals, organize investigations.  
**Needs:** guided workflows, methodology explanations, clear caveats.

### 6.4 Principal investigator or professor

**Goals:** review hypotheses, compare investigations, guide teams, preserve scientific history.  
**Needs:** versioning, collaboration, citation, auditability.

### 6.5 Industrial R&D manager

**Goals:** prioritize candidates, review risk, coordinate teams, assess evidence readiness.  
**Needs:** access control, repeatable decisions, institutional reporting, export.

### 6.6 Platform or data engineer

**Goals:** integrate MaterialGraph APIs and understand methodology versions.  
**Needs:** stable contracts, identifiers, status models, reproducibility metadata.

---

## 6. Core Research Scenarios

The initial design must support at least these scenarios:

1. Replace lithium while preserving phosphate chemistry.
2. Prefer sodium-based alternatives.
3. Reduce cobalt or rare-earth exposure.
4. Find lower-criticality alternatives.
5. Preserve a chemical framework while replacing one element.
6. Explore direct and multi-hop substitution paths.
7. Compare tied candidates with different evidence coverage.
7. Save and rerun an investigation against a newer dataset snapshot.

The canonical reference flow is:

```text
Base material: LiFePO4
Avoid: Li
Prefer: Na
Preserve: Fe, P, O
Target family: phosphate
Max hops: 2
```

---

## 8. Information Architecture

### 8.1 Public surfaces

- Home
- Explore materials
- Public material page
- Example investigations
- Methodology
- Data and provenance
- Documentation
- Pricing or access information

### 8.2 Authenticated research surfaces

- Research workspace
- Objective builder
- Candidate results
- Candidate comparison
- Pathway explorer
- Investigation workspace
- Research history
- Shared investigations
- User settings

### 8.3 Institutional surfaces

- Team workspace
- Members and roles
- Shared collections
- Audit history
- Exports
- Administration

### 8.4 Primary navigation

```text
Explore | Investigations | Methodology | Documentation
```

Authenticated users additionally receive:

```text
Workspace | History | Shared | Account
```

### 8.5 Contextual investigation navigation

Within an investigation:

```text
Material → Objective → Candidates → Evidence → Pathways → Compare → Save
```

The current stage, completed stages, and available next actions must remain visible.

---

## 8. Route Model

Suggested initial route hierarchy:

```text
/
/materials
/materials/:materialId
/investigations/new
/investigations/:investigationId
/investigations/:investigationId/objective
/investigations/:investigationId/candidates
/investigations/:investigationId/compare
/investigations/:investigationId/pathways
/investigations/:investigationId/evidence
/history
/methodology
/data-provenance
/settings
```

Shareable investigation versions should use stable, immutable routes:

```text
/investigations/:investigationId/versions/:versionId
```

URL state should contain only shareable and reproducible navigation state. Temporary UI state such as open popovers should remain local.

---

## 9. Investigation State Model

Canonical investigation states:

```text
DRAFT_OBJECTIVE
READY_TO_RUN
RUNNING
COMPLETED
COMPLETED_PARTIAL
REVIEWING_CANDIDATES
COMPARING
EXPLORING_PATHWAYS
DECISION_RECORDED
ARCHIVED
SUPERSEDED
```

### 10.1 Version rules

- Editing an unexecuted draft updates the same draft.
- Executing a draft creates a result version.
- Re-running with changed data, methodology, or objective creates a new version.
- Historical versions remain readable and reproducible.
- Notes and decisions are versioned separately from scientific computation where appropriate.

### 10.2 Investigation artifact

An investigation should eventually persist:

```text
Investigation
├── Base material
├── Research objective
├── Dataset snapshot
├── Methodology version
├── Objective hash
├── Result status
├── Candidate results
├── Tied-rank groups
├── Selected candidates
├── Selected pathways
├── Comparison state
├── Evidence references
├── Researcher notes
├── Decision state
└── Audit history
```

---

## 11. Screen Specifications

### 11.1 Home page

#### Purpose

Explain what MaterialGraph does, establish scientific credibility, demonstrate a real investigation, and direct users into exploration.

#### Required sections

1. Hero with value proposition.
2. Search by formula or material identifier.
3. MaterialGraph Research Cycle.
4. Interactive or static reference investigation.
5. Explanation of deterministic and explainable reasoning.
6. Research scenarios.
7. Trust and methodology section.
8. Calls to action: explore material, view example investigation, inspect methodology.

#### Primary UX test

Can a researcher understand the product's scientific value and inspect a real example without creating an account?

---

### 11.2 Material workspace

#### Purpose

Provide a trustworthy scientific identity page and entry point into an investigation.

#### Required content

- formula and identifiers;
- material family and applications;
- composition;
- known properties;
- stability and quality indicators;
- criticality and risk;
- relationship overview;
- neighborhood preview;
- provenance access;
- start-investigation action.

#### Rules

- Missing values must be explicit.
- Every property should expose source and transformation where available.
- Material identity must remain usable even when scientific coverage is partial.

---

### 11.3 Objective builder

#### Purpose

Translate research intent into an explicit executable objective while preserving
the source of domain defaults, assumptions, and researcher modifications.

#### Domain-aware entry and templates

Where supported by validated backend contracts, the objective builder may offer:

- Scientific Domain Extension selection or inherited domain context;
- optional Cross-Domain Contexts;
- domain research templates;
- direct advanced objective entry for researchers who do not need a template.

The interface must display active domain, context, and template versions where
they materially affect the objective. Template-derived defaults must be visually
distinguishable from researcher-entered requirements until confirmed.

If composition creates incompatible hard constraints, contradictory assumptions,
or explicit applicability conflicts, the builder must show the conflict before
execution and preserve the researcher's resolution.

#### Fields

- research need / scientific question where present;
- base material or starting scientific context;
- active Scientific Domain Extension and version where applicable;
- active Cross-Domain Contexts and versions where applicable;
- research template and version where applicable;
- template assumptions / proxies and researcher modifications;
- avoid elements;
- prefer elements;
- preserve elements;
- target family;
- maximum hops;
- candidate limit;
- prefer lower criticality;
- require stable materials;
- advanced constraints.

#### Interaction rules

- Separate hard constraints from preferences.
- Explain conflicts before execution.
- Preserve user intent in a human-readable summary.
- Provide safe defaults without hiding their meaning.
- Display estimated search boundary before execution.

---

### 11.4 Candidate results

#### Purpose

Present ranked opportunities without false precision.

#### Required elements

- objective summary;
- reproducibility header;
- computation status;
- top-level boundary or partial-computation notice;
- tied-rank blocks;
- candidate cards or rows;
- constraint satisfaction;
- score contributions and penalties;
- coverage badge;
- evidence access;
- compare action;
- pathway action;
- save or select action.

#### Ranking rules

- Use backend rank groups.
- Never split ties visually.
- Show secondary browsing order only as non-scientific ordering.
- Display penalties and missing data near positive contributions.

---

### 11.5 Evidence panel

#### Purpose

Explain why a result exists and how strong the supporting information is.

#### Required tabs or sections

- Summary
- Score breakdown
- Constraint satisfaction
- Provenance
- Data coverage
- Limitations
- Methodology version

#### Interaction rules

- Open without losing the current results context.
- Support deep links to an evidence item where appropriate.
- Distinguish raw data, calculated data, and inferred signals.
- Never present an inferred value as directly observed.

---

### 11.6 Candidate comparison

#### Purpose

Support side-by-side scientific evaluation, especially for tied candidates.

#### Required behavior

- compare 2–5 candidates initially;
- show common and differing composition;
- display properties with evidence state;
- separate known, unknown, and not comparable values;
- compare rank contributions and penalties;
- compare risk, stability, pathway availability, and coverage;
- allow notes without altering scientific data.

---

### 11.7 Pathway explorer

#### Purpose

Show direct and multi-hop material transitions with inspectable validation and uncertainty.

#### Required behavior

- graph and ordered-path views;
- node selection;
- edge selection;
- path highlighting;
- alternative path selection;
- transition explanation drawer;
- max-depth and search-boundary indicators;
- legends defining every visual encoding;
- accessible tabular fallback.

#### Edge inspection

Selecting an edge must expose:

- source and target material;
- transition type;
- replaced, introduced, and preserved elements;
- scientific plausibility;
- validator outcome;
- evidence and provenance;
- limitations and uncertainty.

---

### 11.8 Investigation workspace

#### Purpose

Persist the Research Cycle as a versioned artifact.

#### Required areas

- investigation header;
- current objective;
- current result version;
- selected candidates;
- saved pathways;
- comparison state;
- evidence bookmarks;
- notes;
- decision record;
- rerun and refine actions;
- version history.

---

### 11.9 Research history

#### Purpose

Allow users to reopen, clone, compare, archive, and continue investigations.

#### Filters

- base material;
- objective;
- status;
- dataset version;
- methodology version;
- owner;
- date;
- shared or private.

---

### 11.10 Methodology and provenance pages

#### Purpose

Provide stable explanations of scoring, data sources, transformations, evidence states, limitations, and version history.

These pages supplement local provenance. They do not replace in-context explanations.

---

## 12. Reusable Scientific Components

Initial component inventory:

- `MaterialIdentityHeader`
- `MaterialCard`
- `ObjectiveSummary`
- `ConstraintChip`
- `TiedRankBlock`
- `CandidateCard`
- `ScientificScore`
- `CoverageBadge`
- `EvidenceStateBadge`
- `ScoreBreakdown`
- `EvidencePanel`
- `ProvenancePopover`
- `ScientificNoticeBanner`
- `PartialComputationBanner`
- `ReproducibilityHeader`
- `TransitionCard`
- `PathCard`
- `GraphNode`
- `GraphEdge`
- `GraphLegend`
- `ComparisonMatrix`
- `InvestigationTimeline`
- `VersionSelector`
- `DecisionRecord`

Each implementation must define props, states, accessibility behavior, and scientific constraints before coding.

---

## 13. Evidence-State Vocabulary

Canonical frontend and backend terms:

- `OBSERVED`
- `CALCULATED`
- `INFERRED`
- `ESTIMATED`
- `UNAVAILABLE`
- `NOT_APPLICABLE`
- `CONFLICTING`
- `STALE`
- `SUPERSEDED`

The same term must have the same meaning across all screens.

---

## 14. API-to-Screen Mapping Principles

Every computational endpoint must define:

- request purpose;
- owning screen;
- consuming components;
- success states;
- partial-computation states;
- empty result states;
- validation responses;
- dependency failures;
- retry rules;
- caching and invalidation;
- reproducibility metadata.

The frontend must not infer computation completeness from HTTP status alone.

---

## 15. Partial Computation Response Contract

A bounded or incomplete scientific computation is not necessarily a server failure.

When the request is valid and returned results are scientifically valid within an explicit boundary, the API should return HTTP `200` with an application-level status.

### 15.1 Example response

```json
{
  "status": "COMPLETED_PARTIAL",
  "reason": "PATHWAY_TRUNCATED_MAX_DEPTH",
  "message": "Search terminated after reaching the configured maximum depth.",
  "search_boundary": {
    "max_hops": 2,
    "max_hops_reached": 2
  },
  "result_metadata": {
    "is_complete": false,
    "returned_candidate_count": 5
  },
  "candidates": []
}
```

### 15.2 Required rendering

The result screen must show all valid returned data and a top-level notice above the result set:

> **Search boundary reached**  
> Search space was bounded at a maximum depth of 2. Valid pathways are shown, but additional pathways may exist beyond this search boundary.

### 15.3 Interaction rules

For `COMPLETED_PARTIAL`, the frontend must:

- display returned results;
- show a prominent notice;
- preserve backend boundary values;
- avoid claims such as “all pathways” or “complete result”;
- expose technical search details;
- offer a refine or broaden action where permitted;
- retain the partial status in saved investigations and exports.

### 15.4 Canonical computation statuses

- `COMPLETED`
- `COMPLETED_PARTIAL`
- `COMPLETED_NO_RESULTS`
- `REJECTED_INVALID_OBJECTIVE`
- `FAILED_DEPENDENCY`
- `FAILED_INTERNAL`

### 15.5 Suggested HTTP mapping

| Computation status | HTTP | Frontend treatment |
|---|---:|---|
| `COMPLETED` | 200 | Normal result |
| `COMPLETED_PARTIAL` | 200 | Valid result with boundary notice |
| `COMPLETED_NO_RESULTS` | 200 | Scientific empty state |
| `REJECTED_INVALID_OBJECTIVE` | 422 | Correctable objective validation |
| `FAILED_DEPENDENCY` | 503 | Recoverable service failure |
| `FAILED_INTERNAL` | 500 | Unexpected system failure |

### 15.6 Canonical reason codes

- `PATHWAY_TRUNCATED_MAX_DEPTH`
- `SEARCH_SPACE_LIMIT_REACHED`
- `CANDIDATE_LIMIT_REACHED`
- `COMPUTATION_TIME_BUDGET_REACHED`
- `INSUFFICIENT_GRAPH_CONNECTIVITY`
- `PARTIAL_EVIDENCE_COVERAGE`
- `UPSTREAM_DATA_UNAVAILABLE`

> Partial completion must be represented as bounded scientific knowledge, not as application failure.

---

## 16. Loading, Empty, Partial, and Error States

### 16.1 Loading

- distinguish initial page loading from computation execution;
- show known objective and boundary while running;
- avoid fake precision in progress percentages unless supplied by the backend;
- permit cancellation only where backend cancellation is supported.

### 16.2 Empty results

`COMPLETED_NO_RESULTS` means the objective executed correctly but found no valid candidates within the declared boundary.

The UI should show:

- the objective;
- constraints that may have limited results;
- the searched boundary;
- refinement suggestions;
- no generic failure language.

### 16.3 Partial evidence

A complete search can still return candidates with incomplete evidence. Search completeness and evidence completeness must be displayed separately.

### 16.4 Failures

Unexpected failures should provide:

- plain-language summary;
- correlation or request identifier where available;
- retry action if safe;
- preservation of the user's objective;
- link to technical details without exposing secrets.

---

## 17. Reproducibility Header

Every computational result and saved investigation version must expose a standardized reproducibility payload.

```ts
export interface ReproducibilityMetadata {
  datasetVersion: string;       // e.g. "2026.07"
  methodologyVersion: string;   // e.g. "discovery-ranking-v1.4"
  objectiveHash: string;        // e.g. "a8f9c2..."
  generatedAt: string;          // ISO-8601 timestamp
  materialGraphVersion: string; // e.g. "v1.9.6-remediated"
  computationStatus:
    | "COMPLETED"
    | "COMPLETED_PARTIAL"
    | "COMPLETED_NO_RESULTS";
}
```

Every computational component rendered inside an investigation screen must receive this metadata through a standardized prop contract rather than reconstructing it from unrelated query state.

```ts
export interface ReproducibleComponentProps {
  reproducibility: ReproducibilityMetadata;
}
```

The `ReproducibilityHeader` renders the compact form:

```text
Dataset snapshot: 2026.07
Methodology: discovery-ranking-v1.4
Objective hash: a8f9c2…
Generated at: 2026-07-30T09:15:00Z
MaterialGraph version: v1.9.6-remediated
Computation status: COMPLETED_PARTIAL
```

The compact header expands into full technical metadata. Field names, status values, and formatting must remain consistent across candidate, comparison, pathway, graph, export, and saved-version surfaces.

---

## 18. Graph Visualization Rules

### 18.1 Required semantics

Every node and edge encoding must have a legend. No encoding may imply unsupported scientific meaning.

### 18.2 Interaction

- selecting a node opens material context;
- selecting an edge opens transition evidence;
- selecting a path highlights only that path;
- tied paths remain tied;
- search boundary remains visible;
- graph state should be recoverable through investigation context.

### 18.3 Accessibility

Every graph must have a navigable tabular or ordered-path alternative. Keyboard users must be able to inspect nodes and transitions.

### 18.4 Graph library allocation

MaterialGraph uses two graph libraries because pathway explanation and dense network exploration have different interaction and performance requirements.

#### React Flow — Pathway Explorer

React Flow is the default renderer for bounded, pathway-oriented views such as:

- ordered substitution paths;
- K-best pathway comparison;
- objective-specific multi-hop traces;
- DAG-like or near-linear `A → B → C` explanations.

React Flow is selected here because native React nodes make it straightforward to embed MaterialGraph components directly inside pathway nodes and edge overlays, including:

- `TransitionCard`;
- `CoverageBadge`;
- `EvidenceStateBadge`;
- inline `ProvenancePopover`;
- partial-boundary markers;
- tied-path labels.

Pathway views must remain deliberately bounded. React Flow must not be used as the default renderer for dense material-family networks where DOM node count would impair performance.

#### Cytoscape.js — Neighborhood and Community Explorer

Cytoscape.js is the default engine for:

- material neighborhoods;
- community and family exploration;
- dense relationship networks;
- centrality and graph-metric overlays;
- networks expected to exceed approximately 100 visible nodes.

Cytoscape.js is selected for its graph-oriented data model, mature layouts, filtering, and support for graph analytics. When profiling shows that canvas rendering is insufficient for the target graph density, the implementation may use a compatible WebGL-capable renderer or extension. WebGL is an escalation path, not an assumed property of the core Cytoscape.js renderer.

#### Shared requirements

Both renderers must provide:

- identical scientific node and edge semantics;
- accessible tabular or ordered-path alternatives;
- inspectable provenance;
- documented legends;
- URL- or investigation-recoverable selection state;
- export behavior that preserves scientific labels and boundary notices.

---

## 19. Accessibility

Minimum target: WCAG 2.2 AA where applicable.

Requirements:

- full keyboard navigation;
- visible focus states;
- semantic headings and landmarks;
- labels for all scientific controls;
- non-color indicators for status and uncertainty;
- table alternatives for graphs;
- screen-reader descriptions for score and coverage relationships;
- motion reduction support;
- sufficient contrast;
- responsive layouts that preserve evidence access.

---

## 20. Responsive Design

Desktop is the primary research environment, but core inspection and review must work on tablets and mobile devices.

### Desktop

- multi-panel workspace;
- side evidence drawer;
- comparison matrix;
- graph plus details.

### Tablet

- collapsible panels;
- sequential comparison;
- graph with bottom-sheet evidence.

### Mobile

- material lookup;
- investigation review;
- candidate inspection;
- evidence and provenance;
- limited graph exploration using ordered path lists.

The objective builder must remain functional on small screens, but dense comparative analysis may use an explicit desktop recommendation.

---

## 21. Security and Privacy

The frontend specification must account for:

- secure authentication;
- role-based authorization;
- private-by-default investigations;
- stable share permissions;
- no public indexing of private investigations;
- safe rendering of user notes;
- protection of tokens and secrets;
- audit history for shared and institutional actions;
- export authorization;
- methodology and dataset identifiers in shared artifacts.

---

## 22. Analytics and Privacy

Product analytics should measure workflow health without collecting unnecessary scientific content.

Useful events include:

- material search completed;
- objective created;
- computation executed;
- partial boundary encountered;
- evidence opened;
- candidate compared;
- pathway inspected;
- investigation saved;
- objective refined.

Do not record private objective contents, notes, unpublished material details, or evidence text unless explicitly justified and consented to.

---

## 23. Phased Frontend Roadmap

### Phase 1 — Trust and identity baseline

**Screens:** Home, material search, material workspace, methodology, provenance.  
**Goal:** Verify material identity and source information within two interactions.

### Phase 2 — Core investigation cycle

**Screens:** Research entry / problem formalization, objective builder, candidate results, evidence panel.  
**Goal:** Complete the canonical LiFePO4 sodium/phosphate investigation with tied ranking and coverage preserved, while ensuring any formalization assumptions remain explicit and bypassable for a precise objective.

### Phase 3 — Comparative and multi-hop exploration

**Screens:** Candidate comparison, pathway explorer, graph views.  
**Goal:** Inspect transition acceptance and compare tied candidates.

### Phase 4 — Versioned investigations

**Screens:** Investigation workspace, history, version comparison, notes.  
**Goal:** Reopen and rerun investigations reproducibly.

### Phase 5 — Collaboration and institutional scale

**Screens:** Shared investigations, comments, team workspaces, permissions, exports, audit history.  
**Goal:** Support collaborative scientific review without weakening reproducibility.

---

## 24. UX Acceptance Criteria

The frontend architecture is implementation-ready when:

- every primary workflow maps to the Research Cycle;
- problem-formalization assumptions are inspectable and editable;
- active domain/context/template versions are visible where they affect reasoning;
- explicit composition conflicts are surfaced rather than silently resolved;
- every backend status maps to an explicit UI state;
- tied ranks remain tied;
- every score has coverage context;
- evidence state vocabulary is consistent;
- provenance is accessible locally;
- partial computation is distinguished from failure;
- graph encodings have documented meaning;
- every result exposes reproducibility metadata;
- unknown values remain unknown;
- all major screens define loading, empty, partial, and error states;
- accessibility requirements are documented;
- private research state has explicit security rules.

---

## 25. Design Review Checkpoints

### Scientific review

- Does the UI preserve backend semantics?
- Are ties, unknowns, uncertainty, and partial evidence visible?
- Are claims bounded by available evidence?
- Is provenance inspectable?

### Research workflow review

- Which stage of the Research Cycle does the feature support?
- What decision does it help the researcher make?
- Is the next meaningful action clear?

### Engineering review

- Is state ownership defined?
- Does the API contract support the screen?
- Are partial and failure states deterministic?
- Is the component reusable and testable?

---

## 26. Open Design Decisions

1. URL-state boundaries for filters, selection, and comparison.
2. Authentication and institutional identity provider strategy.
3. Final investigation persistence schema.
4. Export formats and citation metadata.
5. Public investigation indexing policy.
6. Frontend state management beyond server-state caching.
7. Design token and branding direction.
8. Dataset and methodology version comparison UX.
9. Domain/context/template selection and version-comparison UX after backend
   extension contracts are validated.
10. Conflict-resolution UX for composed objectives.
11. Backend standardization of partial computation contracts.

---

## 27. Deferred Capabilities

- notebook-style investigations;
- publication-ready report generation;
- institutional review workflows;
- general third-party plugin marketplace or unrestricted plugin architecture;
- literature summarization;
- LLM-assisted note organization;
- simulation integration;
- offline investigation review.

Any future AI capability must remain clearly separated from deterministic scientific ranking and must expose source, uncertainty, and claim boundaries.

---

## 28. Canonical Design Principle

> MaterialGraph must preserve the scientific meaning, uncertainty, provenance, and ranking semantics produced by the backend. The interface may clarify scientific information, but it must never strengthen, simplify, reorder, or visually exaggerate a claim beyond the evidence available.
