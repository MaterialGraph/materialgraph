# MaterialGraph Independent Observation Audit

**Status:** Completed and frozen; reconciled on 2026-07-26  
**Audit mode:** Bottom-up, observation first  
**Previous audit documents:** Excluded from the evidence set until final comparison

**Final scope:** Independent post-remediation implementation review  
**Confirmed findings:** 44 `MG-IND` correctness/security findings and 5
`MG-PERF` performance findings  
**Canonical disposition:** Reconciled into
`MaterialGraph_Architecture_Implementation_Audit_v2_Regenerated.md`

> This document is a frozen source audit. Its finding IDs, evidence, and
> observations are preserved as originally recorded. Remediation status is
> maintained only in the canonical `MG-AUD` register.

## Method

The project is inspected from its foundation upward. An item progresses through:

1. observation;
2. concern under investigation;
3. confirmed finding.

No remediation is performed during this audit. Security and performance are
continuous review lenses, but a possible weakness is not classified as a
vulnerability or bottleneck without implementation and runtime evidence.

## Area 1 — Root Scripts

### Files inspected

- `scripts/backfill_material_element_fractions.py`
- `scripts/check_import_counts.py`
- `scripts/cleanup_test_materials.py`
- `scripts/import_materials_project.py`
- `scripts/seed_core_data.py`
- `scripts/seed_material_applications.py`
- `scripts/seed_risk_profiles.py`

Supporting implementation inspected:

- material, element-risk, material-element, application, and
  material-application models;
- database and settings configuration;
- Materials Project normalization and import services;
- composition normalization and backfill services;
- material criticality and risk services.

### Confirmed finding MG-IND-001

**Title:** Conflicting risk-profile scales can persist execution-dependent data  
**Category:** Data correctness / deterministic behavior  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`seed_core_data.py` and `seed_risk_profiles.py` both write
`ElementRiskProfile` records for the same elements and year (`2026`). The model
enforces uniqueness on `(element_id, year)`.

The core seed uses values on an apparent `0–1` scale. The dedicated risk seed
uses values on a `1–10` scale. Both label the source as
`manual_phase_1_seed`.

Their persistence behavior differs:

- the core seed skips an existing profile;
- the dedicated risk seed updates an existing profile.

The active criticality calculation uses `10 - recyclability_score` and
multiplies the mean by `10`, establishing a downstream expectation compatible
with `1–10` inputs rather than the core seed's `0–1` representation.

#### Impact

Database meaning depends on which seed scripts have been executed and in what
order. A database initialized with only the core seed can produce materially
different risk and criticality outputs from a database subsequently processed
by the dedicated risk seed, even though both records report the same source and
year.

#### Follow-up verification

- Inspect migrations, tests, documentation, and deployment/bootstrap commands
  for the declared canonical scale.
- Determine whether any current database contains the `0–1` representation.
- Trace every consumer's assumed range before designing remediation.

### Observations under investigation

#### OBS-SCR-001 — Mutation scripts have no explicit environment guard

Import, backfill, cleanup, and seed scripts operate on the database selected by
runtime settings. The cleanup script commits deletion immediately and has no
dry-run mode. This is an operational-safety and security observation; actual
exposure depends on deployment access and execution procedures.

#### OBS-SCR-002 — Imports are atomic per chemical system, not per complete run

`MaterialImportService.import_materials()` commits each candidate batch.
`import_materials_project.py` invokes it once per chemical system. Failure
during a later system can leave earlier systems committed. Whether this is
undesirable depends on the intended restart and consistency contract.

#### OBS-SCR-003 — Material-application seeding uses heuristic substrings

Application assignment is based on case-sensitive substring checks against
formula strings. This may be an intentional prototype heuristic. Its scientific
classification behavior must be tested against representative formulas before
it is treated as a correctness finding.

#### OBS-SCR-004 — Material-application seeding has query growth

The script loads all materials, iterates over every rule and material, and
performs an existence query for every formula match. This is not a demonstrated
bottleneck for the current small dataset, but it is a scalability risk if used
for substantially larger imports.

#### OBS-SCR-005 — Test-material recognition is not uniform

The cleanup script identifies records using `LIKE 'mp-%test%'`. The composition
backfill service skips only IDs beginning with `mp-test-`. The practical impact
depends on the project's actual test-ID conventions.

#### OBS-SCR-006 — Count inspection verifies quantity, not integrity

`check_import_counts.py` reports three table counts but does not detect orphaned
links, missing composition membership, invalid fraction totals, absent risk
profiles, or incomplete imports. This is an observation about diagnostic scope,
not a defect in a script explicitly named as a count checker.

## Current position

One confirmed finding has been recorded. Six observations remain open and must
be revisited as their dependent layers are inspected. No comparison has been
made with previous audit documents.

## Area 2 — Project and Runtime Configuration

### Files inspected

- `alembic.ini`
- `alembic/env.py`
- `docker-compose.yml`
- `pyproject.toml`
- `requirements.txt`
- `requirements-dev.txt`
- `.env.example`
- `.gitignore`
- `app/core/config.py`
- `app/core/database.py`
- `app/core/logging.py`
- `app/main.py`
- setup instructions in `README.md` and
  `docs/guide/getting_started.md`

The expected `Dockerfile` and common lock files (`uv.lock`, `poetry.lock`, and
`Pipfile.lock`) were not present at the inspected repository paths.

### Sequencing correction — `app/core`

The initial pass traced `config.py`, `database.py`, and `logging.py` as
dependencies of the root configuration, but did not present `app/core` as its
own architectural layer before inspecting models and material services.
`performance.py` was inspected later when supplied.

The audit record preserves the order in which evidence was obtained, while the
conceptual dependency order is:

```text
root configuration
→ app/core runtime foundation
→ models
→ services
```

This sequencing correction does not change the status of an existing finding.

### Confirmed finding MG-IND-002

**Title:** Standard dependency installation selects another repository checkout  
**Category:** Build correctness / reproducibility  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Both the main README and getting-started guide instruct a developer to clone the
repository and run:

```text
pip install -r requirements.txt
```

The committed `requirements.txt` includes an editable VCS requirement for
`materialgraph` fixed to commit
`ba0cc025465dec9353dbc1fc59ea787f095d4ade`. Consequently, the dependency
installation creates and registers another MaterialGraph source checkout
instead of installing the working tree that the developer just cloned.

#### Impact

The installed package identity can refer to a different revision from the
working tree. Imports executed from the repository root may mask the mismatch
because the current directory takes precedence, while commands launched from
another directory can resolve the editable VCS checkout. This makes setup and
diagnostic results dependent on the execution location.

#### Follow-up verification

- Inspect CI, deployment, and developer commands for their working directory.
- Determine why the editable VCS entry was committed.
- Verify package resolution with `pip show materialgraph` and an import-path
  check in each supported environment before remediation.

### Confirmed finding MG-IND-003

**Title:** Setup guide configures an API-key name the importer does not read  
**Category:** Configuration correctness  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

The getting-started guide instructs users to set:

```text
MP_API_KEY=...
```

Runtime settings define `materials_project_api_key`, which maps to
`MATERIALS_PROJECT_API_KEY`. The root import script explicitly checks this
setting before calling Materials Project. The supplied `.env.example` also uses
`MATERIALS_PROJECT_API_KEY`, contradicting the guide.

#### Impact

A new installation that follows the guide cannot run the documented Materials
Project import without independently discovering and correcting the variable
name.

### Confirmed finding MG-IND-004

**Title:** Project version has multiple incompatible authorities  
**Category:** Release metadata / observability  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

- `pyproject.toml` declares version `0.1.0`.
- `Settings.project_version` defaults to `1.0.0`.
- the FastAPI application hard-codes version `1.0.0` instead of using that
  setting;
- the current README describes capabilities as `v1.9.6`.

#### Impact

Package metadata, API metadata, runtime configuration, and user documentation
do not identify the same release. This can impede production diagnosis,
artifact traceability, and API-client compatibility decisions.

### Observations under investigation

#### OBS-CFG-001 — Local PostgreSQL is host-exposed with default credentials

Compose publishes PostgreSQL as `5432:5432` and sets both username and password
to `postgres`. The compose file does not restrict the bind to loopback. This is
a security concern if Compose is run on a network-reachable host, but it is not
yet classified as a vulnerability because the intended use appears to be local
development and host firewall exposure has not been inspected.

#### OBS-CFG-002 — Dependency authorities can diverge

`pyproject.toml` contains unbounded direct dependencies, while
`requirements.txt` is a large exact-version environment snapshot and
`requirements-dev.txt` combines that snapshot with unbounded development
requirements. No conventional lock file was found. The exact requirements file
currently provides repeatability for its listed environment, but there is no
observed mechanism ensuring it remains synchronized with project metadata or
portable across supported platforms.

#### OBS-CFG-003 — Environment inputs are permissive and partially unexplained

Settings ignore unknown keys. `.env.example` declares `MP_API_URL`, but the
inspected settings model does not declare that field. Alembic supports a
separate `DATABASE_MIGRATION_URL`, but the example does not advertise it.
Repository-wide usage and intended compatibility need further tracing.

#### OBS-CFG-004 — Database engine relies on default pool limits

The application enables `pool_pre_ping` but otherwise uses SQLAlchemy pool
defaults. This is not evidence of a current bottleneck. It should be revisited
with the process model, Neon connection limits, concurrency expectations, query
durations, and production service configuration.

#### OBS-CFG-005 — Health response exposes the environment label

The unauthenticated health endpoint returns `settings.environment`. This is a
minor information-exposure observation. Classification depends on whether the
label contains operationally meaningful deployment information and whether the
endpoint is publicly reachable.

### `app/core` observations

#### OBS-CORE-001 — Environment-file discovery depends on working directory

Settings load `.env` using a relative filename during module import. Commands
started outside the repository working directory may therefore select different
configuration sources or fail validation. Systemd working-directory and
environment-file configuration must be inspected before classifying operational
impact.

#### OBS-CORE-002 — Configuration values have minimal semantic validation

The settings model types required and optional strings, but does not constrain
known environment names, validate log levels, reject blank API keys, or enforce
database URL policy by environment. Unknown keys are ignored. This is flexible
for a prototype but can allow misspelled or contradictory configuration to
reach import-time initialization.

#### OBS-CORE-003 — Configuration and engine creation occur at import time

`settings` and the SQLAlchemy engine are created during module import. This
provides early failure for a missing database URL, but it also couples tests,
scripts, migrations, and utility imports to configuration availability before
callers can inject alternatives. The practical testing and deployment impact
requires broader inspection.

#### OBS-CORE-004 — Session cleanup relies on close-time rollback

The FastAPI database dependency closes the session in `finally` but does not
explicitly roll back after a request exception. SQLAlchemy session close
normally releases transactional state, so no defect is recorded. Explicit
transaction ownership and write-endpoint patterns should still be reviewed.

#### OBS-PERF-CORE-001 — Timing utility provides logs, not performance controls

`timed_block()` uses a monotonic high-resolution clock and records duration in a
`finally` block, including failed operations. It logs blocks taking at least
`0.25` seconds by default.

It does not provide request middleware, deadlines, cancellation, query counts,
percentiles, correlation IDs, metrics aggregation, concurrency measurement, or
resource enforcement. Its existence should therefore not be treated as proof
that endpoint performance is monitored or bounded.

#### OBS-PERF-CORE-002 — Performance events use synchronous informational logs

Slow-block events are emitted at `INFO` through the global Loguru logger, whose
configured sink writes to standard output without asynchronous queueing.
This is appropriate for the current prototype. At higher event volume it may
add request latency and makes slow-operation alerting dependent on external log
collection.

#### OBS-SEC-CORE-001 — Logging has no explicit redaction policy

The configured logger writes interpolated messages with source function and
line information. The inspected core and material services do not log database
credentials or the Materials Project API key. However, there is no central
redaction or structured-field policy to protect future callers from logging
sensitive values. This is a forward-looking control gap, not a confirmed
secret exposure.

### Closed observation

#### CLOSED-CFG-001 — `httpx2` is not a dependency typo

The package name initially appeared suspicious because FastAPI tests commonly
use HTTPX. Verification against the package registry showed that `httpx2` is a
real continuation project with verified ownership and provenance. No finding is
recorded merely from its name. Test compatibility will be evaluated separately.

## Current position

Four confirmed independent findings have now been recorded:

- one from root data scripts;
- three from project/runtime configuration.

Eleven observations remain open across script, security, performance,
configuration, and deployment behavior. No remediation has been performed and
no previous audit document has been used for comparison.

## Area 3 — Material Ingestion and Composition Services

### Files inspected

- `app/services/material/composition_service.py`
- `app/services/material/composition_backfill_service.py`
- `app/services/material/import_service.py`
- `app/services/material/project_service.py`
- `app/services/material/query_service.py`

Supporting implementation inspected:

- material, element, and material-element models;
- material API routes and response schemas;
- criticality consumption of persisted fractions;
- root import and backfill scripts.

### Positive observations

- Materials Project composition is taken from structured
  `doc.composition`, not reconstructed from formula text.
- Composition amounts must be finite and positive, and structured fraction
  membership must match element membership.
- Backfill validates complete membership before changing fractions.
- A validation failure during a complete backfill rolls back earlier pending
  changes, while dry-run mode always rolls back.
- External API credentials are not written into stored material data or
  printed by these services.
- Material query retrieval is bounded to one material and uses two predictable
  database queries.

### Confirmed finding MG-IND-005

**Title:** Duplicate element normalization is not honored during persistence  
**Category:** Import correctness / invariant enforcement  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`MaterialCompositionService._normalize_element_membership()` deliberately
deduplicates repeated symbols. `resolve_import_fractions()` therefore accepts a
candidate element list containing duplicates and returns one fraction per
unique symbol.

`MaterialImportService._link_elements()` subsequently iterates over the
candidate's original element list rather than the normalized membership. A
duplicate symbol therefore produces duplicate `MaterialElement` objects for the
same material and element. The database model enforces a unique
`(material_id, element_id)` pair.

#### Impact

The validation layer accepts input that the persistence layer cannot store.
Such a candidate causes the batch transaction to fail at flush or commit rather
than being imported according to the normalization contract. Materials Project
normally supplies unique membership, so the practical production exposure must
still be established; the inconsistency itself is deterministic.

#### Follow-up verification

- Add a characterization case using repeated element membership.
- Inventory every direct `MaterialCandidate` constructor.
- Decide whether duplicates should be rejected or normalized once and passed
  consistently to persistence.

### Observations under investigation

#### OBS-MAT-001 — Missing composition is represented as equal element weights

For compatibility, `resolve_import_fractions()` stores `1.0` for every element
when `composition_fractions` is empty. The `MaterialElement` model carries no
field distinguishing this legacy placeholder from known stoichiometry.
Criticality later consumes these values as weights and normalizes by their
total, producing equal element influence.

This can turn absence of stoichiometric evidence into an equal-weight
assumption. It remains an open concern until direct candidate constructors and
production data provenance are inventoried.

#### OBS-MAT-002 — Composition invariants are service-only

The database requires a fraction value and unique material-element membership,
but it does not constrain fractions to finite positive values or enforce a
normalized total. Import and backfill paths validate those invariants; other
current and future write paths could bypass them. All writers must be
inventoried before determining whether this is an active integrity finding.

#### OBS-MAT-003 — Existing Materials Project records are never refreshed

The importer skips a candidate whenever its `mp_id` already exists. It does not
update scientific properties, stability, raw source data, element membership,
or composition fractions. This may be intentional import-once behavior, but it
also means rerunning the import cannot refresh changed upstream evidence.

#### OBS-MAT-004 — Import query count grows with candidates and elements

For each candidate, the importer queries material existence and then queries
each element individually. This is acceptable for the current capped prototype
batch but creates query growth proportional to total candidate-element
occurrences. It is a scalability risk, not a demonstrated bottleneck.

#### OBS-MAT-005 — Full backfill uses load-all plus per-material queries

The backfill loads every eligible Material row into memory and issues a separate
material-element query for each one. Its all-or-nothing transaction also remains
open for the complete scan. This is reasonable for the current small repair
operation but would scale poorly to a large materials corpus.

#### OBS-MAT-006 — External fetch resilience is delegated implicitly

The service makes a synchronous Materials Project request and does not specify
timeouts, retries, backoff, or response-size validation in MaterialGraph code.
The client library may provide safeguards internally. Its actual defaults and
the operational use of this service must be verified before recording a
reliability or performance finding.

#### OBS-MAT-007 — Detail responses expose membership but not fractions

`MaterialQueryService` retrieves element entities without their
`MaterialElement` rows, and `MaterialDetail` contains element identity but no
composition fraction or fraction provenance. This may match the endpoint's
intended scope, but it limits public inspection of the composition state used
by downstream scientific scoring.

## Current position

Five confirmed independent findings have now been recorded. The material
ingestion/composition group added one confirmed persistence inconsistency,
seven open observations, and several positive controls. No remediation has
been performed and no previous audit document has been used for comparison.

## Area 4 — Core Material Models

### Files inspected

- `app/models/element.py`
- `app/models/material.py`
- `app/models/material_element.py`

### Positive observations

- Element symbols and Materials Project IDs are declared unique and indexed.
- Material-element membership has a named composite uniqueness constraint.
- Both material and element foreign keys declare `ON DELETE CASCADE`, matching
  the intended cleanup behavior of dependent composition links.
- Frequently used foreign keys are indexed.
- Nullable scientific properties distinguish unavailable values from numeric
  zero.
- Multiple materials may share a formula, which is appropriate because
  Materials Project IDs can represent distinct structures or polymorphs.

### Model conclusions

No new confirmed finding is recorded from these three model definitions alone.
They do, however, strengthen several existing observations and expose
additional persistence questions.

### Updated observation

#### OBS-MAT-002 — Composition invariants are service-only

The `MaterialElement` model enforces non-null membership and pair uniqueness,
but `fraction` is an unconstrained database float. The declarative model does
not require it to be finite, positive, at most one, or part of a normalized
per-material total.

Import and backfill services validate these properties before their own writes.
Whether the absence of database-level checks is an active integrity defect
depends on the complete writer inventory and migration state. A normalized
cross-row total cannot be expressed as a simple row check and would require a
different enforcement mechanism.

### Additional observations under investigation

#### OBS-MOD-001 — Element identity is syntactically permissive

The model allows any non-null string up to ten characters as an element symbol,
and atomic number is optional. This supports placeholders created during
imports, but it does not itself ensure that the symbol is a recognized chemical
element or that symbol and atomic number agree. Upstream validation and actual
writer behavior must determine whether invalid identities are reachable.

#### OBS-MOD-002 — Scientific scalar ranges are not constrained

Band gap, energy above hull, formation energy per atom, and density are nullable
floats without finite-value or domain checks. Some of these properties have
meaningful physical bounds while formation energy may legitimately be
negative. The external source currently supplies them, so this remains a data
boundary observation rather than a confirmed data defect.

#### OBS-MOD-003 — Raw source data can drift from normalized columns

`Material.raw_data` stores the source document alongside separately normalized
columns and composition links. The model contains no source revision,
retrieval timestamp, or synchronization marker. Combined with the importer's
skip-existing behavior, normalized fields and raw source evidence have no
model-level freshness contract.

#### OBS-MOD-004 — Source and material type are free-form classifications

`source` and `material_type` use free-form strings. This is flexible for a
prototype but permits spelling and casing variants that can alter equality
filters such as the backfill's `source == "materials_project"` selection.
Existing writers and database contents need inspection before this is treated
as a correctness issue.

#### OBS-MOD-005 — Material ID and source semantics are coupled informally

The globally unique field is named `mp_id`, although the model also supports a
free-form source and tests use synthetic MP-like identifiers. If future
providers use overlapping identifiers, the current identity contract may not
represent `(source, external_id)` cleanly. This is a future extensibility
observation, not a present collision.

#### OBS-PERF-MOD-001 — Material foreign-key index may duplicate a composite prefix

`material_elements.material_id` has an individual index, while the unique
constraint on `(material_id, element_id)` normally creates a composite index
whose leading column can support material-ID lookups in PostgreSQL. The
individual index may therefore add write and storage overhead without improving
the dominant query. Actual migration DDL and query plans must be inspected
before recommending removal.

#### OBS-MOD-006 — Declarative cascade intent still requires migration verification

The model specifies database cascades, but model metadata does not prove that
an already-created production schema contains the same foreign-key actions.
Migration revisions and live schema metadata must be checked before relying on
cascade behavior for cleanup or deletion safety.

## Current position

Five confirmed findings remain. The core model review added no premature
finding; it strengthened the composition-integrity concern, recorded five
additional model observations and one indexing observation, and identified
migration verification as a later requirement.

## Area 5 — Remaining Models and Graph-Job Lifecycle

### Files inspected

- `app/models/application.py`
- `app/models/element_risk_profile.py`
- `app/models/graph_job.py`
- `app/models/material_application.py`
- `app/models/risk_factor.py`

Supporting implementation inspected:

- graph-job service, schemas, routes, and service tests;
- application, element, and risk read routes and schemas;
- seed scripts that write application mappings and risk profiles;
- API router registration.

### Positive observations

- Application and risk-factor names are unique and indexed.
- Element risk profiles preserve nullable values rather than forcing missing
  evidence to zero.
- Risk profiles are unique per element and year under the current
  single-profile design.
- Material-application pairs are unique and use cascading foreign keys.
- Graph jobs use non-sequential UUID identifiers.
- Job status is represented by a database-backed enum rather than an arbitrary
  string.
- Graph-job input and result payloads use PostgreSQL JSONB.
- Job listing is bounded by API validation to at most 100 records.

### Confirmed finding MG-IND-006

**Title:** Pending graph-job claiming is not concurrency-safe  
**Category:** Job correctness / concurrency  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`claim_next_pending_job()` performs these operations separately:

1. select the oldest row whose status is `PENDING`;
2. mutate the returned ORM object to `RUNNING`;
3. commit.

The select uses neither a row lock such as `FOR UPDATE SKIP LOCKED` nor an
atomic conditional update. Two database sessions can select the same pending
row before either commits and both can return it as their claimed job.

The service test verifies single-session claiming only and does not exercise
competing workers.

#### Impact

When more than one worker polls the queue, one graph job can be executed more
than once. Duplicate graph computation wastes resources and can produce
last-writer-wins result or error state.

#### Follow-up verification

- Reproduce with two independent database sessions.
- Determine the intended worker count and retry semantics.
- Inspect whether any external worker performs its own locking.

### Confirmed finding MG-IND-007

**Title:** Graph-job lifecycle permits contradictory state transitions  
**Category:** State integrity / job correctness  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`complete_job()` and `fail_job()` update any existing job without checking its
current status. The existing test suite completes and fails newly created
`PENDING` jobs directly.

Consequently, the service permits:

- `PENDING → COMPLETED` with no `started_at`;
- `PENDING → FAILED` with no `started_at`;
- `COMPLETED → FAILED`;
- `FAILED → COMPLETED`;
- repeated completion or failure.

Completion does not clear an existing `error_message`, and failure does not
clear an existing `result_json`. The model has no constraint relating status to
timestamps, result, or error fields.

#### Impact

A record can claim successful completion while retaining an error, claim
failure while retaining a result, or contain a terminal status without ever
being started. Job history and API responses are therefore not guaranteed to
represent a coherent lifecycle.

### Observations under investigation

#### OBS-RISK-MOD-001 — Risk source cannot coexist within the same year

The uniqueness key is `(element_id, year)` rather than
`(element_id, year, source)`. Although `source` is stored, a manual profile,
USGS profile, or another evidence provider cannot coexist for the same element
and year. This may be an intentional single-canonical-profile design; future
evidence and provenance requirements will determine whether it is limiting or
incorrect.

#### OBS-RISK-MOD-002 — Risk ranges and scale are not self-describing

Risk fields have no database bounds, and the public read schema returns numbers
without scale or unit metadata. This reinforces MG-IND-001: the data model
cannot distinguish `0–1` and `1–10` records carrying the same source and year.
The canonical scale and its enforcement should be resolved when remediation is
planned.

#### OBS-APP-MOD-001 — Suitability semantics are unconstrained

`suitability_score` is nullable and has no range or evidence/provenance field.
The current seed writes `0.75`, but the model does not state whether this is a
probability, normalized heuristic, confidence, or ranking weight. Downstream
consumer behavior must be inspected before classification.

#### OBS-JOB-MOD-001 — Timestamp timezone intent and column type differ

Python defaults create timezone-aware UTC datetimes, but SQLAlchemy `DateTime`
is declared without `timezone=True`. Depending on actual migration DDL and
database/session settings, timezone information may be discarded or normalized
implicitly. Migration and live-schema inspection are required before confirming
stored timestamp behavior.

#### OBS-PERF-JOB-001 — Queue access lacks a composite queue index

Claiming filters by status and orders by creation time. The model has separate
indexes for status and job type but no declared composite `(status,
created_at)` index. Listing also orders globally by `created_at` without a
declared timestamp index. This is not a current bottleneck at prototype volume;
query plans should be measured as the job table grows.

#### OBS-SEC-JOB-001 — Public job payloads have no application-level size limit

The registered graph-job API accepts arbitrary JSON objects and stores them in
JSONB. Routes provide create, list, and detail operations without an
authentication dependency in application code. There is no observed
application-level request-body quota, job-type allowlist, retention policy, or
payload redaction.

This creates potential storage, enumeration, and information-exposure concerns
if the route is publicly reachable. Nginx limits, network exposure, deployment
controls, and intended public usage must be inspected before assigning a
security severity.

#### OBS-JOB-MOD-002 — Job type is free-form

The model and creation schema accept any non-null string, with length enforced
only when the database writes it. No registry or enum ties job types to
supported worker handlers. Invalid job types can therefore enter the queue
unless a downstream worker rejects them.

#### OBS-JOB-MOD-003 — Job records have no ownership or retention metadata

The current prototype has no users or organizations, so ownership is not yet
required. The model also has no expiry, attempt count, lease, heartbeat,
worker identifier, retry limit, or retention marker. These are future queue and
multi-user requirements rather than present model defects.

#### OBS-RISK-MOD-003 — `RiskFactor` is structurally isolated

The inspected model defines named risk factors but no foreign key connects them
to element risk profiles or their individual score columns. Consumer and seed
inspection is needed to determine whether this is an intentionally reserved
taxonomy table or unused legacy structure.

## Model-layer position

All supplied model files have now been inspected. Seven confirmed independent
findings are recorded overall; two arise from graph-job concurrency and
lifecycle behavior. Other range, provenance, timezone, indexing, exposure, and
extensibility questions remain observations pending migrations, consumers,
deployment configuration, and live behavior.

## Area 6 — Material Family, Neighborhood, Similarity, and Recommendation

### Files inspected

- `app/services/material/family_service.py`
- `app/services/material/neighbor_service.py`
- `app/services/material/neighborhood_service.py`
- `app/services/material/similarity_service.py`
- `app/services/material/recommendation_service.py`

Supporting implementation inspected:

- material-intelligence and family routes;
- neighbor, neighborhood, similarity, family, and recommendation schemas where
  available;
- focused similarity and recommendation tests;
- criticality single and bulk retrieval paths;
- application and composition models.

### Positive observations

- Relationship membership uses structured material-element links rather than
  formula substrings.
- Shared element and application rows are collected in batches rather than one
  query per candidate.
- Neighbor material records are loaded in one `IN` query.
- Similarity preserves unknown criticality as `None` and exposes direction as
  `UNKNOWN`.
- Recommendation scoring does not reward or penalize criticality when the
  comparison is unknown.
- Public similarity, recommendation, and neighborhood parameters have explicit
  bounds.
- Neighborhood traversal uses a visited set and a per-request neighbor cache.
- Relationship explanations explicitly warn that structural framework
  similarity has not been validated.

### Confirmed finding MG-IND-008

**Title:** Magnesium is classified and explained as an alkali element  
**Category:** Scientific classification  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`MaterialFamilyService.ALKALI_ELEMENTS` contains `{"Li", "Na", "K", "Mg"}`.
Magnesium is an alkaline-earth metal, not an alkali metal. The set directly
drives `alkali_substitution` classification and explanations phrased as
“alkali substitution from ... to ...”.

#### Impact

Materials involving Mg can receive a scientifically incorrect relationship
label and explanation. Because `alkali_substitution` is considered a strong
relationship, it can also determine whether a material is included in the
family response.

### Confirmed finding MG-IND-009

**Title:** Similarity candidates are truncated before final similarity scoring  
**Category:** Ranking correctness  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

The neighbor service first sorts candidates using:

```text
2 × shared elements + 3 × shared applications
```

The similarity service slices that preliminary list to `limit` and only then
calculates its final score:

```text
20 × shared elements
+ 30 × shared applications
+ stability bonus
+ energy-above-hull bonus
```

The preliminary relationship weights preserve relative relationship ordering,
but they omit the quality bonuses. A candidate outside the preliminary cutoff
can therefore have a higher final similarity score than a retained candidate.

#### Impact

The endpoint does not necessarily return the true top `limit` materials under
its own published similarity score. Recommendation inherits this truncation
through its fixed similarity pool.

### Confirmed finding MG-IND-010

**Title:** Missing criticality evidence receives favorable tie ordering  
**Category:** Evidence semantics / ranking correctness  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Similarity sorts equal-score candidates using:

```text
-abs(criticality_delta or 0)
```

When criticality is unknown, `criticality_delta` is `None`, and `None or 0`
becomes zero. An unknown comparison therefore receives the best possible
secondary value, equal to an exact known tie and ahead of every known nonzero
delta.

#### Impact

Missing criticality evidence can improve ordering among otherwise equal
similarity candidates. This conflicts with the service's explicit `UNKNOWN`
direction and with evidence-aware ranking semantics.

### Confirmed finding MG-IND-011

**Title:** Limited neighborhood responses can contain dangling edges  
**Category:** Graph response integrity  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Neighborhood traversal builds complete node and edge collections, sorts them
independently, and then applies the same numeric `limit` separately:

```text
limited_nodes = sorted_nodes[:limit]
limited_edges = sorted_edges[:limit]
```

No filtering ensures that each retained edge's source and target are present in
`limited_nodes`.

#### Impact

The returned payload can claim a bounded graph while containing edges that
reference omitted nodes. Consumers cannot reconstruct a self-contained
subgraph from the response.

### Confirmed finding MG-PERF-001

**Title:** Similarity performs per-candidate criticality query amplification  
**Category:** Performance / database access  
**Confidence:** High  
**Status:** Confirmed structurally; runtime measurement pending

#### Evidence

Similarity calls `get_material_criticality()` once for the source and once for
every retained neighbor. Each single-material call performs material,
material-element, and risk-profile database queries. A 50-candidate request can
therefore issue approximately 153 criticality-related queries in addition to
neighbor retrieval.

`MaterialCriticalityService` already provides a bulk method, so this query
growth is not required by the underlying calculation.

#### Impact

Database round trips grow linearly with the similarity pool and propagate into
recommendation and scenario-recommendation requests. Actual latency must still
be benchmarked under local and Neon production conditions.

### Confirmed finding MG-PERF-002

**Title:** Neighborhood result limit does not bound traversal work  
**Category:** Performance / resource control  
**Confidence:** High  
**Status:** Confirmed structurally; runtime measurement pending

#### Evidence

At depth 2, the service expands every first-hop neighbor and calls the complete
neighbor service for each one. The `limit` parameter is applied only after the
traversal, node construction, edge construction, and sorting finish.

The public route describes a bounded neighborhood and caps depth at 2, but
`limit=1` and `limit=100` perform the same graph expansion for a given root and
depth.

#### Impact

Response size is bounded, but database work and in-memory edge growth are not
bounded by the requested result limit. Dense or larger graphs can make this
endpoint disproportionately expensive and vulnerable to repeated-cost abuse.

### Observations under investigation

#### OBS-FAM-001 — Phosphate relationship requires oxygen only in the candidate

`phosphate_related` requires phosphorus in both materials but oxygen only in
the candidate. It is then treated as a strong relationship. The explanation
does disclose when the base lacks oxygen, so the implementation may
intentionally mean phosphorus-related chemistry rather than two phosphate
materials. Scientific naming and expected examples require verification.

#### OBS-FAM-002 — Exact relationship ties lack a stable presentation key

Family, neighbor, similarity, and recommendation sorting do not consistently
include material ID or another final deterministic key. Python's stable sort
then preserves input order from database queries that often have no
`ORDER BY`. This may yield varying presentation order for genuine ties.
Tie-preservation requirements must be distinguished from deterministic display
ordering before classification.

#### OBS-NEIGH-001 — Test-material exclusion is inconsistent

Family candidates exclude MP IDs beginning with `mp-test`, while neighbor,
similarity, neighborhood, and recommendation services do not. The practical
effect depends on cleanup guarantees and production database contents.

#### OBS-NEIGH-002 — Shared applications ignore suitability value

Any `MaterialApplication` row counts as a shared application regardless of
whether `suitability_score` is `None`, low, or potentially invalid. The intended
meaning of suitability must be established before deciding whether relationship
evidence should be weighted or filtered.

#### OBS-NEIGH-003 — Symmetric neighborhood relationships can be duplicated

Traversal appends an edge every time a current node reports a neighbor.
Symmetric relationships can consequently appear as both `A → B` and `B → A`,
and edge limiting may favor duplicates. The response's intended directed versus
undirected semantics need verification.

#### OBS-REC-001 — Stability and low energy receive bonuses in two layers

Similarity includes stability and energy-above-hull bonuses. Recommendation
starts from that similarity score and adds separate stability and low-energy
bonuses again. This may be deliberate policy emphasis, but explanations do not
provide a complete numeric contribution breakdown showing the repeated weight.

#### OBS-REC-002 — Fixed recommendation pools can truncate before policy scoring

Recommendation requests a fixed pool of 50 similarity results before applying
criticality adjustments; scenario recommendation uses the same pattern before
scenario adjustment. At current data size this may include all candidates. At
larger scale, candidates outside the upstream pool cannot enter the final top
results even if downstream policy would rank them highly.

#### OBS-PERF-FAM-001 — Family discovery scans the full material corpus

Every family request loads all material-element memberships and all other
materials, then classifies candidates in Python. This is simple and acceptable
for the prototype corpus but scales linearly per request and bypasses the
requested-material locality that a database prefilter could provide.

## Current position

This service group adds four correctness findings and two structural
performance findings. The independent audit now contains eleven `MG-IND`
findings and two `MG-PERF` findings, with latency benchmarking explicitly
deferred. No remediation has been performed and no previous audit document has
been used for comparison.

## Area 7 — Material Criticality, Risk, and Quality

### Files inspected

- `app/services/material/criticality_service.py`
- `app/services/material/risk_service.py`
- `app/services/material/quality_service.py`

Supporting implementation inspected:

- element-risk and material-element models;
- risk and criticality public schemas and routes;
- criticality focused tests;
- seed scale documentation and values;
- similarity and recommendation consumers.

### Positive observations

- Criticality preserves wholly unknown evidence as `None`.
- Criticality exposes element-count and composition-fraction coverage.
- Risk provides an evidence-aware signal distinct from its legacy numeric API.
- Quality uses the evidence-aware risk signal and requires complete risk
  evidence before granting a favorable risk bonus.
- Single and bulk criticality paths share the same response builder, and tests
  verify equivalent results.
- Criticality, risk, and quality all provide bulk retrieval paths.
- Quality uses those bulk paths when computing several materials.
- Latest risk profiles are selected deterministically by descending year.
- Unknown elements are explicitly identified in evidence-aware responses.

### Confirmed finding MG-IND-012

**Title:** Higher abundance increases criticality  
**Category:** Scientific scoring direction  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

The seed contract states:

```text
abundance_score: higher is better
```

Element criticality directly averages `abundance_score` with supply risk,
toxicity, geopolitical risk, and inverted recyclability. Unlike recyclability,
abundance is not inverted. The final mean is multiplied by ten.

Focused tests explicitly encode that an abundance score of `4` produces
criticality `40` and abundance `8` produces criticality `80`.

#### Impact

More abundant elements are treated as more critical, reversing the documented
meaning of the factor. This affects material criticality, similarity deltas,
recommendation adjustments, quality bonuses, discovery scoring, and any other
criticality consumer.

### Confirmed finding MG-IND-013

**Title:** Evidence completeness measures profile presence, not dimension completeness  
**Category:** Evidence semantics  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Both criticality and risk average whichever score dimensions are non-null. An
element is counted as known when at least one relevant dimension exists.
Material-level evidence is marked complete when every element produces a score,
without checking that each profile contains all required dimensions.

The criticality tests explicitly treat two profiles containing only
`abundance_score` as fully known, complete evidence.

#### Impact

A material can report complete evidence even when most risk dimensions are
missing. Coverage fields communicate element coverage but not dimension
coverage, so clients cannot determine whether criticality or risk scores were
computed from comparable evidence.

### Confirmed finding MG-IND-014

**Title:** Partial criticality evidence can earn a favorable quality bonus  
**Category:** Evidence-aware scoring consistency  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Quality receives only `criticality_score` from the criticality response. It
does not receive or check `criticality_evidence_complete` or criticality
coverage before awarding:

- 15% of the quality maximum when criticality is at most 30;
- 8% when criticality is at most 60.

The risk-quality bonus, in contrast, explicitly requires both known and
complete risk evidence.

#### Impact

A favorable criticality value based on one element, a small composition
fraction, or incomplete profile dimensions can increase quality. The same
quality service applies a stricter evidence rule to the closely related risk
signal, producing inconsistent missing-evidence policy.

### Confirmed finding MG-IND-015

**Title:** Public unknown material risk is represented as numeric zero  
**Category:** Public API semantics  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

When no element risk can be calculated, `get_material_risk()` returns:

```text
material_risk_score = 0.0
element_risks = []
```

The public `MaterialRiskRead` schema requires a numeric score and exposes no
`risk_known`, coverage, completeness, or unknown-element fields. The service
comments acknowledge this as backward-compatible behavior and direct newer
internal consumers to the evidence-aware signal.

#### Impact

Public clients cannot distinguish unknown risk from a genuine lowest-risk
score. Even though quality avoids this interpretation, other API consumers may
rank or display insufficient evidence as favorable risk.

### Observations under investigation

#### OBS-RISK-001 — Material risk ignores composition fractions

Material risk averages known element risk scores equally. Criticality weights
element scores by `MaterialElement.fraction`. The two signals may intentionally
measure different concepts, but no inspected contract explains why trace
elements and dominant elements should contribute equally to risk while
contributing proportionally to criticality.

#### OBS-RISK-002 — Latest-profile queries load complete history

Criticality and risk query every profile year for all involved elements, order
the rows, and retain only the first row per element in Python. As profile
history grows, database transfer and object construction grow even though only
the latest row is consumed. This is a scalability observation, not a current
bottleneck for the small history.

#### OBS-QUAL-001 — Quality combines overlapping criticality and risk evidence

Criticality already includes supply risk, toxicity, and geopolitical risk.
Quality then adds a separate risk bonus derived from those same three fields.
This may be an intentional policy emphasis, but the composite score can count
the same underlying evidence through two paths.

#### OBS-QUAL-002 — Quality cache has request-local mutable semantics

The cache is attached to a service instance and stores mutable response
dictionaries. Typical route construction makes it request-local, limiting
staleness. Long-lived composite services or caller mutation can nevertheless
reuse outdated or altered values within that instance. Actual service lifetime
and mutation patterns must be traced.

#### OBS-QUAL-003 — Stability evidence contributes through several layers

`is_stable` and energy above hull both contribute to `stability_score`, both
contribute again to `quality_score`, and earlier similarity/recommendation
layers also add stability and energy bonuses. This may reflect deliberate
multi-stage policy, but end-to-end contribution magnitude requires a complete
score provenance review.

#### OBS-RISK-003 — Legacy numeric helpers remain available internally

`get_material_risk_score()` and `get_material_risk_scores_bulk()` convert
unknown signals to zero. Comments direct new consumers away from them. A
repository-wide caller inventory is required to determine whether any active
ranking path still uses the legacy representation.

#### OBS-CRIT-001 — Invalid stored fractions can propagate into coverage and scores

Criticality trusts persisted fractions and converts falsey values to zero. The
current validated import/backfill paths provide positive finite values, but the
model itself does not enforce them. Negative, non-normalized, or non-finite data
from another writer could distort weighted scores and coverage.

## Material-service layer position

All supplied files in `app/services/material` have now been inspected.
This final group adds four correctness findings. The independent audit now
contains fifteen `MG-IND` findings and two `MG-PERF` findings. Several
cross-layer observations remain open for later discovery, research, migration,
deployment, and live-data inspection.

## Area 8 — Screening, Comparison, Scenario, Sensitivity, Substitution, and Jobs

### Files inspected

- `app/services/candidate_screening_service.py`
- `app/services/candidate_comparison_service.py`
- `app/services/scenario_policy.py`
- `app/services/scenario_ranking_service.py`
- `app/services/sensitivity_analysis_service.py`
- `app/services/substitution_analysis_service.py`
- `app/services/graph_job_service.py`

Supporting implementation inspected:

- screening, comparison, scenario, sensitivity, substitution, and job schemas;
- corresponding API routes;
- focused service tests;
- structured element-matching utility usage;
- material risk evidence-aware and legacy APIs.

### Positive observations

- Screening uses structured material-element membership.
- Risk signals are fetched in bulk before screening.
- Screening exposes risk-known, coverage, completeness, and unknown elements.
- Wholly unknown risk is not labelled as a numeric low-risk value in screening
  responses.
- Screening scores are bounded to `0–100`.
- Comparison represents exact score ties explicitly and orders tied IDs
  deterministically without inventing a winner.
- Scenario policy uses token-aware chemical element matching instead of formula
  substrings.
- Scenario explanations report component adjustments and the final net delta.
- Public routes translate missing targets and unknown preset names into explicit
  HTTP errors.
- The graph-job service matches the previously inspected model and confirms the
  already-recorded claiming and lifecycle findings; no duplicate finding is
  created here.

### Confirmed finding MG-IND-016

**Title:** Unknown risk receives a favorable screening rank  
**Category:** Missing-evidence ranking semantics  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Screening subtracts `risk_score × 5` whenever risk is known. When risk is
unknown, it applies a zero penalty. The response correctly reports unknown
evidence, but the score remains higher than an otherwise identical candidate
with any positive known risk.

Focused tests demonstrate a known risk score of `2.0` receiving a ten-point
penalty while wholly unknown risk receives no penalty.

#### Impact

Missing evidence is not described as low risk, but it is still favored
numerically in ranking. Users can receive an unknown-risk candidate above a
known-risk candidate solely because its evidence is absent.

### Confirmed finding MG-IND-017

**Title:** Scenario ranking cannot handle unknown material risk  
**Category:** Runtime correctness / evidence handling  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`CandidateScreeningResult.material_risk_score` is optional. Scenario ranking
passes it into a response field declared as a required float and, before model
validation, compares it directly with numeric thresholds:

```text
result.material_risk_score <= 2
```

No `risk_known` or `None` check is performed.

#### Impact

If a candidate passing a scenario preset has unknown risk, ranking raises a
`TypeError` instead of returning an evidence-aware result. Existing tests use
seeded known-risk materials and do not cover this path.

### Confirmed finding MG-IND-018

**Title:** Sensitivity analysis cannot handle unknown baseline risk  
**Category:** Runtime correctness / evidence handling  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Sensitivity obtains its baseline from screening, where risk may be `None`.
It passes that optional value into a function annotated as `float` and performs:

```text
baseline_risk_score * multiplier
```

The result schema also requires a numeric baseline risk score.

#### Impact

A stable target with unknown risk can pass baseline screening and then cause
sensitivity analysis to fail during arithmetic or response validation.

### Confirmed finding MG-IND-019

**Title:** Supply-risk scenario multiplier is disconnected from supply risk  
**Category:** Scenario-policy correctness  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`ScenarioPolicy.element` is never used by `ScenarioPolicyEvaluator`. When the
multiplier differs from one, the evaluator multiplies the candidate's complete
recommendation score:

```text
score = recommendation_score × supply_risk_multiplier
```

It does not check whether the candidate contains the affected element and does
not adjust a supply-risk component. A multiplier above one normally increases
the score and is reported as a final bonus.

#### Impact

A scenario described as increased supply risk can reward every candidate,
including those containing the affected element. The named affected element has
no effect unless separately repeated in avoid/prefer lists.

### Confirmed finding MG-IND-020

**Title:** Supply and geopolitical sensitivity scenarios are computationally identical  
**Category:** Sensitivity semantics  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

The sensitivity service defines four scenarios:

- supply risk +25%;
- supply risk +50%;
- geopolitical risk +25%;
- geopolitical risk +50%.

All four multiply the same aggregate `baseline_material_risk_score` and use the
same penalty formula. The two +25% scenarios always produce identical results,
as do the two +50% scenarios.

#### Impact

The output presents dimension-specific sensitivity without varying the named
risk dimension. Users can infer distinct analyses where only labels differ.

### Confirmed finding MG-IND-021

**Title:** Unknown risk is maximally favorable in substitution ranking  
**Category:** Missing-evidence ranking semantics  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Substitution uses the legacy numeric helper
`get_material_risk_score()`, which converts unknown risk to `0.0`. It then
calculates:

```text
risk_component = max(0, (10 - candidate_risk) / 10)
```

Unknown risk therefore produces the maximum `1.0` risk component. The output
schema carries only the numeric score and no evidence state.

#### Impact

Candidates lacking risk evidence gain the strongest possible low-risk ranking
contribution and can be described as having lower or similar risk relative to
the source.

### Confirmed finding MG-PERF-003

**Title:** Screening performs an element-membership N+1 query pattern  
**Category:** Performance / database access  
**Confidence:** High  
**Status:** Confirmed structurally; runtime measurement pending

#### Evidence

Screening loads the complete material table and bulk-loads risk signals, but
then calls `_get_material_element_symbols()` separately for every material.
Comparison, scenario ranking, and sensitivity all invoke this full screening
path, even when the user targets one or two materials.

#### Impact

Database round trips grow linearly with the complete material corpus. A
two-material comparison and a one-material sensitivity request still scan and
score every material.

### Confirmed finding MG-PERF-004

**Title:** Substitution performs per-candidate element and risk queries  
**Category:** Performance / database access  
**Confidence:** High  
**Status:** Confirmed structurally; runtime measurement pending

#### Evidence

Substitution loads all candidate materials and, for each one:

- queries element symbols;
- calls a single-material risk helper, which performs its own element and
  risk-profile queries.

Bulk element membership and bulk risk-signal methods are not used.

#### Impact

Query count grows by roughly three database queries per candidate, before
sorting and response construction. The endpoint will become expensive as the
materials corpus grows.

### Observations under investigation

#### OBS-SCREEN-001 — Maximum energy constraint admits unknown values

When `max_energy_above_hull` is supplied, screening excludes a material only if
its energy is known and exceeds the threshold. A material with unknown energy
passes the maximum constraint without a warning field in the result. Whether
unknown should fail a hard maximum or remain eligible requires an explicit
policy decision.

#### OBS-SCREEN-002 — Partial risk evidence receives a full-form penalty

Any `risk_known=True` signal is multiplied by the same penalty weight, even
when element or dimension coverage is incomplete. The response exposes
coverage, but the numerical confidence of the penalty is not adjusted.

#### OBS-SCREEN-003 — Exact score ties lack stable list ordering

Screening sorts only by score after loading materials without an explicit
database order. Comparison handles two-candidate ties explicitly, but screening
and scenario rank numbers can vary in presentation order among equal scores.

#### OBS-POLICY-001 — Declared custom policy weights are unused

`ScenarioPolicy` carries `penalties` and `bonuses` dictionaries, but the
evaluator always uses class constants and never reads those fields. Their
intended extension contract is unclear.

#### OBS-POLICY-002 — Scenario scores are not bounded

Unlike screening scores, scenario scores can become negative or exceed 100
after multiplication and element adjustments. This may be intentional for
relative policy scoring, but the API does not document a distinct scale.

#### OBS-SENS-001 — Sensitivity baseline is a fixed scenario

Every analysis uses stable materials, lithium scarcity, cobalt avoidance, and
an energy threshold of `0.05`. The request contains only a material ID, so users
cannot distinguish sensitivity to the chosen baseline from sensitivity
intrinsic to the material.

#### OBS-SUB-001 — Element-set similarity is described as chemistry

Substitution uses unweighted Jaccard overlap of element membership and explains
shared elements as “shares chemistry.” It does disclose introduced and removed
elements, but stoichiometry, structure, oxidation state, and synthesis
plausibility are not part of this legacy score.

#### OBS-SUB-002 — Nominally normalized substitution score can exceed one

The weighted similarity and risk components can total `1.0`, after which a
stable candidate receives another `0.05`. If callers interpret `rank_score` as
normalized, stable candidates can exceed the expected maximum.

#### OBS-API-001 — Older request schemas lack resource and domain bounds

`top_n`, element-list sizes, element symbols, and energy thresholds in these
schemas have little or no validation. Negative slicing, excessively large
requested results, invalid symbols, and extreme numeric inputs can reach
services. Full security classification depends on deployment limits and the
small current corpus.

## Top-level service position

This group adds six correctness findings and two structural performance
findings. The independent audit now contains twenty-one `MG-IND` findings and
four `MG-PERF` findings. No remediation has been performed, and earlier audit
documents remain outside the evidence set.

## Area 9 — Public Schemas, Batch 1

### Files inspected

- `app/schemas/application.py`
- `app/schemas/comparison.py`
- `app/schemas/element.py`
- `app/schemas/graph_job.py`
- `app/schemas/material.py`
- `app/schemas/material_common.py`
- `app/schemas/material_criticality.py`
- `app/schemas/material_family.py`

### Schema roles

Most models in this batch are response/serialization contracts. The direct
request boundaries are:

- `CandidateComparisonRequest`;
- `GraphJobCreate`.

This distinction matters: lack of a physical-domain validator on a response
model does not by itself mean untrusted clients can persist invalid data.

### Positive observations

- ORM-facing read models enable attribute-based validation where needed.
- Comparison result type is constrained to `"winner"` or `"tie"`.
- Criticality direction uses a shared `Literal` with explicit unknown state.
- Criticality schemas expose known/unknown status, element and fraction
  coverage, missing elements, and per-element evidence.
- Material scientific properties remain nullable rather than converting
  absence to zero.
- Graph-job status reuses the model enum.
- Graph-job JSON defaults use a factory rather than a shared mutable object.
- Comparison tie lists use factories and preserve nullable winner fields.
- Common material identity models allow the existing empty/not-found service
  representation.

### Schema conclusions

No new confirmed finding is recorded from this batch alone. Several existing
observations are strengthened, and the following boundary questions remain
open until the complete schema directory is inspected.

### Observations under investigation

#### OBS-SCHEMA-001 — Request models silently ignore unexpected fields

No inspected request model sets `extra="forbid"`. Under Pydantic's default
behavior, misspelled or obsolete fields are ignored. A comparison request with
a mistyped constraint can therefore succeed while applying defaults rather
than telling the caller that the intended policy was not used.

This may be an intentional compatibility choice. The pattern must be assessed
across all request schemas before classification.

#### OBS-SCHEMA-002 — Comparison inputs have no domain or resource bounds

Material IDs are not required to be positive; element lists have no maximum
length or symbol validation; and `max_energy_above_hull` has no finite or
nonnegative constraint. Current service logic converts lists to sets and the
corpus is small, limiting immediate impact. API-wide validation policy remains
to be established.

#### OBS-SCHEMA-003 — Graph-job creation accepts unrestricted job types

`job_type` has no minimum, maximum, enum, or supported-handler validation,
despite the database column being limited to 100 characters. Blank or oversized
values can cross the API boundary and either create unusable jobs or fail only
at database write time. This strengthens `OBS-JOB-MOD-002`.

#### OBS-SCHEMA-004 — Graph-job JSON has no shape or size contract

`input_json` accepts arbitrary nested values through `dict[str, Any]`. There is
no discriminated input model by job type or application-level payload-size
bound. This strengthens `OBS-SEC-JOB-001`; deployment request limits and worker
contracts still need inspection.

#### OBS-SCHEMA-005 — Comparison result consistency is service-enforced

The result model independently accepts comparison type, winner fields, tie
lists, and score difference. It does not enforce invariants such as:

- ties have no winner;
- winner results have empty tie lists;
- tied ID and formula lists have equal lengths;
- score difference agrees with the two scores.

The current comparison service builds coherent values, so this is a
regression-detection limitation rather than an active response defect.

#### OBS-SCHEMA-006 — Relationship taxonomies remain free-form

Family relationships and common relationship types are `list[str]`, while
criticality direction is a `Literal`. Free-form relationship values permit
spelling, casing, and vocabulary drift across family, neighbor, discovery, and
research layers. The complete relationship schema set must be inspected before
choosing a canonical representation.

#### OBS-SCHEMA-007 — Criticality coherence is not validated at serialization

Coverage values, counts, fractions, known flags, missing elements, and element
details are modeled independently without range or cross-field checks. The
current service constructs them together, but the schema would not detect
coverage outside `0–1`, negative counts, or a response marked complete while
listing unknown elements.

#### OBS-SCHEMA-008 — Common schema abstraction is only partially adopted

`ORMBase` exists, but other common material models inherit directly from
`BaseModel`, and several read schemas repeat `ConfigDict(from_attributes=True)`.
This is a maintainability observation, not a behavioral defect.

#### OBS-SCHEMA-009 — Material detail omits composition fractions

The detail schema exposes element identity only. This confirms
`OBS-MAT-007`: clients cannot inspect the composition fractions that drive
criticality and other scientific calculations through the material detail
endpoint.

## Schema-layer position

The first schema batch adds no premature finding. It records nine open
validation, consistency, taxonomy, and observability questions. The audit
totals remain twenty-one `MG-IND` findings and four `MG-PERF` findings.

## Area 9 — Public Schemas, Batch 2

### Files inspected

- `app/schemas/material_neighbor.py`
- `app/schemas/material_neighborhood.py`
- `app/schemas/material_recommendation.py`
- `app/schemas/material_risk.py`
- `app/schemas/material_similarity.py`
- `app/schemas/risk.py`
- `app/schemas/scenario_ranking.py`
- `app/schemas/screening.py`
- `app/schemas/sensitivity.py`
- `app/schemas/substitution.py`

### Contract alignment

The neighbor, neighborhood, similarity, recommendation, risk-profile, and
screening models generally match the service values inspected earlier. In
particular, screening now exposes:

- nullable aggregate risk;
- an explicit `risk_known` flag;
- profile coverage;
- known and total element counts;
- evidence completeness;
- the unknown element list.

Those fields preserve uncertainty at the screening response boundary. The
scenario-ranking, sensitivity, substitution, and legacy material-risk
contracts do not preserve the same uncertainty model.

### Existing findings strengthened

No separate finding is created for the following schema evidence because each
is part of an already confirmed service-level finding:

- `MaterialRiskRead.material_risk_score` is non-nullable. The risk service
  explicitly converts absence to `0.0` to satisfy this legacy contract. This
  strengthens `MG-IND-015`.
- `ScenarioRankingResult.material_risk_score` is non-nullable although
  `CandidateScreeningResult.material_risk_score` is nullable and the ranking
  service copies it directly. Its explanation logic also compares the value
  numerically. This strengthens `MG-IND-017`.
- `SensitivityAnalysisResult.baseline_material_risk_score` is non-nullable,
  while its screening source is nullable. The service performs arithmetic
  before constructing the response. This strengthens `MG-IND-018`.
- `SubstituteCandidate.material_risk_score` and
  `SubstitutionResult.source_risk_score` are non-nullable. The substitution
  service uses the legacy numeric helper that maps unknown risk to `0.0`.
  This strengthens `MG-IND-021`.

The evidence shows two coexisting public risk semantics: screening and
criticality contracts can represent unknown values explicitly, while older
risk-dependent contracts require a number. This is now an API-wide contract
issue rather than an isolated implementation detail.

### Positive observations

- Screening uses factories for request lists and unknown-element results,
  avoiding shared mutable defaults.
- Similarity and recommendation reuse the common material, relationship, risk,
  and criticality-direction contracts.
- Criticality direction includes an explicit `"UNKNOWN"` state.
- Neighborhood responses report both returned node and edge counts.
- Risk-profile dimensions remain nullable, preserving missing source data.
- Screening exposes enough evidence metadata for clients to distinguish an
  unknown risk score from a known score.

### Observations under investigation

#### OBS-SCHEMA-010 — Validation policy remains inconsistent across request models

`ScenarioRankingRequest`, `CandidateScreeningRequest`,
`SensitivityAnalysisRequest`, and `SubstitutionRequest` use unconstrained
primitive fields and do not reject unexpected fields. This extends
`OBS-SCHEMA-001` and `OBS-API-001` across the remainder of the currently
inspected request schemas.

Concrete accepted shapes include nonpositive material IDs, blank scenario
names, negative or arbitrarily large `top_n`, negative energy thresholds,
unbounded element lists, and unvalidated element strings. Some values produce
odd slicing semantics rather than a validation error. Runtime exposure still
depends on route and deployment controls.

#### OBS-SCHEMA-011 — Scenario names are validated after schema acceptance

`scenario_name` is a free string even though the service supports a fixed set
of three presets. Unsupported values cross validation and are rejected later
with `ValueError`. Whether clients receive a controlled 4xx response or a 500
depends on route exception handling, which has not yet been inspected.

#### OBS-SCHEMA-012 — Screening evidence fields lack coherence constraints

The screening result independently models `risk_known`, nullable score,
coverage, counts, completeness, and unknown elements. It can serialize
contradictory combinations such as a known risk with no score, coverage above
one, more known elements than total elements, or complete evidence with an
unknown-element list.

The current screening service constructs these fields coherently. This is a
contract-strength and regression-detection concern, not evidence that current
responses are contradictory.

#### OBS-SCHEMA-013 — Risk-profile values have no declared scale

Element risk-profile dimensions are nullable floats with no range metadata.
This does not establish whether the intended domain is `0–1`, `1–10`, or
another scale and therefore cannot detect the conflicting seed scales already
recorded in `MG-IND-001`.

#### OBS-SCHEMA-014 — Score domains and sensitivity vocabulary are free-form

Neighbor, similarity, recommendation, scenario, screening, substitution, and
sensitivity scores have no declared bounds or finite-number constraints.
`sensitivity_level` and sensitivity scenario names are also unrestricted
strings. Some scores may intentionally be open-ended, but the API does not
distinguish normalized, bounded, and ranking-only values.

#### OBS-SCHEMA-015 — Neighborhood graph integrity is not represented

The response independently accepts node and edge counts, node and edge lists,
depth values, and edge endpoints. It does not ensure that counts equal list
lengths or that every edge endpoint exists in the returned node set. The
current dangling-edge behavior is already confirmed as `MG-IND-011`; this
schema would serialize it without signaling partial graph semantics.

#### OBS-SCHEMA-016 — Material risk response omits evidence coverage

`MaterialRiskRead` includes a numeric aggregate and only those element risks
that could be calculated. It does not expose total element count, coverage,
unknown elements, or a known/evidence-complete flag. A response containing
`0.0` and an empty `element_risks` list therefore requires implicit client
knowledge to distinguish absent evidence from measured low risk.

This is the observability side of `MG-IND-015`, not a second finding.

#### OBS-SCHEMA-017 — Relationship vocabulary is still unconstrained

Neighbor, neighborhood, similarity, and recommendation contracts continue to
use `list[str]` for relationship types. This extends `OBS-SCHEMA-006` and
confirms that no common schema-level relationship taxonomy is used in the
material intelligence response set inspected so far.

## Schema-layer position after batch 2

This batch adds no duplicate or premature confirmed finding. It materially
strengthens four existing unknown-risk findings and adds eight contract
observations for later route and test verification. The independent audit
totals remain twenty-one `MG-IND` findings and four `MG-PERF` findings.

## Area 10 — Service Tests, Batch 1

### Files inspected

- `tests/services/test_candidate_comparison_service.py`
- `tests/services/test_candidate_screening_service.py`
- `tests/services/test_scenario_policy.py`

All three files pass Python syntax compilation. They were inspected as test
evidence; the project test suite was not executed because this batch does not
include the complete runnable project and fixtures.

### Behaviors positively protected

- Candidate comparison returns `None` when either requested candidate is not
  present in screening output.
- Exact score equality produces an explicit tie rather than an arbitrary
  winner.
- Tied candidates are ordered deterministically by material ID and remain
  independent of request order.
- Comparison preserves an unknown risk score as `None`.
- Comparison reasoning does not claim unknown risk is lower than known risk.
- Screening applies a numeric penalty when risk is known.
- Screening exposes unknown risk through `None`, `risk_known=False`, zero
  coverage, incomplete evidence, and unknown elements.
- Screening explanations do not label absent evidence as a numeric zero-risk
  observation.
- Scenario policy tests establish the current fixed avoid penalty, preferred
  element bonus, combined net delta, neutral case, and score/delta arithmetic.

The tie tests are especially useful because they protect a deterministic public
contract that is easy to regress accidentally.

### Existing findings strengthened

#### `MG-IND-016` extends through comparison

The screening tests assert that unknown risk receives no risk penalty. They
correctly protect the representation and explanation of uncertainty, but they
do not test ranking neutrality or an explicit unknown-risk policy.

The comparison test goes further: an unknown-risk candidate with score `70`
defeats a known-risk candidate with score `60`, and the expected winner is the
unknown-risk candidate. The test only verifies that the explanation does not
claim lower risk.

This confirms that the remediation represented by these tests is semantic and
observational, not ranking-neutral. Unknown risk is no longer described as
numeric low risk, but absence of a penalty can still improve rank and determine
a comparison winner. This is evidence for existing `MG-IND-016`, not a new
finding.

#### Scenario-policy gaps remain outside the protected behavior

The scenario tests do not exercise:

- `supply_risk_multiplier`;
- whether the policy's target `element` is present in the candidate;
- custom `penalties` or `bonuses`;
- duplicate or overlapping avoid/prefer elements;
- invalid, zero, negative, or extreme multipliers;
- token-boundary cases such as `C` versus `Co` or `N` versus `Na`;
- non-finite recommendation scores.

The absence of these tests does not independently prove a defect. It does mean
that `MG-IND-019`, `OBS-POLICY-001`, and `OBS-POLICY-002` are not guarded by
this suite.

### Observations under investigation

#### OBS-TEST-001 — Unknown-risk tests can imply stronger fairness than they provide

Test names emphasize that unknown risk is not “reported as low” and does not
receive a “false low-risk explanation.” Those claims are accurate, but the
same cases retain a zero penalty. The multi-candidate screening test converts
results to an ID-indexed dictionary and therefore makes no assertion about the
result order.

A future maintainer could reasonably interpret these tests as complete
coverage of unknown-risk ranking semantics even though favorable ranking
remains possible.

#### OBS-TEST-002 — Comparison winner test is weakly deterministic

The database-backed winner test accepts either material ID as the winner:
`winner_material_id in {6, 12}`. It verifies response shape and that the result
is not a tie, but it does not protect the expected scientific scoring outcome
for the fixture data.

This may be intentional if fixture risk data varies. The fixture definitions
must be inspected before deciding whether the test should assert a specific
winner and score rationale.

#### OBS-TEST-003 — Comparison unit doubles do not validate request propagation

The tie and unknown-risk comparison tests use a fake screening service that
returns a fixed list regardless of the screening request. They isolate result
construction well, but cannot detect loss or alteration of scarce elements,
avoid elements, stability, or energy constraints when comparison constructs
the downstream screening request.

#### OBS-TEST-004 — Screening tests bypass element-membership queries

The focused screening tests replace `_get_material_element_symbols` with
lambdas and use a fake risk service. This is appropriate for scoring-unit
tests, but they do not protect exact database membership, bulk-query behavior,
duplicate association handling, or `MG-PERF-003`.

#### OBS-TEST-005 — Scenario tests couple to prose formatting

Several assertions require complete reason substrings containing exact wording
and numeric formatting. They protect explainability output, but may create
friction for harmless prose changes while leaving the more consequential
multiplier semantics untested.

#### OBS-TEST-006 — Boundary and invalid-input behavior is untested

These tests instantiate schemas with valid values only. They do not exercise
the unconstrained request boundaries recorded in `OBS-SCHEMA-001`,
`OBS-SCHEMA-002`, and `OBS-SCHEMA-010`, including identical comparison IDs,
nonpositive IDs, negative thresholds, unexpected fields, or oversized element
lists.

### Test-layer position after batch 1

This test batch adds no new confirmed correctness or performance finding. It
provides useful protection for tie handling and transparent unknown-risk
responses, while confirming that favorable unknown-risk ranking remains
accepted behavior. The independent audit totals remain twenty-one `MG-IND`
findings and four `MG-PERF` findings.

## Area 10 — Service Tests, Batch 2

### Files inspected

- `tests/services/test_graph_job_service.py`
- `tests/services/test_scenario_ranking_service.py`
- `tests/services/test_sensitivity_analysis_service.py`
- `tests/services/test_substitution_analysis_service.py`

All four files pass Python syntax compilation. As with the preceding batch,
the full pytest suite was not executed because the complete project and shared
fixtures are not present in this review workspace.

### Behaviors positively protected

- Job creation persists the job type and input and initializes the job as
  `PENDING`.
- A pending job can be claimed and receives `RUNNING` status and `started_at`.
- Completion and failure persist their principal payloads and a completion
  timestamp.
- The known-fixture scenario ranking returns a nonempty, bounded list beginning
  at rank one.
- Unsupported scenario names are rejected by the service.
- Sensitivity returns four scenarios for the known fixture and returns `None`
  when the material is absent from the fixed baseline screening set.
- Substitution returns a bounded, nonempty candidate list for the known fixture
  and returns `None` for a missing source material.

### Existing findings strengthened

#### Graph-job tests do not exercise ownership under concurrency

`test_claim_next_pending_job` claims one job through one service/session. It
does not use two workers, two sessions, interleaving, row locks, or an assertion
that exactly one claimant succeeds. Consequently, the non-atomic selection and
claim sequence in `MG-IND-006` remains unprotected.

#### Graph-job tests accept unrestricted state transitions

The completion and failure tests call `complete_job` and `fail_job` directly
on newly created `PENDING` jobs. They therefore encode direct
`PENDING → COMPLETED` and `PENDING → FAILED` transitions as successful
behavior. No test rejects:

- completion or failure before claim;
- repeated completion;
- failure after completion;
- completion after failure;
- simultaneous result and error payloads;
- stale or abandoned `RUNNING` jobs.

This directly strengthens `MG-IND-007`.

#### Scenario-ranking unknown-risk path remains untested

The ranking test depends on fixture data that produces a numeric risk score. It
does not inject a screening result with `material_risk_score=None`. Therefore,
it does not exercise either the numeric explanation comparison or the
non-nullable result schema involved in `MG-IND-017`.

#### Sensitivity assertions cannot distinguish duplicated scenario mechanics

The sensitivity test asserts only that four scenario entries exist. It does not
verify scenario names, adjusted scores, deltas, ordering, monotonicity, or that
supply-risk and geopolitical-risk scenarios differ. Two pairs of
computationally identical scenarios therefore satisfy the test, leaving
`MG-IND-020` unprotected.

The test also requires a numeric baseline fixture and does not exercise a
screening result with unknown risk, so `MG-IND-018` remains unprotected.

#### Substitution unknown-risk and query-growth paths remain untested

The substitution test checks only positive similarity/rank values and list
size for one fixture. It does not cover unknown source or candidate risk,
ranking comparisons between known and unknown risk, or risk evidence in the
response. Thus `MG-IND-021` remains unprotected.

It also does not measure query count or growth with corpus size, leaving
`MG-PERF-004` outside the test contract.

### Observations under investigation

#### OBS-TEST-007 — Job lifecycle tests encode permissive transitions

These tests are not merely missing invalid-transition cases: two happy-path
tests explicitly perform terminal transitions from `PENDING`. If a stricter
state machine is introduced, the expected lifecycle in these tests must change
to create, claim, then complete or fail.

#### OBS-TEST-008 — Job terminal-state invariants are weakly asserted

Completion checks result payload and timestamp but not that `error_message` is
empty. Failure checks error and timestamp but not that `result_json` is empty.
Neither checks `started_at`, idempotency, or preservation of the original input.

#### OBS-TEST-009 — Scenario-ranking test protects shape more than ranking

The test checks only maximum length, nonemptiness, first rank, scenario name,
and a nonnegative score. It does not verify rank continuity, descending scores,
deterministic tie ordering, preset filters, risk explanations, or the identity
of expected candidates.

The unsupported-scenario test expects raw `ValueError`, reinforcing the need
to inspect whether the API route converts it into an intentional client error.

#### OBS-TEST-010 — Fixed database IDs make analytical tests fixture-dependent

Scenario, sensitivity, and substitution tests rely on specific seeded material
IDs and on the presence of eligible candidates. This gives some integration
value, but expected behavior can change silently with fixture composition while
broad shape assertions continue to pass.

#### OBS-TEST-011 — Negative and oversized result limits are not tested

Neither `top_n` request is exercised at zero, below zero, or at a large value.
This leaves the slicing behavior and request-boundary concerns in
`OBS-SCHEMA-010` untested.

### Test-layer position after batch 2

This batch adds no new confirmed finding. It increases confidence that
`MG-IND-006`, `MG-IND-007`, `MG-IND-017`, `MG-IND-018`, `MG-IND-020`,
`MG-IND-021`, and `MG-PERF-004` are not currently protected by these tests.
The job tests additionally encode part of the permissive lifecycle as expected
behavior. Totals remain twenty-one `MG-IND` findings and four `MG-PERF`
findings.

## Area 11 — Material-Service Tests

### Files inspected

- `tests/services/material/test_criticality_service.py`
- `tests/services/material/test_material_composition_service.py`
- `tests/services/material/test_material_family_service.py`
- `tests/services/material/test_material_import_service.py`
- `tests/services/material/test_material_quality_service.py`

All five files pass Python syntax compilation. The full pytest suite was not
executed because the complete project and shared fixtures are not present in
this review workspace.

### Behaviors positively protected

- Composition amounts and non-unit fractions are normalized to unit-sum atomic
  fractions.
- Empty, nonpositive, non-finite, missing-member, and unexpected-member
  composition inputs are rejected.
- Structured composition fractions survive import and are persisted on
  material-element associations.
- Materials, elements, and association rows are created, and duplicate
  Materials Project IDs are skipped.
- Criticality distinguishes wholly unknown evidence from known evidence,
  reports element and fraction coverage, excludes unknown elements from the
  numeric aggregation, and keeps bulk and single-material results consistent
  for a known fixture.
- Risk-quality bonuses require both known and complete risk evidence.
- Family explanations avoid asserting validated structural similarity merely
  from phosphate or oxide element membership.

### Existing findings strengthened

#### Criticality tests encode reversed abundance direction

`test_fully_known_criticality_evidence_is_complete` supplies only
`abundance_score` values of `4.0` and `8.0`, then expects element criticalities
of 40 and 80 and a weighted material score of 70. The test therefore actively
protects the direct, risk-increasing treatment of abundance described in
`MG-IND-012`, despite the seed-data contract describing greater abundance as
beneficial.

#### Criticality tests encode dimension-incomplete evidence as complete

The same test expects `criticality_evidence_complete is True` when each
element's profile contains only `abundance_score` and every other criticality
dimension is null. This directly strengthens `MG-IND-013`: current completeness
means that every element has at least one usable dimension, not that the
required dimensions are complete.

#### Composition and import tests expose the duplicate-membership gap

The composition unit test deliberately passes `["Li", "Li", "O"]` and verifies
that fraction resolution deduplicates membership. The import tests, however,
never pass duplicate element symbols. Import persistence still iterates over
the original element list, so the normalized input accepted by the composition
service can produce duplicate association inserts. This materially strengthens
`MG-IND-005`.

#### Quality tests leave partial-criticality bonuses protected indirectly

The quality tests correctly prevent partial or unknown *risk* evidence from
earning a favorable risk bonus. They pass only the numeric
`criticality_score`, however; neither the quality service nor its tests carry
criticality coverage or completeness into scoring. Consequently, a favorable
score derived from partial criticality evidence remains eligible for the
criticality bonus in `MG-IND-014`.

#### Magnesium family classification remains unprotected

The family classification test exercises a valid Li-to-Na alkali substitution
only. It does not test magnesium or distinguish alkali metals from alkaline
earth metals, so the chemically incorrect magnesium classification in
`MG-IND-008` remains outside the test contract.

### Observations under investigation

#### OBS-TEST-012 — Legacy unknown composition is asserted as four unit weights

Both composition and import tests explicitly require missing structured
composition for LiFePO4 to become four `1.0` association fractions. This
preserves backward compatibility but also formalizes a representation that is
indistinguishable in storage from measured/derived fraction data and does not
sum to one. The provenance and downstream interpretation concern remains open.

#### OBS-TEST-013 — Import atomicity and rollback are untested

Import tests cover successful single-candidate persistence and validation
failures before material creation. They do not exercise a failure after a
material has been flushed, a mixed batch where a later candidate fails,
rollback behavior, concurrent import of the same `mp_id`, or refresh of an
existing record.

#### OBS-TEST-014 — Criticality bulk tests protect equality, not query scaling

The bulk method is usefully checked against the single-material response and
for duplicate and missing IDs. No query-count assertion verifies that its
database work remains bounded as material count grows, and no test checks
selection of the latest profile when several profile years exist.

#### OBS-TEST-015 — Invalid persisted fractions are not exercised

Composition validation tests protect service entry points, but criticality
tests construct material-element rows directly with valid fractions only.
They do not cover negative, non-finite, zero-total, or non-normalized persisted
fractions reaching scientific aggregation.

#### OBS-TEST-016 — Quality tests use exact composite scores without component evidence

Several quality assertions require totals such as `11.7` and `13.95`. These
protect the present weighting formula but do not separately assert stability,
energy, criticality, and risk contributions. This can make a compensating
scoring error invisible if the final total remains unchanged.

#### OBS-TEST-017 — Quality bulk and cache behavior are untested

The tests cover only single-material quality retrieval and private builders.
They do not compare bulk and single results, assert bounded query counts,
exercise duplicate IDs, or test whether callers can mutate a cached dictionary
and thereby alter later responses.

### Test-layer position after material-service batch

This batch adds no new confirmed finding. It materially strengthens
`MG-IND-005`, `MG-IND-008`, `MG-IND-012`, `MG-IND-013`, and `MG-IND-014`.
Most notably, the criticality tests encode the reversed abundance direction
and dimension-incomplete evidence semantics as expected behavior. Totals remain
twenty-one `MG-IND` findings and four `MG-PERF` findings.

## Area 12 — Remaining Material-Service Tests

### Files inspected

- `tests/services/material/test_material_risk_service.py`
- `tests/services/material/test_materials_project_service.py`
- `tests/services/material/test_recommendation_service.py`
- `tests/services/material/test_similarity_service.py`

All four files pass Python syntax compilation. The full pytest suite was not
executed because the complete project and shared fixtures are not present in
this review workspace.

### Behaviors positively protected

- Evidence-aware risk signals represent missing risk as `None`, expose coverage
  and known/unknown element counts, and keep scalar and bulk results equal for
  partial element coverage.
- An element profile with no populated risk dimension is treated as unknown.
- Materials Project document normalization retains the reduced formula and
  converts stoichiometric amounts into unit-sum fractions.
- Criticality deltas propagate unknown source or candidate criticality as
  `None`, and direction labels distinguish lower, higher, same, and unknown
  criticality.
- Recommendation-score explanations remain numerically aligned with the
  criticality adjustment, stability and low-energy contributions exercised by
  the tests.
- When lower criticality is not a scoring preference, the recommendation
  explanation correctly labels criticality as contextual rather than as a
  score contribution.

### Existing findings strengthened

#### Public unknown-risk fallback remains outside the risk tests

The risk tests concentrate on `get_material_risk_signal()` and its bulk
equivalent, where unknown evidence is represented correctly. They never call
the public `get_material_risk()` response for a material whose elements lack
risk evidence. Consequently, they do not expose the numeric `0.0` fallback and
missing coverage metadata described by `MG-IND-015`.

The tests also characterize a profile with one available risk dimension as
calculable. This is consistent with the present element-level calculation, but
no assertion distinguishes dimension completeness from element coverage.

#### Similarity pipeline defects are not exercised

The similarity tests call only `_calculate_criticality_delta()` and
`_criticality_direction()`. No test calls `get_similar_materials()`.
Therefore:

- truncating neighbors before final similarity scoring remains unprotected
  (`MG-IND-009`);
- treating unknown criticality delta like zero during tie sorting remains
  unprotected (`MG-IND-010`);
- per-candidate criticality queries remain unmeasured (`MG-PERF-001`).

The helper tests correctly establish the representation of unknown criticality,
but they do not test how that representation affects ranking.

#### Recommendation tests do not protect candidate-pool completeness

Recommendation tests operate on hand-built dictionaries and private scoring
and explanation helpers. They never call `get_recommendations()`. They
therefore cannot detect whether the upstream similarity pool already excluded
a candidate that would receive a higher final recommendation score. This
extends the practical impact of `MG-IND-009` into recommendations without
creating a separate finding.

### Observations under investigation

#### OBS-TEST-018 — Risk weighting is tested only with equal fractions

The partial-coverage risk fixture stores four equal `0.25` fractions, and the
scalar/bulk parity fixture stores two equal `0.5` fractions. Neither case can
distinguish composition-weighted aggregation from the current equal average
over known elements. The open scientific-weighting concern therefore remains
untested.

#### OBS-TEST-019 — Risk profile history and legacy numeric helpers are untested

No risk test creates multiple years for an element, so latest-profile selection
is not protected. The backward-compatible `get_material_risk_score()` and
`get_material_risk_scores_bulk()` methods are also untested for wholly unknown
evidence, even though they convert unknown to `0.0`.

#### OBS-TEST-020 — Materials Project testing covers normalization only

The Materials Project test provides a well-formed fake document and calls
`_normalize_doc()` directly. It does not exercise:

- `fetch_materials()` request construction or result limits;
- zero, negative, or excessive limits;
- malformed or partially populated external documents;
- API exceptions, timeouts, retries, or pagination/truncation behavior;
- empty or invalid chemical-system strings.

This is not evidence that those behaviors are defective, but the external
ingestion boundary has only a happy-path normalization contract.

#### OBS-TEST-021 — Unknown criticality is explicitly score-neutral in recommendations

The recommendation tests expect a candidate with unknown criticality to retain
its full similarity score, while known higher criticality is penalized. In a
mixed ranking this can place unknown evidence ahead of known unfavorable
evidence. That may be an intentional policy, but the tests do not assert an
evidence-aware tie break or explanation of the uncertainty. This remains an
observation pending broader product-policy review.

#### OBS-TEST-022 — Recommendation ordering and bounds are untested

No test exercises final sorting, exact ties, deterministic secondary ordering,
zero/negative/oversized limits, missing source materials, the fixed
recommendation pool of 50, or scenario recommendations. Exact reason strings
protect transparency but are coupled tightly to presentation wording.

### Test-layer position after the remaining material-service tests

This batch adds no new confirmed finding. It materially strengthens
`MG-IND-009`, `MG-IND-010`, `MG-IND-015`, and `MG-PERF-001`, and shows that
the downstream recommendation pipeline does not independently protect itself
from an incomplete similarity candidate pool. Totals remain twenty-one
`MG-IND` findings and four `MG-PERF` findings.

## Shared utility review — `app/utils/chemical_formula.py`

### Scope and role

This utility provides three small operations:

- extracting distinct element-like tokens from a formula;
- checking exact token membership rather than substring membership;
- validating the shape of a single element symbol.

It is deliberately lightweight and does not parse stoichiometry, nesting,
charges, phases, isotopes, or validate symbols against the periodic table.

### Positive controls

- `extract_elements(None)` and `extract_elements("")` return an empty set.
- Formula membership is token-based. For example, `N` is not reported as an
  element of `NaFePO4`.
- Common formulas with coefficients and parentheses, such as `LiFePO4` and
  `Na3Fe(PO4)2`, yield the expected distinct symbols.
- Returning a set is appropriate for membership questions and removes repeated
  occurrences without claiming to preserve stoichiometric quantities.
- The anchored symbol-shape expression rejects lowercase, whitespace,
  numeric suffixes, and symbols longer than two letters.

### Observations under investigation

#### OBS-UTIL-001 — Token extraction is syntactic rather than chemical validation

The regular expression accepts any capital letter followed by an optional
lowercase letter. It therefore accepts nonexistent element-like tokens such as
`Xx`, and malformed text can yield apparently valid tokens:

- `Xx2O` produces `{"Xx", "O"}`;
- `NotAFormula` produces `{"No", "A", "Fo"}`.

Conversely, lowercase input such as `co2` produces no elements. This is not a
defect if all formulas entering the utility have already been canonicalized
and validated by a trusted source. It can become a data-integrity or policy
bypass problem if API input, legacy data, or free-form formulas reach it
directly. Caller and schema tracing is required before classification.

#### OBS-UTIL-002 — Element-symbol validation checks shape, not existence

`is_valid_element_symbol("Xx")` returns true because the function validates
only capitalization and length. Its name can reasonably be read as validating
a real chemical element, while its implementation validates lexical form
only. Whether this is misleading or harmful depends on whether callers also
check the `Element` table or an authoritative periodic-table set.

#### OBS-UTIL-003 — `None` is considered a valid element symbol

The validator returns true for `None`. This may be intentional for optional
query parameters, but it combines optionality with domain validation. A caller
that uses the function as a standalone validity predicate may therefore accept
absence as a valid symbol. Caller contracts must be inspected before deciding
whether this is a defect.

#### OBS-UTIL-004 — Extraction provides membership, not composition semantics

Because coefficients are discarded and results are deduplicated, the utility
cannot support stoichiometric weighting, formula equivalence, normalized
composition, or atom-count comparison. That is appropriate for exact
membership checks, but downstream scientific logic must not treat its output
as a parsed composition.

### Utility-layer position

No new confirmed finding is justified from this isolated utility file. The
observed behavior is suitable for trusted, canonical formula membership, but
its safety depends on caller-side validation and on downstream code respecting
the difference between token membership and chemical composition. These
questions will be traced while reviewing discovery and research services.
Totals remain twenty-one `MG-IND` findings and four `MG-PERF` findings.

## Area 13 — Discovery Candidates, Chains, Edges, Algorithms, and Analytics

### Scope

This pass reviewed:

- `candidate_service.py`;
- `chain_service.py`;
- `edge_intelligence_service.py`;
- `explanation_service.py`;
- `graph_algorithms_service.py`;
- `graph_analytics_service.py`.

The services were evaluated as one dependency path from candidate aggregation
through transition intelligence, bounded traversal, path search, and
NetworkX-based analytics. Services referenced by these files but not supplied
in this batch remain outside the present evidence boundary.

### Positive controls

- Candidate ordering has a deterministic material-ID tie break.
- Candidate element constraints prefer persisted exact membership and use
  formula tokenization only as a fallback.
- Candidate source merging preserves a single base-score breakdown and
  recomputes the source-diversity contribution rather than repeatedly adding
  it.
- Chain search prevents cycles within a path and uses bounded expansion,
  maximum-hop, and result limits.
- Chain cache keys include the normalized avoid/prefer objective.
- Breadth-first unweighted path search correctly treats hop count as the path
  objective.
- Weighted edges are converted to positive costs, preventing negative-cycle
  behavior.
- Community element summaries use the exact `elements` collection attached to
  graph nodes rather than formula substrings.
- Community material lists and IDs are explicitly sorted.
- Candidate explanations include an explicit warning that deterministic
  suggestions still require structural, synthesis, and application
  validation.

### Confirmed finding MG-IND-022

**Title:** Discovery-chain `max_hops` behaves as an exact required depth and
silently discards valid shorter chains

**Evidence**

`_build_chains()` appends a chain only when:

- the dequeued chain has already reached `max_hops`; or
- a newly added transition makes its length exactly `max_hops`.

If a non-base chain has no valid next candidate before that depth, it is
discarded. A valid one-hop chain is therefore absent from a request with
`max_hops=2` unless it can be extended to a second hop. For positive
`max_hops`, the result is effectively an exact-depth chain search despite the
public parameter being named and reported as a maximum.

**Impact**

- Valid shorter discovery paths can disappear when callers increase the
  maximum search depth.
- Sparse or dead-end regions may return no chain even though a valid path was
  found.
- The response does not represent all paths of length `1..max_hops`, which is
  the normal contract implied by a maximum-hop parameter.

**Classification:** Confirmed discovery-correctness finding.

### Confirmed finding MG-IND-023

**Title:** Hop-bounded weighted shortest path prunes valid shallower states by
tracking cost only per material

**Evidence**

`weighted_shortest_path()` records `best_costs[next_id]` using only the
material ID. Under a hop constraint, search state must also include the depth
or remaining hop budget. A cheaper arrival at a node can consume more hops
than a costlier arrival.

A direct counterexample was reproduced against the implemented state rule:

- a cheap three-hop path reaches intermediate node `X` at the depth limit;
- a more expensive two-hop path reaches the same `X`;
- `X -> target` would make the second path a valid three-hop result;
- the costlier two-hop state is rejected because `best_costs[X]` already
  contains the cheaper three-hop cost;
- the method reports no path even though a bounded path exists.

**Impact**

- `path_found` can be false for a reachable target.
- Even when a path is found, cost-only dominance is not valid for the
  constrained shortest-path problem and can exclude the actual best feasible
  path.

**Classification:** Confirmed graph-algorithm correctness finding.

### Confirmed finding MG-IND-024

**Title:** Edge-score saturation erases intended framework and plausibility
distinctions

**Evidence**

The edge score begins at `scientific_plausibility * 100`, adds up to:

- `10` for preserving both phosphorus and oxygen;
- another `5` for preserving oxygen;
- `5` for having both removed and introduced elements;

and then caps the result at `100`.

Consequently:

- every `alkali_substitution` receives `100` before any evidence bonuses,
  including one with no supplied framework or element changes;
- a `shared_element_continuity` edge with P/O preservation and a two-sided
  element change also becomes `100`;
- the nominal bonuses cannot distinguish strong edges once the base score is
  sufficiently high.

The separate plausibility field retains some information, but graph analytics
uses the saturated `edge_score` as the NetworkX relationship weight.

**Impact**

- Distinct evidence profiles collapse to identical graph strength.
- Framework-preservation bonuses frequently have no effect.
- Modularity analysis and average edge-strength summaries can treat
  scientifically different transitions as equivalent.

**Classification:** Confirmed scoring/analytics correctness finding.

### Observations under investigation

#### OBS-DISC-001 — Preferred elements are required at every chain expansion

`_get_next_candidates()` filters each next-hop candidate unless it contains at
least one preferred element. This prevents paths whose intermediate material
does not yet contain a preferred element but whose endpoint introduces it.
Whether preference is intended as a per-hop hard constraint or an endpoint
objective must be checked against discovery schemas, routes, and objective
services.

#### OBS-DISC-002 — Avoided elements do not similarly restrict expansion

Avoid elements participate in transition validation but do not filter the
candidate list in `_get_next_candidates()`. This asymmetry may be intentional:
removing an avoided element can be a gradual objective. The contract should
state clearly whether avoid/prefer inputs are filters, endpoint objectives, or
ranking signals.

#### OBS-DISC-003 — Expansion order truncates the family list before path-level ranking

Chain expansion takes the first six eligible family results and stops. No
path-level score is calculated before this cutoff. The completeness and
ordering implications depend on `MaterialFamilyService` ordering and later
path-ranking services, so classification is deferred.

#### OBS-DISC-004 — Candidate explanations merge evidence from non-selected score sources

When the same material is produced by multiple pipelines, the service keeps
the greatest base score and its score breakdown, but unions all paths and
explanation parts. The resulting narrative can therefore mention a
recommendation, scenario, or family rationale whose numeric score was not the
selected base score. This may be acceptable as provenance, but the response
does not distinguish “source evidence” from “score contribution.”

#### OBS-DISC-005 — Scenario candidates inherit the existing scenario-policy semantics

Candidate generation invokes scenario recommendations with
`supply_risk_multiplier=1.0` and chooses `avoid_element` ahead of
`prefer_element` as the single scenario element. This layer does not repair
the element-insensitive policy behavior already confirmed in `MG-IND-019`.
The effect of supplying both avoid and prefer elements requires route and
objective-service tracing.

#### OBS-DISC-006 — Formula-token fallback can elevate malformed persisted data

Both candidate and chain services use `extract_elements()` when a material has
no persisted composition membership. The utility review established that this
is lexical tokenization rather than chemical validation. Trusted canonical
formulas are safe for membership use, but malformed or noncanonical legacy
formulas could influence avoid/prefer behavior.

#### OBS-DISC-007 — Analytics converts missing node features to numeric zero

`_build_node_features()` converts falsey or missing stability, criticality,
risk, and quality values to `0.0`. This removes the distinction between
unknown evidence and genuine zero. Community averages directly include the
resulting quality value. The graph builder must be reviewed to determine
which fields can actually be absent and whether separate evidence metadata
exists.

#### OBS-DISC-008 — Analytics discards edge direction and can overwrite parallel edges

Discovery graph data is loaded into `nx.Graph`, not `DiGraph` or
`MultiGraph`. Opposite-direction edges become one undirected relationship,
and repeated edges for a pair overwrite attributes. This may be intentional
for similarity-style community analysis, but it differs from directed
discovery traversal. The graph builder and public analytics contract must
establish which meaning is intended.

#### OBS-DISC-009 — Centrality semantics are unweighted while community partitioning is weighted

Degree, betweenness, and closeness centrality ignore `edge_score`; greedy
modularity uses it as relationship strength. This can be a deliberate mix of
topological and weighted analysis, but the API labels do not expose that
choice. A weighted betweenness/closeness calculation would also require
converting strength to distance rather than using the score directly.

#### OBS-DISC-010 — Equal-score analytics ordering is only partially deterministic

Centrality and importance results sort only by the calculated score.
Community ordering sorts only by size, and dominant features sort only by
frequency. Stable insertion order may currently make results repeatable, but
no explicit secondary identity ordering protects exact ties.

#### OBS-DISC-011 — Analytics recomputes expensive centralities within each request

`material_importance()` computes degree, betweenness, and closeness once each.
Both community methods compute the same three measures again for community
summaries after building the graph. This is structurally costly, especially
betweenness centrality, but graph construction limits and realistic graph
sizes must be inspected before assigning a performance finding.

### Discovery-service position after this batch

This batch adds three confirmed correctness findings:
`MG-IND-022`, `MG-IND-023`, and `MG-IND-024`. It also establishes several
cross-service questions for the graph builder, scoring, transition,
objective, schema, route, and test reviews.

The independent audit now contains twenty-four `MG-IND` findings and four
`MG-PERF` findings. No remediation was performed.

## Area 12 — Discovery Graph Construction, K-Best Paths, and Ranking

### Files inspected

- `app/services/discovery/graph_builder.py`
- `app/services/discovery/k_best_path_service.py`
- `app/services/discovery/path_ranking_service.py`
- `app/services/discovery/scoring_service.py`

Supporting implementation and evidence inspected:

- transition validation and edge-intelligence behavior from the preceding
  discovery-service batch;
- material-quality score construction and its declared `15.0` maximum;
- candidate, family, and graph-algorithm interactions already present in the
  evidence set.

All four supplied files passed Python syntax compilation.

### Confirmed finding MG-IND-025

**Title:** K-best paths bypass canonical transition validation

**Evidence**

`DiscoveryGraphBuilder.build_graph()` constructs each candidate edge through
`_build_transition()`, which calls
`DiscoveryTransitionValidator.validate_transition()`. A candidate for which
validation returns `None` does not become an edge.

`DiscoveryKBestPathService`, however, calls
`DiscoveryGraphBuilder.build_adjacency()`. That adjacency method stores every
returned discovery candidate and never calls the transition validator. K-best
enumeration then treats each candidate relation as a traversable edge.
`_transitions_for_path()` reconstructs a transition from candidate
`substitution_path` metadata or infers a type from `discovery_path`; it does
not perform the omitted validation.

This is especially material because graph-builder candidate retrieval sets
`include_substitution_paths=False`. K-best therefore commonly relies on
provenance-label inference rather than the canonical transition result.

**Impact**

- K-best and K-shortest endpoints can return paths containing edges that the
  canonical discovery graph rejects.
- The same source/target pair can have different validity depending on which
  discovery endpoint is called.
- Scientific usefulness can be calculated for a transition that has not
  passed the project's transition rules.

**Classification:** Confirmed cross-service path-validity finding.

### Confirmed finding MG-IND-026

**Title:** Rejected transition candidates remain as disconnected graph nodes

**Evidence**

Within `build_graph()`, each candidate is converted to a node and immediately
written to `nodes_by_id` before `_build_transition()` is called. When
transition validation returns `None`, processing continues without creating
an edge, but the node is not removed.

The resulting graph response can therefore contain a material that was only a
candidate proposal, not a validated graph neighbor and not reachable through
any returned edge.

**Impact**

- Node counts and node-level analytics can include rejected candidates.
- Clients cannot infer that every non-root node belongs to a validated
  discovery path.
- Isolated rejected nodes can be mistaken for valid graph members.

**Classification:** Confirmed graph-integrity finding.

### Confirmed finding MG-IND-027

**Title:** K-best path material metadata can be taken from the wrong incoming
edge

**Evidence**

`_materials_for_path()` resolves every non-root material through
`_find_candidate_by_id()`. That helper searches all adjacency lists and
returns the first candidate with the requested material ID; it does not use
the actual preceding source ID in the enumerated path.

A material can appear as a candidate of more than one source with different
source-relative `discovery_score`, `discovery_path`, and `explanation`
metadata. For a path using `B -> C`, the material entry for `C` can therefore
be copied from an earlier `A -> C` candidate record. Transition construction,
by contrast, correctly looks up the `(source_id, target_id)` pair.

**Impact**

- A returned path can combine transition data for one edge with candidate
  score, provenance, and explanation data from another edge.
- Path explanations and per-material discovery scores may not describe the
  path actually ranked.

**Classification:** Confirmed path-response provenance finding.

### Confirmed finding MG-PERF-005

**Title:** K-best search enumerates every simple path before applying `k`

**Evidence**

`INTERNAL_PATH_LIMIT = 100` is declared but never read.
`_enumerate_simple_paths()` performs breadth-first enumeration of all simple
paths up to `max_hops`, stores every target-reaching path, and has no early
termination or internal cap. Every enumerated path is then materialized,
queried for bulk quality through the ranking service, ranked, sorted, and only
afterward sliced to `[:k]`.

Graph expansion is capped to six candidates per expanded material, but the
number of simple paths remains exponential in depth. `k` bounds only response
length; it does not bound graph construction, path enumeration, memory use,
ranking calls, or database work.

**Impact**

- Increasing `max_hops` can cause exponential CPU and memory growth even when
  the caller requests one result.
- `total_path_count` requires exhaustive enumeration, preventing a genuinely
  bounded K-best implementation.
- The unused internal-limit constant creates a false impression that search
  work is capped.

**Classification:** Confirmed structural scalability finding; runtime latency
benchmarking remains deferred.

### Observations under investigation

#### OBS-DISC-012 — Public graph depth and path-search depth use different guards

`build_graph()` silently caps ordinary graph construction to
`MAX_ALLOWED_DEPTH = 1`, while `build_adjacency()` applies the caller's
`max_depth` without that production guard. K-best defaults to two hops and can
therefore traverse a larger graph than the ordinary graph endpoint. Route
schemas and documentation must establish whether this is deliberate endpoint
policy or an inconsistent safety boundary.

#### OBS-DISC-013 — Graph construction loads element membership for the full corpus

`_get_material_elements_map()` loads every material-element membership row
before bounded traversal starts. This avoids per-node membership queries but
makes a small depth-one graph request scale with the entire database. Realistic
dataset size and endpoint frequency are needed before classifying it as a
bottleneck.

#### OBS-DISC-014 — Graph construction repeats family discovery per expanded node

Relationship validation calls `get_material_families()` once for each expanded
source and caches only within one builder instance. Candidate generation also
does its own work for the same source. This may duplicate full-corpus family
scans already observed in the material-service layer. Query measurement is
needed before assigning a separate performance finding.

#### OBS-DISC-015 — K-best ties have no explicit identity-based ordering

K-best sorting uses only scientific usefulness. K-shortest sorting uses only
hop count and usefulness. Exact ties inherit enumeration and adjacency
insertion order rather than an explicit path-ID tuple, so deterministic output
depends on upstream ordering.

#### OBS-DISC-016 — Path efficiency stops distinguishing paths after two hops

Efficiency grants `10` points for one hop, `7.5` for two hops, and `5` for
every path of three or more hops. If larger hop limits are exposed, paths of
substantially different length receive the same efficiency contribution.
Whether this is intentional coarse policy should be established from research
requirements.

#### OBS-DISC-017 — Material quality is averaged across the complete path

Path quality averages all material-quality values, including the starting
material and intermediates. This can reward a path whose endpoint has lower
quality or penalize a useful endpoint because of its starting material.
The calculation is internally bounded correctly: the apparent concern that
the 15-point weight was ignored was closed after verifying that
`MaterialQualityService.QUALITY_SCORE_MAX` itself is `15.0`.

#### OBS-DISC-018 — Source-diversity reward has no explicit maximum

`calculate_source_diversity_bonus()` adds ten points for every source beyond
the first. Current source vocabularies may impose a small practical ceiling,
but the scoring service itself does not cap the bonus or declare the allowed
source set. This remains a score-contract observation pending candidate-source
and schema review.

### Discovery-service position after this batch

This batch adds three confirmed correctness findings—`MG-IND-025`,
`MG-IND-026`, and `MG-IND-027`—and one structural performance finding,
`MG-PERF-005`.

The independent audit now contains twenty-seven `MG-IND` findings and five
`MG-PERF` findings. No remediation was performed.

## Area 13 — Discovery Substitution, Transition Validation, Traversal, and Warnings

### Files inspected

- `app/services/discovery/substitution_path_service.py`
- `app/services/discovery/transition_validator.py`
- `app/services/discovery/traversal_service.py`
- `app/services/discovery/warning_service.py`

Supporting implementation and evidence inspected:

- discovery candidate construction and warning invocation;
- chain transition construction;
- graph-builder node, edge, depth, and validation behavior;
- path-ranking inputs and empty-path response contract.

All four supplied files passed Python syntax compilation.

### Confirmed finding MG-IND-028

**Title:** Discovery graph reports requested depth instead of its silently
capped effective depth

**Evidence**

`DiscoveryTraversalService.get_graph()` passes the caller's `max_hops` to
`DiscoveryGraphBuilder.build_graph()` and echoes that original value in
`graph_goal.max_hops`.

For ordinary graph construction, however, the builder calculates
`min(max_depth, MAX_ALLOWED_DEPTH)`, where `MAX_ALLOWED_DEPTH = 1`. A request
for two or three hops is therefore executed at one hop while the response
still reports the larger requested value. The traversal service neither
normalizes the response value nor exposes an effective-depth field or warning.

**Impact**

- Clients can interpret a one-hop graph as an exhaustive graph through the
  reported two- or three-hop depth.
- Empty or missing deeper paths can be mistaken for negative discovery
  evidence rather than a production safety cap.
- The same parameter has materially different effective behavior across graph,
  chain, and K-best services without being visible in the graph response.

**Classification:** Confirmed API/service contract and completeness finding.

### Confirmed finding MG-IND-029

**Title:** Discovery graph limits nodes and edges independently, producing
dangling edges

**Evidence**

`get_graph()` returns `graph["nodes"][:limit]` and
`graph["edges"][:limit]` independently. Graph-builder node ordering always
places the root first, followed by material ID; edge ordering begins with hop
depth and source/target IDs.

For example, with `limit=1`, the response contains only the root node but can
also contain the first outgoing edge. The target of that edge is necessarily
absent from the returned node list. More generally, there is no post-slice
referential-integrity check.

**Impact**

- Discovery graph responses can violate their own node/edge integrity.
- Clients constructing a graph can fail to resolve an edge endpoint.
- Counts, visualizations, and downstream graph computations can become
  inconsistent merely by changing the response limit.

This is the discovery-graph manifestation of the limiting pattern already
confirmed for material neighborhoods in `MG-IND-011`; it is recorded
separately because it affects a different public service and implementation.

**Classification:** Confirmed discovery graph-integrity finding.

### Confirmed finding MG-IND-030

**Title:** Subgraph filters are applied after the source graph has already been
truncated

**Evidence**

`get_subgraph()` first calls `get_graph(..., limit=limit)`. That call has
already sliced both nodes and edges. Only afterward does the service apply
`family`, `transition_type`, `min_edge_score`, and `min_quality_score`
filters.

Consequently, a qualifying edge or node positioned beyond the initial
unfiltered slice can never appear, even if fewer than `limit` matching results
are returned. The later `nodes[:limit]` and `edges[:limit]` do not recover the
discarded candidates.

**Impact**

- Filtered subgraphs are not the top bounded subset of all matching graph
  entries; they are the matching subset of an arbitrary earlier slice.
- A response can be empty even though the built graph contains qualifying
  transitions.
- Results depend on graph-builder ordering rather than solely on the requested
  scientific filters.

**Classification:** Confirmed filtering/completeness finding.

### Confirmed finding MG-IND-031

**Title:** Discovery path lookup ignores `max_hops` and searches only direct
edges

**Evidence**

`DiscoveryTraversalService.get_path()` accepts `max_hops`, but the value is
never used. It always calls:

```python
self.graph_builder.build_graph(..., max_depth=1)
```

It then checks only edges whose source is the requested base material and
whose target is the requested target material. There is no traversal,
predecessor reconstruction, or multi-edge path search in this method.

A valid two-hop path therefore returns `path_found=False` even when the caller
requests `max_hops=2` or more.

**Impact**

- The path service cannot fulfill its multi-hop parameter contract.
- Direct-path and K-best endpoints can disagree on reachability for the same
  materials and constraints.
- Callers receive an ordinary no-path response with no indication that the
  requested depth was ignored.

**Classification:** Confirmed path-search correctness finding.

### Observations under investigation

#### OBS-DISC-019 — Magnesium remains classified as an alkali element

`DiscoverySubstitutionPathService.ALKALI_ELEMENTS` contains `Mg`. Both
substitution-path construction and transition reasoning can therefore label
magnesium changes as alkali substitution. This directly strengthens
`MG-IND-008`; it is not a duplicate new finding.

#### OBS-DISC-020 — Transition-metal substitution inference is masked by
validator precedence

The substitution-path service can infer `transition_metal_substitution`.
Transition validation, however, requires at least one strong relationship.
Every strong relationship that can make this inference reachable is selected
earlier by `_select_transition_type()` as either `alkali_substitution` or
`family_expansion`. The substitution path's transition-metal type therefore
does not normally become the canonical validated transition type.

Candidate responses can still expose the substitution-path classification,
while graph transitions can expose `family_expansion` for the same pair.
Schemas, routes, tests, and intended taxonomy must be inspected before
classifying this as a separate correctness defect.

#### OBS-DISC-021 — Avoid constraints prohibit only newly introduced elements

Transition validation rejects an avoided element only when it exists in the
target and not the source. It permits an avoided element to persist from one
hop to the next. This may deliberately support gradual paths that remove the
element later; objective and research services must establish whether
intermediate persistence is allowed and whether endpoint satisfaction is
reported separately.

#### OBS-DISC-022 — Preferred elements affect explanation but not transition
validity

The validator uses preferred elements only to append an explanation when a
preferred element is newly introduced. It does not require preferred-element
presence or introduction. Candidate and chain services may enforce stronger
rules upstream, but direct validator semantics are weaker and require
cross-endpoint verification.

#### OBS-DISC-023 — Warning membership inherits tokenizer trust assumptions

The warning service checks formula membership through
`contains_element()` rather than normalized material-element membership.
This avoids substring errors but inherits the utility-layer behavior for
malformed formulas and lexically valid nonexistent symbols. The practical
impact depends on request element validation and formula-source guarantees.

#### OBS-DISC-024 — Unknown scores are converted to zero in subgraph filtering
and metadata

Subgraph quality and edge filtering use `(value or 0.0)`, and averages also
replace missing values with zero. This makes missing evidence
indistinguishable from measured zero in subgraph eligibility and summaries.
The relevant schemas and quality/edge contracts must be checked before
deciding whether those fields can actually be absent in a valid graph.

### Discovery-service position after this batch

This batch adds four confirmed correctness findings—`MG-IND-028` through
`MG-IND-031`. It strengthens the existing magnesium finding and leaves
transition-taxonomy, constraint, warning, and missing-score semantics for
schema, route, and test verification.

The independent audit now contains thirty-one `MG-IND` findings and five
`MG-PERF` findings. No remediation was performed.

## Area 13 — Final Discovery and Research Schemas

### Files reviewed

- `app/schemas/discovery.py`
- `app/schemas/discovery_graph.py`
- `app/schemas/research_objective_exploration.py`

### Positive controls

- Chain and research-objective depth is bounded to one through three hops.
- Chain, objective, and exploration response limits are bounded to one through
  twenty where they are represented in request models.
- Exploration mode rejects values outside `balanced`, `exploratory`, and
  `strict`.
- Mutable collection defaults commonly use `Field(default_factory=...)`.
- Unknown graph node risk, criticality, energy, stability, and quality values
  remain nullable rather than being forced to zero by these schemas.
- Objective satisfaction separately exposes path-wide and endpoint-specific
  coverage, status, and interpretation.
- Top-ranking status uses a closed literal vocabulary.

### Confirmed finding MG-IND-032

**Title:** Scientific pathway response validation can be bypassed by arbitrary
dictionaries and untyped pathway collections

**Evidence**

`ScientificPathwayAnalysisResponse.pathway_comparison` is declared as:

```python
PathwayComparison | dict
```

The unrestricted `dict` union branch accepts `{}` or any unrelated dictionary,
even though `PathwayComparison` requires `decision_boundary` and defines the
structured ranking, evidence, comparison, and decision fields.

`ScientificPathway.materials` and `ScientificPathway.transitions` are also
declared as bare `list` values. They therefore accept unrelated scalars,
arbitrary dictionaries, and heterogeneous entries instead of enforcing the
material and transition contracts already available in the discovery schema.

A focused Pydantic validation check confirmed that `{}`, `{"unexpected": 1}`,
and a dictionary with an invalid structured-field type all select the raw
dictionary union branch successfully. Bare pathway lists similarly accepted
mixed strings, integers, nulls, and arbitrary dictionaries.

**Impact**

- Malformed or incomplete research comparisons can pass FastAPI response
  validation and be returned with a successful status.
- The generated OpenAPI contract cannot reliably describe pathway materials,
  transitions, or comparison structures.
- Clients cannot depend on fields such as comparison status, decision boundary,
  endpoint material, or pairwise comparison shape being present or typed.
- Cross-service regressions can silently weaken the research response instead
  of failing at the public contract boundary.

**Classification:** Confirmed public response-contract integrity finding.

### Schema evidence strengthening existing findings

- `DiscoveryGraphGoal.max_hops` has no schema-level effective-depth distinction
  or warning. It serializes the requested value supplied by the service even
  when graph execution is capped to one hop, strengthening `MG-IND-028`.
- `DiscoveryGraphResponse` and `DiscoverySubgraphResponse` have no coherence
  validation requiring every edge source and target to exist in `nodes`.
  Dangling responses from `MG-IND-029` therefore serialize normally.
- `DiscoveryPathResponse` can truthfully encode `path_found=False`, but exposes
  neither requested/effective depth nor a limitation warning. It cannot reveal
  that `max_hops` was ignored in `MG-IND-031`.
- The schema cannot repair post-truncation filtering from `MG-IND-030`; no
  pre-filter total, truncation indicator, or completeness warning is exposed.

### Observations under investigation

#### OBS-SCHEMA-018 — Research-objective element inputs are unbounded and unvalidated

`avoid_elements`, `prefer_elements`, and `preserve_elements` accept arbitrary,
duplicate, empty, lexically invalid, or nonexistent strings, with no collection
size bounds. Singular discovery goal elements have the same symbol-validation
gap. This extends `OBS-SCHEMA-010` and the formula-utility trust concern.
Routes and services must establish whether they normalize or reject these
values and whether list size materially amplifies work.

#### OBS-SCHEMA-019 — Scientific vocabularies remain mostly free-form

Transition types, families, preservation bases, quality levels, confidence
levels, evidence readiness, objective statuses, sources, and derivation labels
are predominantly plain strings. Exploration mode and top-ranking status are
exceptions. This extends `OBS-SCHEMA-006`, `014`, and `017`; taxonomy drift
must be checked against service outputs and API documentation.

#### OBS-SCHEMA-020 — Score, coverage, rank, and count coherence is not enforced

Coverage fields, plausibility, edge scores, scientific usefulness, quality
summaries, ranks, positions, counts, density, degree, and priorities have no
domain bounds or cross-field checks. Examples such as `path_found=False` with
nonempty transitions, `hop_count` inconsistent with the transition count,
coverage outside zero-to-one, or a community count inconsistent with the list
would serialize. Current service construction and tests must be reviewed before
classifying concrete reachable inconsistencies.

#### OBS-SCHEMA-021 — Discovery result score structures remain open dictionaries

Discovery score breakdowns, scientific facts' material quality records,
endpoint-sensitive rankings, and most comparative research structures use
untyped dictionaries. This reduces OpenAPI precision and regression detection.
The unrestricted top-level comparison bypass is separately confirmed as
`MG-IND-032`; these nested dictionaries remain an architectural observation
pending service-contract review.

#### OBS-SCHEMA-022 — Mutable defaults are stylistically inconsistent but safe under Pydantic

Several list fields use `=[]` while others use `Field(default_factory=list)`.
Pydantic copies mutable defaults per model instance, so no shared-list defect
is established. Standardizing the style would improve clarity without changing
the present behavior.

### Final schema-layer position

The final discovery/research schema batch adds one confirmed finding,
`MG-IND-032`. It also confirms that response validation does not detect the
effective-depth, dangling-edge, post-truncation filtering, or ignored path-depth
conditions already found in the discovery services.

The independent audit now contains thirty-two `MG-IND` findings and five
`MG-PERF` findings. No remediation was performed.

## Area 14 — Initial Discovery-Service Tests

### Files reviewed

- `tests/services/discovery/test_candidate_service.py`
- `tests/services/discovery/test_discovery_chain_element_membership.py`
- `tests/services/discovery/test_discovery_chain_service.py`
- `tests/services/discovery/test_discovery_edge_intelligence_service.py`
- `tests/services/discovery/test_discovery_graph_algorithms_service.py`

### Positive controls

- Candidate merge tests repeatedly verify that the published discovery score
  equals the sum of its published score-breakdown components.
- Candidate merge tests distinguish the winning base score from the
  source-diversity bonus and prevent repeated encounters from the same source
  from increasing that bonus.
- A later discovery source can populate missing substitution-path evidence.
- Exact normalized membership prevents `N` from matching `Na`.
- Unknown preferred-element membership is not treated as a positive match.
- Database-backed chain tests check cycle avoidance, transition reasons,
  framework list shape, bounded output depth, and the missing-material
  response.
- Basic BFS and DFS tests ensure the starting material appears first in the
  traversal order.

### Test evidence strengthening confirmed findings

#### MG-IND-022 — Exact-depth chain behavior is not detected

The chain depth test asserts only that every returned chain has
`hop_count <= max_hops` and at most that many transitions. Exact-depth output
therefore satisfies the test. The suite does not construct a graph containing
both a valid shorter chain and a longer chain and require both to be returned,
nor does it require a valid dead end below the depth limit to survive.

The tests can therefore pass while `max_hops` continues to behave as an exact
required output depth.

#### MG-IND-023 — Hop-bounded weighted-path state loss is unprotected

The weighted-shortest-path test runs one database fixture with `max_depth=1`
and checks only the algorithm name, IDs, and presence of `path_found`, `path`,
and `path_cost`. It does not require a path to exist and cannot exercise the
confirmed counterexample involving two arrivals at the same node with
different costs and remaining hop budgets.

No synthetic adjacency test protects the necessary state distinction by both
material and hop depth.

#### MG-IND-024 — Edge-score saturation is explicitly encoded as expected

The edge-intelligence test requires an alkali-substitution example with three
preserved framework elements to have:

```python
assert result["scientific_plausibility"] == 1.0
assert result["edge_score"] == 100.0
```

This actively preserves the capped value responsible for the finding. The
tests compare only three isolated examples (`100`, `90`, and `50`); they do
not compare two materially different high-evidence transitions that both
saturate at `100`, nor verify that downstream analytics retains their intended
ordering.

### Candidate-merge provenance observation strengthened

`test_losing_source_still_contributes_contextual_paths_and_explanations`
explicitly requires a losing source's discovery path and explanation to remain
in the merged candidate while the winning source alone supplies the retained
base score breakdown. This guarantees score/breakdown arithmetic consistency,
but it also formalizes the possibility that displayed explanations describe
evidence that did not produce the retained score.

The tests do not expose source attribution beside each explanation fragment or
distinguish scoring evidence from contextual evidence. This strengthens the
existing candidate-provenance observation without establishing a separate
defect.

### Important coverage gaps

- Candidate tests bypass construction and database retrieval with `__new__`
  and call the private `_upsert_candidate()` helper directly. They do not
  exercise complete candidate generation, final ordering, limits, warnings,
  evidence retrieval, or query growth.
- Source-diversity tests cover three sources and therefore do not test the
  previously observed uncapped bonus when more source types are accepted.
- Exact base-score ties preserve the first encountered breakdown, but the tests
  do not vary encounter order or require source-independent deterministic
  provenance.
- Chain tests do not assert that any chain is returned. Their loop assertions
  pass vacuously when `chains` is empty.
- The chain tests do not require shorter valid chains, dead ends, or preferred
  elements introduced only at a later hop.
- The element-membership tests use a supplied normalized `elements_map`; they
  do not exercise malformed formulas, nonexistent requested symbols, or the
  formula-token fallback.
- Graph-algorithm shortest-path tests validate response shape rather than path
  correctness, hop count, endpoints, edge validity, or cost optimality.
- No test in this batch covers K-best validation bypass, exhaustive path
  enumeration, disconnected rejected nodes, wrong incoming-edge metadata,
  traversal depth reporting, dangling graph edges, post-truncation subgraph
  filtering, ignored multi-hop path lookup, or permissive research response
  validation (`MG-IND-025` through `MG-IND-032` and `MG-PERF-005`).
- Boundary and invalid-input behavior for zero, negative, or excessive depth
  and limits is absent from this batch.

### Test execution position

All five supplied files passed Python syntax compilation. The complete pytest
suite and its project fixture environment were not available in this review
workspace, so no claim is made that the tests execute successfully against the
full application.

No distinct new production finding is justified by this test batch. It
materially strengthens `MG-IND-022`, `MG-IND-023`, and `MG-IND-024`, and
strengthens the existing candidate explanation/provenance observation.

## Final audit conclusion

The implementation review is complete. It confirmed 44 `MG-IND` findings and
5 `MG-PERF` findings. No remediation was performed as part of this independent
review.

On 2026-07-26, all 49 findings were reconciled against the existing `MG-AUD`
register:

- 9 were classified as duplicates or broadenings of existing findings;
- 40 were accepted as distinct canonical findings;
- the canonical register therefore expanded from 54 to 94 findings.

This audit remains the evidence source for the independent IDs. Current
statuses, priorities, remediation decisions, and verification results belong
in `MaterialGraph_Architecture_Implementation_Audit_v2_Regenerated.md`.

## Area 22 — API Routes: Risks, Scenario Ranking, Screening, Sensitivity, and Substitutions

### Scope

Reviewed:

- `app/api/v1/routes/risks.py`
- `app/api/v1/routes/scenario_ranking.py`
- `app/api/v1/routes/screening.py`
- `app/api/v1/routes/sensitivity.py`
- `app/api/v1/routes/substitutions.py`

This pass traced the final route batch through the previously inspected
request/response schemas and services. It examined request bounds, response
validation, missing-target behavior, exception translation, unknown-risk
semantics, pagination, and publicly reachable query growth. The supplied
files were reviewed without changing project code.

### MG-IND-044 — Legacy analytical endpoints accept invalid result limits

**Category:** API request correctness / resource bounds  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`ScenarioRankingRequest.top_n` and `SubstitutionRequest.top_n` are unconstrained
integers. The corresponding public routes accept these models unchanged and
the services apply the values directly as Python slice bounds:

```text
results[: request.top_n]
ranked[: request.top_n]
```

A negative value is therefore not rejected. For example, `top_n=-1` returns
every eligible result except the final one, which is not a meaningful
"top N" contract. Zero silently produces an empty result, and arbitrarily
large values are also accepted.

The screening request is similarly unconstrained: its element lists have no
length or symbol validation, and `max_energy_above_hull` has no finite,
nonnegative domain bound. Unlike the bounded `limit` parameters on newer
material and discovery routes, none of the three POST route functions adds a
route-level validation dependency.

#### Impact

Malformed requests produce successful but semantically surprising analytical
responses instead of a consistent validation error. Arbitrarily large result
limits can also expose the complete ranked corpus, while unbounded screening
constraint lists expand the work and request surface of an endpoint that
already scans all materials.

#### Recommended correction

Declare shared bounded fields in the request schemas: require `top_n` within a
documented positive range, require positive material IDs, constrain energy
thresholds to finite nonnegative values, bound element-list lengths, and
validate every element against the canonical periodic-table symbol set. Reject
invalid requests consistently through Pydantic with `422` responses.

### Existing findings exposed at the route boundary

- Scenario ranking catches an unsupported preset's `ValueError` and translates
  it to `400`, but it does not handle the nullable risk failure in
  `MG-IND-017`. A candidate with unknown risk can still trigger an unhandled
  numeric comparison error.
- Sensitivity returns `404` whenever its service returns `None`, but that state
  means the target was absent from the fixed baseline screening result—not
  necessarily that the material does not exist. This retains the baseline and
  unknown-risk problems in `MG-IND-018` and `OBS-SENS-001`.
- Substitution provides a clear missing-source `404`, but it continues to
  expose the favorable legacy unknown-risk semantics in `MG-IND-021`.
- Screening, scenario ranking, and sensitivity publicly expose the full-corpus
  scan and per-material membership-query pattern in `MG-PERF-003`.
- Substitution publicly exposes the per-candidate element and risk query growth
  in `MG-PERF-004`.

These are route-level confirmations of existing findings, not duplicate new
findings.

### Route behavior that is comparatively sound

- Every route in this batch declares a response model.
- Element-risk listing constrains `limit` to `1..100`, requires a nonnegative
  offset, and orders by year descending and unique ID ascending.
- Missing element-risk profiles return an explicit `404`.
- Unknown scenario presets are translated to a controlled `400` response.
- Missing substitution sources return an explicit `404`.
- The sensitivity and substitution routes pass their structured request
  objects directly to the corresponding services without silently dropping
  fields.

### Additional route observations

- The sensitivity route's `404` detail says the material was not found "under
  baseline screening constraints." This is more accurate than saying the
  database row is absent, but `404` still conflates resource existence with
  analytical ineligibility. A successful response with eligibility state, or a
  domain-specific client status, would make the distinction clearer.
- Screening performs no route-level exception translation. Expected validation
  belongs in its schema; unexpected database and service failures currently
  depend on the absent global exception layer.
- Risk-profile response fields preserve nullable source dimensions, which is
  appropriate, but their numeric ranges and cross-field semantics remain
  unconstrained as recorded during schema review.
- Exact screening and scenario score ties inherit database encounter order.
  The routes do not add deterministic secondary ordering, retaining
  `OBS-SCREEN-003`.

### Verification position

All five supplied route files passed Python syntax compilation. The complete
application and database fixture environment were not available together in
this review workspace, so the endpoints were not executed end to end.

This final route batch adds one finding. The current independent-audit total is
forty-four `MG-IND` findings and five `MG-PERF` findings. No remediation was
performed.

## Area 21 — API Routes: Materials, Families, Intelligence, Risks, and Research

### Scope

Reviewed:

- `app/api/v1/routes/material_families.py`
- `app/api/v1/routes/material_neighbors.py`
- `app/api/v1/routes/material_risks.py`
- `app/api/v1/routes/materials.py`
- `app/api/v1/routes/research.py`

This pass traced route inputs, service delegation, response models, not-found
translation, pagination and result bounds, and the public exposure of the
previously reviewed research services. The supplied files were reviewed
without changing project code.

### MG-IND-043 — Public element-symbol validation accepts nonexistent elements

**Category:** API input correctness / scientific constraint validation  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

The scenario-recommendation endpoint describes `element`, `avoid_element`, and
`prefer_element` as valid chemical symbols and explicitly rejects values when
`is_valid_element_symbol()` returns false.

The previously reviewed utility validates only lexical shape. It accepts any
uppercase letter optionally followed by one lowercase letter; it does not
check membership in the periodic table. Consequently, a value such as `Xx`
passes both the route's length constraints and its explicit validation, then
reaches `MaterialRecommendationService.get_scenario_recommendations()`.

The research endpoint likewise accepts `ResearchObjectiveChainRequest`
unchanged. The earlier schema review established that its objective element
lists do not validate periodic-table membership, so nonexistent symbols can
also enter scientific pathway analysis through the public API.

#### Impact

The API communicates a stronger validation guarantee than it enforces.
Nonsensical element constraints can be accepted as successful research or
recommendation requests, influencing warnings, matching, scoring, and
explanations instead of producing a request-validation error. This converts
the earlier utility-layer trust observation into confirmed public behavior.

#### Recommended correction

Use one canonical periodic-table-backed element type for scalar query
parameters and objective lists. Keep optionality separate from validity,
normalize case only under an explicit policy, and reject unknown symbols with a
consistent `422` response across material-intelligence, discovery, scenario,
and research endpoints.

### Existing findings exposed at the route boundary

- The scientific-pathways route declares
  `ScientificPathwayAnalysisResponse`, but that schema still permits the
  bypasses recorded in `MG-IND-032`; the route adds no stronger response
  validation.
- The route returns `ScientificPathwayAnalysisService.analyze()` directly, so
  target-family endpoint mismatch (`MG-IND-036`), explicit-empty membership
  fallback (`MG-IND-037`), contradictory evidence readiness (`MG-IND-038`),
  and explanation provenance errors (`MG-IND-039`) are public response
  behaviors rather than internal-only concerns.
- The neighborhood route bounds depth to `1..2` and limit to `1..100`, but
  response validation does not repair the dangling-edge behavior already
  confirmed in `MG-IND-011`.
- Similarity and recommendation routes pass their bounded limits directly to
  services, but response limits do not correct pre-score truncation
  (`MG-IND-009`) or favorable unknown-criticality tie ordering
  (`MG-IND-010`).

These are extensions of existing findings, not duplicate route findings.

### Route behavior that is comparatively well bounded

- Every route in this batch declares a response model.
- Material listing constrains `limit` to `1..100`, constrains `offset` to
  nonnegative values, and orders by the unique internal material ID.
- Similarity and recommendation limits are constrained to `1..50`.
- Neighborhood depth and response size are explicitly bounded.
- Scenario risk multipliers are constrained to `0..10`.
- Material, detail, family, neighbor, similarity, neighborhood, criticality,
  recommendation, scenario-recommendation, and material-risk handlers all
  perform an explicit or shared missing-material check.
- Basic material, detail, and risk lookups return explicit `404` responses
  rather than an empty successful payload.

### Additional route observations

- `POST /materials/{material_id}/research/scientific-pathways` performs no
  route-level existence check and translates no domain exception. Its missing-
  material status therefore depends entirely on the research service and
  global exception behavior, unlike every other material-specific route in
  this batch.
- Research objective element lists remain unbounded in count at the schema and
  route boundaries. Together with the absence of global request-size and rate
  controls and the exhaustive K-best behavior in `MG-PERF-005`, this warrants
  endpoint load testing before public deployment, but the supplied route alone
  does not establish a measured performance defect.
- Material IDs are unconstrained integers. Zero and negative values normally
  become ordinary not-found lookups, so this is contract looseness rather than
  a demonstrated correctness defect.
- Family, neighbor, criticality, recommendation, and research handlers do not
  translate expected service/domain errors beyond missing-material handling;
  database and service failures continue to depend on the absent global
  exception layer noted during application-composition review.
- The material-detail handler constructs its schema from
  `material.__dict__`. Pydantic's normal extra-field handling prevents the
  SQLAlchemy state field from entering the declared response, but explicit
  field mapping would make the boundary less dependent on model configuration.

### Verification position

All five supplied route files passed Python syntax compilation. The complete
application, schemas, service dependencies, and database fixture environment
were not present together in this review workspace, so the endpoints were not
executed end to end.

This route batch adds one finding. The current independent-audit total is
forty-three `MG-IND` findings and five `MG-PERF` findings. No remediation was
performed.

## Area 20 — API Routes: Applications, Comparison, Discovery, Elements, Graph Jobs, and Health

### Scope

Reviewed:

- `app/api/v1/routes/applications.py`
- `app/api/v1/routes/comparison.py`
- `app/api/v1/routes/discovery.py`
- `app/api/v1/routes/elements.py`
- `app/api/v1/routes/graph_jobs.py`
- `app/api/v1/routes/health.py`

This pass examined request validation, parameter propagation, response-model
enforcement, status handling, database dependency use, pagination, and the
security boundary established by the previously reviewed application
composition. The supplied files were reviewed without changing project code.

### MG-IND-040 — Equivalent discovery element inputs have inconsistent route validation

**Evidence**

The candidates, subgraph, connected-community, and modularity-community routes
declare both `avoid_element` and `prefer_element` with:

- minimum length `1`; and
- maximum length `3`.

The chains, graph, and path routes expose the same conceptual parameters as
plain optional strings, without these constraints. Those values are forwarded
unchanged into `DiscoveryChainService` or `DiscoveryTraversalService`.

The length-constrained routes still do not validate membership in the periodic
table, so this finding is about route parity rather than complete chemical
validation.

**Impact**

The API accepts or rejects the same research constraint depending on the
selected endpoint. Empty strings and arbitrarily long values can reach shared
discovery logic through chains, graph, and path even though sibling endpoints
return request-validation errors for them. This produces an inconsistent
public contract and expands the formula-token trust concern already recorded
for the utility and service layers.

**Recommended correction**

Use one reusable element-symbol request type or dependency across every
discovery route. Validate canonical chemical symbols, normalize whitespace and
case under an explicit policy, and preserve `None` separately from invalid
input.

### MG-IND-041 — Discovery community endpoints bypass response-contract validation

**Evidence**

`GET /materials/{material_id}/discovery/communities/connected` and
`GET /materials/{material_id}/discovery/communities/modularity` declare no
`response_model`. Their raw service return values are therefore serialized
without a route-level schema. This differs from the candidates, chains,
objective, graph, subgraph, and path endpoints in the same module.

**Impact**

Malformed, incomplete, or accidentally expanded analytics output can be
returned with a successful status instead of being caught at the API boundary.
Internal fields added later can also become public unintentionally. The absence
of a model prevents OpenAPI from expressing a reliable analytics response
contract and leaves counts, scores, community membership, and graph coherence
unchecked.

**Recommended correction**

Define explicit connected-community and modularity-community response schemas,
including bounds and cross-field invariants where practical, and attach them as
route response models.

### MG-IND-042 — Graph-job mutation and global job history lack an application authorization boundary

**Evidence**

The graph-job router exposes:

- unauthenticated `POST /graph-jobs`;
- unauthenticated paginated `GET /graph-jobs`; and
- unauthenticated `GET /graph-jobs/{job_id}`.

The previously reviewed `app/main.py` and API composition install no global
authentication or authorization dependency. The list query is global rather
than owner-scoped, and the job records are returned through the complete
`GraphJobRead` model. UUID identifiers make opportunistic detail guessing
harder but do not protect the list endpoint, and they do not authorize job
creation.

**Impact**

At the application boundary currently present in the reviewed code, any caller
can submit graph work and enumerate job history. This creates resource-abuse,
operational-metadata disclosure, and cross-user isolation risks if the API is
reachable by more than one trusted caller. An external gateway could reduce
the deployment exposure, but no such control exists in the reviewed
application layer.

**Recommended correction**

Require an authenticated principal for graph-job routes, apply create/read
authorization and owner or tenant scoping, add submission rate/quota controls,
and expose only fields required by the caller. Retain infrastructure controls
as defence in depth rather than the sole authorization mechanism.

### Route behavior that is comparatively well bounded

- Application and element list routes constrain `limit` to `1..100`, constrain
  `offset` to nonnegative values, provide deterministic primary ordering, and
  return explicit `404` responses for missing IDs.
- Candidate comparison declares a structured response model and translates the
  service's not-found result to `404`.
- Graph-job IDs are parsed as UUIDs at the route boundary, so malformed IDs
  receive framework validation errors before reaching the service.
- The versioned health response is small and does not query the database or
  disclose the environment label.
- Discovery depth and result limits are bounded at the route layer, although
  earlier service findings show that some limits do not constrain effective
  work or are not honoured semantically.

### Additional route observations

- Candidate lookup alone translates a missing material through
  `result["mp_id"] is None`; the other discovery routes depend entirely on
  service-specific missing-material behavior. End-to-end route tests should
  verify consistent `404` semantics.
- `family` and `transition_type` subgraph filters are unrestricted free-form
  strings, reinforcing the earlier schema-vocabulary observation.
- The community routes use `max_depth`, while neighboring discovery routes use
  `max_hops`; both are propagated directly, but the public terminology remains
  inconsistent.
- None of these routes translates expected domain exceptions other than
  explicit not-found cases. Service/database failures will depend on global
  exception behavior, which was also absent from the reviewed composition
  layer.
- Offset pagination has no stable secondary key in the application and element
  queries. If names or symbols are not unique at the database level, equal
  values could make page boundaries unstable; the reviewed routes alone do not
  establish that precondition.

### Verification position

All six supplied route files passed Python syntax compilation. The complete
application, schemas, service dependencies, and database fixture environment
were not present together in this review workspace, so the endpoints were not
executed end to end.

This route batch adds three findings. The current independent-audit total is
forty-two `MG-IND` findings and five `MG-PERF` findings. No remediation was
performed.

## Area 19 — Application and API-v1 Composition

### Files inspected

- `app/main.py`
- `app/api/v1/api.py`
- `app/api/v1/route_utils.py`

Supporting contracts inspected:

- application settings and release metadata previously reviewed in Area 2;
- material identity schemas and the persisted material model;
- the existing API-router inventory.

### Finding position

No new confirmed finding is justified by these three composition files.

This pass reconfirms `MG-IND-004`: `Settings.project_version` exists, but
`FastAPI(version=...)` hard-codes `"1.0.0"` instead of consuming the setting.
The application metadata therefore remains a separate version authority.

It also reconfirms `OBS-CFG-005`: the root, unauthenticated `/health` response
returns the configured environment label.

### Positive controls

- The versioned API has one explicit composition root and one `/api/v1`
  prefix.
- Every router imported by `app/api/v1/api.py` is included exactly once in
  that file.
- Application startup and shutdown use FastAPI's lifespan mechanism rather
  than deprecated startup/shutdown decorators.
- The root health endpoint is asynchronous, side-effect free, and does not
  perform a database query.
- `ensure_material_found()` emits a consistent `404` and public error message
  for its current missing-result sentinel.

### Observations under investigation

#### OBS-API-COMP-001 — Global API security policy is absent from composition

The FastAPI application and aggregate `APIRouter` declare no global
authentication/authorization dependency, rate limiter, trusted-host
middleware, HTTPS redirect, or request-size policy. FastAPI's documentation and
OpenAPI endpoints are also left at their enabled defaults.

These absences establish that the application-composition layer does not
provide those controls. They are not yet classified as a vulnerability because
individual route dependencies and the Nginx/network deployment boundary have
not been reviewed. CORS is likewise absent, but CORS is a browser-origin policy
and its absence should not be treated as API authentication.

#### OBS-API-COMP-002 — No application-wide exception translation is defined

`app/main.py` registers no application-wide exception handlers. Unhandled
service or database exceptions therefore use FastAPI's default failure
behavior unless individual routes translate them. Route review must determine
whether expected domain failures receive coherent status codes and whether any
responses or logs expose sensitive details.

#### OBS-API-COMP-003 — Material existence is inferred from one response field

`ensure_material_found(result)` treats `result["mp_id"] is None` as equivalent
to a missing material rather than checking an explicit not-found result or
material identifier. The current persisted `Material.mp_id` contract is
non-null, so a false `404` is not established for ordinary database-backed
materials. However, the shared `MaterialIdentity` response contract allows
`mp_id=None`, and the helper accepts any dictionary. Caller review must verify
that every service uses `mp_id=None` exclusively as its not-found sentinel and
never returns a valid local/non-Materials-Project record without an `mp_id`.

#### OBS-API-COMP-004 — Health semantics are duplicated across API roots

The application defines `/health` and the aggregate router also registers a
versioned health router under `/api/v1`. The supplied files do not show whether
both endpoints return equivalent semantics or are intentionally split into
liveness and readiness checks. The health route and deployment probes should
be reviewed together to prevent divergent operational signals.

#### OBS-API-COMP-005 — Router behavior cannot be validated from aggregation

The aggregate router shows registration order and inclusion, but not each
router's prefix, tags, dependencies, operation IDs, or path declarations.
Duplicate final paths, conflicting parameter routes, missing response models,
and inconsistent security cannot be determined from this file alone. Those
questions belong to the route-by-route endpoint pass.

### Test execution position

All three supplied files passed Python syntax compilation. No full application
import was attempted because the attached review workspace does not contain the
complete package tree required by their imports.

No new `MG-IND` or `MG-PERF` finding is added. The independent audit remains at
thirty-nine `MG-IND` findings and five `MG-PERF` findings. No remediation was
performed.

## Area 18 — Remaining Research Services

### Files inspected

- `app/services/research/objective_service.py`
- `app/services/research/research_evidence_intelligence_service.py`
- `app/services/research/scientific_pathway_analysis_service.py`

Supporting implementations cross-checked:

- `DiscoveryChainService`
- `DiscoveryPathRankingService`
- `MaterialQualityService`
- the previously reviewed endpoint-sensitive and comparative research
  services;
- the exact-element utility and discovery path-ranking semantics; and
- the scientific-pathway response contract.

### Confirmed finding MG-IND-036

**Title:** Target-family filtering accepts chains whose endpoint does not match the target family  
**Category:** Research-objective correctness / endpoint semantics  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`ResearchObjectiveService._matches_target_family()` accepts a chain when any
transition contains the target text in its transition type or reason. For the
special `"phosphate"` case, it accepts the chain when any transition shares
`P` and `O`.

The method does not inspect the final material's family or require the target
family to remain true at the endpoint. A multi-hop chain can therefore pass
because an early transition is phosphate-related even when a later transition
ends outside that target family. Free-text reason substring matching further
makes eligibility depend on narrative wording rather than structured endpoint
classification.

#### Impact

A research objective specifying a target family can return and rank a pathway
whose final candidate does not belong to that family. The response provides no
field identifying which transition satisfied the filter, so a consumer can
reasonably interpret the endpoint as satisfying the requested family.

#### Follow-up verification

- Establish whether `target_family` is an endpoint constraint, a path-wide
  continuity constraint, or merely a requirement that the path touch the
  family.
- Use structured endpoint family membership instead of transition-reason
  substring matching.
- Add a multi-hop test that enters the requested family and then leaves it.

### Confirmed finding MG-IND-037

**Title:** Scientific analysis reparses explicitly empty endpoint membership and can contradict path ranking  
**Category:** Cross-service objective correctness / evidence provenance  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`ScientificPathwayAnalysisService._endpoint_elements()` uses:

```python
structured_elements = endpoint.get("elements")
if structured_elements:
    return sorted(set(structured_elements))
```

An explicitly present empty list is false, so the method falls back to parsing
`formula` or `pretty_formula`. The previously reviewed
`DiscoveryPathRankingService` deliberately treats a present structured
`elements` field, including an empty list, as authoritative and does not
replace it with formula-derived membership.

For an endpoint such as `{"elements": [], "formula": "NaFePO4"}`, discovery
path ranking has no canonical endpoint membership and awards no preferred-Na
endpoint credit, while scientific pathway analysis infers `Na` from the
formula and reports that endpoint objective as satisfied.

#### Impact

The same successful research response can combine a score produced under one
endpoint-evidence rule with an objective-satisfaction explanation produced
under another. Formula tokenization can convert explicitly empty structured
evidence into apparently known element membership.

#### Follow-up verification

- Distinguish field absence from an explicitly empty structured list.
- Reuse one canonical endpoint-membership resolver across discovery and
  research services.
- Test absent, `None`, empty, and populated structured membership separately.

### Confirmed finding MG-IND-038

**Title:** Evidence readiness can be labelled strong while every declared external evidence category is missing  
**Category:** Research evidence communication / scientific overstatement  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`build_evidence_summary()` always returns five missing-evidence categories:
experimental synthesis, electrochemical performance, scientific literature,
DFT validation, and manufacturing feasibility.

`_evidence_readiness()` receives only `supporting_signals` and
`weak_assumptions`; it does not receive or evaluate `missing_evidence`. It
returns `"strong"` when at least five deterministic signals and at most two
weak assumptions exist. Shared-element overlap, removed elements, introduced
elements, score thresholds, and material quality can meet that threshold while
all five external evidence categories remain absent.

#### Impact

The same evidence summary can state that all major empirical and external
validation sources are unavailable while presenting generic
`evidence_readiness` as `"strong"`. Without a qualifier limiting readiness to
deterministic graph evidence, clients can overinterpret research maturity.

#### Follow-up verification

- Define whether readiness measures deterministic signal completeness,
  experimental readiness, or overall research evidence maturity.
- Incorporate missing-evidence severity or rename and qualify the field.
- Test the maximum deterministic-signal case with all external evidence
  missing.

### Confirmed finding MG-IND-039

**Title:** Scientific explanations mislabel shared-element continuity as transition plausibility  
**Category:** Explanation correctness / score provenance  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

Two methods use the `shared_element_continuity` component to make a statement
about transition plausibility:

- `_strengths()` appends `"Transition plausibility score is strong."` when
  `shared_element_continuity >= 15`;
- `_confidence()` appends `"Transition plausibility is strong..."` under the
  same continuity threshold.

`transition_plausibility` is a separate score-breakdown component and the
evidence-intelligence service correctly checks that component directly.
Therefore, a pathway can have high shared-element continuity and low or absent
transition-plausibility credit while both strengths and confidence reasons
claim strong transition plausibility.

#### Impact

Research-facing narratives can attribute confidence to evidence that did not
produce it. This weakens the otherwise explicit distinction between
compositional overlap and encoded transition plausibility.

#### Follow-up verification

- Check `transition_plausibility` for plausibility statements.
- Keep shared-element continuity statements limited to compositional
  continuity and the existing structural-preservation disclaimer.
- Add a test with high continuity and zero transition plausibility.

### Observations under investigation

#### OBS-RES-007 — Target-family matching uses unrestricted free text

Outside the phosphate shortcut, target-family eligibility can be triggered by
the target substring appearing anywhere in a transition reason. Invalid or
ambiguous target-family strings are not rejected at this service boundary.
Route and schema review should establish the supported family vocabulary and
whether free-text fallback is intentional.

#### OBS-RES-008 — Pathway identity omits materials without IDs

`_build_pathway_id()` silently skips material entries whose `material_id` is
missing. With the permissive scientific-pathway response structures already
recorded in `MG-IND-032`, malformed pathways can collide with shorter valid
identities. Normal service-generated chains appear to contain IDs, so the
production impact depends on whether malformed upstream data can reach this
method.

#### OBS-RES-009 — Quality cache lifetime is not scoped to one analysis

The service-level `_quality_cache` is updated during prefetch but is not cleared
at the start of `analyze()`. A reused service instance can retain old material
quality after database changes. Typical per-request construction may make this
irrelevant; route dependency lifetime must be inspected before classification.

#### OBS-RES-010 — Readiness is based on signal count rather than independence

Removed and introduced elements, objective alignment, transition
plausibility, continuity, and quality are counted as separate signals without
accounting for common upstream derivation. Beyond `MG-IND-038`, the readiness
threshold therefore measures count rather than source diversity or evidence
independence.

#### OBS-RES-011 — Generic strengths can exceed the stated objective

Any removed elements are described as avoided or replaced, and any introduced
elements as target or alternative elements, without intersecting them with the
requested objective. The statements may be intended as broad pathway
descriptions, but route/test review should confirm that clients do not read
them as objective-specific claims.

### Positive controls

- Required preserved elements are intersected across every transition rather
  than accepted from only one hop.
- Path-wide removal/introduction events and final-endpoint objective
  satisfaction are represented separately.
- Multi-element objective coverage is deterministic, order-independent, and
  exposes matched and unmatched elements.
- Shared-element continuity is explicitly labelled as element overlap and
  structural preservation remains `False`.
- Pathway IDs are stable for ordinary chains containing material IDs.
- Material quality is bulk-prefetched, avoiding a per-opportunity quality
  query pattern within one analysis.
- Missing experimental, literature, DFT, performance, and manufacturing
  evidence is stated explicitly, with researcher actions.
- The final response preserves a clear researcher decision boundary.

### Test execution position

All three supplied files passed Python syntax compilation. Focused static and
in-memory counterexamples establish the endpoint-membership inconsistency,
target-family endpoint failure, readiness contradiction, and score-to-
explanation mismatch. The complete application test suite and database-backed
research pipeline were not available in this review workspace.

This batch adds `MG-IND-036`, `MG-IND-037`, `MG-IND-038`, and `MG-IND-039`.
No new performance finding is confirmed. The independent audit now contains
thirty-nine `MG-IND` findings and five `MG-PERF` findings. No remediation was
performed.

## Area 13 — Research Services: Objective Exploration and Comparative Ranking

### Files inspected

- `app/services/research/objective_exploration_service.py`
- `app/services/research/endpoint_sensitive_research_ranking_service.py`
- `app/services/research/comparative_research_intelligence_service.py`

Supporting contracts inspected:

- `app/schemas/research_objective_exploration.py`
- the previously reviewed discovery objective, path-ranking, quality, and
  scientific-pathway response contracts.

### Confirmed finding MG-IND-033

**Title:** Strict research exploration does not enforce its declared hard constraints  
**Category:** Research-objective correctness / contract fidelity  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`ResearchObjectiveExplorationService` describes strict mode as using explicit
hard constraints and states in its candidate warning that a retained avoided
element should be treated as a hard rejection.

The implementation does not reject that candidate. `_score_material()` merely
subtracts 25 points, `_build_candidate_warnings()` adds a warning, and
`_rank_candidates_from_chains()` retains the candidate in the ranked result.
The request schema accepts `"strict"` as a first-class mode and the response
does not distinguish candidates that failed a hard constraint.

#### Impact

A client selecting strict mode can receive and potentially prioritize a
candidate that violates an explicit avoidance constraint. The response's
warning acknowledges the violation but does not make the ranked result conform
to the mode's declared semantics.

#### Follow-up verification

- Inspect research routes and endpoint documentation for the promised strict
  mode contract.
- Check research tests for retained avoided elements in strict mode.
- Establish whether strict mode should reject only endpoint violations or any
  violation along the complete pathway.

### Confirmed finding MG-IND-034

**Title:** Intermediate research candidates receive evidence from later transitions  
**Category:** Research ranking correctness / pathway provenance  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

`_rank_candidates_from_chains()` iterates through every intermediate and
endpoint material in `materials[1:]`, but passes the complete chain-wide
`transitions` list to `_score_material()` and `_build_reasons()` for every one
of those materials.

The scoring method awards continuity, alkali-substitution, and target-family
points once per transition. Consequently, a material reached after the first
hop can receive points and explanations from second- or later-hop transitions
that occur only after that material. The same later evidence is also repeated
for every earlier candidate in the chain.

#### Impact

Candidate scores and explanations do not describe the pathway prefix that
actually reaches the candidate. Earlier intermediates can outrank other
candidates because of downstream evidence belonging to a different endpoint,
and their explanations can claim connection through transition types that
occur only later.

#### Follow-up verification

- Check whether the intended ranked unit is each material endpoint or the
  complete chain.
- Compare each candidate only with the material and transition prefix ending
  at its occurrence.
- Add a multi-hop test in which only the final transition satisfies the target
  family or preservation objective.

### Confirmed finding MG-IND-035

**Title:** Research comparison layers apply incompatible tie semantics  
**Category:** Deterministic ranking / response consistency  
**Confidence:** High  
**Status:** Confirmed; remediation deferred

#### Evidence

The three comparison decisions use different numeric rules:

- endpoint-sensitive ranking rounds each scientific usefulness score to two
  decimal places before forming score groups;
- comparative top-ranking uses exact equality against the exact maximum score;
- pairwise comparison rounds the score difference to two decimals before
  deciding whether the pair is tied.

For example, scores `90.004` and `90.001` produce:

- one endpoint-sensitive score group at `90.00`;
- a `"unique"` comparative top-ranking at exact score `90.004`; and
- a pairwise `"tie"` with displayed score difference `0.00`.

The pairwise tie explanation then says both pathways have the same
deterministic scientific usefulness score, although their stored scores are
different.

#### Impact

One successful research response can make mutually incompatible claims about
whether the same pathways are tied. Consumers cannot reliably reconcile the
top-ranking summary, endpoint-sensitive grouping, and pairwise explanation.

#### Follow-up verification

- Establish one canonical score precision and tie policy.
- Apply it before every top-group, endpoint-group, and pairwise decision.
- Test values immediately above and below the chosen tolerance boundary.

### Observations under investigation

#### OBS-RES-001 — Candidate evidence is merged across source chains

When a material occurs in multiple chains, its numeric score is the maximum
from any one chain, while reasons and warnings are deduplicated unions from all
chains. The explanation can therefore include evidence that did not produce
the selected score. This repeats the broader mixed-provenance pattern observed
in discovery candidate merging; intended research provenance should be
established before classification.

#### OBS-RES-002 — Candidate and chain limits are applied independently

The service slices ranked candidates and original-order chains separately.
Returned candidates need not be represented by the returned chain slice, and
returned chains need not explain the highest-ranked candidates. Whether both
lists are intended to be directly traceable must be confirmed from the route
and product contract.

#### OBS-RES-003 — Endpoint grouping uses strict lexicographic priority

Endpoint-sensitive ordering compares quality, then stability, then energy
above hull, criticality, risk, and finally evidence readiness. A small
difference in the first available dimension dominates every later dimension.
This is deterministic but its scientific policy and scale compatibility are
not declared.

#### OBS-RES-004 — Missing endpoint evidence is ordered below known evidence

The endpoint-sensitive service uses numeric floors for missing values, which
avoids treating unknown risk as zero or low risk. However, missingness is not
reported as a separate coverage dimension, and readiness is evaluated only
after all numeric dimensions. Route/test review should verify that this
ordering is intentional and transparent.

#### OBS-RES-005 — Pairwise comparisons cover adjacent ranks only

`_pairwise_comparisons()` sorts opportunities and zips each item with its next
neighbor. For `n` pathways it returns `n - 1` adjacent comparisons rather than
all `n(n - 1)/2` pairs. The field name may lead clients to expect complete
pairwise coverage; the intended contract should be checked in routes,
documentation, and tests.

#### OBS-RES-006 — Exact secondary ordering is inherited from input order

Scientific-score sorting and endpoint evidence-group sorting do not add a
stable domain identifier as a secondary key. Python preserves input order, but
the service does not define whether upstream ordering is stable. This can make
equal-evidence output ordering depend on database or graph traversal order.

### Test execution position

All three supplied files passed Python syntax compilation. Focused in-memory
counterexamples confirmed the tie-policy inconsistency. The complete
application test suite and database-backed research pipeline were not
available in this review workspace.

This batch adds `MG-IND-033`, `MG-IND-034`, and `MG-IND-035`. No new
performance finding is confirmed. The independent audit now contains
thirty-five `MG-IND` findings and five `MG-PERF` findings. No remediation was
performed.

## Area 17 — Composition Backfill Test

### File inspected

- `tests/scripts/test_backfill_material_element_fractions.py`

Supporting implementation cross-checked:

- `app/services/material/composition_backfill_service.py`
- `scripts/backfill_material_element_fractions.py`

The supplied test file and both supporting Python files pass syntax
compilation. The complete pytest suite was not executed because the full
project fixture environment is not present in this review workspace.

### Behaviors positively protected

- A structured Materials Project composition dictionary is converted to a
  symbol-to-float amount mapping without parsing formula text.
- Missing `raw_data`, absent or empty composition, null composition, and a
  non-dictionary composition are represented as unavailable.
- A plainly nonnumeric composition amount raises `ValueError` with a
  diagnostic message identifying the problem.

These assertions support the backfill's intended evidence boundary: it repairs
fractions only from stored structured composition and does not guess
stoichiometry from a formula.

### Coverage position

Despite its filename, the test exercises only the static
`extract_composition_amounts()` helper. It never executes
`backfill_material()`, `run()`, or the command-line `main()` function.
Consequently, it does not protect:

- normalization of amounts into unit-sum fractions;
- rejection of nonpositive or non-finite amounts through the complete
  backfill path;
- database/composition membership mismatch detection;
- failure when a material has no `MaterialElement` rows;
- exact changed-link counts and preservation of unchanged links;
- repeat-run idempotency;
- dry-run rollback and apply-mode commit;
- rollback of all earlier pending repairs when a later material fails;
- summary counters for discovered, eligible, updated, unchanged, skipped, and
  failed materials;
- exclusion of `mp-test-*` records;
- source filtering and targeted `--mp-id` selection;
- command-line argument parsing, exception rollback, and session closure; or
- database query growth described in `OBS-MAT-005`.

The unavailable-input parameterization is useful but does not distinguish all
malformed structured values. Empty symbols and duplicate symbols after string
normalization are not exercised. Numeric strings are accepted by the
implementation, while booleans also coerce to floats at extraction time; the
test does not establish whether either behavior is intended. Nonpositive and
non-finite values are rejected later by `MaterialCompositionService`, so their
absence here is primarily an end-to-end coverage gap rather than a separate
defect in this extraction helper.

### Test-layer conclusion

No new production finding is justified by this missed test. It adds a narrow
positive characterization of structured composition extraction, but the
backfill operation and CLI remain effectively untested by the supplied file.
The independent audit remains at thirty-two `MG-IND` findings and five
`MG-PERF` findings. No remediation was performed.

## Area 15 — Transition and Traversal Discovery-Service Tests

### Files reviewed

- `tests/services/discovery/test_discovery_transition_validator.py`
- `tests/services/discovery/test_discovery_traversal_service.py`
- `tests/services/discovery/test_discovery_warning_service.py`
- `tests/services/discovery/test_path_ranking_semantics.py`
- `tests/services/discovery/test_substitution_path_semantics.py`
- `tests/services/discovery/test_substitution_path_service.py`
- `tests/services/discovery/test_transition_semantics.py`

### Positive controls

- Warning tests protect exact element membership for `N` versus `Na` and `S`
  versus `Si`.
- Transition validation tests cover scalar and multi-element objective inputs
  and require all newly introduced preferred elements to appear in the reason.
- Substitution-path and transition tests consistently qualify inferred
  preservation as element overlap and explicitly state that structural
  preservation has not been validated.
- Path-ranking semantic tests score this evidence as
  `shared_element_continuity`, not `framework_preservation`, while preserving
  the intended 30-point component.
- Traversal responses are checked for deterministic node and edge ordering
  against the supplied database fixture.

### Test evidence strengthening confirmed traversal findings

#### MG-IND-028 — Effective graph depth remains untested

The graph tests request `max_hops=2`, but do not require a node or edge at hop
depth two. They also do not compare the response's reported goal depth with the
maximum depth actually present in the graph.

The tests therefore pass when graph construction silently caps execution at
one hop while returning the requested depth of two.

#### MG-IND-029 — Returned graph closure remains untested

The graph test requires nonempty `nodes` and `edges` and inspects fields on the
first edge. It never asserts that every edge source and target ID occurs in the
returned node set. Independent node and edge slicing can continue to produce
dangling edges without violating the test.

The large fixture limit of 50 also makes the truncation condition less likely
to be exercised.

#### MG-IND-030 — Post-truncation subgraph filtering remains untested

The family-filter test checks only that every returned edge has family
`phosphate`. It does not compare the result with all qualifying edges in an
untruncated parent graph, require expected material IDs, or test a small limit
that excludes qualifying results before filtering.

The test protects filter purity but not filter completeness.

#### MG-IND-031 — Multi-hop path lookup remains untested

The path test requests `max_hops=2` but asserts only that the response contains
the keys `path_found`, `materials`, and `transitions`. It does not require
`path_found` to be true, require material `7` to be reached, or construct a
target reachable only through two hops.

Consequently, direct-edge-only path lookup and complete failure to find the
fixture target can both pass.

### Avoidance semantics are explicitly encoded

`test_multi_element_avoidance_allows_retained_avoided_elements` requires a
transition to remain valid when `Co` is already present in the source and is
retained in the target, even though `Co` appears in `avoid_elements`.

This actively preserves the existing rule that avoidance rejects only newly
introduced avoided elements. It strengthens `OBS-DISC-021`, but it does not by
itself establish a production defect: the correct classification depends on
whether `avoid_elements` means "do not introduce" or "must be absent from the
result." The public objective wording and route documentation should settle
that contract.

### Preservation terminology is comparatively well protected

The path-ranking, substitution-path, traversal-reason, and transition tests
form a consistent regression boundary:

- `preserved_framework` remains as a legacy alias of `shared_elements`;
- `preservation_basis` is `element_overlap`;
- `structural_preservation_validated` is false;
- reasons explicitly disclaim validated structural preservation; and
- ranking awards shared-element continuity rather than framework-preservation
  credit.

These assertions protect the earlier terminology/provenance correction.
However, they do not validate crystal structure, coordination environments,
space groups, or structure-matching evidence.

### Important remaining coverage gaps

- No test covers magnesium, so the incorrect alkali classification in
  `MG-IND-008` remains unprotected.
- No test compares substitution-path classification with canonical transition
  classification for transition-metal substitution, leaving transition-type
  masking in `OBS-DISC-020` unprotected.
- Transition tests do not exercise malformed formulas, nonexistent symbols,
  missing element lists, or formula-token fallback behavior.
- Warning tests use ordinary valid formulas and do not expose the tokenizer's
  trust limitations.
- No traversal test uses small limits, verifies edge/node closure, checks
  effective depth, or establishes completeness before and after subgraph
  filtering.
- No path test requires a real multi-hop result, validates hop count, checks
  endpoint identity, or verifies transition/material alignment.
- Transition-validation tests do not cover deterministic relationship
  precedence, empty relationship sets, missing IDs, or agreement with graph
  builder and K-best construction.
- The concise path-ranking semantic tests check exact scores for one synthetic
  transition but do not exercise database-backed material quality or compare
  competing paths.

### Test execution position

All seven supplied files passed Python syntax compilation. The complete pytest
suite and its project fixture environment were not available in this review
workspace, so no claim is made that the tests execute successfully against the
full application.

No distinct new production finding is justified by this final test batch. It
materially strengthens `MG-IND-028`, `MG-IND-029`, `MG-IND-030`, and
`MG-IND-031`; explicitly preserves the retained-avoidance rule; and confirms
that element-overlap versus structural-preservation terminology is strongly
protected.

The independent audit remains at thirty-two `MG-IND` findings and five
`MG-PERF` findings. No remediation was performed.

## Area 16 — Graph, K-Best, Ranking, and Scoring Discovery Tests

### Files reviewed

- `tests/services/discovery/test_discovery_graph_analytics_service.py`
- `tests/services/discovery/test_discovery_graph_builder.py`
- `tests/services/discovery/test_discovery_k_best_path_service.py`
- `tests/services/discovery/test_discovery_path_ranking_service.py`
- `tests/services/discovery/test_discovery_scoring_service.py`

### Positive controls

- Path-ranking tests thoroughly distinguish path events from final endpoint
  state. An avoided element removed and later reintroduced earns no endpoint
  credit, and a preferred element introduced and later removed likewise earns
  no endpoint credit.
- Multi-element objective credit is proportional, order-independent, and
  capped at the declared 25-point objective weight.
- Missing endpoint composition earns no objective credit, while a structured
  `elements` field takes precedence over formula tokenization even when the
  structured list is explicitly empty.
- Path explanations separately report transition events, satisfied endpoint
  objectives, unsatisfied endpoint objectives, and unavailable endpoint
  evidence.
- Discovery scoring uses exact normalized element membership, so `N` does not
  match `Na`.
- Unknown candidate membership is score-neutral and does not earn the avoided-
  element-removed bonus.
- Source-diversity tests distinguish unique sources from repeated evidence and
  verify replacement rather than accidental accumulation of the published
  diversity component.
- Graph analytics has a focused test proving that dominant-element summaries
  use canonical node membership rather than reparsing formula text. This
  protects the earlier exact-membership correction.
- Basic graph-builder tests ensure canonical elements and material-quality
  metadata are present on generated nodes.

### Test evidence strengthening confirmed findings

#### MG-IND-025 — K-best validation bypass remains unprotected

`test_discovery_graph_builder_returns_adjacency` checks only that adjacency is
a dictionary, contains the starting material, and maps it to a list. It never
compares adjacency transitions with the transitions accepted by
`build_graph()`, nor supplies a candidate that canonical transition validation
rejects.

The K-best tests then consume that adjacency through the public K-best service
without asserting that every returned edge would also exist in the canonical
validated graph. The validation-parity failure can therefore persist while all
of these tests pass.

#### MG-IND-026 — Disconnected rejected graph nodes remain unprotected

The graph-builder tests inspect the first node and selected metadata fields,
but they do not create a rejected transition and require its candidate node to
be absent. They also do not assert that every non-start node participates in
at least one accepted edge.

Consequently, a candidate rejected at the edge-validation stage can remain as
a disconnected node without violating any assertion in this batch.

#### MG-IND-027 — Wrong incoming-edge material metadata remains unprotected

The K-best tests do not inspect path material metadata, transition-to-material
alignment, discovery scores, or explanations. They never construct a material
that is reachable from two different parents with different candidate
metadata and require the chosen path's actual incoming edge to supply that
metadata.

The global `_find_candidate_by_id()` lookup can therefore continue selecting
metadata from an unrelated adjacency list.

#### MG-PERF-005 — Exhaustive enumeration is hidden by response-limit tests

`test_k_best_path_service_respects_k_limit` verifies only:

```python
assert len(result["paths"]) <= 1
```

This checks the final response slice, not the amount of path enumeration or
ranking performed before slicing. It does not inspect the unused
`INTERNAL_PATH_LIMIT`, instrument path expansion, or exercise a branching
graph. The test is fully compatible with enumerating and ranking every simple
path before applying `k`.

### K-best assertions can pass vacuously

The K-best fixture tests never require at least one path:

- The basic result test checks only that `paths` is a list.
- Scientific-usefulness ordering compares the possibly empty score list with
  its sorted form.
- The `k` test accepts zero paths.
- Hop-count ordering compares the possibly empty hop list with its sorted
  form.

As a result, all four tests can pass even if material `7` is unreachable or
path construction regresses to always returning an empty list. They do not
protect endpoint correctness, maximum-hop compliance, simple-path identity,
transition count, or `path_count`/`total_path_count` coherence.

### Analytics coverage position

The first four analytics tests are principally response-shape checks against a
database fixture. They require at least one material and verify only the named
centrality field. The composite material-importance test verifies descending
numeric ordering, which is useful, but the suite does not:

- exercise a graph with known centrality values;
- protect edge direction or parallel-edge semantics;
- verify whether edge scores should be interpreted as strengths or distances;
- distinguish weighted from unweighted centrality;
- test deterministic secondary ordering for equal scores;
- test connected components or greedy-modularity behavior; or
- protect unknown node features from being converted to favorable or
  unfavorable numeric zero.

The canonical dominant-element test is valuable and directly protects exact
element membership. Its one-node graph does not, however, exercise community
edge aggregation, family counts, hub tie handling, density, or saturated edge
weights.

### Graph-builder coverage position

The graph-builder tests establish response shape and metadata presence, but do
not require:

- adjacency and canonical graph validation parity;
- every edge endpoint to exist among returned nodes;
- every non-start node to be connected;
- exact depth-frontier behavior;
- deterministic node or edge ordering;
- structured unknown-evidence semantics for risk and criticality; or
- bounded database work and family/candidate reuse.

`result["nodes"][0]` also relies on current encounter order without explicitly
asserting that the first node is the requested starting material.

### Path-ranking coverage position

This is the strongest test file in the batch. It comprehensively protects the
endpoint-specific objective semantics introduced while resolving the earlier
path-wide-versus-endpoint mismatch. It also verifies the public explanation
distinguishes historical path events from final objective satisfaction.

Its remaining limits are:

- Tests instantiate the service without a database, so material quality always
  contributes zero and bulk quality lookup is not exercised.
- Most synthetic transitions assume `alkali_substitution`; they do not compare
  plausibility weights across canonical transition types or expose transition-
  type masking.
- Shared-element continuity and path-efficiency boundaries are represented in
  the first total-score assertion but are not independently tested across
  their branches.
- Formula fallback tests use ordinary valid formulas and do not cover malformed
  text or nonexistent symbols.
- Exact full-score and score-breakdown coherence are asserted in only a narrow
  synthetic case.

These are focused coverage gaps, not new production findings.

### Discovery-scoring coverage position

The scoring tests properly protect exact membership, unknown membership,
distinct-source counting, bonus replacement, and the known lower-criticality
direction bonus. They do not test:

- more than three discovery sources, leaving the observed uncapped
  source-diversity behavior unprotected;
- partial or unknown criticality evidence reaching the recommendation
  candidate;
- malformed direction strings;
- stability and shared-application bonus combinations;
- complete score/breakdown conservation across all scoring stages; or
- invalid candidate element symbols.

### Test execution position

All five supplied files passed Python syntax compilation. The complete pytest
suite and its project fixture environment were not available in this review
workspace, so no claim is made that the tests execute successfully against the
full application.

No distinct new production finding is justified by this test batch. It
materially strengthens `MG-IND-025`, `MG-IND-026`, `MG-IND-027`, and
`MG-PERF-005`. It also confirms that endpoint-based, multi-element objective
alignment and exact element membership are comparatively well protected.

The independent audit remains at thirty-two `MG-IND` findings and five
`MG-PERF` findings. No remediation was performed.
