# MaterialGraph Engineering Strengths

This document captures architectural patterns that have demonstrated
long-term value during MaterialGraph development.

Future implementations should preserve these patterns whenever possible.

---

# Layered Intelligence

Foundation

↓

Discovery

↓

Knowledge Graph

↓

Research Intelligence

↓

Evidence Intelligence

Each layer owns a single responsibility.

---

# Deterministic Scientific Reasoning

MaterialGraph's canonical scientific reasoning is deterministic and reproducible
from explicit inputs, source-data versions, configuration, software version,
and ordering rules.

LLMs may assist with interpretation, orchestration, retrieval, or
summarization.

LLMs do not silently replace canonical deterministic reasoning or establish
scientific conclusions.

---

# Canonical Scientific Services

Each scientific concept has one implementation.

Examples

- MaterialCompositionService
- MaterialQualityService
- MaterialCriticalityService

Duplicate scientific logic is avoided.

---

# Explainability First

Every recommendation explains:

- why
- evidence
- assumptions
- weaknesses
- validation priorities

---

# Evidence Separation

Scientific computation is separated from evidence.

Evidence enriches reasoning.

Evidence does not silently alter deterministic algorithms.

---

# Progressive Production Hardening

Performance improvements must preserve scientific semantics.

Examples

- caching

- bulk loading

- graph expansion limits

- request timing

---

# Stable API Evolution

Public API contracts should remain stable.

Responses may be extended.

Existing fields should remain compatible.

---

# Endpoint-Sensitive Ranking

Scientific usefulness and endpoint differentiation are treated as
independent concepts.

---

# Explicit Unknown Handling

Unknown information is explicitly represented rather than hidden.

Missing evidence is never silently interpreted.

---

# Reasoning, Evidence, and Execution Separation

Research orchestration, deterministic reasoning, evidence retrieval, external
scientific computation, and researcher review are distinct responsibilities.

Orchestration should compose canonical scientific capabilities rather than
duplicate or replace their reasoning.

External computation may provide validation evidence, but it does not silently
become MaterialGraph's canonical scientific reasoning.

---

# Adapter-Oriented Scientific Integration

Specialized scientific tools should remain responsible for the domain
computation they are designed to perform.

MaterialGraph should own the surrounding research context, modeling readiness,
provenance, task/result integration, and validation state where appropriate.

Integrations should use explicit, replaceable boundaries where practical rather
than coupling MaterialGraph's scientific meaning to one specific simulator,
library, or workflow engine.

---

# Scoped Research Knowledge

Public, organization-private, project-scoped, workspace-scoped, and
researcher-contributed evidence may coexist while preserving their provenance
and access scope.

Private or scoped evidence may enrich authorized research investigations.

It must not silently modify canonical shared knowledge, datasets, rules, models,
or scoring policies.

Promotion into shared or canonical knowledge requires explicit review,
governance, provenance preservation, and versioning.

---

# Scientific Resolution Awareness

Material-level, compositional, or global structural signals must not be treated
as proof that scientifically important local environments are equivalent.

Relevant local context may include:

- coordination environments;
- substitution sites;
- defects;
- interfaces;
- surfaces;
- local bonding;
- other domain-specific local structures.

Where local behavior materially affects the research question, missing or
contradictory local evidence must remain an explicit validation gap even when
global signals are favourable.