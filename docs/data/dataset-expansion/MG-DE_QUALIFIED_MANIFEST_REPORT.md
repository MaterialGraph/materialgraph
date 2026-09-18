# MG-DE-005 Qualified Manifest Report

**Execution commit:** `abecf62bae47213503219c3dae0c44b70950f953`
**Source release:** `2026.04.13`
**Retrieved at:** `2026-09-17T09:14:36.7131839+00:00`
**Selection contract:** `materials-project-selection-v3`
**Database writes performed:** No
**Import authorized:** No

## Outcome

The revised 48-system Materials Project acquisition completed without reaching
a configured bound and passed every MG-DE-005 offline inspection gate. The
manifest is accepted as the immutable input to MG-DE-006 scientific cohort
review. Acceptance here establishes source traversal, provenance, structure,
coverage, and boundedness; it does not authorize database import or claim
domain-wide representativeness.

| Measurement | Result |
|---|---:|
| Accepted source identities | 1,727 |
| Rejected records | 0 |
| Duplicate source identities | 0 |
| Source records seen | 1,727 |
| Pages fetched | 54 |
| Source traversal complete | Yes |
| Stable materials | 141 |
| Near-stable materials | 1,586 |
| Unique formulas | 651 |
| Formulas with polymorphs | 234 |
| Materials in polymorph groups | 1,310 |
| Acquisition duration | 153.139 seconds |
| Offline inspection duration | 4.104 seconds |

All 1,727 records contained band gap, density, energy above hull, and formation
energy per atom. The manifest payload digest is
`902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`.
The exact 4,996,610-byte manifest file has SHA-256
`7939dcfd0fab9a8e7e43f7395c59c874673ed19aaf49d1a942650a69595e3daa`.

## Element representation

| Element | Materials |
|---|---:|
| Ca | 75 |
| Co | 291 |
| Fe | 399 |
| K | 63 |
| Li | 1,213 |
| Mg | 100 |
| Mn | 749 |
| Na | 276 |
| Ni | 288 |
| O | 1,712 |
| P | 618 |
| S | 15 |
| Si | 174 |

The complete query traversal returned no qualifying records for `Li-Fe-S` and
`Na-Ni-S` at or below 0.05 eV/atom. These are zero-result source observations,
not missing traversal. Sulfide representation is thin and lithium-containing
systems are comparatively dense; MG-DE-006 must assess the resulting
scientific usefulness and bias before any import qualification.

## Revision evidence

The first execution used a 0.1 eV/atom ceiling and stopped at 3,000 accepted
identities before 15 Na systems were visited. It correctly failed the
source-completeness gate and was never imported. Offline sensitivity retained
1,455 of that truncated cohort at 0.05 eV/atom. The reviewed version 3 contract
therefore preserved all 48 systems and the 3,000-material bound while reducing
the energy-above-hull ceiling to 0.05 eV/atom.

The first and revised manifests remain external evidence and are not committed
to Git. The revised evidence set includes the acquisition result and timing,
inspection report and timing, source release, operator terms-review record,
prior-attempt reference, qualified outcome, and SHA-256 inventory. A durable
copy was independently verified against the manifest file hash above.

## Remaining gates

- MG-DE-006 accepted the cohort with explicit imbalance, polymorph,
  zero-result, stability, and attribution limitations recorded in the
  [scientific cohort report](MG-DE_SCIENTIFIC_COHORT_REPORT.md).
- The manifest must then be qualified in disposable local PostgreSQL before an
  isolated Neon test environment is considered.
- Production import, EC2 deployment, production Neon writes, schema changes,
  service restart, and canary execution remain unauthorized.
