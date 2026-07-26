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

## 13. Validation Status Must Be Explicit

Implementation, testing, audit remediation, researcher review, computational
validation, and experimental validation are different states.

MaterialGraph is currently engineering-tested and undergoing audit remediation.
It has not yet been independently scientifically validated by materials
researchers, DFT cross-validation, or experiment.

Resolving an implementation finding means that the specified defect was
corrected and verified within its documented engineering scope. It does not
scientifically validate the affected output.
