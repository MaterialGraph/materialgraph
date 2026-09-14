# MG-DE-003: Request paths contain scale-sensitive broad loading

**Status:** Open
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
