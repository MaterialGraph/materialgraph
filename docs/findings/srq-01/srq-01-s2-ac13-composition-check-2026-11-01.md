# SRQ-01 — AC13 stored-composition check

| Field | Value |
|---|---|
| Date | 2026-11-01 |
| Purpose | Measure, before PR-A, how many stored compositions the application can use for exact alkali formula analog (EFA) classification |
| Database | Local Docker PostgreSQL, `materialgraph_test_mg_de_007` (1,727 materials) |
| Code | `main` at `0374c28`; functions `normalise_stored_composition` and `compositions_equal` from `app/services/material/search_service.py` |
| Method | Read-only Python script outside the repository; `SELECT` queries only |

## 1. Usable stored composition

| Measure | Count |
|---|---|
| Records | 1,727 |
| Usable (`normalise_stored_composition` succeeds) | 1,727 |
| Not usable | 0 |

## 2. Consistency with element records

Stored-composition element sets were compared with each material's `material_elements` symbols.

| Measure | Count |
|---|---|
| Records with differing element sets | 0 |

The basis for EFA classification (stored composition) and the basis for today's candidate pool (element records) agree for every record.

## 3. Alkali content

| Alkali present | Records |
|---|---|
| Li only | 1,213 |
| Na only | 276 |
| K only | 63 |
| None | 175 |
| More than one alkali | 0 |
| Rb or Cs | 0 |

No current record can produce the reason codes `replacement_alkali_in_source`, `replaced_alkali_in_candidate` or `multiple_alkali_changes`. At most two EFA groups per source can exist (for a Li source: Na and K).

## 4. Rule sanity check on real data

LiFePO₄ (mp-19017) composition with Li replaced by Na, compared using `compositions_equal` (TAU = 1e-6):

| Candidate | Formula | Exact match |
|---|---|---|
| mp-19226 | NaFePO₄ | True |
| mp-746030 | NaFePO₄ | True |
| mp-753672 | NaFePO₄ | True |
| mp-1192859 | NaFePO₄ | True |
| mp-19028 | Na₃Fe(PO₄)₂ | False |

## 5. Limitations

Local database equality with production was not verified record by record. The check exercises existing functions directly; it is not a test of PR-A code, which does not yet exist.
