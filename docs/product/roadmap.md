# MaterialGraph Roadmap

## Vision

MaterialGraph is evolving into a deterministic, explainable research-assistance
knowledge graph. It computationally explores and prioritizes material
opportunities while researchers retain authority over scientific interpretation
and validation.

The roadmap separates implementation, engineering verification, audit
remediation, researcher review, and scientific validation. A feature may be
implemented without being scientifically validated.

---

## Status Definitions

| Status | Meaning |
|---|---|
| Implemented | Code or endpoint exists |
| Tested | Relevant automated tests exist and pass in the tested scope |
| Audited | Reviewed against intended architecture and semantics |
| Remediated | A specified audit defect was corrected and verified within scope |
| Researcher-reviewed | Evaluated by relevant independent domain researchers |
| Scientifically validated | Supported by appropriate literature, structural, computational, or experimental validation |

---

## Implemented Capability Baseline — v1.9.6

### Foundation Intelligence

- Material Graph Foundation;
- Material Neighborhood and Family Intelligence;
- Similarity and Recommendation Engines;
- Criticality Analysis;
- Scenario Policy Engine.

### Discovery Intelligence

- Discovery Candidate Engine;
- Explainable Discovery Scoring and Warnings;
- Substitution Path Engine;
- Multi-Hop Discovery Chains;
- Discovery Path Ranking;
- Research-Objective Exploration.

### Knowledge-Graph Intelligence

- Graph Builder and Traversal;
- BFS, DFS, Dijkstra, and K-best path workflows;
- Graph Analytics;
- Community Detection and Intelligence;
- Ranked Subgraph Exploration;
- Material Quality;
- Node and Edge Intelligence;
- PostgreSQL-backed graph-job routes and persistence.

### Research and Evidence Intelligence

- Scientific Pathway Analysis;
- Research Opportunity Analysis;
- Objective Evaluation;
- Comparative Research Intelligence;
- Endpoint-Sensitive Research Ranking;
- Evidence Summaries and Attribution;
- Missing-Evidence and Weak-Assumption Reporting;
- Validation Priorities and Evidence Readiness.

These capabilities are implemented and partly tested. They are not thereby
independently scientifically validated.

---

## Current Engineering Baseline — Audit Closure and Production Integrity

The canonical architecture and implementation audit (`MG-AUD-*`) is complete
within its documented engineering scope:

- 94 canonical findings were tracked;
- 92 were remediated;
- 2 were recorded as accepted behavior;
- 0 remain open in that audit.

The later independent implementation audit (`MG-IA-*`) is also closed: all 20
actionable findings were verified, with 1 post-freeze invalidation recorded.

These closures do not establish scientific validity. The separate Stage 1
security review (`MG-SEC-*`) remains in progress, and scientific/researcher
validation remains incomplete.

Current engineering priorities are therefore:

1. complete the separate security review and evidence-backed hardening;
2. preserve regression coverage and deterministic semantics after audit closure;
3. harden graph-job worker ownership, lifecycle, authorization, and recovery
   before public route activation;
4. measure representative repository-scale graph and search workloads;
5. preserve dataset, configuration, rule, evidence, and software-version
   provenance;
6. maintain documented known limitations and real-response verification as the
   system evolves.

Resolution means engineering correction and scoped verification. It does not
mean researcher, computational, or experimental validation.

---

## Product Milestone — Integrated Research Workspace

After the high-priority engineering baseline is stable, the next product
milestone is to make the implemented intelligence available through the
**MaterialGraph Research Cycle** rather than through disconnected endpoint or
feature views.

The workspace should allow a researcher to:

1. begin from a research need, scientific question, material, or explicit
   objective;
2. formalize the problem and starting context where needed;
3. define or confirm an explicit research objective;
4. receive ranked, explained candidates;
5. inspect evidence, assumptions, warnings, and missing information;
6. explore relationships and pathways;
7. compare alternatives without manufacturing false certainty;
8. save the investigation and its reproducibility context;
9. share or collaborate with appropriate access controls;
10. refine the objective and continue the investigation.

Initial delivery priorities:

- research-need and material entry with identity-aware selection;
- problem-formalization support that exposes introduced assumptions;
- objective editor with explicit preference and constraint semantics;
- candidate and explanation workspace;
- evidence and validation-gap inspection;
- pathway and graph exploration;
- side-by-side comparison;
- investigation state and reproducibility metadata;
- bounded export or sharing for controlled research review;
- iterative objective refinement without losing prior context.

This milestone should be treated as workflow integration, not as permission to
add unrelated features. Each frontend or collaboration capability should state
which stage of the Research Cycle it improves and how it preserves scientific
meaning, provenance, uncertainty, and researcher authority.

---

## Research Validation Phase

After the high-priority engineering findings are addressed:

- create literature-backed reference case studies;
- recruit independent materials researchers for structured review;
- compare selected pathways with structural evidence;
- perform targeted DFT or other appropriate computational cross-validation;
- record favourable, unfavourable, and inconclusive outcomes;
- publish a validation matrix and limitations;
- revise rules only through attributed, reviewed, versioned evidence.

Experimental validation is a separate later activity and may require research
partners.

---

## Research Workflow Validation Milestone

Before the mature MaterialGraph Research Cycle and researcher-facing interaction
model are treated as stable, validate them against representative scientific
practice. The objective is not to replace established researcher methods, but to
identify where MaterialGraph can structure, connect, preserve, or improve them
without weakening scientific meaning.

Required work:

- document representative end-to-end materials-research workflows across more
  than one research context;
- identify common stages and scientifically important domain-specific
  differences;
- map existing researcher methods, databases, literature workflows, simulation
  tools, structural-analysis tools, experimental steps, and decision points to
  the MaterialGraph Research Cycle;
- identify where researchers currently lose provenance, repeat searches, compare
  evidence manually, or struggle to preserve investigation context;
- distinguish workflow friction that MaterialGraph can legitimately reduce from
  scientific activities that should remain owned by established methods or
  specialist tools;
- conduct structured review with independent materials researchers;
- test representative frontend workflows with real or literature-backed case
  studies;
- record which interactions are useful, confusing, missing, redundant, or
  scientifically misleading;
- revise the Research Cycle, terminology, state model, and frontend flow where
  evidence requires it;
- document domain-specific extensions rather than forcing one universal research
  procedure.

Workflow validation should answer:

1. Does each major MaterialGraph interaction correspond to a recognizable
   research task?
2. Does MaterialGraph reduce friction without changing the scientific meaning of
   the task?
3. Can researchers continue using established domain methods and tools?
4. Are objective, evidence, method, provenance, uncertainty, and decision context
   preserved across those transitions?
5. Which workflow steps are common across domains, and which require explicit
   domain-specific handling?
6. Which current MaterialGraph assumptions should change based on researcher
   evidence?

Completion of this milestone does not mean that MaterialGraph is scientifically
validated. It establishes that the product workflow has been checked for
compatibility with representative research practice. Scientific claims and
individual research outputs still require the appropriate literature,
computational, structural, experimental, and researcher validation.

---

## Domain Extension Architecture Validation Milestone

MaterialGraph should validate the Core/extension boundary before treating
domain-extensibility as a stable platform capability.

The objective is not to build many vertical products immediately. It is to test
whether common scientific-reasoning semantics can remain stable while
domain-specific scientific meaning is supplied through explicit, governed
extensions.

Required work:

1. study representative workflows from at least two scientifically distinct
   materials domains;
2. identify which objective, evidence, provenance, pathway, validation, and
   reproducibility semantics genuinely remain common;
3. identify which properties, terminology, applicability rules, evidence
   requirements, validation criteria, and external methods are domain-specific;
4. distinguish Scientific Domain Extensions from cross-domain decision contexts
   such as supply risk, sustainability, economics, or regulation;
5. define a conservative validation-requirement contract in which the Core tracks
   validation state while domain extensions define scientific requirements;
6. define versioned, inspectable research-template semantics and preserve
   template-derived assumptions in the investigation;
7. define conflict and applicability checks for composed domains, contexts,
   templates, and researcher constraints;
8. prototype one narrowly scoped reference extension without hard-coding its
   scientific meaning into the Core;
9. test whether domain experts can review or maintain appropriate extension
   content without weakening governance;
10. validate extension behavior with representative case studies and researcher
    review before stabilizing an extension API or schema.

Exit criteria should include:

- no domain-specific scientific threshold is required in the shared Core merely
  to support the reference extension;
- extension and template versions are attributable and reproducible;
- validation requirements remain domain-owned but Core-visible;
- explicit composition conflicts are surfaced rather than silently resolved;
- extension configuration is treated as untrusted until reviewed and validated;
- adding a second representative domain does not require reconstruction of the
  reasoning architecture.

This milestone establishes an architectural boundary, not scientific validation
of every possible domain or industry.

---

## Conditional Scientific Compute Integration Milestone

External scientific computation should be introduced only where a validated
research workflow demonstrates that it materially improves MaterialGraph's
ability to help researchers evaluate or validate an opportunity.

MaterialGraph should not become a general-purpose scientific simulation
platform. Its role should be to connect deterministic research intelligence
with appropriate domain computation while preserving research context,
provenance, uncertainty, and validation status.

Potential work includes:

* model-specific Physical Modeling Readiness profiles;
* explicit prerequisite and blocking-gap reporting;
* adapter contracts for external scientific tools and workflows;
* targeted DFT and electronic-structure integration;
* molecular-dynamics workflow integration where scientifically applicable;
* thermodynamic, structural, electrochemical, or other domain-specific
  computation where justified by validated use cases;
* versioned computational input and result records;
* engine, software-version, parameter, structure, configuration, and assumption
  provenance;
* references to computational artifacts and outputs;
* integration of computational results into the Scientific Knowledge Layer as
  attributed evidence;
* researcher-visible distinction between readiness, execution, numerical
  convergence, model validity, and agreement with experimental evidence.

The preferred integration direction is:

```text
Research Opportunity
        │
        ▼
Evidence / Property Context
        │
        ▼
Model-Specific Readiness
        │
        ▼
External or Dedicated Scientific Compute
        │
        ▼
Versioned Result + Provenance
        │
        ▼
Evidence / Validation Context
        │
        ▼
Continued Research Cycle
```

Implementation should begin with narrowly scoped adapters around demonstrated
research needs rather than a universal simulation abstraction.

Before adopting a scientific engine, library, or open-source project:

1. identify the researcher question and validation need;
2. establish the required material, structure, property, and model inputs;
3. define ownership between MaterialGraph and the external computation system;
4. define reproducible input and output contracts;
5. preserve engine, version, configuration, assumptions, and artifact
   provenance;
6. define failure, convergence, uncertainty, and validation semantics;
7. evaluate licensing, security, infrastructure, and operational cost;
8. verify that integration improves a real MaterialGraph research workflow.

This milestone is conditional. Audit remediation, engineering integrity,
reference case studies, researcher review, and scientific-validation work take
precedence. External computation should be added because demonstrated research
value requires it, not because integration with a scientific tool is
technically possible.

---

## Research Workflow and Knowledge Milestones

- Research Workflow Compatibility and Validation;
- Domain Extension Architecture Validation;
- versioned Scientific Domain Extensions and Cross-Domain Decision Contexts where validated;
- inspectable domain research templates with explicit assumptions and applicability;
- Research Validation Planning;
- Research Gap Analysis;
- Hypothesis Exploration;
- genuine multi-objective optimization with explicit constraint semantics;
- attributed evidence capture;
- organization- and project-private evidence overlays with explicit provenance, access scope, and separation from canonical shared knowledge;
- local structural and scientific-environment evidence where validated use cases require coordination-, site-, defect-, interface-, surface-, or local-bonding context;
- review and disagreement workflows;
- versioned Scientific Knowledge Layer.

---

## Conditional Platform Milestone — Document-Oriented Features

PostgreSQL remains MaterialGraph's authoritative system of record. MongoDB is
not required for the current scientific core and is not a replacement for
relational material, composition, relationship, criticality, discovery,
recommendation, or graph-job data.

Evaluate a secondary document store only after a concrete product feature
requires flexible, nested, independently evolving documents, such as:

- saved research sessions and exploration state;
- user workspaces, collections, notes, and saved searches;
- optional AI-assistant conversation and tool history;
- versioned graph-result snapshots;
- heterogeneous metadata from literature, patent, chemical, or materials-data
  sources.

Before implementation:

1. define the workload, ownership boundary, retention policy, and consistency
   requirements;
2. compare MongoDB with PostgreSQL JSONB, Redis, object storage, and other
   appropriate alternatives;
3. document why a second database provides material benefit;
4. define provenance, versioning, security, backup, recovery, and observability;
5. prototype and benchmark the selected workload;
6. adopt MongoDB only if the evidence justifies its added operational
   complexity.

If adopted, MongoDB will remain a complementary store. PostgreSQL will retain
canonical scientific and transactional authority, and document records will
reference canonical relational identifiers rather than establish competing
material identities.

---

## Distributed Computation

- harden PostgreSQL graph jobs before expansion;
- introduce a Go GraphCompute Worker where profiling justifies it;
- add bounded background analytics and candidate ranking;
- preserve deterministic ordering, ownership, and retry semantics;
- ensure performance work does not change graph meaning.

---

## High-Performance Graph Processing

- evaluate a Rust graph engine after algorithmic and semantic correctness;
- implement bounded large-scale traversal and path search;
- replace exhaustive enumeration where necessary;
- benchmark against the canonical Python implementation;
- preserve reproducibility and explanation provenance.

---

## Governed ML and AI Integration

Graph embeddings, machine learning, and optional LLM assistance may be explored
only after the deterministic and validation foundations are stable.

They may assist retrieval, summarization, interface workflows, or hypothesis
organization, but must not silently replace canonical scientific computation or
present generated text as validated evidence.

---

## Long-Term Outcome

MaterialGraph should become useful because its opportunities are inspectable,
its limits are explicit, its evidence is traceable, and its validation status
is honest—not because internal scores are presented as scientific proof.