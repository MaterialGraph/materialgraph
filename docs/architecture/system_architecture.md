# MaterialGraph System Architecture

## Overview

MaterialGraph is a layered, deterministic knowledge-graph platform for
materials research assistance and decision support.

It converts source data into inspectable computational opportunities through
explicit graph construction, scoring, objective evaluation, and comparison.
The system does not establish scientific validity; researchers remain
responsible for interpretation and external validation.

---

## Intelligence Layers

```mermaid
flowchart TD
    A["Materials source data"] --> B["Graph foundation"]
    B --> C["Foundation intelligence"]
    C --> D["Discovery intelligence"]
    D --> E["Knowledge-graph intelligence"]
    E --> F["Research and evidence intelligence"]
    F --> G["Researcher review and external validation"]
```

### Research Experience Architecture

The intelligence layers should be exposed through the **MaterialGraph Research
Cycle**: start from a material, define an objective, generate explained
candidates, inspect evidence, explore pathways, compare alternatives, save and
share the investigation, and refine the objective.

This cycle is a researcher-facing orchestration boundary rather than a new
scientific-computation layer. It should compose canonical outputs from the
existing services, preserve investigation context and provenance, and avoid
reimplementing scoring, constraints, evidence interpretation, or graph
semantics in the frontend or workspace layer.

```mermaid
flowchart LR
    A["Material and objective"] --> B["Canonical intelligence services"]
    B --> C["Explainable research workspace"]
    C --> D["Saved investigation context"]
    D --> E["Collaboration and review"]
    E --> F["Refined objective"]
    F --> B
```

### Graph Foundation

**Purpose**

- represent materials and explicit relationships;
- preserve source identifiers and provenance;
- construct graph nodes and edges;
- provide persistence and canonical composition data.

### Foundation Intelligence

**Question:** What is known or computed about an individual material and its
immediate relationships?

**Implemented services**

- Material Graph;
- Neighborhood;
- Material Families;
- Similarity;
- Recommendation;
- Criticality;
- Scenario Policies.

### Discovery Intelligence

**Question:** Which computational opportunities warrant investigation?

**Implemented services**

- Discovery Candidates;
- Explainable Scoring and Warnings;
- Substitution Paths;
- Discovery Chains;
- Path Ranking;
- Research-Objective Exploration.

Discovery outputs are ranked hypotheses derived from current data and encoded
rules—not validated discoveries.

### Knowledge-Graph Intelligence

**Question:** How are materials connected within MaterialGraph's model?

**Implemented services**

- Graph Builder and Traversal;
- BFS, DFS, Dijkstra, and K-best path workflows;
- Graph Analytics;
- Community Detection and Community Intelligence;
- Ranked Subgraph Exploration;
- Material Quality;
- Node and Edge Intelligence.

Graph relationships and communities are model constructs unless supported by
separate external validation evidence.

### Research and Evidence Intelligence

**Question:** How can multiple opportunities be compared for a research
objective?

**Implemented services**

- Research-Objective Exploration and Evaluation;
- Scientific Pathway Analysis;
- Research Opportunity Analysis;
- Comparative Research Intelligence;
- Endpoint-Sensitive Research Ranking;
- Evidence Summaries;
- Missing-Evidence and Weak-Assumption Reporting;
- Validation Priorities and Evidence Readiness.

Internal support, data completeness, external evidence coverage, validation
readiness, and scientific-validation status must remain separate concepts.

### Scientific Knowledge Layer

**Planned purpose**

- store attributed literature, observations, simulations, and experiments;
- preserve successful, unsuccessful, inconclusive, and conflicting results;
- preserve investigation and validation history;
- support canonical/shared, organization-private, project/workspace, and other
  explicitly scoped research evidence;
- preserve contributor, source, access-scope, review, disagreement, and version
  provenance;
- support review, disagreement, and versioned knowledge enrichment.

Evidence scope and canonical scientific status are separate dimensions. Private
or project-scoped evidence may inform authorized investigations without silently
becoming shared MaterialGraph knowledge. This layer must not silently alter
deterministic computation. Reviewed evidence may influence an explicitly
versioned dataset or policy only through an explicit governance process.

### Planned Scientific Compute Boundary

MaterialGraph should integrate with specialized scientific computation without
becoming a general-purpose simulator. Research Intelligence may identify a
validation need and Physical Modeling Readiness may determine whether required
inputs and assumptions are sufficiently specified. Execution should then occur
through an adapter or scientific-task contract appropriate to the external or
dedicated workflow.

```mermaid
flowchart TD
    A["MaterialGraph Research Intelligence"] --> B["Physical Modeling Readiness"]
    B --> C["Scientific task / adapter contract"]
    C --> D["External or dedicated scientific workflow"]
    D --> E["Versioned scientific result"]
    E --> F["Scientific Knowledge Layer"]
    F --> G["Researcher review and continued investigation"]
```

Potential workflows may include DFT and electronic-structure calculations,
molecular dynamics, structural analysis, spectroscopy-oriented workflows,
thermodynamic or electrochemical modeling, and other domain computation where a
validated research use case requires them.

Scientific task and result contracts should preserve, where applicable:

- material and structure identity;
- research objective and requested property or validation question;
- engine, software version, and adapter version;
- parameters, conditions, configuration, and assumptions;
- input and output artifacts;
- execution and convergence status;
- uncertainty and warnings;
- provenance and validation status.

External results enter MaterialGraph as attributed computational evidence.
Execution success or numerical convergence must not automatically be interpreted
as physical validity or experimental agreement.

### Future Research Orchestration Boundary

The Research Experience Architecture may later coordinate deterministic
MaterialGraph reasoning, evidence retrieval, Physical Modeling Readiness,
external scientific computation, and researcher review. Planning and
orchestration are not themselves new scientific authorities.

```mermaid
flowchart TD
    A["Research question"] --> B["Planning / orchestration"]
    B --> C["Canonical MaterialGraph reasoning"]
    B --> D["Evidence retrieval"]
    B --> E["Scientific compute boundary"]
    C --> F["Research context"]
    D --> F
    E --> F
    F --> G["Researcher review"]
```

A future AI or rule-based planner should call and compose canonical services
rather than recreate scoring, constraints, evidence interpretation, graph
semantics, or domain computation. This preserves the separation between research
planning, deterministic reasoning, scientific execution, and researcher
judgement.

---

## Cross-Cutting Architecture

| Concern | Architectural requirement |
|---|---|
| Provenance | Trace outputs to source data, rules, configuration, and software version |
| Validation status | Separate engineering verification from researcher, computational, and experimental validation |
| Uncertainty | Preserve unknown values; never treat missing evidence as favourable |
| Canonical semantics | Reuse one implementation for composition, scoring, constraints, evidence, and ties |
| API contracts | Validate inputs consistently and expose explicit response schemas |
| Persistence | Preserve graph, evidence, and job-state integrity |
| Background jobs | Provide atomic claiming, consistent transitions, ownership, and bounded execution |
| Security | Enforce authentication, authorization, resource ownership, and bounded inputs |
| Observability | Record failures, performance, version context, and audit-relevant events |
| Performance | Optimize without changing graph or scientific semantics |

---

## Runtime Architecture

### Data Persistence Strategy

PostgreSQL is MaterialGraph's authoritative system of record. The current
scientific core depends on well-defined relationships, joins, constraints,
transactions, deterministic querying, indexing, and versioned schema
migrations.

The following records remain in PostgreSQL:

- materials, elements, and normalized material compositions;
- material relationships and graph persistence;
- criticality and risk data;
- discovery, recommendation, and objective-evaluation records;
- graph-job state and other transactional application records;
- canonical provenance, configuration, and validation-status records.

MaterialGraph may later introduce MongoDB as a secondary document store when a
validated product feature has a genuinely document-oriented access pattern.
Candidate workloads include:

- saved research sessions containing objectives, generated results,
  visualization state, notes, and bookmarks;
- user workspaces, collections, dashboards, and saved searches;
- optional AI-assistant conversations, tool outputs, and interaction metadata;
- immutable or versioned graph-result snapshots;
- heterogeneous metadata ingested from literature, patent, chemical, or
  materials-data sources.

MongoDB would complement PostgreSQL rather than replace it. Canonical material,
relationship, criticality, discovery, and recommendation data must not be
duplicated into a second competing system of record.

Before adopting MongoDB, the proposed workload must be evaluated against
PostgreSQL JSONB, Redis, object storage, and other simpler alternatives. The
decision should consider query patterns, consistency requirements, retention,
cost, backup and recovery, observability, security, operational burden, and
data ownership. Storing a value as JSON is not by itself sufficient
justification for adding a document database.

Heterogeneous scientific metadata must retain source attribution, source-schema
version, ingestion version, normalization status, validation status, and links
to canonical PostgreSQL entities regardless of its storage engine. Cached or
derived documents must record their source-data, configuration, and software
versions and must never become an untracked authority for scientific outputs.

```mermaid
flowchart TD
    A["React frontend"] --> B["FastAPI backend"]
    B --> C["PostgreSQL system of record"]
    B -. "Future, workload-gated" .-> D["MongoDB document store"]
    C --> E["Canonical scientific and transactional data"]
    D --> F["Sessions, workspaces, conversations, snapshots, source metadata"]
```

### Backend

- Python;
- FastAPI;
- SQLAlchemy;
- Pydantic v2;
- NetworkX;
- Alembic.

### Data and Infrastructure

- PostgreSQL / Neon PostgreSQL;
- AWS EC2;
- Nginx;
- systemd;
- Docker for local development.

### Verification

- pytest;
- deterministic regression tests;
- API and production endpoint checks;
- architecture and implementation audit.

Production endpoint verification confirms only the tested request, deployed
version, and dataset. It does not establish complete regression coverage,
concurrency safety, authorization correctness, large-dataset performance, or
scientific validity.

---

## Current Engineering Status

The listed intelligence services are implemented, but the project is undergoing
reconciled architecture and implementation audit remediation.

The canonical audit register contains 94 findings: 23 resolved within their
documented engineering scope and 71 requiring remediation or a policy decision
at the time of this architecture update.

MaterialGraph has not yet completed independent materials-researcher review,
literature-backed case studies, DFT cross-validation, or experimental
validation.

---

## Planned Architecture

- Research Gap Analysis and Hypothesis Exploration;
- versioned Scientific Knowledge Layer with explicit evidence scope and canonicalization governance;
- Physical Modeling Readiness and adapter-oriented external scientific compute integration;
- future research orchestration that composes canonical reasoning, evidence, and scientific compute without duplicating their semantics;
- optional workload-validated document storage for research sessions,
  workspaces, AI conversations, snapshots, or heterogeneous source metadata;
- stronger authentication, authorization, and job ownership;
- Go GraphCompute Worker;
- Rust graph engine;
- distributed, bounded graph jobs;
- graph embeddings and carefully governed ML integration.