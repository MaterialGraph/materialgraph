# MaterialGraph frontend implementation decisions and working method

**Status:** Living implementation record  
**Scope:** Read-only Material Explorer and Objective Investigation  
**Last reviewed:** 2026-09-23

## 1. Purpose

This record explains the decisions and verification method used to build the
current frontend. It complements, but does not replace:

- `docs/architecture/MATERIALGRAPH_FRONTEND_UX_DESIGN.md`, which defines the
  longer-term product and scientific UX direction;
- `docs/implementation/FRONTEND_ARCHITECTURE.md`, which defines the target
  technical architecture;
- `docs/implementation/FRONTEND_IMPLEMENTATION_ROADMAP.md`, which defines the
  planned milestones; and
- `docs/implementation/MATERIAL_EXPLORER_CONTRACT_REVIEW.md`, which records the
  initial read-only contract review.

Those documents describe where the product is going. This document records
what is implemented, why it was implemented that way, which claims the current
contracts support, and how future slices should be reviewed.

## 2. Decision hierarchy

When sources disagree or a proposed screen requires unsupported data, use this
order:

1. actual registered API route and response schema;
2. captured response from an identified non-production environment;
3. repository tests and service implementation for semantic clarification;
4. product and UX specifications as the desired future state;
5. presentation proposals and screenshots.

A planned field is not an implemented contract. A successful HTTP response is
not evidence of scientific completeness. A visual label must not strengthen a
backend claim.

## 3. Delivery method used

Each frontend slice followed the same bounded sequence.

### 3.1 Review the contract before drawing the screen

For every route, inspect:

- HTTP method and URL;
- path, query, and JSON-body inputs;
- nullable and optional fields;
- ordering guarantees;
- score names and scopes;
- constraint and warning semantics;
- search limits and truncation metadata;
- validation or evidence boundaries; and
- fields that are absent but requested by the product specification.

Do not infer a query parameter when the route expects JSON. Do not invent
dataset versions, methodology versions, server timestamps, confidence,
coverage, tie groups, or provenance when the response does not contain them.

### 3.2 Use one bounded live reference investigation

Where an isolated non-production API and database are available:

1. identify the environment and repository commit;
2. verify the source material identity independently;
3. save the exact request body;
4. capture method, URL, status, raw response, size, and individual elapsed time;
5. retain the raw response unchanged as review evidence; and
6. distinguish repository-verified semantics from observations of that one
   response.

The Objective Investigation reference used local material ID `5`, verified as
`mp-19017` / LiFePO4. Its response demonstrated that ranked materials and
returned chains are different collections: a ranked material may not occur in
any returned chain, while another material may occur only as an intermediate.
This observation drove the separate two-column presentation and membership-
derived role labels.

A failed local setup is a verification gap. It is not evidence that an endpoint
fails or behaves in a particular way.

### 3.3 Implement one vertical slice

The first implementation included only:

- source-material selection;
- material identity and returned properties;
- read-only candidate discovery;
- structured objective submission;
- ranked objective results;
- returned composition chains;
- request, error, warning, limitation, and search-boundary states.

Comparison, graph views, saved investigations, authentication, and historical
reproducibility remain separate future slices.

### 3.4 Review in the browser against the live response

Automated tests verify deterministic mappings and states. Browser screenshots
verify hierarchy, density, overflow, sticky/scroll behavior, repeated copy, and
whether the visual presentation implies more than the data supports. Small
presentation findings were handled in focused follow-up changes rather than
mixed into contract or scoring work.

## 4. Current technical architecture

The current frontend is intentionally smaller than the target architecture.

| Concern | Current decision | Future trigger |
|---|---|---|
| Application shell | One React entry point and one continuous material workspace | Introduce routes when screens require independent, shareable navigation |
| Material server state | `useMaterialExplorer` owns list, detail, and discovery request states | Adopt TanStack Query when caching, invalidation, or cross-route reuse becomes necessary |
| Objective state | `useObjectiveInvestigation` owns submitted request, loading, errors, retry, and result | Move only when saved/versioned investigations require shared state |
| Objective draft | Local form state, separate from the last submitted request | Preserve this separation when drafts become persistent |
| URL state | Selected local material ID in `?material=` | Add only reproducible/shareable selections supported by stable contracts |
| API types | Explicit TypeScript types close to each feature | Add runtime schema validation when external contract volatility justifies it |
| Styling | Shared tokens and feature-oriented class names in one stylesheet | Split styles when ownership or build size makes the boundary useful |
| Graph library | None | Select only after graph interaction, accessibility, and performance requirements are verified |

This is deliberate incremental architecture, not a rejection of the target
architecture. React Router, TanStack Query, Zod, and a graph library should not
be introduced merely to match a planned folder diagram.

### 4.1 Feature boundaries

- `frontend/src/api.ts` contains shared transport behavior and current material
  and candidate contracts.
- `frontend/src/useMaterialExplorer.ts` owns the read-only explorer request
  lifecycle.
- `frontend/src/candidatePresentation.ts` converts structured discovery signals
  into cautious researcher-facing presentation while leaving the original
  backend explanation accessible.
- `frontend/src/objective/contract.ts` mirrors the objective request and response
  fields used by the UI.
- `frontend/src/objective/request.ts` validates draft input and builds the exact
  POST body.
- `frontend/src/objective/useObjectiveInvestigation.ts` keeps objective request
  state isolated from candidate-discovery state.
- `frontend/src/objective/ObjectiveInvestigation.tsx` renders the objective form,
  ranked results, returned chains, policies, and scientific/search limitations.

The Objective Investigation was kept separate from candidate discovery because
the two endpoints have different request shapes, scores, constraints, reasons,
and search metadata. Their scores must not be compared as if they share a scale.

## 5. State and request decisions

### 5.1 Draft versus applied request

Changing an objective form does not relabel an existing response. Results are
associated with the last submitted request, and a new result replaces the old
one only after a new run. Retry resubmits that applied request.

### 5.2 Cancellation and stale data

Effects use `AbortController`. When material identity or a submitted request
changes, the previous request is cancelled. Current results are cleared while a
new request is pending so stale data is not presented as current.

### 5.3 Error states

Transport errors, HTTP failures, and 422 validation details remain distinct.
Validation locations returned by the backend are converted into field paths;
the client does not replace them with a generic scientific interpretation.

### 5.4 Objective limits

The response contract contains both `objective.limit` and top-level `limit`.
Repository inspection established that the top-level limit caps returned ranked
materials and eligible chains for this route, while `objective.limit` is also
reported as the requested underlying chain limit. The current single control
sends the same value to both fields. This is documented in the UI support text
and must be revisited if the backend separates their behavior.

## 6. Scientific presentation decisions

### 6.1 Scores are neutral rule outputs

- Candidate discovery score, objective rule score, and chain usefulness rule
  score are named separately.
- Scores do not receive success colors, gauges, confidence language, or
  scientific-value judgments.
- Negative scores mean rule penalties, not negative scientific value.
- Equal objective scores receive one neutral note; API order is preserved and
  no tie reason or breakdown is invented.

### 6.2 Composition relationships are not reactions

Returned objective chains are rendered as ordered material records separated by
composition-relationship blocks. Bare reaction arrows are not used.

Each relationship displays only fields returned for that transition:

- readable, qualified form of `transition_type`;
- `shared_elements` for that consecutive pair;
- original returned reason in progressive disclosure;
- relationship and preservation bases in details; and
- structural/mechanistic validation flags.

`alkali_substitution` is presented as **Possible alkali composition
substitution**, not as a demonstrated substitution. `family_expansion` is
presented as **Composition family relationship**. Unknown future identifiers
use a neutral `Reported relationship` fallback and require backend clarification
before receiving a more specific scientific label.

The **Not validated** state belongs to the relationship-level structural or
mechanistic claim. It does not label the entire material and does not imply that
the displayed composition or shared-element list is invalid.

### 6.3 Shared-element continuity

Shared-element continuity means the element overlap returned for each
consecutive relationship. It is not inferred only from source and endpoint, and
it does not establish structural preservation, a reaction mechanism, synthesis
feasibility, or application performance.

### 6.4 Ranked materials and returned chains remain separate

Candidate roles and links are derived from actual membership in returned
chains, never from rank or score:

- `Source`;
- `Intermediate in returned chain`;
- `Final material in returned chain`; or
- both intermediate and final if separate returned chains establish both roles.

If no returned chain includes a ranked material, the card says **No returned
chain includes this material.** One contextual note explains that this does not
establish the absence of a composition-level relationship. No disabled or
speculative chain link is shown.

### 6.5 Preserve original backend content

Researcher-facing summaries may qualify structured fields and reduce repetition,
but original backend explanations and reasons remain inspectable. Raw reasons
currently contain identifiers such as `alkali_substitution`; this is an explicit
copy limitation, not permission for the client to rewrite scientific content
without a structured backend field.

### 6.6 Missing evidence remains missing

Material properties are displayed as returned. The client does not translate
missing values to zero, infer field-level provenance, or treat a stored stability
flag as a complete evidence assessment. Unsupported provenance and evidence
coverage are disclosed rather than fabricated.

## 7. Search boundaries and provenance

The Objective Investigation keeps these response concepts distinct:

- `generated_chain_count`: generated before objective filtering;
- `returned_chain_count`: included in the response;
- `result_truncated`: the returned result set was limited;
- `search_truncated`: bounded search stopped at its search-state budget; and
- `scientific_completeness_guaranteed`: whether the backend guarantees
  scientific completeness.

`search_truncated: false` is not rendered as “complete.” HTTP 200 is not treated
as scientific validation. The submitted structured request is displayed as
client-observed request context; returned mode, policies, warnings, and metadata
are identified as backend response fields.

## 8. Information hierarchy and visual direction

The implementation combines three agreed visual modes:

- Research Journal for material identity and scientific narrative;
- Precision Workbench for compact ranked lists and controls; and
- Modern Scientific Studio for objective investigation and deeper reasoning.

Progressive disclosure keeps lists scannable while preserving reasons, scoring,
policies, and original explanations. Neutral borders, typography, whitespace,
and focus styles carry hierarchy. The implementation avoids KPI cards, gauges,
progress bars, decorative gradients, and score-based status colors.

The desktop Objective Results view keeps ranked materials and returned
composition chains in separate columns and collapses to one column at narrower
widths. The dossier and objective content flow with the page to avoid clipped
section headings and nested-scroll confusion.

## 9. Verification standard

Every result feature should test the contract boundary rather than only snapshot
markup.

Current tests cover:

- exact GET/POST route construction and POST body;
- aligned objective limits;
- response and validation error handling;
- one-step and multi-step chains;
- relationship type, shared elements, and step count from corresponding
  transition records;
- intermediate/final roles derived from membership;
- ranked materials with and without a returned chain;
- equal and unequal objective scores;
- validated and unvalidated relationship flags;
- zero ranked materials and zero returned chains as independent states;
- result limitation versus search truncation; and
- candidate explanation and score-factor presentation.

For each frontend change:

1. run the focused tests while editing;
2. run the complete frontend test suite;
3. run the strict TypeScript/Vite production build;
4. inspect `git diff --check`;
5. review the live reference workflow in the browser when an API is available;
6. report exact copy changes, unsupported claims removed, contract questions,
   and deviations; and
7. stop for review before expanding scope.

## 10. Pull-request discipline

Frontend changes are delivered as small, reviewable slices on protected `main`:

- foundation and module extraction;
- researcher-facing candidate copy;
- focused scrolling/copy polish;
- structured Objective Investigation;
- composition-chain presentation; and
- objective-result clarity.

Presentation-only changes must say explicitly that scoring, ordering, API
contracts, database state, and production configuration are unchanged. Local
reference request/response captures and Git bundles are review artifacts and
must not be accidentally added to product commits.

## 11. Open contract and architecture questions

Do not resolve these in the client by assumption:

1. structured researcher-facing reason codes that remove the need to display or
   parse backend prose;
2. a vocabulary/version contract for future relationship types;
3. property-level provenance, evidence quality, measurement conditions, and
   coverage;
4. dataset and methodology versions and stable investigation identifiers;
5. formal rank/tie semantics beyond equality of returned numeric scores;
6. server-side material search and formula/source-ID lookup;
7. separate meanings and future behavior of the two objective limit fields;
8. accessible graph interaction and performance requirements; and
9. saved-investigation immutability and historical rerun semantics.

## 12. Checklist for the next frontend slice

- [ ] Identify the exact route, schema, and environment.
- [ ] Capture an actual bounded response if a safe environment exists.
- [ ] List supported fields and absent fields separately.
- [ ] Define scientific claims and explicit non-claims.
- [ ] Keep new state within the owning feature until sharing is necessary.
- [ ] Preserve backend order and distinct score domains.
- [ ] Derive roles, links, and labels from returned fields.
- [ ] Provide loading, validation, API failure, empty, limited, and truncated
      states where the contract supports them.
- [ ] Keep original backend explanations accessible.
- [ ] Add contract-focused tests and run the full frontend build.
- [ ] Perform a live browser review without treating it as broad performance
      evidence.
- [ ] Record unresolved contract questions and stop before unrelated features.

## 13. Standalone source-first property comparison (2026-09-23)

The first comparison workspace accepts an explicit local source ID and two or
three distinct candidate IDs. The local reference defaults to IDs 5, 6, and 7;
the displayed values are always fetched from current material-detail responses.
The launcher does not read Candidate Discovery or Objective Investigation state.
Their future selection trays remain separate, and no shareable URL is defined.

Each column independently fetches `GET /api/v1/materials/{id}/detail`. The
pairwise `POST /api/v1/comparison/materials` endpoint screens and scores two
candidates, so its winner/tie result is not a reported-property comparison.
Each fetch has its own loading, success, error, and retry lifecycle. Selection
changes remount and abort old requests; an error in one column preserves other
columns and their source-relative differences. When the source fails, candidate
records remain visible but differences are unavailable.

The table displays band gap, energy above hull, formation energy per atom,
density, stored stability classification, material type, and listed elements.
Numeric values are displayed with at most four fractional digits using the
client formatter, while arithmetic uses the original response numbers. This is
a display convention, not a backend precision or uncertainty claim. Numeric
zero is Available; null is Unknown. Both true and false stability flags are
available stored classifications, with no supporting basis supplied by this
endpoint. An empty elements array means no elements were listed in the record.

Candidate-minus-source differences are arithmetic only when both field values
are numbers. Matching units do not establish comparable calculation methods or
conditions; the methodology notice states the scientific boundary. Source ID,
selected IDs, and any explicitly passed launch context are investigation
context, not property-level provenance, dataset version, or historical record.

## 14. Workflow selection into property comparison (2026-09-24)

Candidate Discovery and Objective Investigation each own a separate, empty-on-new-
result comparison selection. Selecting a result is an independent control:
opening a Discovery dossier or following a returned-chain link does not select
anything; selecting for comparison does not change the inspected result or the
API ordering. Each workflow allows up to three comparison materials. Two are
required to launch; the source is supplied explicitly by the workflow and does
not occupy a candidate slot. The tray retains selected identities and allows
removal at the limit.

The workflow passes one launch value containing the source local ID, two or
three selected material identities, the workflow of origin, and bounded
investigation context. Discovery context comes from the applied response goal,
not the editable Avoid/Prefer fields. Objective context comes from the
submitted structured request, not the current form draft. Ranked Objective
materials retain their rank-result role and any membership in the actual
returned composition chains. A ranked result without returned-chain membership
is labeled as ranked only. Unranked chain members cannot be selected through
this slice. Chain roles are selection context, not validated reactions or
scientific provenance.

The comparison view receives the launch value and continues to fetch every
current `/detail` record independently. It does not reuse result-list properties,
scores, or pathway values. The comparison table, uncertainty handling, and
arithmetic interpretation are unchanged. The standalone ID-entry workspace
remains available.

Launching temporarily hides the existing workbench while keeping its mounted
state. The explicit Return button restores the originating workflow and its
selection, and focus moves between the comparison heading and originating
workflow. New results clear their own workflow's selection. Changing the source
remounts both workflows and clears their selections. The two selection sets
never merge. No permanent comparison route, browser-history entry, shareable
URL, saved state, or cross-workflow comparison is created; those need separate
contracts. Selection of arbitrary unranked chain members is also deferred.

## 15. Comparison routing and sharing v1 (2026-09-24)

This section supersedes section 14's statement that comparison URLs and
history entries are absent. The frontend serializes comparisons on the `/`
path with query keys in canonical order: `view=compare`, `v=1`, `source`,
`candidates`, `workflow`, and optional `context`. Two or three ordered,
distinct positive safe local material IDs are required; the source cannot
also be a candidate. This frontend URL version is not a dataset or scientific
methodology version. Links depend on the local ID mapping of the instance
where they were created; portable external-ID resolution needs a backend API.

The optional context is compact UTF-8 JSON encoded as unpadded base64url.
It holds applied Discovery Avoid/Prefer with limit 10 and substitution paths
disabled, or the submitted Objective request with both independent limits.
It never holds returned ranks, chain memberships, scores, detail values, or
UI state. The ceilings are 1,600 relative URL characters, 1,200 encoded
context characters, and 900 decoded JSON bytes. Current frontend Objective
families are `null` or `phosphate`; the backend's unrestricted family strings
are outside this v1 frontend URL contract. Duplicate/unknown parameters,
source ambiguity with `?material=`, malformed values, and noncanonical
encoded context make the link invalid. Absent context is explicitly labelled.

Opening or refreshing a comparison independently refetches current `/detail`
records. Neither research workflow reruns automatically. A source fetch
failure prevents source-relative inspection. Failed candidate requests keep
their columns as material-not-found or API errors, separate from Unknown
properties in successful records. Cold Objective restoration omits historic
rank and chain roles; a live in-app launch still shows returned roles.

An in-app comparison pushes a history entry and keeps its workbench mounted.
Return and browser Back restore that in-memory selection; Forward shows the
comparison again. After a cold load or refresh, Open enters the relevant
workflow with source and available recorded inputs prefilled, without results,
selection, or an automatic investigation. Browser Back follows real browser
history. Copy comparison link copies the canonical URL for the current
instance; it does not preserve old values or establish reproducibility,
current result membership, or scientific comparability.

## 16. Materials Project record attribution (2026-09-24)

When a successful `/detail` response has `source: materials_project`, the
Source Context material identity and the independent comparison display a
single compact attribution beside the record data: “Material record data:
Materials Project (CC BY 4.0). MaterialGraph calculates the discovery,
objective, chain, and comparison analysis shown here.” The attribution links
to Materials Project, its CC BY 4.0 license, and its citation guidance.
Record-source labels render `materials_project` as “Materials Project” while
retaining any other source string as reported. A mixed-source comparison
credits the fetched Materials Project record once for the whole table; an
unfetched or other-source record cannot trigger that credit. Cold-opened
comparison links use freshly fetched details and the same rule. This does
not infer Materials Project provenance for individual Discovery or Objective
results, or for the analysis computed by MaterialGraph. Dataset-wide
attribution and release-level scientific provenance remain separate tasks.

## 17. Pilot dataset coverage at results (2026-09-24)

Discovery displays a cohort-coverage sentence before its returned-candidate
count for successful results, including empty results. Objective displays the
corresponding sentence directly under “Ranked materials” for successful
results, including empty rankings. The notices explain the selected population
available to the workflows. They remain separate from request-specific Search
scope, scientific completeness, material-detail limitations, and source
attribution. “Material identities” preserves the distinction between records
that share a formula. The permanent UI omits the qualified 1,727-identity
deployment count, which could become stale; the count belongs in the pilot
briefing. No backend cohort metadata or endpoint was added for this display.

## 18. Returned composition chain legibility (2026-09-25)

The existing Objective chain cards identify Source, Intermediate, and Final
as positions within the returned chain only. Composition relationship blocks
remain between consecutive material records; no reaction direction is implied.
Known relationship identifiers retain qualified researcher-facing labels;
unrecognized identifiers use a neutral label. Raw identifiers appear in the
existing expanded technical details. Relationship basis, element-overlap
continuity basis, structural-preservation validation, and mechanism validation
are displayed as distinct returned fields. The chain usefulness rule score
appears at chain scope, with its returned breakdown in expanded details.
Neither node roles nor composition overlap establish reaction intermediates,
products, structural preservation, or validated pathways.

## 19. Eligible composition chain reasons (2026-09-25)

Objective ranked-material reasons describe membership in an eligible
composition chain because ranking precedes the response limit on returned
chains. Backend human-facing reasons now say “eligible composition chain” and
“composition relationship”; the former `pathway` wording could imply a
physical route. A ranked material can still have no returned chain. The
frontend renders backend reasons as supplied, and machine-readable API fields
and identifiers remain unchanged. Separate Scientific Pathway and Candidate
Discovery substitution-path surfaces are outside this correction.
