# MaterialGraph Scientific Principles

## Purpose and Scientific Boundary

MaterialGraph is a deterministic research-assistance and decision-support
platform. It computationally generates, ranks, compares, and explains material
opportunities using available data and explicit rules.

MaterialGraph outputs are hypotheses and prioritization signals. They do not
establish novelty, structural preservation, transformation or synthesis
feasibility, physical performance, or scientific correctness. Researchers
retain responsibility for interpretation and must validate relevant conclusions
through literature, structural analysis, domain-specific computation,
experiments, or other appropriate scientific methods.

These principles govern every architectural and implementation decision.

---

## 1. Reproducible Deterministic Computation

Given the same explicit inputs, source-data version, configuration, software
version, and ordering rules, MaterialGraph should produce the same ordered
outputs and explanations.

Determinism makes computation reproducible and auditable. It does not make an
output scientifically valid.

---

## 2. Explainability

Every recommendation, ranking, traversal result, pathway hypothesis, and
research opportunity should expose the data, rules, scores, assumptions,
warnings, and limitations that materially influenced it.

An explanation describes how MaterialGraph produced an output. It is not proof
that the output is scientifically correct.

---

## 3. Researcher Authority

MaterialGraph assists research; it does not make autonomous scientific
decisions.

The platform presents opportunities. Researchers decide which opportunities to
investigate and how to validate them.

---

## 4. Ranking and Constraint Semantics

MaterialGraph is inclusive by default: candidates are ranked, explained,
warned, and scored rather than silently discarded.

Objectives must distinguish:

- **Preference** — influences ranking without excluding a result.
- **Soft constraint** — applies a penalty and warning.
- **Hard endpoint constraint** — excludes a result whose endpoint does not
  satisfy the requirement.
- **Hard path-wide constraint** — excludes a result when any disallowed path
  condition occurs.

Unknown evidence must not be assumed to satisfy a hard constraint unless the
objective explicitly permits unknown values.

---

## 5. Evidence Taxonomy

MaterialGraph must not describe every computed relationship as a scientific
fact. Outputs should be classified as:

| Category | Examples |
|---|---|
| Source data | Composition, Materials Project identifier, reported stability fields |
| Derived measurement | Criticality score, normalized composition, graph centrality |
| Rule-based inference | Material-family classification, substitution classification, pathway hypothesis |
| External validation evidence | Literature, structural comparison, DFT result, synthesis outcome, experiment |

A graph relationship can be a reproducible fact about MaterialGraph's model
without being a validated physical relationship.

---

## 6. Explicit Uncertainty

MaterialGraph must expose uncertainty and distinguish:

- known favourable evidence;
- known unfavourable evidence;
- incomplete or unknown evidence;
- internal rule support;
- external evidence coverage;
- scientific validation status.

Missing evidence must remain unknown. It must not improve rankings, scores,
readiness, confidence, or recommendations.

---

## 7. Research Opportunities, Not Scientific Conclusions

MaterialGraph presents multiple computationally identified opportunities rather
than declaring a single scientifically correct answer.

Each opportunity should communicate:

- strengths and trade-offs;
- risks and warnings;
- assumptions and missing evidence;
- internal support;
- validation priorities;
- applicable constraints.

In MaterialGraph, **discovery** means deterministic computational exploration
and prioritization. It does not mean experimental discovery, confirmed novelty,
synthesis feasibility, or validated performance.

---

## 8. Confidence and Readiness Vocabulary

Confidence and readiness outputs describe support within MaterialGraph's
available data and deterministic rules. They are not probabilities of
scientific correctness.

Where applicable, the platform should keep these dimensions separate:

- internal rule support;
- source-data completeness;
- external evidence coverage;
- validation readiness;
- scientific validation status.

Internal support must never be presented as external scientific evidence.

---

## 9. Evidence and Reviewed Evolution

Researchers may contribute evidence through experiments, simulations,
literature, structural analysis, and observations.

Evidence must remain attributed, reviewable, and versioned. It must not silently
or automatically alter scientific computation. Reviewed evidence may influence
later, explicitly versioned datasets, rules, models, or scoring policies while
preserving provenance and reproducibility.

Researcher feedback is valuable evidence, but it is not automatically treated
as authoritative truth.

Evidence may be public, organization-private, project-scoped, or
researcher-scoped. Access scope does not determine scientific validity. Private
evidence may inform authorized research contexts without silently becoming
canonical shared knowledge. Promotion into canonical datasets, rules, models,
or policies requires explicit review, preserved provenance, and versioned
governance.

---

## 10. Structured Scientific Data Takes Precedence

When structured scientific data is available, MaterialGraph must use it as the
canonical source for that field.

Formula parsing and other inferred representations must not override explicitly
provided structured values, including explicitly empty values.

---

## 11. Scientific Semantics Before Performance

Caching, indexing, batching, graph limits, pruning, and parallel execution must
preserve documented scientific and graph semantics.

An optimization must not change candidate eligibility, path meaning, evidence
meaning, ordering, or explanations unless the change is explicit, versioned,
tested, and documented.

---

## 12. Canonical Interpretation and Provenance

Each scientific concept should have one canonical implementation reused across
the platform. Normalization, composition handling, scoring, constraint
evaluation, evidence interpretation, and tie semantics must not diverge between
services.

Every research-facing result should retain enough provenance to identify the
source data, derived signals, rules, configuration, and software version that
produced it.

---

## 13. Global Signals Must Not Hide Local Scientific Differences

Material-level, compositional, or global structural similarity must not be
interpreted as evidence that scientifically important local environments are
equivalent. Relevant local context may include coordination environments,
substitution sites, defects, interfaces, surfaces, local bonding, or other
domain-specific structures.

Where local behavior materially determines the research question, missing or
contradictory local evidence must remain explicit even when global signals are
favourable. Global averages must not erase scientifically important local
validation gaps.

---

## 14. Validation Status Must Be Explicit

Implementation, testing, audit remediation, researcher review, computational
validation, and experimental validation are different states.

MaterialGraph is currently engineering-tested. The architecture and implementation
audits have been closed within their documented engineering scopes, while the
separate Stage 1 security review remains in progress. MaterialGraph has not yet
been independently scientifically validated by materials researchers, DFT
cross-validation, or experiment.

Resolving an implementation finding means that the specified defect was
corrected and verified within its documented engineering scope. It does not
scientifically validate the affected output.

---

## 15. Problem Formalization Must Preserve Researcher Intent

MaterialGraph may help translate an incompletely specified research need into an
explicit objective, but it must not silently choose the researcher's scientific
priorities. Assumptions, proxies, inferred constraints, and suggested preferences
introduced during formalization must be visible, editable, attributable, and
preserved with the investigation.

A researcher with a precise objective must be able to supply it directly.

---

## 16. Evidence Must Preserve Epistemic Context

Evidence provenance is necessary but not sufficient. Where applicable, an evidence
record should preserve enough context to understand what the evidence can
legitimately support, including source or contributor, evidence basis, method,
material/structure/local context, conditions, parameters, sample or run count where
meaningful, uncertainty, review status, corroboration, contradiction, and
applicability limitations.

Access scope, evidence quantity, and scientific strength are separate dimensions.
A private observation or single failed synthesis may be decision-relevant without
establishing a universal scientific conclusion. Conflicting evidence should remain
inspectable unless an explicit reviewed process justifies a stronger synthesis.

---

## 17. Pathway Semantics Must Be Typed

MaterialGraph must distinguish:

- **reasoning pathways**, which explain graph-based computational connection;
- **transformation pathways**, which propose scientifically meaningful physical
  transformations requiring appropriate evidence and validation;
- **synthesis pathways**, which are supported by appropriate experimental or other
  scientific evidence under stated conditions.

Graph reachability, path score, or multi-hop plausibility does not by itself
promote a reasoning pathway into a transformation or synthesis pathway.

---

## 18. Exclusion Must Not Erase Reasoning

Hard constraints may remove a candidate from the eligible result set, but the
system should preserve the reason for exclusion where practical and relevant to
reproducibility. Negative reasoning is part of scientific explanation.

A saved investigation should therefore be able to distinguish "not generated",
"generated but ineligible", "eligible but ranked lower", and "unknown because
required evidence was unavailable" where the implementation can support those
states unambiguously.

---

## 19. Exploration Policy Must Be Explicit and Reproducible

Scientific constraints define the permissible research space. Exploration policy
defines how MaterialGraph searches within that space. A targeted, balanced, or
exploratory posture may legitimately alter prioritization or which eligible regions
are surfaced, but it must not silently weaken hard constraints.

The exploration policy and its parameters must be inspectable and preserved with
the investigation whenever they materially affect results.

---

## 20. Research-Facing Results Should Support a Reproducible Reasoning Trace

Where applicable, a saved investigation should retain enough information to
reconstruct the major computational decisions that produced a result: objective,
constraints, exploration policy, source/evidence versions, configuration, rules,
software version, eligibility decisions, score decomposition, pathway reasoning,
and researcher overrides or rationale.

Replay against a different knowledge or software state must identify the versions
involved and should distinguish changes caused by the research objective from
changes caused by data, evidence, configuration, rules, or implementation.

---

## 21. Core Scientific-Reasoning Semantics and Domain-Specific Meaning Must Remain Separate

MaterialGraph's Core should own scientific-reasoning semantics reusable across
domains: objective and constraint classes, evidence and epistemic states,
provenance, uncertainty, pathway semantics, validation-state structure,
deterministic reasoning, conflict detection, and reproducibility.

Domain extensions should own domain-specific scientific meaning, including
properties, terminology, applicability conditions, evidence requirements,
validation criteria, and domain research templates.

The Core must not silently hard-code one domain's scientific priorities as
universal MaterialGraph semantics.

---

## 22. Configurability Does Not Establish Scientific Authority

A domain rule, validation requirement, evidence mapping, or research template
does not become scientifically trustworthy merely because MaterialGraph can
represent or execute it.

Domain extensions and templates should be attributable, inspectable, versioned,
reviewable, testable, and validated for their intended scope. Learned or
AI-generated proposals must pass an explicit evidence and review process before
they can influence trusted deterministic behavior.

---

## 23. Composed Scientific Context Must Expose Conflicts

An investigation may combine a scientific domain extension, cross-domain decision
contexts, a research template, and researcher-defined objectives or constraints.
Composition must not silently resolve contradictions among those sources.

Where explicit semantics reveal incompatible hard constraints, contradictory
assumptions, applicability conflicts, or incompatible validation requirements,
MaterialGraph should detect and explain the conflict before relying on the
composed objective.

The Core may identify the inconsistency. Scientific-priority resolution remains
with the researcher, and the resolution should be preserved with the
investigation where it materially affects results.

