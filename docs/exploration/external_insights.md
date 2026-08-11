# MaterialGraph External Insights

## Purpose

This document records external projects, institutional initiatives,
scientific tools, and industry observations that may provide useful
insight for MaterialGraph.

Entries are exploratory unless explicitly marked otherwise. Recording an
idea here does not make it a MaterialGraph requirement, roadmap
commitment, architectural decision, or scientifically validated
capability.

Durable insights should be promoted into canonical documentation only
after their relevance has been evaluated.

------------------------------------------------------------------------

# 1. Molecular-Dynamics and External Scientific Tooling

## Why We Examined It

External molecular-simulation projects raised the question of whether
MaterialGraph should implement physical simulation capabilities itself
or connect research intelligence to mature scientific tools.

## Relevant Observations

Scientific simulation systems require specialized domain knowledge,
inputs, numerical methods, infrastructure, convergence handling, and
post-processing. Reimplementing those systems inside MaterialGraph could
duplicate mature specialist software and substantially expand scientific
scope.

## Potential MaterialGraph Insight

MaterialGraph can create value by determining what research opportunity
requires validation, whether the material and research context are
sufficiently specified, which modeling route may be appropriate, what
prerequisites remain missing, and how computational inputs, assumptions,
outputs, and provenance relate to the original investigation.

Specialized scientific software can continue to own domain computation.

``` text
MaterialGraph Research Intelligence
        |
        v
Model-Specific Readiness
        |
        v
External Scientific Tool / Workflow
        |
        v
Versioned Computational Result
        |
        v
Attributed Evidence
        |
        v
Continued MaterialGraph Investigation
```

## Current Decision

**PROMOTED TO CANONICAL DOCUMENTATION**

This contributed to Physical Modeling Readiness and the adapter-oriented
Scientific Compute boundary.

------------------------------------------------------------------------

# 2. Apheris and Private / Domain Scientific Context

## Why We Examined It

Scientific-model adaptation using small amounts of program-specific
private data highlighted the gap between public scientific datasets and
organization-specific research environments.

## Relevant Observations

Organizations may possess unpublished experimental results, proprietary
simulation results, failed or inconclusive experiments, internal
measurements, proprietary structures/formulations, and researcher
observations.

Private scientific information may be useful to an organization's
research without being appropriate for automatic publication or
canonicalization.

## Potential MaterialGraph Insight

MaterialGraph should distinguish canonical/shared knowledge from
organization-, project-, workspace-, or researcher-scoped evidence.
Private evidence may enrich an authorized investigation while preserving
source, access scope, review state, and provenance.

Private evidence must not silently become canonical shared scientific
knowledge.

The following concepts should remain separate:

1.  **Data/context adaptation** --- organization-specific evidence.
2.  **Reasoning contextualization** --- explicit objectives/rules
    applied within that context.
3.  **Model adaptation** --- future fine-tuning of a learned model, if a
    validated learned layer is eventually introduced.

## What MaterialGraph Should Not Infer From It

This does not currently justify foundation models, GNN fine-tuning,
LoRA/PEFT, federated learning, or automatic modification of canonical
rules by private evidence.

## Current Decision

**PROMOTED TO CANONICAL DOCUMENTATION**

------------------------------------------------------------------------

# 3. Localized Scientific Evidence Versus Global Signals

## Why We Examined It

Examples in adjacent scientific fields showed that strong aggregate
performance can conceal failure at a scientifically decisive local
environment.

## Relevant Observations

The materials-science analogue includes coordination environments,
substitution sites, defects, interfaces, surfaces, local bonding, and
other application-specific local structures.

A material may appear favourable under global/compositional signals
while lacking evidence that the local environment relevant to the
research question is preserved or appropriate.

## Potential MaterialGraph Insight

``` text
Composition
    |
    v
Phase / Structure
    |
    v
Local Scientific Environment
    |
    +-- coordination
    +-- substitution site
    +-- defect
    +-- interface
    +-- surface
    +-- local bonding
```

Missing local evidence should remain an explicit validation gap even
when global signals are favourable.

## What MaterialGraph Should Not Infer From It

This does not prescribe a GNN or any particular implementation.
Local-environment intelligence may eventually use structural analysis,
descriptors, external computation, graph methods, learned models, or
other validated approaches.

## Current Decision

**PROMOTED TO CANONICAL DOCUMENTATION**

------------------------------------------------------------------------

# 4. Argonne ChemGraph

## Why We Examined It

ChemGraph explores orchestration of computational chemistry/materials
workflows using scientific software and AI-assisted workflow planning.

## Relevant Observations

Scientific systems can separate research/workflow planning, tool
selection, scientific execution, result processing, and researcher
interaction. The system identifying a research question does not need to
implement every scientific capability internally.

## Potential MaterialGraph Insight

``` text
Research Planning / Orchestration
             |
     +-------+--------+
     |       |        |
     v       v        v
MaterialGraph Evidence Scientific
Deterministic Retrieval Compute
Reasoning
     |       |        |
     +-------+--------+
             |
             v
       Research Context
             |
             v
      Researcher Review
```

MaterialGraph's deterministic reasoning engine can remain a specialized
reasoning capability inside a broader future workflow. External
computation should use explicit task/result contracts and adapters where
practical.

## What MaterialGraph Should Not Infer From It

ChemGraph's use of agents or LLM orchestration does not mean
MaterialGraph should replace deterministic reasoning with agents or
become a smaller copy of ChemGraph.

## Current Decision

**ARCHITECTURAL INSIGHT ACCEPTED / PROMOTED WHERE APPLICABLE**

No ChemGraph-specific implementation dependency is planned.

------------------------------------------------------------------------

# 5. FORUM-AI

## Why We Examined It

FORUM-AI represents a large institutional effort toward integrated
AI-assisted materials research involving planning, specialized
capabilities, knowledge representation, simulation, experimentation, and
iterative hypothesis refinement.

## Relevant Observations

The initiative reinforces that research planning can be separated from
specialized reasoning/execution; scientific knowledge can ground
workflows; simulations, literature, data, and experiments can
participate in an iterative investigation; and scientific systems may
increasingly compose specialized capabilities rather than rely on one
universal model.

## Potential MaterialGraph Insight

MaterialGraph's Research Cycle may eventually evolve toward a closed
validation loop:

``` text
Research Objective
        |
        v
Discover and Explain
        |
        v
Evaluate Evidence
        |
        v
Identify Knowledge Gap
        |
        v
Choose Validation Route
   +----+-----+
   |    |     |
   v    v     v
Literature Compute Experiment
   |    |     |
   +----+-----+
        |
        v
Attributed New Evidence
        |
        v
Re-evaluate / Refine
        +-----------> cycle
```

A future planner may coordinate MaterialGraph reasoning, evidence
retrieval, scientific computation, and researcher review without
becoming the scientific authority for each capability.

## Strategic Interpretation

MaterialGraph should not attempt to compete by claiming to be a
universal autonomous AI scientist. A more defensible identity is
**inspectable materials research intelligence infrastructure**.

## What MaterialGraph Should Not Infer From It

FORUM-AI does not establish that MaterialGraph needs an LLM planner now,
autonomous scientific decisions, multi-agent architecture, foundation
models as canonical reasoning, or automated laboratories.

## Current Decision

**ARCHITECTURAL INSIGHT ACCEPTED / NO DIRECT IMPLEMENTATION COMMITMENT**

------------------------------------------------------------------------

# 6. DOE Critical Minerals and Materials Framework

## Source

U.S. Department of Energy --- Critical Minerals and Materials.

## Why We Examined It

MaterialGraph already includes deterministic criticality/supply-risk
intelligence and supports research objectives involving lower
criticality, element avoidance, substitution, and scenario policies.

DOE provides an authoritative real-world framework against which the
long-term meaning of MaterialGraph criticality intelligence can be
examined.

## Relevant Observations

DOE's framework indicates that criticality is multidimensional and
contextual rather than simply a timeless intrinsic property of an
element.

Relevant considerations may include supply risk, basic availability,
producer diversity/concentration, geopolitical/regulatory/social
factors, competing technology demand, substitutability, importance to
energy technologies, material intensity, and technology/demand
scenarios.

Critical-material concepts may also apply beyond individual elements to
minerals, feedstocks, or engineered materials.

## Potential MaterialGraph Insight

``` text
Criticality Context
        |
        +-- entity
        +-- application
        +-- geography
        +-- time horizon
        +-- technology scenario
        +-- supply-risk dimensions
        +-- importance / demand context
        +-- evidence provenance
```

MaterialGraph should be cautious about treating one element-level score
as universally representing criticality across every research objective.

Authoritative external criticality assessments could eventually become
evidence inputs rather than something MaterialGraph attempts to replace.
MaterialGraph could then help researchers explore alternatives,
trade-offs, evidence, uncertainty, and validation priorities.

## Relationship to Existing Architecture

Potentially relevant capabilities include Criticality Service, Element
Risk Profiles, Scenario Policies, Research Objectives, Substitution
Exploration, Evidence Intelligence, and provenance/evidence coverage.

## What MaterialGraph Should Not Infer From It

The current criticality implementation should not be changed solely
because this framework exists. MaterialGraph should not claim that its
deterministic criticality score is equivalent to a DOE criticality
assessment.

The methodology and related authoritative frameworks should be studied
more deeply before schema, scoring, or scientific-policy changes are
proposed.

## Current Decision

**EXPLORATORY --- NO IMPLEMENTATION COMMITMENT**

## Promotion Criteria

Consider promotion if researcher use cases demonstrate contextual
criticality requirements; authoritative methodologies can be represented
reproducibly; the current element-level model demonstrably limits useful
research; identity/scenario/evidence/provenance semantics are
understood; and implementation can preserve deterministic, inspectable
reasoning.

------------------------------------------------------------------------

# 7. Cross-Project Lessons

## Public Scientific Data Is a Foundation, Not the Entire Research Context

Industrial and institutional research may depend on private structures,
measurements, simulations, failures, processing conditions, and
observations. MaterialGraph should represent those contexts without
weakening canonical knowledge boundaries.

## Planning, Reasoning, and Execution Are Different Responsibilities

A future research planner does not need to become the deterministic
reasoning engine or scientific simulator. MaterialGraph should preserve
explicit ownership boundaries.

## The Knowledge Graph Should Become Scientifically Richer, Not Merely Larger

Scaling should not mean only adding material nodes. Scientific richness
may include structures/phases, properties/conditions, local
environments, evidence, literature, simulations, experiments,
disagreements, validation history, and private/scoped research context.

## External Computation Should Return Evidence, Not Automatic Truth

Execution, convergence, model validity, and experimental agreement
remain different states.

## Unknown Evidence Must Remain Unknown

MaterialGraph should continue distinguishing internal support, evidence
coverage, validation readiness, and scientific validation status.

## Researcher Authority Remains Central

Even as scientific systems become more automated, researchers should
retain visibility and authority over interpretation, validation, and
decisions.

------------------------------------------------------------------------

# 8. Ideas Deliberately Not Promoted

The following ideas have been encountered but currently do not
constitute MaterialGraph requirements:

-   GNNs as a replacement for deterministic graph reasoning;
-   graph foundation models as a required architecture;
-   LoRA or PEFT;
-   federated learning;
-   autonomous multi-agent scientific decision-making;
-   embedded DFT or MD engines;
-   autonomous laboratory control;
-   ternary-computing infrastructure;
-   contributor revenue sharing or a scientific-knowledge marketplace.

Some may become relevant later. Their presence in external projects is
not sufficient justification for implementation.

------------------------------------------------------------------------

# 9. Future Exploration Questions

For each external project or idea, ask:

1.  What researcher problem does it solve?
2.  Does MaterialGraph already address part of that problem?
3.  Does it reveal a genuine MaterialGraph gap?
4.  Is the insight scientific, architectural, product-related, or merely
    technological?
5.  Would adopting it strengthen or weaken MaterialGraph's deterministic
    and inspectable core?
6.  Does it require new evidence or researcher validation?
7.  Can it integrate through an existing boundary?
8.  Would an external tool be more appropriate than internal
    implementation?
9.  What uncertainty or provenance requirements would it introduce?
10. Does it deserve promotion into canonical documentation or remain
    exploratory?

The purpose of this log is not to maximize the number of ideas
MaterialGraph adopts.

Its purpose is to help MaterialGraph **learn broadly while changing
deliberately**.
