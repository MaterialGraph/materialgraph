# MG-DE-006 Scientific Cohort Review Plan

**Status:** Ready for independent execution
**Input:** Qualified MG-DE-005 manifest only
**Database writes authorized:** No
**Network access required:** No

## Objective

Determine whether the qualified 1,727-material cohort is scientifically useful
for MaterialGraph's first focused battery-relevant discovery dataset. This is
not a claim that the cohort represents all materials science, every battery
chemistry, or the upstream Materials Project database.

The review separates reproducible measurements from scientific judgment. The
tool verifies that the exact MG-DE-005 payload is being reviewed and measures
system balance, chemistry-family balance, elemental representation, stability
bands, formula multiplicity, and polymorph density. A reviewer must then record
whether the limitations are acceptable for the stated product scope.

## Immutable input

The only approved input has:

- payload digest
  `902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`;
- selection contract `materials-project-selection-v3`;
- source release `2026.04.13`;
- 1,727 accepted source identities;
- complete traversal of the 48 requested chemical systems;
- zero duplicate source identities.

The manifest stays outside Git. Do not copy the manifest or API credentials
into the repository.

## Required review dimensions

1. **Scope fit:** The cohort is assessed only for a focused near-stable
   battery-material discovery starting point.
2. **Chemical-system balance:** Record every requested system, including
   zero-result and sparse systems. Do not treat a complete zero-result query as
   missing traversal.
3. **Chemistry-family balance:** Compare oxide, phosphate, silicate, and
   sulfide representation.
4. **Element balance:** Record carrier-ion and transition-metal representation,
   especially lithium dominance and thin sulfur coverage.
5. **Stability:** Separate the source stable flag, exact zero-energy records,
   `(0, 0.025]`, and `(0.025, 0.05]` eV/atom bands.
6. **Polymorphs:** Record singleton formulas, formulas with multiple material
   identities, materials in those groups, and maximum formula multiplicity.
7. **Attribution:** Product presentation must identify Materials Project,
   source release, retrieval provenance, and applicable CC BY 4.0 attribution.

No universal numeric balance threshold is invented for this review. A high or
low count is evidence to interpret against intended use, not an automatic
scientific verdict.

## Independent execution

Run from a clean checkout with the project virtual environment active:

```powershell
$EvidenceRoot = `
  "$env:LOCALAPPDATA\MaterialGraph\Evidence\MG-DE-005-2026.04.13-v3-90210923"

$ManifestPath = Join-Path `
  $EvidenceRoot `
  "materials-project.manifest.json"

$ReviewPath = Join-Path `
  $EvidenceRoot `
  "scientific-cohort-review.json"

if (Test-Path $ReviewPath) {
  throw "Scientific cohort review output already exists"
}

python scripts/review_materials_scientific_cohort.py `
  --manifest $ManifestPath `
  --output $ReviewPath `
  --sparse-system-threshold 5
```

The command must exit zero, report no integrity failures, set
`ready_for_scientific_decision` to `true`, keep `scientific_decision` pending,
and keep `database_import_authorized` false.

## Decision outcomes

After reviewing the complete JSON evidence, record exactly one outcome:

- **Accept for disposable PostgreSQL qualification:** scientifically useful
  for the stated focused scope, with limitations explicitly retained;
- **Revise source contract:** useful direction, but imbalance or missing
  chemistry requires a new immutable manifest;
- **Reject:** unsuitable for the intended initial product scope.

Even an acceptance authorizes only the next disposable local PostgreSQL gate.
It does not authorize Neon, production, EC2 deployment, application restart,
or public claims of domain-wide representativeness.
