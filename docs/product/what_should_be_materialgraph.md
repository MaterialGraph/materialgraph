# What MaterialGraph Should Be

> **Project direction, scientific boundaries, and development
> principles**
>
> Initial version derived from architecture and code review through
> **v1.9.6 --- Endpoint-Sensitive Research Ranking**.

## 1. Purpose of This Document

This document defines what MaterialGraph should become and what it
should avoid becoming.

It is intentionally different from a feature list, roadmap, or
architecture inventory. It records project-level principles discovered
by reviewing the actual implementation and real API behavior.

This document should be updated only when code review, researcher
feedback, real-response verification, or external validation reveals
something important about:

-   researcher usefulness;
-   scientific meaning;
-   verifiability;
-   system boundaries;
-   architecture integration;
-   misleading terminology;
-   missing capabilities;
-   duplicated intelligence;
-   uncertainty;
-   validation needs.

MaterialGraph should not grow by accumulating impressive-sounding
features. It should grow by improving the quality, usefulness,
traceability, and scientific honesty of research decision support.

------------------------------------------------------------------------

## 2. Core Identity

MaterialGraph should be:

> **A deterministic, explainable, graph-driven materials research
> intelligence system that helps researchers explore, compare, inspect,
> and validate material opportunities while keeping scientific judgement
> with the researcher.**

MaterialGraph may:

-   organize materials and relationships;
-   generate constrained discovery opportunities;
-   explore multi-hop pathways;
-   rank using explicit deterministic dimensions;
-   expose score breakdowns;
-   compare alternatives;
-   identify evidence gaps;
-   expose assumptions;
-   preserve unresolved ties;
-   prioritize validation needs;
-   show why an opportunity was generated;
-   help researchers decide what to inspect next.

MaterialGraph must not claim to replace:

-   domain expertise;
-   literature review;
-   crystallographic analysis;
-   DFT or other computational validation;
-   synthesis planning by experts;
-   laboratory experiments;
-   peer review;
-   scientific judgement.

------------------------------------------------------------------------

## 2.1. Mission-Level Objective

> **Build an exceptional scientific software system and create the
> infrastructure through which domain experts can encode, inspect, and
> use their knowledge.**

This mission clarifies MaterialGraph's role. The platform should not
attempt to replace materials scientists or convert software-generated
signals into substitutes for domain expertise. Its purpose is to provide
durable scientific infrastructure through which expert knowledge,
evidence, assumptions, relationships, constraints, and research
decisions can become more structured, inspectable, reproducible, and
reusable.

The intended knowledge workflow is:

``` text
Encode
  │
  ▼
Connect
  │
  ▼
Reason
  │
  ▼
Inspect
  │
  ▼
Compare
  │
  ▼
Preserve
  │
  ▼
Share
  │
  ▼
Refine
  └──────────────↺
```

Domain experts remain responsible for scientific judgement.
MaterialGraph should provide the infrastructure that helps them express
what is known, distinguish it from what is inferred or missing, examine
relationships and alternatives, preserve the reasoning behind decisions,
and continue an investigation without losing scientific context.

### Mission gate for future capabilities

A proposed capability should be evaluated against the following
question:

> **Does this help domain experts encode, connect, inspect, reason over,
> preserve, share, or use scientific knowledge more effectively while
> maintaining provenance, uncertainty, and scientific boundaries?**

If the answer is unclear, the capability should not enter the core
product merely because it is technically impressive. This gate applies
equally to future AI assistance, literature integration, private
evidence overlays, physical-modeling integrations, collaboration
features, and new compute infrastructure.

This mission complements the MaterialGraph Research Cycle: the mission
defines **why MaterialGraph exists**, while the Research Cycle defines
**how researchers experience that mission**.

------------------------------------------------------------------------

## 2.2. The MaterialGraph Research Cycle

MaterialGraph should not feel like a collection of scientific APIs,
endpoint pages, or isolated analysis tools. It should feel like one
continuous, inspectable research investigation.

> **MaterialGraph should help a researcher move from a scientific
> question to an evidence-backed material decision through a continuous,
> explainable, and iterative workflow.**

The intended cycle is:

``` text
Start From a Material
        │
        ▼
Define a Research Objective
        │
        ▼
Generate Ranked, Explained Candidates
        │
        ▼
Inspect Evidence, Assumptions, and Gaps
        │
        ▼
Explore Relationships and Pathways
        │
        ▼
Compare Alternatives
        │
        ▼
Save the Investigation
        │
        ▼
Share and Collaborate
        │
        ▼
Refine the Objective
        │
        └───────────────────────────────↺
```

The loop is essential. Scientific exploration rarely ends after one
ranked result or comparison. Researchers revise constraints, test
another hypothesis, inspect different evidence, and continue from what
they learned. MaterialGraph should preserve that continuity rather than
forcing each query to begin as an unrelated task.

### Product identity rule

The platform's differentiation should come less from any single
algorithm and more from how naturally the complete workflow supports
scientific exploration. Algorithms, scores, graph operations, evidence
views, and collaboration features should contribute to a coherent
investigation rather than exist as a feature collection.

### Design and roadmap gate

Every proposed capability should answer at least one of these questions:

1.  Which stage of the Research Cycle does it improve?
2.  How does it help the researcher move to the next stage?
3.  Does it preserve the context, evidence, and decisions from earlier
    stages?
4.  Does it support refinement and continued exploration?

If a feature does not materially improve the Research Cycle, its
priority should be questioned before implementation. This rule
complements the scientific and architectural gates elsewhere in this
document and helps prevent MaterialGraph from becoming a disconnected
feature factory.

------------------------------------------------------------------------

## 2.3. MaterialGraph Should Separate Scientific Knowledge From Research Perspective

Different researchers may investigate the same material, relationships, and
evidence while pursuing fundamentally different research objectives.

For example, researchers starting from the same material may prioritize
different concerns:

- supply criticality or resource availability;
- structural or chemical continuity;
- performance-related properties;
- sustainability;
- application suitability;
- validation readiness;
- cost or other research constraints.

These differences should not require separate representations of the underlying
scientific knowledge, nor should MaterialGraph imply that one universal ranking
or definition of a "good" candidate is scientifically correct.

The intended separation is:

``` text
Shared Scientific Knowledge
        │
        ├── materials
        ├── identities
        ├── relationships
        ├── properties
        ├── evidence
        ├── provenance
        └── uncertainty
        │
        ▼
Explicit Research Objective
        │
        ├── constraints
        ├── preferences
        ├── preservation requirements
        ├── target context
        └── exploration bounds
        │
        ▼
Objective-Sensitive Reasoning
        │
        ▼
Contextual Candidates / Pathways / Comparisons
        │
        ▼
Inspect Evidence, Trade-offs, and Uncertainty
```

The underlying material facts, relationships, provenance, evidence, and
uncertainty should remain independently inspectable. The research objective
should determine which constraints, preferences, pathways, trade-offs, and
validation needs matter for the current investigation.

This creates an important principle:

> **Different research objectives may produce different rankings, pathways,
> or priorities from the same underlying scientific knowledge without creating
> a contradiction. The methodology should remain consistent and inspectable
> even when the research perspective changes.**

MaterialGraph should therefore avoid encoding a candidate as universally
"good", "bad", "best", or "preferred" when that judgement depends on the
research objective.

For example, a candidate that is attractive under a supply-risk objective may
be less attractive under a structural-continuity or performance-oriented
objective. MaterialGraph should preserve the reason for that difference rather
than collapsing the perspectives into one global judgement.

### Objective-dependent results must remain reproducible

Researcher-specific perspective must not weaken determinism.

Given the same:

- underlying knowledge and evidence versions;
- research objective;
- configuration;
- software version;
- ordering rules;

MaterialGraph should produce the same objective-sensitive result and
explanation.

Changing the objective may legitimately change the result. Changing the
researcher without changing the explicit objective should not.

### Research objectives should remain separate from canonical knowledge

A researcher's preferences or constraints should not silently mutate canonical
material facts or graph relationships.

The preferred conceptual boundary is:

``` text
Canonical / Shared Knowledge
        +
Explicit Research Context
        =
Contextual Research Intelligence
```

This separation is important for saved investigations, comparison,
collaboration, future private research contexts, and scientific reproducibility.
MaterialGraph should be able to preserve not only **what result was produced**
but also **from which research perspective it was produced**.

### Design and architecture consequence

Future objective modeling, ranking, comparison, validation-priority
intelligence, saved investigations, and researcher-facing interfaces should
preserve this distinction explicitly.

When evaluating a new capability, MaterialGraph should ask:

1. Is this information an underlying scientific fact, relationship, evidence
   item, or uncertainty state?
2. Is it part of the researcher's current objective or perspective?
3. Does it change the shared knowledge, or only how that knowledge is explored
   and evaluated?
4. Can another researcher apply a different objective to the same knowledge
   without corrupting or overwriting the first investigation?
5. Can the system explain why the two objectives produced different results?

The goal is not to make every research perspective equivalent. Some objectives
may be unsupported, internally inconsistent, scientifically inappropriate, or
blocked by missing evidence. MaterialGraph should expose those limitations
rather than force an answer.

The governing idea is:

> **Shared knowledge should remain objective-independent where scientifically
> appropriate; exploration and decision support should be objective-sensitive,
> explicit, reproducible, and inspectable.**

-------------------------------------------------------------------------------

## 3. The System Should Work as One Intelligence Pipeline

The reviewed implementation shows a meaningful layered flow:

``` text
Research Objective
        │
        ▼
Discovery Chain Generation
        │
        ▼
Objective Filtering
        │
        ▼
Deterministic Path Ranking
        │
        ▼
Research Opportunity Construction
        │
        ▼
Evidence Enrichment
        │
        ▼
Comparative Research Intelligence
        │
        ▼
Endpoint-Sensitive Tie Analysis
        │
        ▼
Researcher Decision Support
```

This is a direction MaterialGraph should preserve.

New capabilities should normally improve or enrich this flow rather than
create parallel, disconnected intelligence systems.

A new service should answer:

1.  What upstream output does it consume?
2.  What genuinely new information does it add?
3.  Which downstream capability uses that information?
4.  Why does this logic belong here rather than in an existing service?
5.  Can the researcher inspect the result?

If these questions are unclear, implementation should not begin.

------------------------------------------------------------------------

## 4. MaterialGraph Should Prefer Honest Uncertainty Over Artificial Precision

The verified LiFePO4 → Na/phosphate case is an important project
principle.

For the objective:

-   avoid `Li`;
-   prefer `Na`;
-   preserve `Fe`, `P`, `O`;
-   target `phosphate`;
-   `max_hops = 2`;
-   `limit = 5`;

MaterialGraph returned five scientifically distinct endpoint
opportunities:

-   Na3Fe3(PO4)4
-   Na9Fe3P8O29
-   NaFeP2O7
-   NaFePO4
-   Na3Fe(PO4)2

All five received the same scientific usefulness score of `94.95`.

The correct response was not to invent a tie-breaker.

The v1.9.5 comparative layer exposed meaningful differences while
preserving the tie. The v1.9.6 endpoint-sensitive layer examined
available endpoint evidence and still preserved the tie because current
evidence did not justify deterministic differentiation.

This behavior should remain a core principle:

> **If available evidence cannot justify differentiation, MaterialGraph
> should say so explicitly.**

A genuine tie is a valid scientific decision-support output.

Tie preservation must apply not only to numeric scores but also to
summaries, labels, selected representatives, and downstream comparisons.

> **If several pathways share the highest supported score or evidence
> state, MaterialGraph must not imply a unique winner merely because
> list order, stable sorting, or a selection function returns one
> item.**

A tied top group should remain a tied top group unless additional
evidence justifies differentiation.

------------------------------------------------------------------------

## 5. MaterialGraph Should Distinguish Signal From Proof

A major finding from code review is that some current scientific
language can be stronger than the underlying computation.

For example, current transition logic derives `preserved_framework` from
the intersection of element symbols present in the source and target
materials.

That is useful as a deterministic compositional signal.

However:

> **Shared elements are not proof of preserved crystal structure,
> bonding topology, phase behavior, coordination environment, or
> functional framework.**

Therefore MaterialGraph should distinguish among concepts such as:

-   shared elemental composition;
-   preserved chemistry overlap;
-   inferred family continuity;
-   encoded relationship continuity;
-   structural framework preservation;
-   experimentally validated preservation.

These concepts must not be treated as interchangeable.

### Directional rule

Until stronger structural evidence exists, outputs derived from element
intersection should use terminology that reflects what is actually
known.

Prefer language such as:

-   `shared_compositional_framework`
-   `shared_chemistry_elements`
-   `composition_overlap`
-   `preserved_element_set`

Avoid implying verified structural preservation unless supported by
appropriate structural evidence.

This is not merely a naming issue. Terminology affects researcher trust
and the scientific interpretation of downstream ranking, confidence,
comparison, and evidence outputs.

The same inferred signal may propagate through multiple layers:

``` text
element-set overlap
        │
        ▼
preserved_framework
        │
        ▼
framework-preservation score
        │
        ▼
supporting signal
        │
        ▼
confidence / readiness interpretation
        │
        ▼
comparative research output
```

This creates an important rule:

> **An inferred signal must not become stronger merely because multiple
> downstream services reuse it. Repetition across ranking, evidence, and
> comparison layers does not create independent evidence.**

MaterialGraph should preserve provenance through the full pipeline so a
researcher can distinguish several independent supporting facts from
several downstream interpretations of the same upstream fact.

------------------------------------------------------------------------

## 6. MaterialGraph Should Make Objective Semantics Match Actual Execution

Current objective handling exposes list-shaped concepts such as:

-   `avoid_elements`
-   `prefer_elements`
-   `preserve_elements`

However, reviewed objective-chain execution currently forwards only the
first avoid element and first prefer element into chain generation and
path ranking.

This creates an important principle:

> **The apparent expressiveness of a research objective must match the
> actual semantics executed by the system.**

MaterialGraph should not accept a richer objective shape while silently
executing only a subset unless that limitation is explicit.

Future work should determine whether to:

-   support all avoid/prefer elements end to end;
-   constrain the schema to actual supported semantics; or
-   expose explicit warnings when only part of an objective is applied.

The correct choice should be made after tracing all dependent services.
It should not be patched locally without understanding candidate
generation, transition validation, ranking, comparison, and backward
compatibility.

------------------------------------------------------------------------

## 7. Search-Space Construction Is Part of Scientific Meaning

The reviewed chain service is production-aware:

-   bounded hop depth;
-   bounded expansion;
-   cycle prevention;
-   candidate caching;
-   relationship caching;
-   family-result caching;
-   delegated transition validation.

These are valuable engineering properties.

However, the chain-generation process also determines which
opportunities can ever reach downstream intelligence.

Therefore:

> **Search-space construction is not only a performance concern. It is
> part of the scientific behavior of MaterialGraph.**

Limits such as:

-   maximum hops;
-   expansion limits;
-   candidate ordering;
-   family-neighborhood selection;
-   preferred-element filtering;
-   chain completion rules;

can influence which research opportunities are visible and which remain
unseen.

MaterialGraph should make these constraints inspectable and should avoid
presenting a bounded search result as exhaustive discovery.

Production safety and scientific completeness are different concerns.
The system should represent that distinction clearly.

------------------------------------------------------------------------

## 8. Transition Validation Should Be Conservative and Explainable

Current transition validation requires recognized relationships and at
least one strong relationship before accepting a transition.

This conservative direction should be preserved.

MaterialGraph should prefer:

-   explicit accepted relationship classes;
-   deterministic validation rules;
-   inspectable rejection reasons;
-   explicit removed elements;
-   explicit introduced elements;
-   explicit shared elements;
-   traceable transition types.

It should avoid:

-   accepting graph adjacency as sufficient scientific plausibility;
-   inferring strong chemistry from weak similarity alone;
-   hiding why a transition was accepted;
-   silently upgrading an inferred relationship into verified evidence.

A transition should be understood as:

> **an explainable research hypothesis or exploration step supported by
> encoded relationships and available evidence**

---not as proof that the physical transformation is experimentally
feasible.

------------------------------------------------------------------------

## 9. MaterialGraph Should Preserve Layer Ownership

The reviewed architecture currently has a useful separation of concerns:

-   objective service orchestrates objective-constrained chain
    selection;
-   chain service constructs bounded multi-hop opportunities;
-   transition validator owns transition acceptance;
-   path ranking owns scientific usefulness scoring;
-   scientific pathway analysis constructs researcher-facing
    opportunities;
-   evidence intelligence owns evidence summaries and gaps;
-   comparative intelligence owns comparison;
-   endpoint-sensitive ranking examines tied endpoints without replacing
    the original score.

This separation should be protected.

### Ownership rule

New capabilities should reuse existing outputs rather than recreate
them.

Examples:

-   comparison should not become a second ranking engine;
-   endpoint-sensitive analysis should not recreate material quality;
-   evidence intelligence should not invent transition plausibility;
-   graph centrality should not silently become scientific usefulness;
-   confidence should not duplicate the total score under a different
    name;
-   validation planning should not fabricate missing evidence.

------------------------------------------------------------------------

## 10. MaterialGraph Should Treat Researcher-Facing Language as Part of the Model

Explanations are not cosmetic.

Terms such as:

-   `preserved_framework`;
-   `scientific_plausibility`;
-   `confidence`;
-   `evidence_readiness`;
-   `stable`;
-   `strong`;
-   `validated`;

carry scientific meaning.

MaterialGraph should ensure that the strength of its language does not
exceed the strength of the underlying evidence.

Every researcher-facing term should be traceable to:

-   a stored property;
-   a deterministic rule;
-   a graph fact;
-   an attributed external source;
-   or an explicitly labeled inference.

If a term is inferential, the output should make that visible.

------------------------------------------------------------------------

## 11. MaterialGraph Should Separate Internal Support From External Scientific Evidence

MaterialGraph currently derives useful support from its own
deterministic intelligence layers. Examples include:

-   graph relationships;
-   objective alignment;
-   ranking dimensions;
-   material-property heuristics;
-   transition-type rules;
-   graph-derived pathway facts;
-   deterministic comparisons.

These are valuable forms of **internal deterministic support**.

They are not automatically equivalent to **external scientific
evidence**, such as:

-   attributed scientific literature;
-   experimental synthesis reports;
-   independently validated computational results;
-   measured electrochemical data;
-   crystallographic or structural evidence;
-   independently sourced property measurements.

MaterialGraph should keep these categories explicit.

> **A pathway should not receive a researcher-facing interpretation of
> strong scientific evidence solely because several internally derived
> signals agree when literature, experimental, structural, or
> computational validation is absent.**

Evidence readiness should therefore communicate what kind of evidence is
ready, not merely how many internal signals are present.

Where useful, MaterialGraph should distinguish concepts such as:

-   `internal_support_strength`;
-   `external_evidence_readiness`;
-   `evidence_coverage`;
-   `validation_readiness`.

The exact schema should be decided only after reviewing current
consumers and avoiding duplicate concepts. The principle is more
important than any specific field name.

------------------------------------------------------------------------

## 12. Missing Evidence Must Remain Missing

Absence of evidence must not silently become favorable evidence.

> **Unknown risk is not low risk. Partial evidence coverage is not
> equivalent to complete evidence. Missing evidence must never receive a
> favorable score merely because a numeric fallback resembles a
> desirable value.**

This principle applies beyond risk intelligence. It should govern:

-   missing material properties;
-   missing risk profiles;
-   incomplete element coverage;
-   absent literature evidence;
-   unavailable structural evidence;
-   unavailable experimental validation;
-   unavailable computational validation.

Whenever incomplete coverage can materially affect ranking, confidence,
or comparison, MaterialGraph should expose coverage alongside the value.

Useful coverage concepts may include:

-   whether the value is known;
-   fraction of relevant entities covered;
-   known and unknown contributors;
-   whether evidence is complete;
-   provenance of available values.

The risk-intelligence correction made during the v1.9.6 architecture
audit is an example of this principle: unknown risk must remain
distinguishable from known low risk, and downstream quality scoring must
not reward missing risk evidence.

------------------------------------------------------------------------

## 13. MaterialGraph Should Separate Internal Consistency From External Validity

Passing tests proves important things:

-   code behavior is stable;
-   contracts are preserved;
-   deterministic rules execute as expected;
-   regressions can be detected.

But passing tests does not prove:

-   scientific correctness;
-   synthesis feasibility;
-   structural preservation;
-   experimental performance;
-   usefulness to researchers.

MaterialGraph should maintain two distinct validation tracks.

### Engineering validation

-   unit tests;
-   integration tests;
-   API contract tests;
-   performance tests;
-   regression tests;
-   production monitoring.

### Scientific and researcher validation

-   representative case studies;
-   literature cross-checking;
-   domain-expert review;
-   comparison with known materials behavior;
-   DFT or domain-specific computational checks where appropriate;
-   researcher workflow feedback;
-   experimental validation where possible.

Both tracks are necessary.

------------------------------------------------------------------------

## 14. MaterialGraph Should Become Verifiable, Not Merely Explainable

Explainability answers:

> Why did the system produce this result?

Verifiability should also answer:

> What facts support it, where did those facts come from, what is
> inferred, what is missing, and how could a researcher check it?

MaterialGraph should increasingly make visible:

-   source provenance;
-   property provenance;
-   rule provenance;
-   relationship provenance;
-   evidence attribution;
-   missing evidence;
-   assumptions;
-   validation priorities;
-   uncertainty boundaries.

A polished explanation without inspectable support is not enough for a
research system.

------------------------------------------------------------------------

## 15. MaterialGraph Should Be Useful to More Than One Research Persona Without Becoming Vague

Potential users may include:

-   materials researchers;
-   computational materials scientists;
-   battery researchers;
-   R&D teams;
-   critical-material analysts;
-   supply-risk researchers;
-   research program decision-makers.

MaterialGraph should not claim equal readiness for all of these users.

Each use case should be earned through:

-   appropriate data;
-   appropriate objectives;
-   appropriate evidence;
-   representative case studies;
-   user feedback.

The shared platform can remain broad, while validated workflows should
be specific.

------------------------------------------------------------------------

## 16. New Capabilities Should Be Evidence-Driven

Before naming or implementing the next milestone, inspect:

1.  current code;
2.  current service ownership;
3.  a real API response;
4.  the exact limitation;
5.  what evidence is missing;
6.  what a researcher would need next.

Then choose the smallest capability that improves the system.

Potential future directions may include:

-   stronger evidence provenance;
-   validation planning;
-   multi-element objective semantics;
-   structural evidence integration;
-   property-specific endpoint analysis;
-   literature-linked evidence;
-   researcher-facing case-study workflows.

These are possibilities, not automatic roadmap commitments.

The next capability should be selected because the current system
demonstrates a need for it.

------------------------------------------------------------------------

## 17. A Practical Gate for Every Future Feature

Before implementation, answer:

1.  What researcher question does this capability answer?
2.  What current limitation demonstrates the need?
3.  Which layer owns the logic?
4.  What existing services does it reuse?
5.  What new information does it add?
6.  What is the scientific basis?
7.  Can the researcher inspect the basis?
8.  Does it duplicate an existing score or signal?
9.  What happens when data is missing?
10. Can uncertainty remain unresolved?
11. Can a genuine tie remain a tie?
12. What terminology could overstate the evidence?
13. What requires external validation?
14. What real case study will verify usefulness?
15. What production cost or search bias could it introduce?

If these questions cannot be answered clearly, the feature should not be
added yet.

------------------------------------------------------------------------

## 18. MaterialGraph Should Support Open-Ended Material and Element Exploration

The long-term research goal should not be limited to a fixed seed
dataset or a small set of preselected materials.

> **A researcher should eventually be able to begin from any material,
> element, material family, property target, or constrained research
> objective that the system can identify and support with traceable
> data.**

Valid research entry points may include:

-   an element such as `Li`, `Na`, `Fe`, or `Mg`;
-   a known material formula;
-   a material family;
-   a property target;
-   an application context;
-   an avoidance constraint;
-   a preservation constraint;
-   a substitution question;
-   a multi-objective research problem.

The intended direction is:

``` text
Research Question
        │
        ▼
Query / Identity Resolution
        │
        ▼
Known Data and Coverage Check
        │
        ├── sufficient ──► research intelligence pipeline
        │
        └── insufficient
                 │
                 ▼
       controlled data acquisition
                 │
                 ▼
       normalization + provenance
                 │
                 ▼
       graph integration / temporary research context
                 │
                 ▼
       research intelligence pipeline
```

This does not mean MaterialGraph should pretend to know every material.

When a requested material or element is outside current coverage, the
system should explicitly distinguish:

-   known and locally available;
-   externally resolvable;
-   partially characterized;
-   identity-ambiguous;
-   unsupported by current data;
-   unavailable for a requested analysis.

### Universal exploration requires identity discipline

Scaling beyond a curated dataset requires a stronger identity model.

MaterialGraph should distinguish where scientifically necessary among:

-   canonical material identity;
-   composition identity;
-   phase identity;
-   structure identity;
-   polymorph identity;
-   source-specific identity;
-   aliases and naming variants.

A shared formula must not automatically imply identical phase,
structure, properties, or physical behavior.

### Dynamic ingestion must be controlled

Future external data acquisition should preserve:

-   source attribution;
-   source licensing constraints;
-   retrieval time;
-   dataset version;
-   normalization decisions;
-   conflicting values;
-   missing values;
-   uncertainty;
-   whether data is stored, cached, or temporary.

> **Universal exploration should expand the research space without
> weakening provenance, identity precision, or scientific honesty.**

------------------------------------------------------------------------

## 19. MaterialGraph Should Include Physical Modeling Readiness as a First-Class Intelligence Layer

MaterialGraph should eventually help a researcher determine not only
what may be worth investigating, but whether a candidate or research
hypothesis is sufficiently specified to proceed into a particular
physical modeling workflow.

> **Physical Modeling Readiness should assess readiness for modeling. It
> should not claim that a model has been executed, validated, or shown
> to represent reality merely because required inputs appear
> available.**

The intended pipeline is:

``` text
Research Opportunity
        │
        ▼
Evidence and Property Context
        │
        ▼
Physical Modeling Readiness
        │
        ▼
Model-Specific Readiness Profile
        │
        ├── ready
        ├── partially ready
        ├── blocked by missing inputs
        ├── applicability uncertain
        └── unsupported
        │
        ▼
Future Model Routing / External Compute
        │
        ▼
Attributed Simulation Result
        │
        ▼
Evidence and Validation Loop
```

### Readiness must be model-specific

MaterialGraph should avoid a single universal
`physical_modeling_readiness_score` that collapses fundamentally
different requirements.

Potential readiness profiles may include:

-   DFT readiness;
-   molecular dynamics readiness;
-   thermodynamic modeling readiness;
-   phase-field readiness;
-   finite-element readiness;
-   electrochemical modeling readiness;
-   quantum-model readiness.

Each profile should define its own:

-   required inputs;
-   optional inputs;
-   blocking gaps;
-   applicability conditions;
-   assumptions;
-   evidence requirements;
-   uncertainty handling;
-   validation expectations.

For example, DFT readiness may depend on structural and calculation
context, while molecular dynamics readiness may depend on an appropriate
potential or force field, topology, thermodynamic conditions, and
simulation configuration.

### Readiness should expose missing prerequisites

A researcher-facing result should be able to communicate:

``` text
Model route: DFT

Available:
- composition
- atomic species
- crystal structure
- lattice parameters

Unresolved:
- partial occupancy
- magnetic initialization

Missing:
- explicit calculation assumptions

Readiness:
PARTIAL

Blocking gaps:
- unresolved occupancy

Recommended next action:
- resolve structure representation before model execution
```

The exact schema should be implemented only after reviewing actual
modeling workflows and domain requirements.

### Hamiltonian and model-family reasoning must remain conservative

For future quantum or statistical physical modeling, MaterialGraph may
help represent relationships such as:

``` text
Research Target
      │
      ▼
Degrees of Freedom
      │
      ▼
Relevant Interactions
      │
      ▼
Candidate Model Family
      │
      ▼
Required Parameters
      │
      ├── available
      ├── uncertain
      └── missing
```

For example, the system may identify that a magnetic research context
appears compatible with investigation through a Heisenberg-type model
while still reporting missing exchange parameters.

It must not infer:

-   that the selected Hamiltonian is uniquely correct;
-   that parameters are known when they are not;
-   that solving a mathematical model validates the physical system;
-   that model applicability is established without evidence.

### Physical Modeling Readiness should reuse existing intelligence

It should consume, where appropriate:

-   material identity;
-   property observations;
-   structural evidence;
-   evidence attribution;
-   uncertainty;
-   contradiction intelligence;
-   research objectives;
-   validation priorities.

It should not create a parallel evidence system or silently reinterpret
missing data as readiness.

------------------------------------------------------------------------

## 20. MaterialGraph Should Treat Physical Compute as a Future Integration Boundary

MaterialGraph should not attempt to become every scientific simulator.

Its stronger long-term role is to connect research intelligence with
appropriate modeling workflows while preserving clear boundaries.

``` text
MaterialGraph Research Intelligence
        │
        ▼
Physical Modeling Readiness
        │
        ▼
Model / Workflow Selection
        │
        ▼
External or Dedicated Compute
        │
        ├── electronic-structure workflow
        ├── molecular simulation workflow
        ├── thermodynamic workflow
        ├── continuum workflow
        └── other validated domain workflow
        │
        ▼
Versioned Result + Provenance
        │
        ▼
MaterialGraph Evidence Context
```

Every imported simulation result should preserve, where available:

-   engine and version;
-   method family and calculation mode;
-   model, potential, functional, or equivalent scientific-method
    identity;
-   model/version identity where distinct from the execution engine;
-   input configuration;
-   material identity;
-   structure version;
-   property definition and units;
-   parameter set;
-   relevant calculation conditions;
-   assumptions;
-   convergence state;
-   execution time;
-   output artifact references;
-   uncertainty or applicability information where available;
-   validation status.

> **A computed result should become attributed evidence context, not
> automatic scientific truth.**

### Computational evidence comparability must be explicit

Method and version metadata are scientific provenance, not merely
software metadata. Results referring to the same nominal property should
not automatically be treated as equivalent or directly comparable when
method, model/version, structure representation, property definition,
conditions, parameterization, convergence, uncertainty, or applicability
differ.

Where sufficient metadata exists, MaterialGraph may eventually classify
comparability conservatively:

``` text
DIRECTLY_COMPARABLE
COMPARABLE_WITH_QUALIFICATIONS
NOT_DIRECTLY_COMPARABLE
COMPARABILITY_UNKNOWN
```

The exact vocabulary should be designed only after representative
scientific workflows are studied. Missing scientific metadata must not
be silently interpreted as compatibility.

> **Computational evidence should be compared or combined only when the
> scientific basis for that comparison is itself inspectable.**

MaterialGraph should also distinguish:

-   readiness to run;
-   successful execution;
-   numerical convergence;
-   model validity;
-   agreement with experiment.

These are separate states.

### External scientific tools should extend MaterialGraph rather than be duplicated

MaterialGraph should treat mature scientific software, specialist
open-source projects, institutional workflows, and domain-specific
computation systems as potential integration boundaries rather than
capabilities that must be reimplemented internally.

Relevant external capabilities may include:

-   electronic-structure and DFT workflows;
-   molecular-dynamics engines and preparation tools;
-   thermodynamic and phase-equilibrium workflows;
-   structure-analysis and crystallographic tools;
-   electrochemical modeling;
-   continuum or finite-element workflows;
-   domain-specific scientific post-processing and validation tools.

The existence of a useful external scientific project should not
automatically create a MaterialGraph feature requirement. Instead,
MaterialGraph should ask:

1.  Does the tool address a validation or modeling need produced by the
    MaterialGraph Research Cycle?
2.  Is the capability outside the appropriate ownership boundary of
    MaterialGraph's deterministic research-intelligence core?
3.  Can MaterialGraph determine whether the research opportunity is
    sufficiently specified for the external workflow?
4.  Can inputs, outputs, assumptions, versions, and provenance be
    represented explicitly?
5.  Can results return to MaterialGraph as attributed evidence without
    being treated as automatic scientific truth?
6.  Does integration provide greater researcher value than
    reimplementing or loosely duplicating the external capability?

The preferred long-term relationship is:

``` text
MaterialGraph Discovery / Research Intelligence
        │
        ▼
Model-Specific Readiness Assessment
        │
        ▼
External Scientific Tool / Workflow
        │
        ▼
Versioned Computational Result
        │
        ▼
Attributed Evidence and Validation Context
        │
        ▼
Continued MaterialGraph Investigation
```

For example, MaterialGraph may identify and explain a material
opportunity and determine that it is potentially ready for a
molecular-dynamics workflow. A specialized molecular-simulation tool may
then prepare, execute, or analyze the simulation. MaterialGraph's
responsibility is not to reproduce that simulator, but to preserve the
relationship between the original research objective, the selected
material and structure, modeling prerequisites, computational inputs,
assumptions, execution metadata, outputs, and resulting validation
evidence.

This creates an important architectural principle:

> **MaterialGraph should own research intelligence, orchestration
> context, provenance, and validation integration where appropriate;
> specialized scientific engines should continue to own the domain
> computation they are designed to perform.**

External integrations should therefore be adapter-oriented and
replaceable where practical. MaterialGraph should avoid coupling
scientific meaning to one specific simulation engine, library, or
external project unless the scientific workflow itself requires that
dependency.

Before adopting an external scientific tool or project, MaterialGraph
should evaluate at least:

-   scientific applicability;
-   maturity and maintenance status;
-   reproducibility;
-   input and output contracts;
-   provenance capabilities;
-   licensing and redistribution constraints;
-   computational and infrastructure requirements;
-   failure and convergence semantics;
-   security implications of external execution;
-   whether equivalent functionality already exists within an
    established MaterialGraph boundary.

This principle allows MaterialGraph to benefit from advances across the
computational-materials ecosystem without becoming a collection of
embedded simulators or weakening the deterministic research-intelligence
core.

------------------------------------------------------------------------

## 21. MaterialGraph Should Separate Canonical Knowledge From Private Research Context

MaterialGraph should eventually allow organizations, research groups,
projects, and individual researchers to use private scientific knowledge
alongside shared or canonical MaterialGraph knowledge without silently
converting private evidence into global scientific truth.

Private research context may include:

-   unpublished experimental measurements;
-   proprietary simulation or computational results;
-   failed, negative, or inconclusive experiments;
-   organization-specific material formulations or process conditions;
-   internal observations, annotations, and expert assessments;
-   project-specific structures, properties, relationships, or
    constraints.

The intended separation is:

``` text
Canonical / Shared Knowledge
        │
        ├──────────────┐
        │              │
        ▼              ▼
Public Evidence   Private Research Context
                       │
                       ├── organization evidence
                       ├── project evidence
                       ├── researcher observations
                       ├── proprietary computation
                       └── unpublished experiments
        │              │
        └───────┬──────┘
                ▼
       Contextual Research Intelligence
```

Every private contribution should preserve, where applicable, its
provenance, ownership or access scope, research context, version,
validation status, and relationship to canonical material identities.
Conflicts between private and shared evidence should remain visible
rather than being resolved by silent overwrite or precedence rules.

> **Private evidence should be usable within the research context that
> owns or is authorized to access it, but it should not become canonical
> MaterialGraph knowledge merely because it influenced a result.**

Promotion of private evidence into shared or canonical knowledge should
require an explicit, governed process with appropriate attribution,
review, validation, licensing, and permission checks.

This boundary allows MaterialGraph to support industrial and
institutional research while preserving scientific provenance,
confidentiality, and the distinction between shared knowledge and
organization-specific experience.

### MaterialGraph Should Distinguish Global Material Signals From Local Scientific Environment

MaterialGraph should avoid assuming that strong composition-level, bulk,
or global structural similarity implies similarity at the scientifically
decisive local environment.

Where relevant to a validated research question, future evidence and
reasoning should be capable of distinguishing among:

-   composition and bulk material properties;
-   phase and global crystal structure;
-   local coordination environments;
-   substitution or dopant sites;
-   defects and vacancies;
-   interfaces and grain boundaries;
-   surfaces and active sites;
-   local bonding or neighborhood geometry.

A candidate may appear strongly aligned under global signals while
differing at a local site that controls stability, transport, catalytic
behavior, defect chemistry, or another target property. MaterialGraph
should therefore avoid allowing a strong global score or similarity
signal to conceal missing or contradictory local evidence.

The intended direction is:

``` text
Material / Candidate
        │
        ├── Composition Context
        ├── Phase / Structure Context
        └── Local Scientific Environment
                ├── coordination
                ├── substitution site
                ├── defect
                ├── interface
                ├── surface
                └── local bonding
```

This is a scientific representation principle, not a commitment to a
specific GNN, descriptor, loss function, or machine-learning
architecture. Appropriate implementation may later use structural
databases, deterministic descriptors, graph representations, external
computation, learned models, or combinations of these approaches where
validated use cases justify them.

------------------------------------------------------------------------

## 22. MaterialGraph Should Be Architected for Polyglot Compute Without Premature Distribution

The current Python, FastAPI, and PostgreSQL foundation should remain the
primary development environment while scientific semantics and
researcher workflows are still evolving.

However, the architecture should prepare for future compute
specialization.

A possible long-term ownership model is:

``` text
FastAPI / Python
├── API contracts
├── research orchestration
├── objective handling
├── evidence and provenance
├── explanation assembly
├── experiment management
└── rapidly evolving scientific intelligence

Future Go Compute Services
├── concurrent graph exploration
├── high-throughput background jobs
├── large traversal workloads
├── batch path computation
└── worker coordination where justified

Future Rust Compute Core
├── performance-critical kernels
├── memory-sensitive graph operations
├── numerical routines
├── compact scientific computation
└── validated reusable compute modules
```

This is a direction, not a commitment to immediate decomposition.

### Introduce another runtime only when there is evidence

A Go service should be considered when measurements show needs such as:

-   sustained concurrent experiment workloads;
-   graph traversal dominating request or worker time;
-   large batch exploration;
-   Python worker throughput becoming a demonstrated constraint.

A Rust component should be considered when measurements show needs such
as:

-   performance-critical numerical kernels;
-   memory-sensitive graph operations;
-   repeated hot loops that remain bottlenecks after algorithmic
    optimization;
-   a stable compute contract suitable for a lower-level implementation.

Other technologies should be evaluated by the same rule.

> **MaterialGraph should adopt a technology because a measured workload
> and stable ownership boundary justify it, not because the technology
> appears impressive.**

### Prepare boundaries early

Even before introducing Go, Rust, or another runtime, MaterialGraph
should strengthen:

-   typed request and result schemas;
-   explicit service ownership;
-   experiment identifiers;
-   versioned compute contracts;
-   deterministic test fixtures;
-   benchmark cases;
-   timing instrumentation;
-   job-state semantics;
-   reproducibility metadata.

This allows later extraction without forcing premature microservices.

------------------------------------------------------------------------

## 23. MaterialGraph Should Be Deployed and Validated in Controlled Stages

Professional deployment should be treated as part of research
validation, not merely infrastructure hosting.

The project should avoid two extremes:

-   remaining indefinitely private while claiming researcher usefulness;
-   opening unrestricted expensive research computation before
    scientific and operational boundaries are understood.

A staged direction is preferable.

### Stage 1 --- Controlled Research Preview

Purpose:

-   verify deployment behavior;
-   expose bounded workflows;
-   collect early scientific criticism;
-   measure real endpoint cost;
-   validate reproducibility and provenance.

Characteristics may include:

-   static React research interface;
-   FastAPI API;
-   PostgreSQL;
-   bounded synchronous computation;
-   strict graph-depth and result limits;
-   local or simple background jobs;
-   experiment identifiers;
-   timing and error observability;
-   invited users.

The goal is not scale.

> **The goal is to discover where MaterialGraph is scientifically
> misleading, operationally fragile, or genuinely useful.**

### Stage 2 --- Research Validation Beta

Introduce only when repeated external use demonstrates the need.

Possible additions:

-   persistent research accounts;
-   private experiments;
-   background job queue;
-   shared cache;
-   API keys;
-   quotas;
-   rate limiting;
-   saved workspaces;
-   researcher feedback;
-   result versioning;
-   stronger monitoring and backups.

### Stage 3 --- Professional Research Platform

Introduce when usage proves a need for compute separation, stronger
service levels, institutional workflows, or private data.

Possible additions:

-   separate API and compute workers;
-   managed cache;
-   stronger database operations;
-   dedicated graph compute;
-   specialized Go or Rust components where profiling justifies them;
-   institutional access controls;
-   private deployments;
-   auditable integrations.

### Endpoint cost should influence execution mode

A useful classification is:

``` text
Class A — cheap
lookup, metadata, saved result retrieval

Class B — moderate
bounded candidate generation, small path search, cached comparison

Class C — expensive
community detection, large graph expansion, k-best path exploration,
comparative research workloads

Class D — research compute
large objective exploration, batch studies, future modeling or ML workloads
```

A likely execution direction is:

``` text
A → synchronous

B → synchronous when bounded, otherwise cached or queued

C → asynchronous background jobs

D → dedicated compute infrastructure
```

The classification should be based on measurement, not labels alone.

### External validation should be systematic

Researcher feedback should be structured into failure and usefulness
categories such as:

-   incorrect identity;
-   invalid edge;
-   weak substitution;
-   missing property;
-   misleading terminology;
-   poor ranking;
-   insufficient evidence;
-   misleading confidence;
-   invalid pathway;
-   search-space omission;
-   useful opportunity;
-   known result rediscovered;
-   novel result worth investigation.

Feedback must not automatically become truth. It should remain
attributed, reviewable input.

### Commercialization should follow demonstrated value

Researcher use does not automatically imply payment.

MaterialGraph should first learn:

-   which workflows researchers repeat;
-   which capabilities save meaningful time;
-   which outputs influence decisions;
-   whether labs need collaboration;
-   whether institutions need private workspaces;
-   whether industrial teams need proprietary data integration;
-   whether users need API access or private deployment.

Potential future paid capabilities may include:

-   private research workspaces;
-   larger compute quotas;
-   institutional collaboration;
-   proprietary dataset integration;
-   API access;
-   private deployment;
-   industrial pilots;
-   support and audit requirements.

> **The business model should emerge from validated research value
> rather than forcing early payment around an unvalidated system.**

------------------------------------------------------------------------

## 24. MaterialGraph Should Develop Validation Priority Intelligence

MaterialGraph should eventually help researchers move beyond merely
seeing that evidence is missing toward understanding **which unresolved
question is most important to address next for the current research
objective**.

> **Validation Priority Intelligence (VPI) should prioritize
> decision-relevant validation needs without pretending that
> MaterialGraph can establish scientific validity by itself.**

The intended progression is:

``` text
Research Objective
        │
        ▼
Candidate / Pathway / Comparison
        │
        ▼
Evidence and Uncertainty Assessment
        │
        ▼
Validation Priority Intelligence
        │
        ▼
Which unresolved question matters most next?
        │
        ├── literature / attributed evidence
        ├── structural or local-environment evidence
        ├── external computation
        ├── experiment
        └── researcher review
        │
        ▼
Attributed New Evidence
        │
        ▼
Re-evaluate the Investigation
        └──────────────────────────────↺
```

### VPI should prioritize gaps, not fabricate answers

Validation Priority Intelligence should consume existing research
context rather than create a parallel scientific truth system.

Where appropriate, it may use:

-   the research objective and explicit constraints;
-   candidate and pathway claims;
-   evidence coverage and provenance;
-   known versus unknown states;
-   contradictory or incomplete evidence;
-   structural and local-environment gaps;
-   criticality or application-specific context;
-   scenario and sensitivity results;
-   Physical Modeling Readiness;
-   validation history.

Its responsibility is to answer:

1.  What claim or assumption is currently unresolved?
2.  How important is that claim to the research objective?
3.  Could resolving it materially change ranking, comparison, pathway
    interpretation, or a go/no-go research decision?
4.  What class of validation could address the gap?
5.  Why should this validation need be considered before another one?

MaterialGraph must not convert absence of evidence into a recommendation
that the underlying scientific claim is probably true.

### Priority should remain inspectable

VPI should avoid presenting a single opaque score as though validation
priority were an intrinsic physical property.

A researcher-facing result may instead expose dimensions such as:

``` text
Validation need: structural preservation

Objective relevance:        HIGH
Evidence-gap severity:      HIGH
Decision sensitivity:       HIGH
Existing evidence coverage: LOW
Validation readiness:       MEDIUM

Priority: HIGH

Reason:
The research objective depends on structural continuity, but the current
opportunity is supported primarily by composition/family relationships.
Resolving this gap could materially change the candidate interpretation.
```

If numeric components are used internally, their rules, inputs,
provenance, and uncertainty should remain inspectable.

### Decision sensitivity can make validation more useful

A particularly valuable future direction is to ask whether an unresolved
assumption is capable of changing the research decision.

``` text
Assumption supported              Assumption contradicted
        │                                  │
        ▼                                  ▼
Candidate order: A > B > C        Candidate order: C > B > A
```

An unresolved assumption that can reverse or materially alter the
decision may deserve higher validation priority than one whose
resolution leaves the decision unchanged.

This should build on explicit scenario and sensitivity semantics rather
than introduce an independent ranking engine.

### VPI should recommend validation classes conservatively

A validation priority may point toward a class of next action, for
example:

-   inspect attributed literature;
-   resolve material or structure identity;
-   obtain structural evidence;
-   inspect a local coordination environment;
-   run an appropriate external computational workflow;
-   obtain an experimental measurement;
-   request domain-expert review.

MaterialGraph should not recommend a specific scientific method unless
the method's applicability and prerequisites are sufficiently
represented.

MaterialGraph should distinguish the responsibilities involved in moving
from a validation need to computational evidence:

``` text
Validation Priority Intelligence
        │
        ▼
Validation Route Selection
        │
        ▼
Model-Specific Physical Modeling Readiness
        │
        ▼
External Scientific Compute
        │
        ▼
Computational Evidence Comparability
        │
        ▼
MaterialGraph Evidence Context
```

VPI asks **what unresolved question matters most**. Validation Route
Selection asks **what class of evidence could address it**. Physical
Modeling Readiness asks **whether the prerequisites for that route are
sufficiently represented**. External engines remain responsible for
domain computation. Evidence comparability asks whether returned results
can legitimately be compared or combined.

MaterialGraph should not recommend a specific method merely because an
engine supports it. Method selection must remain constrained by the
scientific question, applicability, prerequisites, and available
evidence.

### Researcher authority remains central

VPI is decision support, not autonomous scientific authority.

The researcher should be able to inspect why a validation need was
prioritized, disagree with or override the priority, choose another
validation route, record why a different action was taken, and preserve
the resulting evidence and decision history.

> **The purpose of VPI is not to tell researchers what is scientifically
> true. It is to help them decide what is most valuable to establish
> next.**

### Implementation gate

Validation Priority Intelligence should be designed before it is
scheduled for implementation.

Before roadmap promotion, MaterialGraph should establish:

-   representative researcher use cases;
-   explicit ownership boundaries;
-   deterministic and inspectable priority semantics;
-   interaction with evidence intelligence and scenario/sensitivity
    analysis;
-   treatment of unknown, contradictory, and private evidence;
-   validation-route semantics;
-   representative cases where priority can be checked by domain
    experts;
-   safeguards against implying scientific validity from workflow
    completion.

The first useful version should remain narrow. It may prioritize known
evidence gaps using existing MaterialGraph intelligence before any
autonomous data acquisition, active learning, experiment control, or
agentic orchestration is considered.

------------------------------------------------------------------------

## 25. Current Direction After v1.9.6

The immediate priority should not be feature accumulation.

The priority should be:

1.  understand the current code path end to end;
2.  trace one representative real response through the full intelligence
    stack;
3.  document strategically important findings before remediation changes
    the observed baseline;
4.  identify semantic mismatches;
5.  identify where terminology overstates evidence;
6.  identify where one upstream inference propagates through multiple
    downstream layers;
7.  identify where search constraints shape scientific outputs;
8.  fix critical correctness issues discovered during inspection;
9.  verify fixes with focused tests, the full suite, and representative
    real responses where possible;
10. build reference case studies;
11. seek researcher feedback;
12. add capabilities only where demonstrated gaps exist.

The current LiFePO4 → Na/phosphate objective should continue to serve as
a reference trace while the architecture audit proceeds. Its five-way
`94.95` tie is especially useful for checking whether downstream
services preserve uncertainty rather than manufacturing differentiation.

The project is now mature enough that restraint, auditability, and
remediation are part of good engineering.

------------------------------------------------------------------------

## 26. North Star

MaterialGraph's mission-level objective remains:

> **Build an exceptional scientific software system and create the
> infrastructure through which domain experts can encode, inspect, and
> use their knowledge.**

The North Star should therefore be judged not by the number of features,
algorithms, or generated recommendations, but by whether researchers can
use MaterialGraph to make scientific knowledge and decision context more
structured, inspectable, verifiable, reproducible, and reusable.

MaterialGraph should help researchers answer:

-   What opportunities exist?
-   Why were they generated?
-   What relationships support them?
-   What trade-offs distinguish them?
-   What evidence is available?
-   What evidence is missing?
-   Which assumptions are weak?
-   What cannot currently be differentiated?
-   What should be validated next?
-   Is this opportunity ready for a specific physical modeling workflow?
-   Which modeling prerequisites are missing or uncertain?
-   What is known locally, what requires external resolution, and what
    is outside current coverage?
-   How can the reasoning be independently checked?

MaterialGraph should not hide uncertainty behind ranking precision.

It should make the boundary between:

-   known;
-   derived;
-   inferred;
-   missing;
-   uncertain;
-   and experimentally unvalidated

as clear as possible.

> **The goal is not to make MaterialGraph appear certain. The goal is to
> make materials research exploration more structured, inspectable,
> verifiable, and useful while preserving scientific judgement with the
> researcher.**
>
> **Long term, MaterialGraph should help researchers move coherently
> from open-ended material or element exploration, through explainable
> opportunity and evidence analysis, toward model-specific physical
> readiness and externally validated computation---without confusing
> inference, readiness, simulation, or validation with scientific
> proof.**