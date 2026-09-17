# MG-DE Materials Project Source Contract

**Contract version:** `materials-project-selection-v3`
**Normalization version:** `materials-project-summary-v1`
**Status:** Implemented; MG-DE-005 controlled real-source execution pending
**Production import authorized:** No

## Authority and license

The source is the Materials Project API summary endpoint. Materials Project
states that its data is available under the Creative Commons Attribution 4.0
International license. Every manifest records `CC-BY-4.0` and the canonical
license URL. MaterialGraph must retain Materials Project attribution when these
records are displayed, exported, or redistributed.

Primary references:

- [Materials Project terms](https://legacy.materialsproject.org/terms)
- [Materials Project API](https://next-gen.materialsproject.org/api)
- [`SummaryRester.search` client contract](https://materialsproject.github.io/api/_autosummary/mp_api.client.routes.materials.summary.SummaryRester.html)

The operator must recheck the current terms and attribution requirements on
the acquisition date. Repository metadata and historical links do not replace
that review. The official client documents chemical-system, stability, field,
chunk, page, and deterministic sort parameters used by this contract.

Contributed datasets with different terms are excluded from this contract. A
new reviewed contract is required before importing them.

## Release and retrieval identity

The operator must provide the current authoritative Materials Project database
version as `--source-release`. Before each page, the client compares the API
heartbeat database version with that declaration; a mismatch aborts source
acquisition. The current client/API path does not promise historical query
pinning, so a release change during acquisition fails closed instead of silently
combining releases. A timezone-aware ISO-8601 retrieval start time is required
as `--retrieved-at`.

The manifest digest covers the release, retrieval time, license, normalization
version, selection-contract version, selection scope, rejections, and accepted
normalized records. Retrieval time is evidence, not a substitute for a release
identifier.

## Inclusion and exclusion

Version 3 includes only records returned by the reviewed summary endpoint for
the explicitly listed chemical systems and declared stability policy. It can
express either stable-only retrieval or an explicit finite energy-above-hull
ceiling; the revised MG-DE-005 pilot uses 0 through 0.05 eV/atom and never uses an
unbounded unstable-material query. Deprecated and GNoME records are explicitly
excluded from the MG-DE-005 summary query. Paging, page size, page count,
source-record count, accepted-material count, retry count, and chunk size are
bounded manifest inputs.

The following normalized fields are requested:

- Materials Project material identity;
- reduced and displayed formula;
- element membership and normalized stoichiometric fractions;
- band gap, energy above hull, formation energy per atom, and density;
- Materials Project stability flag.

Records that cannot satisfy the normalization contract are rejected with a
sanitized reason. Missing optional scientific values remain `null`; they are
never converted to zero, false, or a favorable value.

## Identity, polymorph, and alias rules

- A Materials Project `material_id` is the source identity.
- Distinct source identities remain distinct MaterialGraph materials, including
  polymorphs that share a formula.
- Formula equality is never sufficient to merge materials.
- Existing material rows without matching provenance are conflicts and are not
  silently adopted or overwritten.
- Aliases are not inferred. Mapping multiple source identities to one canonical
  material requires a future explicit, evidence-backed alias decision.
- Source records and normalized MaterialGraph records remain separately hashed.

## Refresh outcomes

| Outcome | Rule | Database effect |
|---|---|---|
| `inserted` | Source identity has no material or provenance record | Create material, membership, provenance, and event |
| `updated` | Proven source identity exists and either source or normalized digest changed | Replace reviewed mutable scientific fields and membership; append event |
| `unchanged` | Source and normalized digests and normalization version match | Preserve material; advance provenance and append event |
| `conflicted` | Material identity exists without matching provenance, or provenance resolves inconsistently | Preserve existing material; append conflict event |
| `rejected` | Source record cannot be normalized | Do not create or update a material; append sanitized rejection event |
| `retired` | Previously active identity is absent from a completed refresh of the identical source selection scope | Mark the source record inactive; preserve the material and append event |

Retirement is deliberately non-destructive. Public-query exclusion and any
delete or archival policy require separate measured implementation; until that
gate is complete, no production refresh or expanded-dataset publication is
authorized.

## Import-run and event invariants

- Each checkpoint owns one UUID import-run identity.
- Resume must reuse that identity and exact manifest digest.
- Run metadata is immutable after creation.
- One outcome event is stored per accepted or rejected manifest item; retirement
  events are added only after complete scope reconciliation.
- Only an identical selection-contract version and selection-scope digest may
  retire a prior active source record.
- Empty manifests are rejected. A manifest stopped by its accepted-material
  bound is marked incomplete and cannot infer retirement from unseen records.
- A completed run records reconciled outcome counts and completion time.
- A run containing conflicts completes as `completed_with_conflicts`; the CLI
  reports the counts and exits nonzero so it cannot be mistaken for an accepted
  refresh.
- Source payloads remain in the material record; audit events store digests and
  sanitized reasons rather than duplicating payloads.
