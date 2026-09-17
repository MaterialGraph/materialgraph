# MG-DE-005 Real-source Pilot Plan

**Status:** Ready for controlled reacquisition under revised scope
**Revision baseline:** `f9e5400d8c25df1da5fcd48760008435bfa7d55b`
**Database writes authorized:** No
**Production or Neon writes authorized:** No

## Objective

Capture and independently inspect the first immutable Materials Project
manifest that can later be qualified in disposable PostgreSQL. MG-DE-005 ends
at an accepted manifest and inspection report. It does not import, publish, or
synchronize material records.

## Scientific boundary

The first pilot is intentionally focused on MaterialGraph's already-tested
ion-substitution and phosphate reasoning rather than presented as a complete
materials-science dataset. The selection contract is:

- source: Materials Project summary endpoint;
- deprecated and GNoME records excluded explicitly;
- chemical-system families: oxides for `Li`, `Na`, `Mg`, `K`, and `Ca` with
  `Fe`, `Mn`, `Co`, and `Ni`; phosphates for `Li`, `Na`, and `Mg` with those
  transition metals; and sulfides and silicates for `Li` and `Na` with those
  transition metals (48 exact systems in total);
- stable and near-stable materials with energy above hull from 0 through
  0.05 eV/atom;
- accepted-material bound: 3,000;
- source-record bound: 5,000;
- page size and import chunk size: 100;
- maximum pages per system: 25;
- maximum fetch attempts per page: 3;
- normalized properties: composition fractions, stability, band gap, energy
  above hull, formation energy per atom, and density.

This is a focused pilot, not evidence of domain-wide representativeness.
Additional elements, chemical families, metastable materials, structures, and
application-specific properties require later reviewed contracts.

## Preconditions

1. Work from a clean commit descended from the recorded baseline.
2. Store the API key only in the excluded local environment file or process
   environment. Never print or copy it into evidence.
3. Review the current Materials Project terms, attribution requirement, API
   documentation, and database-version notice on the execution date.
4. Record the authoritative database version returned by the API.
5. Create a private evidence directory with a new manifest path. Existing
   manifests and inspection reports must never be overwritten.
6. Keep `DATABASE_URL` and `DATABASE_MIGRATION_URL` pointed at the ordinary
   test database even though neither acquisition nor inspection uses them.

## Controlled acquisition

Read the current release without exposing the API key:

```powershell
python scripts/read_materials_project_release.py
```

Record a UTC retrieval start immediately before the manifest command. Replace
the placeholders with those recorded values:

```powershell
python scripts/import_materials_project.py `
  --manifest "$EvidenceRoot\materials-project.manifest.json" `
  --source-release "<authoritative-release>" `
  --retrieved-at "<timezone-aware-UTC-timestamp>" `
  --page-size 100 `
  --chunk-size 100 `
  --max-materials 3000 `
  --max-source-records 5000 `
  --max-pages-per-system 25 `
  --max-fetch-attempts 3 `
  --maximum-energy-above-hull 0.05
```

Do not add `--apply` or the unbounded `--include-unstable` option. The explicit
energy-above-hull bound includes near-stable records. The acquisition path does
not load database modules and cannot write material records.

## Offline inspection

Disconnecting the network is permitted for this step. The inspector validates
the manifest digest and semantic structure, then records element, chemical
system, stability, formula/polymorph, rejection, duplicate, and property
coverage counts:

```powershell
python scripts/inspect_materials_manifest.py `
  --manifest "$EvidenceRoot\materials-project.manifest.json" `
  --output "$EvidenceRoot\materials-project.inspection.json" `
  --minimum-materials 500 `
  --maximum-materials 3000 `
  --minimum-property-coverage 0.95 `
  --require-source-complete
```

The default required elements are `Li`, `Na`, `Mg`, `K`, `Ca`, `Fe`, `Mn`,
`Co`, `Ni`, `O`, `P`, `S`, and `Si`.
A gate failure returns exit code 2 and must be investigated rather than
weakened after seeing the data. Changing a gate or selection scope requires a
reviewed decision and a new manifest.

## Acceptance criteria

- the release check succeeds before every fetched page;
- source traversal is complete rather than stopped at a global bound;
- 500 to 3,000 unique source identities are accepted;
- required elemental coverage is present;
- each normalized optional scientific property has at least 95% coverage;
- the digest, counts, duplicate identities, candidates, and normalized
  compositions pass semantic validation;
- rejected records contain only source identity, page, chemical system, and a
  sanitized reason;
- a reviewer confirms current license and attribution obligations;
- no database connection, import checkpoint, or database mutation occurs;
- the manifest and report stay out of Git because they may be large and are
  execution evidence tied to a particular source release.

If the complete 48-system result contains fewer than 500 records, reaches a
configured bound, or fails coverage, MG-DE-005 remains open. Record the result
and revise the scientific selection contract before making another request.

## First execution and revision

The first independent execution against Materials Project release `2026.04.13`
used the original 0.1 eV/atom ceiling and stopped at the approved 3,000-material
bound after 3,068 source records and 53 pages. It had no rejections or duplicate
identities and complete property coverage, but it was not source-complete: 15 Na
systems had not been visited. No database write occurred and that manifest is
not authorized for import.

Offline sensitivity retained 1,455 of those truncated records at 0.05 eV/atom,
compared with 2,349 at 0.075 eV/atom. Decision MG-DE-D-014 therefore preserves
all 48 systems, completeness, and the 3,000-material ceiling while narrowing
the near-stability ceiling to 0.05 eV/atom. The revision increments the
selection contract to `materials-project-selection-v3`; it requires a new
manifest path and a new retrieval timestamp.

## Next gate

An accepted MG-DE-005 manifest may proceed to MG-DE-006 scientific cohort
review. Database import remains prohibited until that review approves the
manifest for isolated PostgreSQL qualification. Isolated Neon qualification
and production canary work remain later, separately authorized gates.
