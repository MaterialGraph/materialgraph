# MG-DE-003: Request paths contain scale-sensitive broad loading

**Status:** Closed
**Priority:** Second implementation wave
**Initial expansion blocker:** Yes

## Observation

Repository inspection identified several paths whose initial work scales with
the stored dataset rather than the requested result:

- unscoped candidate screening loads every material;
- substitution analysis loads every material except the source;
- discovery graph construction loads the complete material-element mapping;
- family discovery selects all materials sharing any base element and performs
  substantial classification in Python.

Existing response, depth, and branching limits are valuable but do not bound
all of this upstream work.

## Impact

Common elements and denser families can increase query volume, memory, and
request duration even when the final response is small. This can conflict with
the application, database, and proxy timeout hierarchy on the small production
instance.

## Required outcome

- apply scientifically equivalent candidate narrowing in SQL;
- scope material-element loading to the active candidate/subgraph set;
- define deterministic candidate caps or staged ranking where scientifically
  appropriate;
- preserve explanations and current result semantics;
- add indexes only where representative query plans justify them.

## Acceptance evidence

Focused tests must prove preserved semantics. The representative fixture must
record query counts, significant query plans, latency, and memory for each
affected path, including dense common-element cases.

## Implementation checkpoint

Candidate screening now pushes its existing stability and energy eligibility
constraints into SQL before bulk scoring. Substitution analysis selects only
materials sharing a source element, which excludes exactly the candidates whose
Jaccard similarity would be zero. Discovery graph construction loads element
composition incrementally for the source and the already bounded active
candidate frontier rather than for the complete dataset.

Material-family candidate selection now expresses the existing strong
relationship rules as a SQL union before loading material rows and full
composition: at least three shared elements, a shared transition metal, or
phosphate co-membership when the base contains phosphorus. Python
classification remains authoritative, preserving explanations and ordering.

No index was added without representative PostgreSQL query-plan evidence.

## Closure evidence

Independent PostgreSQL execution at commit `69f0bda15f2a2ffe76c265ecc3bbfe60fc35f7a7`
qualified screening, substitution, family, discovery candidates, discovery
graph, discovery path, recommendations, and scientific pathways against the
1,000-material fixture. All requests returned HTTP 200 below the existing
deadline. Peak traced Python allocation stayed below 10 MiB; the scoped
material-element plan used an index-only scan; curated detail and criticality
JSON matched completely. See [the qualification report](../MG-DE_QUALIFICATION_REPORT.md).
