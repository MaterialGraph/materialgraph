# MG-DE-006 Scientific Cohort Report

**Execution commit:** `c7ebc1a1a2b4be66036b1a56b68b384226830095`
**Manifest payload digest:** `902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9`
**Review evidence SHA-256:** `1897c042a4884700ec52c222542840c1c1654033dc39b739c9c407fa21829740`
**Scientific decision:** Accept for disposable PostgreSQL qualification
**Neon or production import authorized:** No

## Decision

The 1,727-material cohort is scientifically useful as MaterialGraph's first
focused, near-stable battery-material discovery dataset. It is accepted for the
next isolated local PostgreSQL qualification gate with the limitations below.
It is not representative of materials science broadly, the complete Materials
Project database, all battery chemistries, or experimentally validated
materials.

This decision is based on complete traversal of the approved 48-system source
scope, reproducible identity and property evidence, meaningful oxide,
phosphate, and silicate coverage, explicit near-stability bounds, and preserved
polymorph identities. Acceptance does not convert sparse evidence or source
zeroes into negative scientific conclusions.

## Integrity result

The offline review completed in 5.837 seconds with exit code zero. It matched
the exact approved manifest digest, source, selection contract, accepted count,
complete traversal, and zero-duplicate contract. There were no integrity gate
failures. The generated 4,894-byte review JSON has SHA-256
`1897c042a4884700ec52c222542840c1c1654033dc39b739c9c407fa21829740`.

## Scope and chemistry balance

| Measurement | Result |
|---|---:|
| Accepted source identities | 1,727 |
| Requested systems | 48 |
| Represented systems | 46 (95.83%) |
| Zero-result systems | `Li-Fe-S`, `Na-Ni-S` |
| Oxides | 920 (53.27%) |
| Phosphates | 618 (35.78%) |
| Silicates | 174 (10.08%) |
| Sulfides | 15 (0.87%) |

Nine represented systems contained fewer than five records: `Li-Co-S` (4),
`Li-Mn-S` (4), `Li-Ni-S` (1), `Na-Co-S` (1), `Na-Co-Si-O` (2), `Na-Fe-S`
(3), `Na-Fe-Si-O` (4), `Na-Mn-S` (2), and `Na-Ni-Si-O` (1).

Lithium occurs in 1,213 records (70.24%), manganese in 749 (43.37%), and
oxygen in 1,712 (99.13%). Sodium has 276 records, while potassium, magnesium,
and calcium have 63, 100, and 75. This imbalance is acceptable for the focused
initial cohort but must remain visible in dataset and product claims.

## Stability distribution

| Band | Materials | Fraction |
|---|---:|---:|
| Source stable flag | 141 | 8.16% |
| Energy above hull exactly zero | 141 | 8.16% |
| Above zero through 0.025 eV/atom | 622 | 36.02% |
| Above 0.025 through 0.05 eV/atom | 964 | 55.82% |

The source stable flag and exact-zero counts agree. Most records are bounded
near-stable computational candidates rather than source-stable materials.
MaterialGraph must preserve this distinction in filters, evidence, ranking
explanations, and exports.

## Formula and polymorph representation

The cohort contains 651 unique formulas. Of these, 417 occur once and 234 have
multiple source identities. Those polymorph groups contain 1,310 materials
(75.85% of the cohort); the largest formula groups contain 70 and 73 source
identities.

This density is consistent with the explicit decision to preserve Materials
Project identities rather than merge on formula. It is scientifically useful
for phase-sensitive discovery, but formula-equivalent identities can crowd
ranked results. Before expanded data is publicly presented, the product must
identify polymorphs clearly and provide diversity or grouping behavior without
silently discarding source identities.

## Accepted limitations and presentation requirements

- Sulfide analysis is exploratory because only 15 records are present.
- `Li-Fe-S` and `Na-Ni-S` are complete-query source zeroes at the approved
  release and energy ceiling; they do not prove that such materials do not
  exist.
- Lithium-heavy and oxygen-heavy representation reflects the reviewed focused
  source contract and cannot support domain-wide prevalence claims.
- A source-stable material and a bounded near-stable candidate must never be
  presented as equivalent evidence.
- Formula equality must not collapse polymorphs, while interfaces and ranking
  results must prevent unexplained polymorph crowding.
- Displays and exports must attribute Materials Project, identify database
  release `2026.04.13`, retain retrieval provenance, state CC BY 4.0, and link
  users to source and license information.

## Authorization boundary

MG-DE-006 authorizes only planning and execution of a disposable local
PostgreSQL qualification using the exact approved manifest. It does not
authorize writes to shared development databases, isolated Neon, production
Neon, production EC2 deployment, public dataset publication, schema changes,
service restart, backup restoration, or a production canary.
