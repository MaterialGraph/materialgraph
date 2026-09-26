# MaterialGraph External Scientific Validation Plan

**Status:** Deferred — planning artifact only  
**Execution trigger:** Completion of the current MaterialGraph Release 1 implementation, real-response investigation walkthrough, and establishment of a stable external-testing baseline  
**Scope:** External scientific evaluation, researcher outreach, pilot qualification, and early commercial-signal collection

---

## 1. Purpose

MaterialGraph has accumulated substantial internal technical evidence through implementation, testing, dataset qualification, provenance controls, uncertainty handling, performance work, security assurance, and production-oriented engineering.

Internal technical evidence, however, does not establish that MaterialGraph solves a sufficiently important problem for materials researchers or industrial R&D teams.

The next major validation step is therefore external.

The purpose of this phase is to determine whether relevant domain experts find MaterialGraph:

- scientifically understandable;
- sufficiently transparent to critique;
- useful for narrowing candidate spaces;
- capable of reducing research-screening effort;
- appropriately explicit about uncertainty and limitations;
- applicable to real research questions beyond the demonstration case; and
- potentially valuable enough to justify continued use, an institutional pilot, or eventually a commercial relationship.

This phase is **not intended to obtain endorsements**.

Critical, negative, and contradictory feedback must be preserved alongside positive feedback. The objective is to learn where MaterialGraph provides genuine research value and where its assumptions, evidence, data, interfaces, or scientific boundaries are insufficient.

---

## 2. Execution Boundary

This plan should not be executed during the current Release 1 implementation work.

External outreach should begin only after:

1. Release 1 implementation is complete.
2. The real-response investigation walkthrough has been completed successfully.
3. Major known presentation or scientific-interpretation problems have been resolved.
4. A stable pilot baseline can be identified and recorded.
5. The system can be demonstrated without requiring significant intervention from the developer.
6. Known scientific limitations can be communicated clearly.
7. The external evaluation package described in this document is ready.

Once the pilot baseline is frozen, discretionary feature development should be limited while initial external validation is underway unless a serious correctness, security, reliability, or scientific-communication issue requires intervention.

The purpose is to evaluate a reasonably stable system rather than continuously changing the subject of the evaluation.

---

## 3. Validation Principle

MaterialGraph should not attempt to prove its value by accumulating large numbers of superficial users.

The initial objective is a small number of high-quality evaluations from people whose work overlaps directly with MaterialGraph's capabilities.

An initial outreach cohort of approximately **30 highly relevant contacts** will be assembled.

The desired outcome is approximately **10–20 meaningful expert evaluations over the broader validation phase**, recognizing that additional outreach may be required to reach that number.

Quality and relevance take priority over maintaining an exact numerical distribution between researcher categories.

---

## 4. MaterialGraph Positioning for Evaluation

MaterialGraph should be presented conservatively and precisely.

### 4.1 What MaterialGraph Is

MaterialGraph is an explainable materials-discovery system that applies explicit constraints, deterministic graph operations, structured evidence, and inspectable scoring logic to materials research questions.

The system is intended to help researchers explore and prioritize candidate spaces while retaining visibility into:

- source data;
- provenance;
- constraints;
- scoring contributions;
- composition relationships;
- uncertainty;
- unavailable evidence; and
- scientific limitations.

MaterialGraph should initially be evaluated primarily as a **research prioritization and search-space reduction tool**, not as an autonomous scientific decision-maker.

### 4.2 What MaterialGraph Is Not

MaterialGraph is not an unconstrained generative system producing candidate materials from model output.

It does not claim that a ranked candidate is experimentally viable merely because it appears in a result set.

It does not convert missing evidence into negative evidence.

It does not treat computational evidence, experimental evidence, unknown information, and unvalidated relationships as interchangeable.

Composition-level relationships or chains must not be represented as demonstrated reaction mechanisms or synthesis pathways unless appropriate evidence exists.

MaterialGraph's purpose is to expose enough reasoning and evidence for researchers to inspect, challenge, verify, or reject its results.

---

## 5. Researcher Evaluation Package

No outreach campaign should begin until a compact evaluation package is available.

The package should minimize the time required for a researcher to understand what MaterialGraph does while providing sufficient technical detail for serious scrutiny.

### 5.1 Two-to-Three-Minute Walkthrough

Prepare a short narrated or silent demonstration based on one concrete research question.

The initial candidate scenario is the existing LiFePO₄ investigation involving lithium avoidance, sodium preference, preservation constraints, criticality considerations, and composition-level candidate relationships.

The walkthrough should show:

- source material;
- research objective;
- Avoid / Prefer / Preserve constraints;
- relevant discovery configuration;
- returned candidates;
- ranking explanation;
- evidence/provenance;
- uncertainty states;
- relationship information;
- scientific limitations; and
- the distinction between composition relationships and experimentally established synthesis/reaction pathways.

The demonstration should not attempt to showcase every MaterialGraph feature.

Its purpose is to let a researcher understand one complete investigation quickly.

### 5.2 “What MaterialGraph Is / Is Not” Boundary Sheet

Prepare a short boundary document explaining:

- intended use;
- inappropriate interpretations;
- deterministic versus generative behavior;
- treatment of uncertainty;
- provenance expectations;
- evidence limitations;
- interpretation of rankings;
- interpretation of composition relationships; and
- areas that remain unvalidated.

This document should make it easier for researchers to critique the system without first reverse-engineering its claims.

### 5.3 One-Page Methodology Abstract

Prepare a concise methodology document describing, at minimum:

- principal data sources;
- ingestion and normalization approach;
- relevant graph model;
- candidate-generation process;
- constraint handling;
- scoring methodology;
- provenance handling;
- uncertainty semantics;
- important scientific assumptions; and
- known limitations.

The methodology should be sufficiently specific that a technically experienced researcher can understand why a result was generated.

### 5.4 Frictionless Feedback

The primary evaluation should avoid a long generic satisfaction survey.

Initial structured questions should include:

1. **Where did the ranking, candidate-selection, or relationship logic conflict with your scientific/domain intuition?**
2. **What important constraint, property, or evidence was missing from this investigation?**
3. **Was the provenance and reasoning trace sufficient for you to understand and independently verify why the result was returned?**
4. **Could this workflow save meaningful time during initial candidate screening or research prioritization?**
5. **Would you use MaterialGraph on one of your own research questions? If not, what would need to change before you would?**

Open-ended observations should be preserved rather than forcing all responses into predefined categories.

---

## 6. Initial Outreach Cohorts

The first outreach set should contain approximately 30 highly relevant contacts.

The 30 contacts may initially be distributed roughly across three cohorts, but relevance takes priority over achieving an exact 10/10/10 allocation.

### 6.1 Academic Researchers

Potential participants include:

- principal investigators;
- postdoctoral researchers;
- senior PhD researchers; and
- computational materials researchers.

Priority research areas include:

- battery cathode discovery;
- material substitution;
- critical-mineral replacement;
- computational materials discovery;
- materials informatics;
- composition/property relationships; and
- related screening problems that overlap with current MaterialGraph capabilities.

Postdoctoral and senior PhD researchers should receive significant attention because they may interact directly with the computational workflows being evaluated.

**Primary evaluation angle:**

> Help us determine where the candidate-selection and ranking logic withstands scientific scrutiny and where it fails.

### 6.2 Industrial R&D

Potential participants include:

- materials scientists;
- computational materials scientists;
- battery researchers;
- formulation scientists;
- R&D engineers; and
- technical research leaders.

Relevant organizations may operate in:

- batteries and energy storage;
- advanced materials;
- chemicals;
- ceramics;
- metals;
- critical materials; and
- other domains where material substitution or candidate screening is consequential.

**Primary evaluation angle:**

> Can this approach expose useful candidate trade-offs or narrow an initial search space faster than existing screening workflows?

Initial outreach is for technical evaluation, not an immediate enterprise sales pitch.

### 6.3 Materials Informatics, Databases, and Scientific Software

Potential participants include:

- materials database contributors or maintainers;
- scientific-software researchers;
- knowledge-graph practitioners;
- materials-informatics researchers; and
- developers of related computational research tools.

**Primary evaluation angle:**

> Critique MaterialGraph's representation of provenance, uncertainty, relationships, normalization, reproducibility, and evidence dependencies.

---

## 7. Contact Selection

Contacts should not be selected merely because they are prominent materials scientists.

Each contact should have an identifiable connection to a problem MaterialGraph can currently demonstrate.

Where possible, record:

- researcher name;
- organization;
- role;
- research area;
- relevant recent publication/project;
- why MaterialGraph may be relevant;
- cohort;
- preferred contact channel; and
- proposed personalized outreach angle.

Recent publications should be reviewed before outreach so messages can reference genuine overlap rather than generic materials-science interests.

---

## 8. Outreach Principles

Outreach should be personal, short, technically honest, and respectful of researchers' time.

MaterialGraph should not be presented as a scientifically proven platform before external validation has occurred.

The request should emphasize **criticism rather than endorsement**.

A typical framing may be:

> I am developing MaterialGraph, an early-stage research tool for explainable materials discovery. It explores candidate substitutions and composition relationships using explicit constraints, evidence provenance, uncertainty states, and inspectable ranking logic.
>
> I am looking for researchers willing to spend approximately 20–30 minutes evaluating a real research workflow and identifying where the system is scientifically useful, misleading, incomplete, or incorrect.
>
> I am not looking for an endorsement. Critical scientific feedback is the purpose of the evaluation.

Personalized outreach should then explain why that particular researcher's work makes their perspective relevant.

Bulk generic outreach should be avoided during the initial phase.

---

## 9. Evaluation Method

Where practical, evaluation should measure behavior and task performance rather than relying solely on stated opinions.

For a relevant research task, record:

- research question;
- how the researcher would normally investigate it;
- tools normally used;
- approximate normal effort/time;
- MaterialGraph workflow used;
- time required with MaterialGraph;
- candidates considered useful or irrelevant;
- missing constraints or evidence;
- independent verification required;
- scientific objections;
- trust/provenance concerns;
- usability problems;
- whether the researcher continued exploring voluntarily; and
- whether the researcher wanted to apply MaterialGraph to another problem.

Time savings should not be reported without preserving enough context to understand what tasks were compared.

A faster answer that a researcher does not trust is not equivalent to a useful productivity improvement.

---

## 10. External Validation Register

All outreach and feedback should be maintained in a structured **External Validation Register**.

Suggested fields include:

- contact ID;
- researcher/organization;
- cohort;
- research relevance;
- relevant publication/project;
- outreach date;
- response;
- evaluation date;
- research task;
- observations;
- scientific criticism;
- missing data/property/constraint;
- provenance/trust assessment;
- usability issue;
- requested capability;
- time-saving observation;
- willingness to reuse;
- own-problem/data request;
- institutional interest;
- commercial/pilot signal;
- follow-up action; and
- status.

Negative and neutral feedback must be retained.

The register should distinguish observations from interpretations.

---

## 11. Interpreting Feedback

A single researcher's preference should not automatically become a product requirement.

Feedback should be classified according to strength and repetition.

### 11.1 Individual Signal

Example:

> “The ionic-radius constraint appears too restrictive for this chemistry.”

Action:

Record the observation and investigate the scientific basis.

Do not automatically modify the heuristic.

### 11.2 Repeated Independent Signal

If several independent researchers encounter the same limitation, it becomes stronger evidence of a systematic problem or missing requirement.

Action:

Prioritize scientific investigation and, where supported, remediation or product development.

### 11.3 Evidence-Supported Scientific Criticism

If a researcher supplies literature, data, counterexamples, or another reproducible basis demonstrating a weakness, treat the issue as high-value scientific evidence regardless of whether it has yet been repeated.

### 11.4 Own-Problem Signal

Examples:

> “Can I try this with another cathode chemistry?”

> “Can I test this using our dopant candidates?”

This indicates movement from evaluating MaterialGraph's demonstration toward applying MaterialGraph to a real research problem.

It should trigger a follow-up conversation and potential invite-only evaluation.

### 11.5 Continued-Use Signal

Examples:

> “Can our lab continue using this?”

> “Can I share this with another researcher in our group?”

This represents stronger evidence of practical usefulness and should be tracked separately from positive feedback.

### 11.6 Institutional Pilot Signal

Examples include questions about:

- private datasets;
- deployment;
- confidentiality;
- integration;
- security;
- multiple researchers;
- organizational access;
- continued availability; or
- formal evaluation.

These may justify discussion of a bounded institutional pilot.

### 11.7 Commercial Signal

Questions concerning pricing, licensing, procurement, enterprise deployment, paid continued access, or contractual evaluation should be recorded separately as early commercial evidence.

They should not be interpreted as revenue until an actual commercial commitment exists.

---

## 12. Avoiding Confirmation Bias

The external validation phase must not become an exercise in proving that MaterialGraph is successful.

The process should actively seek evidence capable of disproving current assumptions.

Particular attention should be paid to:

- scientifically implausible candidates;
- missing constraints;
- misleading ranking explanations;
- unsupported relationships;
- insufficient provenance;
- uncertainty presented too confidently;
- important workflows MaterialGraph cannot represent;
- results that require excessive manual verification;
- tasks for which existing tools are already substantially better; and
- cases where MaterialGraph does not save meaningful research effort.

Repeated negative evidence may require changing the product direction rather than merely adding features.

---

## 13. Initial Success Indicators

Early validation should not be judged primarily by account registrations, page views, or generic positive comments.

More meaningful signals include:

- researchers completing a full investigation;
- researchers challenging specific scientific assumptions;
- repeated identification of the same useful capability;
- repeated identification of the same missing requirement;
- measurable reduction in screening effort;
- researchers voluntarily exploring beyond the demonstration;
- requests to investigate another material;
- requests to use researchers' own problems or datasets;
- requests for continued access;
- introductions to colleagues;
- requests from a research group to evaluate the system; and
- interest in an institutional pilot.

The strongest early signal is not:

> “This looks interesting.”

It is movement toward:

> “Can I use this for my problem?”

and eventually:

> “Can we continue using this?”

---

## 14. Progression After Initial Validation

The intended progression is:

**Release 1 implementation**

→ **Real-response investigation walkthrough**

→ **Stable pilot baseline**

→ **Researcher evaluation package**

→ **Initial targeted outreach**

→ **Expert evaluations**

→ **Repeated-signal analysis**

→ **Evidence-driven product changes**

→ **Own-problem evaluations**

→ **Invite-only research pilots**

→ **Institutional/R&D pilots**

→ **Commercial validation**

This progression is not automatic.

Each stage should be justified by evidence collected during the preceding stage.

---

## 15. Commercial Optionality

External scientific validation is not solely a sales exercise.

If MaterialGraph demonstrates valuable capabilities, several future commercial structures may eventually be considered, including:

- hosted software access;
- private workspaces;
- enterprise deployment;
- API access;
- technology licensing;
- domain-specific licensing;
- strategic partnerships;
- data/integration arrangements; or
- licensing or transfer of particular technology assets.

No decision regarding sale or licensing of core MaterialGraph intellectual property should be made solely from early validation interest.

The immediate objective is to establish credible evidence that particular MaterialGraph capabilities solve real research problems.

---

## 16. Revisit Trigger

This document should be revisited when:

- Release 1 implementation is complete;
- the real-response investigation walkthrough is complete;
- blocking scientific/presentation issues have been addressed; and
- MaterialGraph is sufficiently stable to expose to external researchers.

At that point, the next actions are:

1. Review and update this plan against the actual Release 1 capability.
2. Freeze and document the external pilot baseline.
3. Produce the walkthrough.
4. Produce the boundary sheet.
5. Produce the methodology abstract.
6. Establish the feedback mechanism.
7. Create the External Validation Register.
8. Research and qualify the first outreach cohort.
9. Review the first contacts before sending outreach.
10. Begin controlled external scientific validation.

Until that trigger is reached, this document remains a **deferred execution plan**.

---

## 17. Core Principle

MaterialGraph should not ask researchers to trust its conclusions because the software appears sophisticated.

It should give researchers enough evidence, provenance, uncertainty information, and reasoning visibility to decide for themselves whether an output deserves further investigation.

The purpose of external validation is to determine whether that approach provides enough real scientific value for researchers to incorporate MaterialGraph into their work.