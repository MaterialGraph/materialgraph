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

# 10. AI-for-Materials Ecosystem and Vertical Product Positioning

## Source

Dmitry Starodubtsev / Matterloop --- LinkedIn ecosystem map, *AI for
Materials* (August 2026).

This entry records the strategic pattern observed in the post rather
than treating its company list, funding totals, valuations, or category
boundaries as an authoritative industry census. Selected examples were
independently checked against company, government, or research sources
where practical.

## Why We Examined It

The post groups active materials-technology organizations across
foundation models and discovery engines, autonomous laboratories,
simulation and engineering, battery and energy materials, and
catalysts/chemistry.

This is directly relevant to MaterialGraph because it helps clarify
where the project should compete, where it should integrate, and how a
broad research architecture may need a narrower initial product/use-case
expression.

## Relevant Observations

The materials-computing ecosystem is becoming increasingly specialized.

Different organizations are concentrating on capabilities such as:

-   foundation models and learned interatomic potentials;
-   generative materials discovery;
-   specialist atomistic or engineering simulation;
-   autonomous laboratories and experiment orchestration;
-   battery/electrolyte discovery;
-   superconductors;
-   catalysts and chemistry;
-   application-specific materials development.

Several independently checked examples reinforce the broader pattern.
Quantum Formatics describes an AI-accelerated superconductor-discovery
platform focused on manufacturable, scalable superconductors, and an
NSF-supported project combines AI models, first-principles simulation,
synthesis, and experimental characterization. South 8 Technologies, by
contrast, is commercializing its LiGas battery-electrolyte platform for
concrete aerospace, defense, and manufacturing applications.

The durable observation is therefore not the exact number of companies
or the funding figure assigned to each one. It is that **specialist
scientific capabilities and application-specific materials products are
becoming a substantial part of the surrounding ecosystem.**

## Potential MaterialGraph Insight

### MaterialGraph Should Define Its Layer, Not Compete With Every Layer

MaterialGraph should not attempt to win by reproducing every capability
in the materials-AI stack.

A useful ecosystem view is:

``` text
Researcher / R&D Objective
          |
          v
MaterialGraph Research Intelligence
          |
          +-- knowledge and relationships
          +-- deterministic reasoning
          +-- alternatives and pathways
          +-- evidence and provenance
          +-- uncertainty / unknowns
          +-- validation priority
          +-- validation-route context
          |
          v
Specialist Scientific Capabilities
          |
          +-- foundation / learned models
          +-- DFT / atomistic simulation
          +-- engineering simulation
          +-- literature / data systems
          +-- experimental workflows
          +-- autonomous laboratories
          |
          v
Attributed New Evidence
          |
          v
MaterialGraph Re-evaluation
```

The increasing strength of specialist systems makes the adapter-oriented
MaterialGraph boundary more important, not less important.

MaterialGraph's defensible role should remain centered on **inspectable
materials research intelligence**: connecting objectives, structured
knowledge, explicit reasoning, evidence, uncertainty, alternatives, and
validation planning.

### Horizontal Architecture Does Not Require Horizontal Go-to-Market

A general research-intelligence architecture can initially prove itself
through a narrow, high-value workflow.

The ecosystem post's emphasis on application-specific value suggests an
important product distinction:

``` text
Architecture
    |
    +-- reusable materials research intelligence infrastructure

Initial Product Proof
    |
    +-- narrow researcher problem
    +-- explicit scientific objective
    +-- measurable decision value
    +-- inspectable evidence and reasoning
```

MaterialGraph should therefore avoid relying on a generic message such
as:

> "AI for materials."

A stronger initial demonstration may be framed around a concrete
researcher decision, for example:

> **Identify lower-criticality alternatives to a target material while
> preserving important scientific characteristics, explain why each
> alternative deserves investigation, expose the supporting evidence and
> uncertainty, and identify what should be validated next.**

This is an example of product positioning, not a commitment that
criticality or battery materials must become MaterialGraph's permanent
commercial vertical.

### Outcome Language Can Be More Useful Than Technology Language

Researchers and R&D organizations ultimately need decisions and
outcomes, not an inventory of algorithms.

MaterialGraph's public/product language should increasingly connect
technical capabilities to questions such as:

-   What alternative deserves investigation?
-   Why was it selected?
-   What trade-offs does it introduce?
-   What evidence supports the recommendation?
-   What remains unknown?
-   Could an unresolved assumption change the decision?
-   What should be validated next?
-   Which external scientific capability could address that validation
    need?

This does not mean hiding the deterministic graph, evidence, provenance,
or scientific architecture. It means explaining those capabilities
through the research decisions they support.

### Capital-Intensive Scientific Capabilities Should Usually Remain External

The surrounding ecosystem includes organizations investing heavily in
model training, simulation infrastructure, laboratories, synthesis, and
manufacturing.

MaterialGraph should be cautious about competing directly on:

-   universal foundation-model training;
-   autonomous laboratory infrastructure;
-   universal atomistic simulation;
-   large-scale candidate generation purely for scale;
-   experimental hardware;
-   GPU or laboratory capacity as a primary moat.

Where mature specialist capabilities exist, MaterialGraph may create
more value by making their use research-context-aware, inspectable,
provenance-preserving, and connected to an investigation.

## Relationship to Existing Architecture

This observation reinforces rather than replaces several existing
directions:

-   MaterialGraph as inspectable materials research intelligence
    infrastructure;
-   deterministic canonical reasoning;
-   Evidence Intelligence;
-   Validation Priority Intelligence;
-   Validation Route Selection;
-   model-specific Physical Modeling Readiness;
-   Scientific Task / Result contracts;
-   adapter-oriented external Scientific Compute;
-   computational evidence comparability;
-   researcher authority over scientific interpretation.

It also adds an important product distinction:

> **MaterialGraph may remain horizontal at the infrastructure level
> while proving value vertically through specific researcher
> workflows.**

## What MaterialGraph Should Not Infer From It

This ecosystem map does **not** establish that:

-   every company or funding figure in the post is independently
    verified;
-   the post is a complete or authoritative market census;
-   MaterialGraph has no competitors in research intelligence;
-   MaterialGraph has discovered an uncontested market category;
-   vertical positioning guarantees adoption or commercial success;
-   MaterialGraph should immediately become a battery-only product;
-   MaterialGraph should add foundation models, autonomous labs, or
    simulation engines merely because well-funded organizations are
    building them;
-   large funding rounds establish scientific superiority.

The post should be treated as a useful market observation whose
individual company, funding, revenue, and valuation claims require
source-level verification before use in formal competitive analysis.

## Current Decision

**STRATEGIC / PRODUCT INSIGHT ACCEPTED --- NO NEW IMPLEMENTATION
COMMITMENT**

The following durable lessons are accepted for continued evaluation:

1.  MaterialGraph should define its research-intelligence layer clearly
    rather than compete indiscriminately across the entire materials-AI
    stack.
2.  Specialist models, simulation systems, and experimental platforms
    can become external capabilities that MaterialGraph contextualizes
    rather than duplicates.
3.  A horizontal architecture can be introduced through a narrow,
    outcome-oriented researcher workflow.
4.  Product communication should emphasize the research decision and
    evidence problem solved rather than generic "AI for materials"
    positioning.

## Promotion Criteria

Consider promotion into canonical product/strategy documentation when:

-   representative researcher conversations confirm a high-value initial
    workflow;
-   the selected workflow can be demonstrated with scientifically
    credible data and evidence;
-   the workflow exercises MaterialGraph's actual differentiators rather
    than generic AI capability;
-   competitor and adjacent-system analysis confirms the boundary
    remains useful;
-   outcome-oriented positioning can be stated without overstating
    scientific validation or commercial readiness.

No implementation milestone is created by this observation.

------------------------------------------------------------------------

# 11. Nature Materials: The Data-Only Illusion and the Gap From Compound to Useful Material

## Source

Berend Smit and Susana Garcia --- *The data-only illusion in materials
discovery*, *Nature Materials* (2026), examined together with a LinkedIn
discussion by Aldo Ferrari highlighting implications for synthesis,
application-specific functionality, and intellectual-property context.

## Why We Examined It

The commentary challenges the assumption that materials discovery can
advance primarily by scaling datasets and predictive models. This is
directly relevant to MaterialGraph because the project is intended to
support scientifically inspectable research decisions rather than equate
candidate generation with discovery.

The discussion also makes an important distinction between identifying a
plausible compound and establishing a material that is synthesizable,
characterizable, functional, and useful for a particular human or
industrial objective.

## Relevant Observations

Materials data differ from domains such as language and images in
important ways. Experimentally characterized materials occupy a
comparatively sparse and heterogeneous scientific landscape, and useful
materials depend on synthesis conditions, structures, processing,
characterization, application context, and expert scientific knowledge.

A computationally proposed compound therefore does not automatically
constitute a useful material.

``` text
Predicted / Proposed Compound
            |
            v
Scientific Plausibility
            |
            v
Synthesis Feasibility
            |
            v
Characterization / Validation
            |
            v
Application-Relevant Functionality
            |
            v
Useful Material for a Stated Objective
```

Failure can occur at any transition. A candidate may be computationally
attractive but difficult to synthesize, unstable under relevant
conditions, incompatible with processing requirements, poorly suited to
the target application, or unsupported by sufficient evidence.

The durable lesson is therefore that **prediction, synthesis,
validation, and utility are different scientific states**.

## Potential MaterialGraph Insight

### Candidate Generation Must Not Be Equated With Materials Discovery

MaterialGraph should preserve explicit distinctions among candidate
identification, scientific plausibility, evidence state, validation
readiness, physical or experimental validation, and objective-specific
usefulness.

``` text
Research Objective
        |
        v
Candidate / Pathway
        |
        v
Why It May Be Relevant
        |
        v
Evidence + Provenance
        |
        v
Unknowns / Contradictions
        |
        v
Validation Priority
        |
        v
Validation Route / Readiness
        |
        v
New Evidence
        |
        v
Researcher Evaluation of Utility
```

A candidate ranking should therefore remain a research aid rather than a
declaration that a material has been discovered or established as
useful.

### Domain Knowledge Should Participate in Reasoning, Not Merely Post-Process Predictions

The commentary reinforces MaterialGraph's existing direction toward
structured scientific knowledge, explicit relationships, constraints,
evidence, and researcher-defined objectives.

MaterialGraph should not assume that sufficiently large datasets can
eliminate the need for domain knowledge. Where scientific rules or
relationships are represented canonically, they should remain
attributable, inspectable, bounded by their applicability, and open to
revision through appropriate scientific governance.

This supports the distinction between:

``` text
Data / Observations
        +
Scientific Knowledge
        +
Research Objective
        +
Explicit Reasoning
        +
Validation
        =
Research Intelligence
```

rather than treating model output alone as scientific authority.

### Material Utility Is Objective-Dependent

Whether a material is useful cannot be determined independently of the
research or application objective.

The same candidate may be attractive for one investigation and
unacceptable for another because of differences in required performance,
stability, criticality, toxicity, processing, cost, operating
conditions, structural characteristics, or other constraints.

MaterialGraph should therefore continue treating the **Research
Objective as first-class scientific context** rather than searching for
a universally "best" material.

A stronger eventual question is not merely:

> Is this candidate scientifically interesting?

but:

> **What evidence supports this candidate as useful for this stated
> research objective, what trade-offs remain, and what must still be
> established?**

### Synthesis and Scale-Up Context May Become Important Evidence Dimensions

The article's carbon-capture example emphasizes that predicted
performance is insufficient if a candidate cannot be synthesized or
translated into a practical material.

MaterialGraph does not currently need to become a synthesis-planning or
manufacturing platform. However, future evidence models may need to
represent relevant states such as:

-   synthesis demonstrated / not demonstrated / unknown;
-   synthesis conditions and provenance;
-   reproducibility evidence;
-   processing constraints;
-   scale-up evidence or uncertainty;
-   application-condition validation.

These should be evidence dimensions rather than automatically inferred
properties.

### Intellectual-Property Context Is a Legitimate Future Exploration Question

The associated LinkedIn discussion also raises patent-landscape and
freedom-to-operate considerations for commercially exploitable
materials.

This is potentially relevant to enterprise research decisions:

``` text
Scientifically Promising
        +
Validation / Feasibility
        +
Application Utility
        +
Commercial / IP Context
        ->
Potentially Actionable R&D Opportunity
```

However, patent status and freedom-to-operate are specialized
legal/technical questions. MaterialGraph should **not** create a
patentability, infringement, or FTO score without dedicated data
sources, explicit semantics, provenance, specialist validation, and
appropriate legal boundaries.

For now, IP intelligence remains an exploratory external context that
could eventually be integrated through specialist evidence or external
tools.

## Relationship to Existing Architecture

This observation reinforces rather than replaces several existing
MaterialGraph directions:

-   Research Objectives as first-class context;
-   deterministic and inspectable reasoning;
-   Evidence Intelligence;
-   unknown and contradiction handling;
-   local and structural scientific context;
-   Validation Priority Intelligence;
-   Validation Route Selection;
-   Physical Modeling Readiness;
-   Scientific Task / Result contracts;
-   external Scientific Compute integration;
-   investigation history and provenance;
-   researcher authority over scientific interpretation.

It also strengthens an important semantic boundary:

> **Candidate != validated material != useful material for an
> objective.**

## What MaterialGraph Should Not Infer From It

This commentary does **not** establish that MaterialGraph should:

-   reject machine learning or large scientific datasets;
-   claim that AI cannot contribute substantially to materials
    discovery;
-   implement synthesis prediction immediately;
-   implement manufacturing or scale-up simulation;
-   treat expert opinion as unquestionable canonical truth;
-   automatically infer usefulness from synthesis success;
-   add patent/FTO scoring to candidate ranking;
-   claim that its current reasoning establishes experimental utility;
-   broaden scope before representative researcher workflows justify it.

The lesson is not "data is unimportant." The lesson is that
**data-driven prediction is only one part of the materials-discovery and
materials-development process**.

## Current Decision

**DURABLE SCIENTIFIC / PRODUCT INSIGHT ACCEPTED --- NO NEW
IMPLEMENTATION COMMITMENT**

The following principles are accepted for continued evaluation:

1.  candidate generation must remain distinct from scientific validation
    and objective-specific material utility;
2.  domain knowledge, evidence, and research context remain necessary
    complements to data-driven methods;
3.  Research Objectives should remain first-class because usefulness is
    context-dependent;
4.  synthesis, processing, scale-up, and application evidence may
    eventually become important evidence dimensions;
5.  IP/FTO intelligence is a legitimate future exploration area but
    requires specialist boundaries and should not enter current scoring
    or canonical reasoning.

## Promotion / Implementation Criteria

Consider additional canonical promotion or implementation only when:

-   representative researcher workflows demonstrate that synthesis,
    processing, application, or commercial context materially changes
    decisions;
-   the relevant scientific states and evidence semantics can be
    represented honestly;
-   authoritative or appropriately attributed data sources are
    available;
-   missing evidence can remain explicitly unknown;
-   domain experts can evaluate representative outputs;
-   any IP-related capability has clear provenance, legal boundaries,
    and specialist validation;
-   the added context improves researcher decisions without turning
    MaterialGraph into an unbounded universal materials platform.

------------------------------------------------------------------------

# 12. Discovered Materials --- Material Discovery Bench and Scientific Research Evaluation

## Source

Discovered Materials --- *Material Discovery Bench* (2026), an
open-ended, long-horizon benchmark for AI-driven materials discovery in
semiconductor applications.

## Why We Examined It

Material Discovery Bench is relevant to MaterialGraph not because
MaterialGraph should reproduce an AI-agent benchmark, but because it
makes a broader question concrete:

> **How should a scientific research system be evaluated beyond ordinary
> software correctness?**

MaterialGraph already distinguishes engineering validation from
scientific and researcher validation. Material Discovery Bench provides
an external example of a system attempting to evaluate a realistic,
multi-objective scientific research task rather than only isolated model
accuracy or software behavior.

The benchmark asks models to search for thermally conductive dielectric
materials relevant to semiconductor 3D integration while satisfying
multiple property and stability constraints and proposing a plausible
synthesis route.

## Relevant Observations

### 1. Scientific evaluation can be organized around a realistic research objective

The benchmark does not evaluate candidate generation in isolation. A
successful candidate must satisfy several requirements simultaneously,
including thermal, dielectric, mechanical, stability, novelty, process,
and synthesis-related considerations.

This reinforces an important MaterialGraph principle:

``` text
Scientific Benchmark
        |
        +-- explicit research objective
        +-- multiple simultaneous constraints
        +-- scientifically meaningful success criteria
        +-- evidence / verification requirements
        +-- failure and rejection states
        +-- validation beyond candidate generation
```

A future MaterialGraph evaluation should likewise test whether the
system helps with a coherent research decision rather than rewarding the
production of large numbers of candidates.

### 2. Computationally promising does not mean synthesizable or useful

Material Discovery Bench reports that the tested systems produced many
computationally promising candidates, while plausible synthesis routes
were much harder to obtain.

The durable lesson is the attrition boundary:

``` text
Computationally Promising Candidate
        |
        v
Plausibly Synthesizable
        |
        v
Experimentally Attempted
        |
        v
Successfully Synthesized
        |
        v
Characterized / Reproduced
        |
        v
Application-Relevant Material
```

These states must not be collapsed.

This reinforces the existing MaterialGraph distinction:

> **candidate != validated material != useful material for an
> objective**

A computational result can support investigation without becoming
evidence of experimental feasibility or application utility.

### 3. Benchmark optimization can diverge from scientific intent

The benchmark documents reward-hacking and objective-circumvention
behavior, including attempts to exploit novelty checks or submit
unsupported property values.

This demonstrates a general evaluation risk:

``` text
Optimize Evaluation Metric
        !=
Satisfy Scientific Intent
```

For MaterialGraph, this strengthens the case for explicit objective
semantics, inspectable constraint satisfaction, provenance, conservative
validation, and researcher review.

A future benchmark should therefore test not only whether an output
reaches a score threshold, but whether the system satisfied the intended
scientific meaning of the task.

### 4. Long-horizon scientific work requires persistent research state

The benchmark also reports degradation, confusion, or loss of task
coherence during very long model runs.

MaterialGraph should not infer that long-context AI agents are required.
Instead, the observation reinforces the value of explicit, persistent
investigation state:

``` text
Research Objective
        |
        v
Investigation State
        |
        +-- hypotheses
        +-- candidates
        +-- attempted directions
        +-- rejected directions
        +-- evidence
        +-- contradictions
        +-- unknowns
        +-- validation priorities
        +-- researcher decisions
        |
        v
Next Research Action
```

The research investigation should exist as structured, versioned state
rather than depend on a model remembering the investigation internally.

### 5. Horizontal research infrastructure can be evaluated through a narrow vertical

Material Discovery Bench focuses on a concrete semiconductor materials
problem rather than attempting to benchmark "materials discovery"
universally.

This reinforces the previously recorded distinction:

> **Horizontal architecture does not require horizontal validation or
> go-to-market.**

MaterialGraph may remain general research-intelligence infrastructure
while eventually validating its usefulness through one or more narrow,
scientifically meaningful workflows.

The initial evaluation question should not be:

> How many materials can MaterialGraph generate?

A more appropriate direction may be:

> **How well does MaterialGraph support an inspectable, evidence-aware,
> objective-sensitive research decision?**

## Potential MaterialGraph Insight

MaterialGraph may eventually need a scientific/research evaluation
framework that complements its engineering test suite.

A possible evaluation stack is:

``` text
Engineering Correctness
        |
        +-- unit / integration tests
        +-- API contracts
        +-- migrations
        +-- deterministic regression tests
        |
        v
Scientific Semantic Correctness
        |
        +-- objective semantics
        +-- constraint fidelity
        +-- relationship / pathway validity
        +-- evidence and provenance integrity
        +-- uncertainty honesty
        |
        v
Research-Task Evaluation
        |
        +-- useful candidate / pathway identification
        +-- evidence quality
        +-- decision-relevant unknowns
        +-- validation-priority usefulness
        +-- reproducibility
        |
        v
External Scientific / Researcher Validation
        |
        +-- literature cross-checking
        +-- specialist computation
        +-- domain-expert review
        +-- experimental evidence where appropriate
        +-- researcher workflow evaluation
```

This is an evaluation direction, not yet a specification for a
MaterialGraph benchmark.

## Required Broader Investigation Before Promotion

Material Discovery Bench should be treated as **one case study**, not as
the template from which MaterialGraph immediately designs its own
benchmark.

Before proposing a MaterialGraph-specific scientific or research
benchmark, investigate how other scientific research systems,
materials-discovery platforms, computational-science tools, and
autonomous or AI-assisted research systems are evaluated.

That investigation should compare, where evidence is available:

1.  what scientific capability or research task is being evaluated;
2.  what constitutes success, partial success, failure, or abstention;
3.  whether evaluation measures model performance, scientific validity,
    researcher usefulness, workflow efficiency, or some combination;
4.  how multi-objective scientific requirements are represented;
5.  how uncertainty, missing evidence, contradictory evidence, and
    unsupported claims are treated;
6.  how novelty and duplication are assessed;
7.  how benchmark gaming, reward hacking, leakage, or proxy-metric
    failure are detected;
8.  how computational predictions are separated from synthesis,
    characterization, experimental validation, and real-world utility;
9.  whether human domain experts participate in rubric design or
    evaluation;
10. how reproducibility, provenance, method/version identity, and
    evaluation artifacts are preserved;
11. whether evaluation reflects realistic researcher workflows or only
    isolated benchmark tasks;
12. how performance changes across scientific domains, data regimes, or
    out-of-distribution cases;
13. what evidence exists that benchmark performance correlates with
    actual research usefulness.

The intended investigation sequence is:

``` text
Material Discovery Bench
        |
        v
Study Its Evaluation Methodology
        |
        v
Investigate How Other Scientific Systems Are Evaluated
        |
        v
Compare Evaluation Philosophies and Failure Modes
        |
        v
Identify What Is Relevant to MaterialGraph
        |
        v
Define MaterialGraph Evaluation Principles
        |
        v
Only Then Consider a
MaterialGraph Scientific / Research Benchmark
```

This broader comparison should include both successful evaluation
approaches and documented weaknesses. The purpose is not to find a
benchmark to copy, but to understand what responsible evaluation of
scientific research software actually requires.

## What MaterialGraph Should Not Infer From It

Material Discovery Bench does **not** currently justify:

-   turning MaterialGraph into an autonomous AI scientist;
-   replacing deterministic canonical reasoning with long-running LLM
    agents;
-   optimizing for number of generated materials;
-   treating computational screening as experimental discovery;
-   using one benchmark score as a proxy for scientific usefulness;
-   adopting the benchmark's semiconductor objective as MaterialGraph's
    permanent product vertical;
-   assuming that an LLM grader can establish scientific truth;
-   creating a MaterialGraph benchmark before representative scientific
    evaluation methods have been investigated;
-   adding a roadmap implementation milestone solely because this
    benchmark exists.

## Current Decision

**HIGH-VALUE EXTERNAL EVALUATION INSIGHT --- BROADER INVESTIGATION
REQUIRED / NO MATERIALGRAPH BENCHMARK COMMITMENT**

The durable lessons are:

1.  scientific systems need evaluation beyond software correctness;
2.  realistic evaluation should preserve multi-objective scientific
    intent;
3.  candidate generation, synthesizability, validation, and utility must
    remain separate states;
4.  benchmark scores can be gamed and therefore cannot substitute for
    inspectable scientific semantics;
5.  persistent structured investigation state is important for
    long-horizon research;
6.  narrow scientific workflows may provide a practical way to evaluate
    a broader research architecture;
7.  MaterialGraph should investigate how other scientific systems are
    evaluated before defining its own scientific/research benchmark.

## Promotion Criteria

Consider promoting a MaterialGraph scientific/research benchmark into
canonical documentation or the roadmap only after:

-   multiple scientific-system evaluation approaches have been
    investigated;
-   representative materials-science research workflows have been
    studied;
-   the intended evaluation target is explicit;
-   scientific validity is separated from benchmark performance;
-   objective semantics and anti-gaming requirements are understood;
-   evidence, provenance, uncertainty, and abstention behavior can be
    evaluated;
-   domain experts can review the proposed evaluation criteria;
-   the benchmark measures something meaningfully related to researcher
    usefulness rather than merely producing an attractive score;
-   the evaluation can be reproduced with versioned inputs, methods,
    rules, and artifacts.

No implementation milestone is created by this observation.

------------------------------------------------------------------------

# 13. Industrial Materials R&D: Learning-Driven Development and Researcher Decision Authority

## Source

Serge Lapshin --- LinkedIn discussion, *Materials AI: From Bayesian Optimization to Learning-Driven R&D* (August 2026), describing industrial materials development as a multi-constraint process involving materials science, AI/ML, experimental design, simulation, laboratory automation, scale-up knowledge, application expertise, and R&D data infrastructure.

## Why We Examined It

The post is relevant because it frames materials R&D around better scientific decisions rather than model output alone. A candidate that performs well on one predicted or measured property may still fail because of processability, stability, impurity sensitivity, raw-material variability, customer qualification, cost, regulatory constraints, manufacturing robustness, or scale-up requirements.

This reinforces a founding MaterialGraph boundary: the platform should improve the researcher's decision context without becoming the scientific decision-maker.

## Relevant Observations

Industrial materials development is inherently multi-objective and context-dependent. Prediction or optimization can narrow the search space and help prioritize work, but practical value depends on evidence and constraints distributed across scientific, experimental, process, manufacturing, application, and organizational contexts.

A useful conceptual distinction is:

``` text
Algorithm / Model / MaterialGraph Signal
                |
                v
Candidate or Research Opportunity
                |
                v
Evidence + Trade-offs + Unknowns
                |
                v
Validation Options / Priorities
                |
                v
Researcher / R&D Team Judgement
                |
                v
Research Decision
```

The durable lesson is not that Bayesian optimization or Materials AI should be rejected. It is that **learning faster and testing more intelligently remain means for improving human scientific decisions, not substitutes for scientific judgement.**

## Potential MaterialGraph Insight

### MaterialGraph Should Support Decisions, Not Make Them

MaterialGraph may rank, compare, expose trade-offs, identify uncertainty, prioritize validation needs, and show how a result changes under an explicit objective. It should not silently convert those outputs into an instruction that a researcher must choose a particular material, pathway, experiment, or validation route.

A researcher-facing result should preserve the conditional meaning of ranking:

> **Under this stated objective, these constraints, this methodology, and the currently available evidence, this candidate ranks highest.**

This must remain distinct from:

> **This is the material the researcher should use.**

The latter requires scientific and practical judgement that may depend on context MaterialGraph does not possess.

### Validation Priority Intelligence Must Preserve Researcher Choice

VPI should identify which unresolved questions appear most decision-relevant and explain why resolving them may matter. It may suggest an appropriate class of validation where applicability is represented. It should not autonomously prescribe the next experiment as scientific truth.

Researchers should be able to inspect, disagree with, override, or defer a validation priority and preserve the reason for doing so. This makes VPI a decision-support capability rather than an autonomous research authority.

### Industrial Constraints Are Evidence and Objective Context, Not Automatic Universal Scores

Processability, impurity sensitivity, raw-material variability, manufacturability, scalability, customer qualification, cost, regulatory constraints, and manufacturing robustness may eventually matter to MaterialGraph investigations. They should not be collapsed prematurely into one universal industrial-readiness score.

Where such dimensions are introduced, MaterialGraph should preserve their definitions, conditions, provenance, evidence coverage, uncertainty, and objective relevance.

### Evaluation Should Include Decision-Support Quality

This observation also strengthens the emerging evaluation direction recorded through Material Discovery Bench. MaterialGraph should eventually be evaluated not only on whether it generates a plausible or known candidate, but also on whether it provides sufficiently accurate, relevant, inspectable, and uncertainty-aware information for a researcher to make a better-informed decision.

Possible evaluation questions include:

- Were important trade-offs exposed rather than hidden by a single score?
- Were missing or contradictory evidence states visible?
- Was the ranking correctly scoped to the stated objective and evidence state?
- Did the system distinguish recommendation strength from scientific validity?
- Could the researcher understand why alternatives differed?
- Did validation priorities identify decision-relevant uncertainty without removing researcher authority?

## Relationship to Existing Architecture

This reinforces existing MaterialGraph directions: Research Objectives, deterministic ranking, comparative intelligence, Evidence Intelligence, uncertainty and contradiction handling, VPI, Validation Route Selection, investigation history, external scientific-tool integration, and researcher authority over interpretation and decisions.

## What MaterialGraph Should Not Infer From It

This post does **not** establish that MaterialGraph should implement Bayesian optimization, automate industrial R&D, model every manufacturing constraint now, autonomously choose experiments, or create a universal industrial-readiness score. Those capabilities require separate evidence, semantics, researcher validation, and scope justification.

## Current Decision

**DURABLE PRINCIPLE REINFORCED / PROMOTED TO CANONICAL DOCUMENTATION --- NO NEW IMPLEMENTATION COMMITMENT**

The promoted principle is:

> **MaterialGraph should improve the quality of scientific decisions by structuring alternatives, evidence, trade-offs, uncertainty, and validation needs while preserving the researcher's authority to decide.**

------------------------------------------------------------------------

# 14. Evidence Intelligence: Independent Information, Redundancy, and Decision Value

## Source

Robert Vrabel --- *Determinant Dynamics under Low-Rank Perturbations: A Unified Framework for Singular Systems* (2026), encountered through a LinkedIn discussion emphasizing the geometric interpretation that new independent directions can expand a represented volume while redundant directions do not.

This entry records the broader evidence-intelligence question prompted by that idea. It does **not** adopt determinant dynamics, pseudodeterminants, or the paper's matrix formalism as a MaterialGraph evidence method.

## Why We Examined It

MaterialGraph already treats evidence as more than a collection of supporting records. Existing directions distinguish provenance, missing evidence, contradiction, comparability, objective relevance, validation priority, and scientific validation state.

The post raises a useful additional question:

> **When new evidence is added to an investigation, what scientifically relevant information does it actually contribute?**

Several records may appear to provide substantial support while ultimately depending on the same underlying dataset, experiment, computational method, database record, or derived source. Conversely, one independent measurement or method may materially change the evidence state even though it adds only one additional record.

This suggests that evidence quantity and evidence contribution should remain distinct concepts.

## Relevant Observations

### Evidence Collection and Evidence Processing Are Different Responsibilities

A mature evidence workflow may need to distinguish evidence acquisition, identity/scope, provenance, quality/applicability, comparability, independence/redundancy, agreement/contradiction, coverage, objective relevance, decision sensitivity, potential information value, and validation priority.

These dimensions need not become a single linear implementation pipeline. The important point is that "we have more evidence" is not equivalent to "we have proportionally more independent scientific information."

### Evidence Quantity Is Not Evidence Diversity

MaterialGraph should eventually be able to distinguish, where scientific semantics and provenance permit it, multiple records reporting the same underlying result; independent measurements of the same claim; different computational methods addressing the same property; evidence obtained under materially different conditions; corroborating or contradictory evidence; evidence that is not scientifically comparable; and evidence whose dependency or provenance is unknown.

Five records should not automatically be interpreted as five independent confirmations.

At the same time, related or repeated evidence is not necessarily useless. Replication, corroboration, methodological agreement, reinterpretation, and broader condition coverage can each have scientific value. MaterialGraph should therefore avoid both naive evidence counting and naive deduplication.

### Evidence Relationships May Be First-Class Scientific Context

A future evidence model may need relationships such as `derived_from`, `corroborates`, `contradicts`, `independently_supports`, `shares_underlying_source_with`, `shares_method_with`, `validates_under_different_conditions`, `not_comparable_with`, and `dependency_unknown`.

These are conceptual examples, not a proposed schema or controlled vocabulary.

The broader architectural insight is that evidence may itself form a graph of claims, sources, methods, dependencies, conditions, and validation relationships rather than exist only as flat attachments to a material or candidate.

### Evidence Strength Should Not Be Collapsed Prematurely Into One Score

A researcher may benefit more from an inspectable evidence profile than from a single aggregate number. Relevant dimensions could include evidence coverage, source diversity, independent support, method agreement, structural evidence, experimental evidence, objective relevance, and decision sensitivity.

MaterialGraph should be cautious about collapsing coverage, diversity, independence, quality, agreement, applicability, and objective relevance into a universal "evidence score." If aggregate measures are eventually introduced, their components and limitations should remain inspectable.

### Information Contribution May Matter to Validation Priority

This observation extends the existing Validation Priority Intelligence direction.

VPI currently asks which unresolved question matters most to the research decision. A later evidence-intelligence question may be:

> **Among scientifically appropriate validation options, which one is likely to contribute the most decision-relevant and sufficiently independent information?**

Possible considerations include objective relevance, independence/redundancy, uncertainty reduction, decision sensitivity, and applicability/readiness.

This does not mean that MaterialGraph should automatically optimize experiments or calculate a universal information-gain value. It means that the **incremental scientific contribution of evidence** may eventually be relevant when explaining why one validation need deserves attention before another.

## Relationship to Existing Architecture

This observation extends Evidence Intelligence, evidence provenance and coverage, unknown and contradiction handling, computational evidence comparability, Research Objectives, scenario and sensitivity semantics, Validation Priority Intelligence, Validation Route Selection, Scientific Task / Result contracts, investigation history, and researcher authority over validation and decisions.

It also reinforces a broader MaterialGraph principle:

> **Evidence should be processed according to its scientific meaning and contribution to the investigation, not merely accumulated and counted.**

## What MaterialGraph Should Not Infer From It

This observation does **not** currently justify using determinants or pseudodeterminants to score scientific evidence; assuming evidence can be represented meaningfully as independent numerical vectors; implementing a universal information-gain formula; assigning independence automatically from source count; treating different methods as automatically independent; discarding repeated or correlated evidence as scientifically worthless; creating a universal evidence-strength score; autonomously selecting experiments; or changing current candidate ranking solely because this concept is attractive.

Any quantitative treatment of evidence dependence, novelty, information gain, or expected validation value would require explicit scientific semantics, appropriate representations, calibration, representative researcher workflows, and domain-expert validation.

## Current Decision

**HIGH-VALUE EVIDENCE-INTELLIGENCE INSIGHT --- EXPLORATORY / NO IMPLEMENTATION COMMITMENT**

The durable principle to retain is:

> **MaterialGraph should eventually distinguish evidence quantity from evidence diversity, independence, comparability, corroboration, contradiction, coverage, objective relevance, and decision value. Additional evidence is valuable not merely because it increases the number of supporting records, but because of what scientifically relevant information it contributes to the investigation.**

The determinant-based mathematics that prompted this observation is **not** promoted into MaterialGraph architecture.

## Promotion / Implementation Criteria

Consider further canonical promotion or implementation only when representative researcher workflows show that correlated, duplicated, or dependent evidence materially affects decisions; evidence identity and provenance are sufficiently structured to reason about dependency honestly; comparability and independence semantics can be defined for specific evidence classes; unknown dependency can remain explicitly unknown; corroboration and replication can be preserved without being mistaken for independent evidence; any quantitative measure has a scientifically defensible interpretation rather than manufactured precision; VPI can use evidence contribution without confusing expected information value with scientific validity; domain experts can evaluate representative evidence profiles and validation-priority explanations; and researcher authority remains explicit.

No implementation milestone is created by this observation.

------------------------------------------------------------------------

# 15. Cross-Project Lessons

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

## Horizontal Architecture Can Be Proven Through Vertical Workflows

MaterialGraph can preserve a reusable research-intelligence architecture
while initially demonstrating value through a narrow, outcome-oriented
materials workflow. Product focus and architectural generality do not
need to be the same thing.

## Differentiate by Research Decisions, Not Generic AI Claims

As foundation models, simulators, autonomous laboratories, and vertical
materials products become more capable, MaterialGraph should make its
differentiation explicit: inspectable objectives, reasoning, evidence,
uncertainty, alternatives, and validation planning.

## Specialist Capability Growth Strengthens the Integration Boundary

A richer external ecosystem increases the value of explicit task/result,
provenance, readiness, and evidence-comparability boundaries.
MaterialGraph should preferentially compose mature specialist
capabilities where that is scientifically and product-wise justified
rather than duplicate them.

## Prediction, Validation, and Utility Are Different Scientific States

A generated or ranked candidate should not silently become a discovered
or useful material. MaterialGraph should preserve the transitions among
plausibility, synthesis, characterization, validation, and
objective-specific utility.

## Material Utility Is Defined Relative to a Research Objective

A material can be scientifically credible yet unsuitable for a
particular application or constraint set. Research Objectives should
remain first-class context for interpreting candidate value, evidence,
trade-offs, and validation needs.

## Domain Knowledge Complements Data-Driven Methods

Scientific data and learned models can be powerful inputs, but materials
research also depends on structured domain knowledge, conditions,
synthesis and processing context, evidence provenance, and expert
interpretation. MaterialGraph should compose these sources without
treating any single one as automatic scientific truth.

## Evidence Quantity and Evidence Contribution Are Different

More evidence records do not necessarily mean proportionally more independent
scientific information. MaterialGraph should eventually preserve evidence
dependencies, redundancy, corroboration, contradiction, comparability,
coverage, and objective relevance where those relationships can be established
honestly.

## Researcher Authority Remains Central

Even as scientific systems become more automated, researchers should
retain visibility and authority over interpretation, validation, and
decisions.

------------------------------------------------------------------------

# 16. Ideas Deliberately Not Promoted

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

# 17. Future Exploration Questions

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

-   How are other scientific research systems evaluated, and which
    evaluation principles are appropriate for measuring MaterialGraph's
    scientific and researcher usefulness without confusing benchmark
    performance with scientific validity?

-   How should MaterialGraph represent evidence dependence, redundancy,
    corroboration, and independent information contribution without inventing
    unjustified quantitative precision, and when should those distinctions
    influence validation priority?
