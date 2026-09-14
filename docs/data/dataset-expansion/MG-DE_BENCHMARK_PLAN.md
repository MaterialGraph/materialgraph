# MG-DE Benchmark Plan

## Objective

Establish whether the first dataset target can be imported, queried, backed up,
and reasoned over within MaterialGraph's existing bounded request and scientific
correctness contracts.

## Fixture requirements

The fixture must be deterministic and record its generation or selection
manifest. It should contain approximately 1,000 materials and deliberately
include:

- both common and rare elements;
- dense and sparse material families;
- stable and unstable materials;
- polymorph and source-identity cases;
- complete, partial, and missing optional properties;
- duplicate source records and controlled invalid records;
- the current curated regression cohort.

Synthetic records may be used for performance testing, but must never be
presented as scientific source evidence.

## Import scenarios

1. Manifest-only dry run.
2. Clean import into an empty test database.
3. Identical rerun with no unintended changes.
4. Controlled interruption between chunks followed by resume.
5. Changed-source rerun exercising insert, update, unchanged, conflict, reject,
   and retirement policies.
6. Failed chunk demonstrating the documented atomicity boundary.
7. Manifest and database count reconciliation.

## Request scenarios

Measure at minimum:

- material listing and detail;
- neighbors and similarity;
- family classification and recommendations;
- candidate screening with and without explicit IDs;
- substitution analysis;
- discovery candidates, graph, path, and scientific pathways;
- representative dense common-element neighborhoods.

## Recorded measurements

Each result must record:

- commit and fixture manifest digest;
- database engine and relevant configuration;
- row counts for primary and association tables;
- cold and warm wall-clock latency;
- database query count and significant query plans;
- application peak resident memory when reliably measurable;
- response status and complete deterministic result comparison;
- timeout, rejection, or resource-limit behavior;
- backup size and duration in the test environment.

## Initial acceptance gates

- all imports terminate within their declared scope;
- interruption and rerun do not create duplicates or ambiguous state;
- accepted/rejected/inserted/updated/unchanged counts reconcile to the manifest;
- all current tests pass;
- curated reference responses match complete pre-change JSON unless an approved
  scientific change explicitly supersedes them;
- representative requests complete within existing application and proxy
  deadlines;
- no request path performs an unintended whole-dataset material or relationship
  load;
- query plans avoid demonstrated pathological scans at the target size;
- memory remains compatible with the deployment budget under the approved
  single-request benchmark method;
- backup behavior remains compatible with documented recovery objectives.

No concurrency or load test is authorized by this plan. Any such test requires
a separate bounded procedure and explicit approval.
