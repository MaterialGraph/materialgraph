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

## Current Priority — Audit Remediation and Production Integrity

The original architecture audit and independent post-remediation audit have
been reconciled into one canonical register.

At the time of this roadmap update:

- 94 distinct canonical findings are tracked;
- 23 are resolved within their documented engineering scope;
- 71 remain open or require policy decisions.

Current remediation priorities are:

1. scientific-scoring and abundance-direction correctness;
2. unknown-risk propagation and non-favourable uncertainty handling;
3. scenario and sensitivity semantics;
4. graph, traversal, and path integrity;
5. strict objective and endpoint-family enforcement;
6. evidence-readiness and explanation accuracy;
7. graph-job concurrency, ownership, and authorization;
8. bounded K-best search and query-performance work.

Resolution means engineering correction and scoped verification. It does not
mean researcher or experimental validation.

---

## Next Milestone — Engineering Validation Baseline

- remediate or explicitly decide all P0/P1 findings;
- expand focused and full regression coverage;
- verify graph closure, depth, and canonical transition semantics;
- unify constraint, tie, composition, and evidence interpretations;
- enforce API input bounds and response contracts;
- harden graph-job state transitions and ownership;
- define dataset, configuration, and software-version provenance;
- benchmark representative graph workloads;
- publish documented known limitations.

---

## Product Milestone — Integrated Research Workspace

After the high-priority engineering baseline is stable, the next product
milestone is to make the implemented intelligence available through the
**MaterialGraph Research Cycle** rather than through disconnected endpoint or
feature views.

The workspace should allow a researcher to:

1. start from a material;
2. define a research objective;
3. receive ranked, explained candidates;
4. inspect evidence, assumptions, warnings, and missing information;
5. explore relationships and pathways;
6. compare alternatives without manufacturing false certainty;
7. save the investigation and its reproducibility context;
8. share or collaborate with appropriate access controls;
9. refine the objective and continue the investigation.

Initial delivery priorities:

- material search and identity-aware selection;
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

## Research Workflow and Knowledge Milestones

- Research Validation Planning;
- Research Gap Analysis;
- Hypothesis Exploration;
- genuine multi-objective optimization with explicit constraint semantics;
- attributed evidence capture;
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