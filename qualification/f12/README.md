# F12 dataset-pinned qualification

`qualify_dataset.py` checks a running MaterialGraph backend against an
expectations file. It uses only the Python standard library, sends only GET
requests, and pauses about 0.25 s between requests to stay well under the
admission limits.

This directory is not collected by pytest (no file is named `test_*.py` or
`*_test.py`) and no CI workflow runs it. It is run by hand.

## Usage

```
python qualification/f12/qualify_dataset.py --base-url <url> --expectations <file> --mode baseline|qualify [--no-auth] [--report <path>]
```

- `--base-url`: the backend root, for example `http://127.0.0.1:8000`.
- `--expectations`: an expectations JSON file, such as
  `production-2026.04.13.json`.
- `--mode`: `qualify` (the default) or `baseline`.
- `--no-auth`: send no credentials, for a local backend. Without it the script
  prompts for the HTTP Basic Auth username and password with `getpass`. The
  credentials are held in memory only; they are never echoed, logged, stored,
  printed or written to the report.
- `--report`: write a JSON report of the observations and results. It contains
  no credentials.

## Steps

1. **Precondition** (both modes). One formula search (`LiFePO4`, limit 1)
   supplies the dataset block. `source_release`, `dataset_total` and
   `composition_exclusion_count` must equal the expectations; otherwise the
   script prints `fixture is for a different dataset` and stops. Release and
   count are a precondition, not proof of dataset identity.
2. **Fingerprint** (both modes). Every material is read from
   `GET /api/v1/materials` in pages of 100. The row count must equal
   `dataset_total`. The fingerprint is the SHA-256 of the UTF-8 bytes of
   `json.dumps(rows, separators=(",", ":"), ensure_ascii=True)`, where `rows` is
   `[id, mp_id, formula, energy_above_hull]` per material, sorted by `id`.
   - `baseline` prints the fingerprint and row count and stops. It runs no
     search cases, so it also works on a Release 1 backend.
   - `qualify` stops if the expectations have no fingerprint, or if the
     fingerprint differs (`dataset differs from the qualified fixture`).
3. **Cases** (`qualify` only, after both checks pass), each PASS or FAIL:
   formula FePO4Li, formula NaFePO4, chemsys Li-Fe-P-O (all pages, element sets),
   formula Ti2C (zero matches with a scoped message), formula lifepo4 (422
   `invalid_formula`), mp_id mp-19017, auto `#5`, and
   `GET /api/v1/materials/dataset-summary` equal to the Step 1 dataset block.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Baseline captured, or every case passed |
| 1 | At least one case failed |
| 2 | Dataset mismatch: precondition, row count or fingerprint; no cases run |
| 3 | `qualify` with no fingerprint in the expectations; no cases run |
| 4 | Connection failure, timeout, refused credentials or an unexpected HTTP status |

## Expectations

`production-2026.04.13.json` holds the production values. Its material IDs are
production local IDs. `fingerprint` stays `null` until it is captured with
`--mode baseline` against production.

Expectations change only through a reviewed change: never edit them to make a
run pass.
