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

# 7. Agents, Loops, and Dependency-Graph Workflow Design

## Source

Mahax --- *Agents, Loops, Graphs. Everything You Need to Know in One
Place.*

## Why We Examined It

The article describes agentic work through tool-using agents, iterative
loops, and dependency graphs. It is not materials-science guidance, but
several workflow-engineering ideas are relevant to MaterialGraph's
future Research Cycle, Scientific Compute boundary, and possible
orchestration layer.

## Relevant Observations

Four engineering patterns are particularly useful:

1.  **Explicit task contracts.** Bounded nodes with defined input/output
    shapes are easier to compose and validate than unconstrained
    free-text handoffs.
2.  **Dependency rather than sequence.** Workflow edges should represent
    genuine data dependencies. Independent tasks may be executed
    independently or in parallel.
3.  **Bounded iterative loops.** Iteration needs an explicit check,
    retained state about prior attempts, and a hard stop condition.
4.  **Separation of production and checking.** Generating an output
    should not itself establish that output's validity.

## Potential MaterialGraph Insight

### Scientific Task and Result Contracts

Future scientific integrations should prefer explicit contracts around
specialized computations.

``` text
ScientificTask
    |
    +-- material / structure identity
    +-- research objective or validation question
    +-- method
    +-- parameters and conditions
    +-- assumptions
    +-- provenance requirements
    +-- expected result schema
```

``` text
ScientificResult
    |
    +-- task identity
    +-- engine and version
    +-- inputs / parameters
    +-- execution or convergence state
    +-- outputs and artifacts
    +-- uncertainty where available
    +-- provenance
    +-- validation status
```

These contracts can allow MaterialGraph to integrate external scientific
capabilities without coupling canonical research semantics to one
particular tool.

### Dependency-Aware Research Workflows

Future Research Cycle orchestration should model genuine dependencies
rather than forcing every research activity into one linear sequence.

``` text
                    Research Objective
                           |
                           v
                    Candidate Selection
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       Literature      Criticality    Structural
        Evidence        Evidence       Evidence
             |             |             |
             +-------------+-------------+
                           |
                           v
                    Readiness Check
                           |
                           v
                 Scientific Validation
                           |
                           v
                    Researcher Review
```

Where branches are genuinely independent, parallel execution may improve
responsiveness without changing scientific semantics.

### Bounded Validation Loops

MaterialGraph may eventually support iterative workflows such as:

``` text
Objective
   |
   v
Discover
   |
   v
Evaluate Evidence
   |
   v
Identify Validation Gap
   |
   v
Validate
   |
   v
Record New Evidence
   |
   v
Re-evaluate / Refine
```

Automated checks must remain limited to things the system can actually
establish, such as schema validity, hard-constraint satisfaction,
deterministic consistency, evidence/provenance completeness,
execution/convergence state, and explicit stopping/resource limits.

A self-checking workflow must not equate successful workflow completion
with scientific correctness.

### Generation, Verification, and Scientific Validation

MaterialGraph should continue distinguishing:

``` text
Generation / Exploration
          !=
Deterministic Verification
          !=
Evidence Evaluation
          !=
Physical / Experimental Validation
          !=
Researcher Judgment
```

The verifier does not have to be another AI agent. Depending on the
claim, verification may use deterministic rules, tests, database
constraints, independent scientific methods, external simulation,
experimental evidence, or researcher review.

## Relationship to Existing Architecture

This reinforces existing MaterialGraph directions rather than creating a
new architectural layer:

-   Research Cycle orchestration;
-   separation of planning, reasoning, evidence, and execution;
-   adapter-oriented Scientific Compute integration;
-   explicit task/result boundaries;
-   deterministic canonical reasoning;
-   researcher authority over scientific interpretation and validation.

## What MaterialGraph Should Not Infer From It

The usefulness of agent graphs for workflow orchestration does **not**
imply that MaterialGraph should become a multi-agent scientific
reasoning system.

This article does not justify replacing canonical deterministic
reasoning with LLM agents, creating an agent for every service, allowing
an AI checker to declare scientific validity, autonomous unbounded
research loops, or adding orchestration complexity before the underlying
researcher workflow is reliable.

## Current Decision

**ARCHITECTURAL INSIGHT ACCEPTED --- NO AGENT IMPLEMENTATION
COMMITMENT**

The durable lessons are explicit contracts, dependency-aware workflow
design, bounded iteration, and separation of generation from
verification/validation.

No roadmap milestone or agent implementation is created by this
observation.

## Promotion Criteria

Consider additional canonical documentation or implementation only if:

-   real Research Cycle workflows demonstrate repeated orchestration
    needs;
-   task boundaries and dependencies are stable enough to formalize;
-   parallel execution can preserve deterministic semantics;
-   automated checks have objective pass/fail meaning;
-   stopping/resource limits can be enforced;
-   researcher evaluation shows automation improves the workflow rather
    than obscuring scientific reasoning.

------------------------------------------------------------------------

# 8. ORNL Self-Driving Science and Adaptive Evidence Acquisition

## Source

Oak Ridge National Laboratory --- *AI powers self-driving science*.

## Why We Examined It

ORNL described a materials-characterization workflow in which incoming
experimental measurements were analyzed during the experiment and used
to guide what should be measured next.

The important MaterialGraph question is not whether MaterialGraph should
control scientific instruments. It is whether research intelligence can
become more useful by identifying which unresolved evidence would be
most valuable to obtain next.

## Relevant Observations

The workflow illustrates an adaptive research pattern:

``` text
Current Evidence
        |
        v
Identify Uncertainty / Information Need
        |
        v
Choose Next Measurement
        |
        v
Acquire New Evidence
        |
        v
Analyze Result
        |
        v
Update Research State
        |
        +--------------------------> repeat where justified
```

For MaterialGraph, the durable lesson is broader than autonomous
experimentation: **missing evidence can potentially be prioritized
according to its value to the current research decision rather than
merely displayed as missing.**

## Potential MaterialGraph Insight

This observation contributed to the proposed canonical capability
**Validation Priority Intelligence (VPI)**.

VPI asks:

> **Given this research objective and current evidence state, what
> unresolved question is most important to establish next, and why?**

``` text
Research Objective
        |
        v
Candidate / Pathway / Comparison
        |
        v
Evidence + Unknowns + Contradictions
        |
        v
Validation Priority Intelligence
        |
        +-- literature / evidence review
        +-- structural or local evidence
        +-- external computation
        +-- experiment
        +-- researcher review
        |
        v
Attributed New Evidence
        |
        v
Re-evaluate / Refine
```

The initial value does not depend on autonomous laboratories.
MaterialGraph could first help researchers prioritize validation needs
using evidence gaps, objective relevance, decision sensitivity,
readiness, and existing provenance.

### From Evidence Coverage to Decision-Relevant Validation

A mature evidence system should be able to distinguish:

``` text
"What evidence is missing?"
            |
            v
"What missing evidence matters to this objective?"
            |
            v
"Could resolving it change the research decision?"
            |
            v
"What validation class could address it?"
```

This creates a bridge among Evidence Intelligence, scenario/sensitivity
analysis, Physical Modeling Readiness, external scientific compute, and
future experimental evidence.

### Validation Requests Should Preserve Research Context

``` text
ResearchObjective
        |
        v
EvidenceGap
        |
        v
ValidationPriority
        |
        v
ValidationRequest
        |
        v
Computation / Experiment / Review
        |
        v
EvidenceArtifact
        |
        v
InvestigationRevision
```

Where implemented, this relationship should preserve material/structure
identity, objective context, requested claim, method or route,
conditions, provenance, result status, uncertainty, and researcher
interpretation.

## Relationship to Existing Architecture

This insight connects existing or proposed capabilities rather than
replacing them:

-   Research Objectives;
-   Evidence Intelligence;
-   unknown and contradiction handling;
-   scenario and sensitivity semantics;
-   structural/local-environment evidence;
-   Physical Modeling Readiness;
-   Scientific Task / Result contracts;
-   external scientific-compute adapters;
-   investigation history and provenance.

VPI should reuse those layers rather than become another independent
ranking or evidence system.

## What MaterialGraph Should Not Infer From It

The ORNL example does **not** establish that MaterialGraph currently
needs:

-   autonomous laboratory control;
-   direct instrument integration;
-   active learning;
-   autonomous experiment selection;
-   an LLM or agent deciding scientific truth;
-   automated publication of experimental results into canonical
    knowledge.

Those are separate capabilities requiring their own scientific, safety,
infrastructure, governance, and researcher-validation justification.

## Current Decision

**DURABLE INSIGHT PROMOTED TO CANONICAL DIRECTION AS VALIDATION PRIORITY
INTELLIGENCE --- NO AUTONOMOUS EXPERIMENT IMPLEMENTATION COMMITMENT**

The promoted principle is that MaterialGraph should eventually help a
researcher identify the most decision-relevant validation need, not
merely list missing evidence.

## Promotion / Implementation Criteria

Before VPI becomes a roadmap implementation milestone:

-   representative researcher workflows should demonstrate the need;
-   validation-priority semantics should be deterministic and
    inspectable;
-   priority must remain distinct from scientific validity;
-   evidence gaps, contradictions, and unknown states must remain
    honest;
-   decision sensitivity should avoid manufactured precision;
-   validation classes and readiness boundaries should be explicit;
-   domain experts should be able to evaluate representative priority
    outputs;
-   autonomous acquisition or instrument control should remain outside
    scope unless separately justified.

------------------------------------------------------------------------

# 9. Matlantis PFP v9 and High-Fidelity Atomistic Simulation

## Source

Matlantis Corporation --- *Matlantis Upgrades Core Technology Behind Its
Universal Atomistic Simulator with PFP v9* (July 16, 2026).

## Why We Examined It

PFP v9 demonstrates the rapid evolution of specialist atomistic
simulation systems and makes several questions concrete for
MaterialGraph's future validation workflow: validation-route selection,
computational provenance, evidence comparability, and the boundary
between MaterialGraph and specialist scientific engines.

## Relevant Observations

Matlantis reports that PFP v9.0.0 officially releases its r²SCAN
calculation mode across the same 96-element coverage as PBE, including
lanthanides and actinides. It expands support for surface reactions and
adsorption structures, coordination complexes, and molecular crystals.

Matlantis also reports improved agreement with experimental data for
crystal and surface stability, melting point, and water viscosity.
r²SCAN becomes the default calculation mode when a method is not
explicitly selected, while PBE remains available.

The durable MaterialGraph lesson is not that one calculation mode should
be preferred universally. It is that **method choice, model/version
identity, and calculation context materially affect the scientific
meaning of a result.**

## Potential MaterialGraph Insight

### Validation Route Selection Is Distinct From Validation Priority

VPI answers **what unresolved question matters most to the current
research decision**. A separate responsibility should answer **what
class of evidence could appropriately address that question**.

``` text
Research Objective
        |
        v
Validation Priority Intelligence
        |
        v
Validation Route Selection
        |
        +-- literature / attributed evidence
        +-- structural characterization
        +-- electronic-structure workflow
        +-- atomistic simulation
        +-- thermodynamic workflow
        +-- experiment
        +-- domain-expert review
        |
        v
Route-Specific Readiness
```

The availability of a fast or broadly capable simulator must not itself
make that simulator the scientifically appropriate route.

### Method and Model Version Are Scientific Provenance

A computational result should preserve enough identity to explain how it
was produced: material/structure identity, property definition, method
family, calculation mode, model/potential/functional, engine/version,
model version, parameters/conditions, convergence,
uncertainty/applicability, provenance, and validation status.

### Computational Evidence Comparability

MaterialGraph should not silently treat two computational values as
equivalent evidence merely because they share the same property label.
Relevant differences may include method, model/version, structure
representation, property definition/units, conditions, parameterization,
convergence, uncertainty, and applicability. Where required metadata is
absent, comparability should remain unknown rather than assumed.

### Local and Non-Bulk Scientific Context Is Reinforced

The emphasis on surfaces, adsorption systems, coordination complexes,
and molecular crystals reinforces an existing conclusion:
composition-level or bulk/global signals are not sufficient for every
materials-science question.

## Relationship to Existing Architecture

This reinforces VPI, validation-route semantics, model-specific Physical
Modeling Readiness, Scientific Task/Result contracts, external
Scientific Compute adapters, local scientific-environment intelligence,
evidence provenance, and validation-state separation.

## What MaterialGraph Should Not Infer From It

The release does **not** establish that MaterialGraph should implement
its own universal atomistic simulator, adopt r²SCAN universally, treat
ML interatomic potentials as replacements for all modeling approaches,
integrate Matlantis specifically, automatically compare outputs from
different methods/versions, or equate improved benchmark agreement with
universal scientific validity.

## Current Decision

**ARCHITECTURAL INSIGHT ACCEPTED --- NO MATLANTIS INTEGRATION
COMMITMENT**

Three durable lessons are accepted:

1.  validation-route selection should be explicit and distinct from
    validation priority;
2.  method/model/version identity is part of scientific provenance;
3.  computational evidence comparability must be assessed rather than
    assumed.

## Promotion / Implementation Criteria

Before implementation milestones are created, representative
computational workflows should be examined; property/method identity
semantics should be defined; comparability rules should be conservative
and domain-appropriate; missing metadata must preserve an unknown state;
domain experts should review representative cases; and no
vendor-specific adapter should be prioritized without a demonstrated
researcher workflow or integration need.

------------------------------------------------------------------------

# 10. Cross-Project Lessons

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

## Computational Method Identity Is Part of Scientific Provenance

A computational value is inseparable from the method, model/version,
structure, conditions, assumptions, and property definition that
produced it.

## Computational Evidence Comparability Must Be Established, Not Assumed

Results sharing a property label are not automatically comparable.
Missing scientific metadata should preserve unknown comparability rather
than silently imply compatibility.

## Validation Priority and Validation Route Are Different Questions

VPI should prioritize the unresolved gap; validation-route logic should
identify suitable evidence classes; route-specific readiness should
determine whether a proposed computation is sufficiently specified.

## External Computation Should Return Evidence, Not Automatic Truth

Execution, convergence, model validity, and experimental agreement
remain different states.

## Unknown Evidence Must Remain Unknown

MaterialGraph should continue distinguishing internal support, evidence
coverage, validation readiness, and scientific validation status.

## Explicit Contracts Enable Safe Composition

Future integrations and orchestration should prefer bounded
responsibilities with explicit input/output contracts. This improves
provenance, validation, replaceability, and composition without blurring
scientific ownership.

## Workflow Edges Should Represent Real Dependencies

Research workflows should distinguish genuine data dependencies from
arbitrary sequence. Independent work may be parallelized only when
scientific semantics and shared-state assumptions remain safe.

## Iteration Requires Objective Checks and Hard Limits

Automated loops are appropriate only where the system has a meaningful
check and an explicit stopping condition. Scientific validity must not
be inferred merely because a workflow reached its own completion
criterion.

## Missing Evidence Can Become a Validation-Planning Input

Evidence coverage should not stop at reporting what is absent. Where the
scientific semantics are sufficiently understood, MaterialGraph may help
distinguish which unresolved evidence is most decision-relevant and
which validation class could address it.

Validation priority, validation execution, and scientific validity
remain separate concepts.

## Researcher Authority Remains Central

Even as scientific systems become more automated, researchers should
retain visibility and authority over interpretation, validation, and
decisions.

------------------------------------------------------------------------

# 11. Ideas Deliberately Not Promoted

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

# 12. Future Exploration Questions

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