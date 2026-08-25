# MG-IA-003 Change Impact — Populated Core-Domain Migration

## Status

Verified locally: 1 focused migration test, 18 adjacent tests, 647 full-suite
tests, Ruff, and Git whitespace validation passed.

## Before

Revision `1d204c6d38c0` added `materials.source` as non-null immediately. A
database containing valid rows from predecessor revision `4368e3ecc291` could
not satisfy that operation because those rows had no source value.

## After

The migration adds the column as nullable, labels predecessor rows with the
explicit provenance state `legacy_unknown`, and then enforces `NOT NULL`.

## Impact

- Migration reliability: **Yes** — populated predecessor databases can
  upgrade.
- Scientific honesty: **Yes** — historical provenance is marked unknown
  rather than guessed.
- Runtime API behavior: **No change**.
- Runtime scoring or ranking: **No change**.
- Current deployed databases already at or beyond the revision: **No automatic
  mutation**.
- Fresh databases and future migration replay: **Use the corrected transition**.
- Downgrade contract: **Unchanged** — the existing downgrade removes the
  source column.
