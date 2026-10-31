# SRQ-01 — S2 local data checks

| Field | Value |
|---|---|
| Date | 2026-10-31 |
| Purpose | Section 7, step 2 of the S2 specification (rev 3.1): data facts needed before PR-0 and PR-A |
| Database | Local Docker PostgreSQL 16, database `materialgraph_test_mg_de_007` (1,727 materials) |
| Method | Read-only `SELECT` queries in psql; no writes |

## 1. Dataset identity

The local database holds 1,727 materials, the same count as production (MP release 2026.04.13 import plus 28 curated records).

| MP ID | Formula | Local ID | Production ID (S1) |
|---|---|---|---|
| mp-19017 | LiFePO₄ | 5 | 5 |
| mp-19028 | Na₃Fe(PO₄)₂ | 6 | 6 |
| mp-19226 | NaFePO₄ | 10 | 10 |
| mp-1040459 | NaFe₃P₃O₁₃ | 2594 | 70 |
| mp-1192859 | NaFePO₄ | 2908 | 384 |
| mp-746030 | NaFePO₄ | 3618 | 1094 |

Curated records keep the same local IDs as production. **Imported records have different local IDs.** Local ID is therefore not a stable identity across environments, which supports using MP ID for ordering (R5). Full record-level equality with production was not verified.

## 2. MP ID format

All 1,727 MP IDs match `^mp-[0-9]+$` (0 non-matching rows). The R5 numeric key applies to every record; the fallback for non-matching IDs is still specified but currently unused.

## 3. NaFePO₄ records

| MP ID | Local ID | Energy above hull (eV/atom) | `is_stable` |
|---|---|---|---|
| mp-19226 | 10 | 0 | true |
| mp-746030 | 3618 | 0.0049 | false |
| mp-753672 | 3671 | 0.0058 | false |
| mp-1192859 | 2908 | 0.0404 | false |

The fourth record, unconfirmed in the S1 finding, is **mp-753672**. Its production local ID was not checked. Which record corresponds to which NaFePO₄ polymorph remains unverified.

## 4. Stored composition

| Measure | Count |
|---|---|
| Records | 1,727 |
| `raw_data` missing | 0 |
| `raw_data.composition` missing | 0 |
| `raw_data.composition` is a JSON object | 1,727 |

Curated and imported records store composition in the same shape: element → amount per unit cell. For example, NaFePO₄ (mp-19226 and mp-746030) is stored as Na 4, Fe 4, P 4, O 16, and Na₃Fe(PO₄)₂ (mp-19028) as Na 6, Fe 2, P 4, O 16. Key order differs between import paths, which does not affect comparison.

Implications for the specification:

- Cell-based amounts confirm that EFA comparison must use normalised fractions (2.1, D8); comparing raw amounts or formula strings would fail.
- Normalised, LiFePO₄ and all four NaFePO₄ records correspond under Li→Na, and Na₃Fe(PO₄)₂ does not (`ratios_differ`), consistent with AC2.
- 1,727 is an upper bound for usable compositions. The exact AC13 count depends on the exclusions in `normalise_stored_composition` and will be measured in code.

## 5. Not established by these checks

Record-level equality between this database and production; production local IDs for mp-753672; polymorph identity; the AC13 usable-composition count.
