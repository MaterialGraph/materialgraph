# MG-IA-IMP-001 — Repair corrupted multiplication symbols in criticality-test comments

- Classification: maintainability improvement
- Priority: P3
- Confidence: high

`test_criticality_service.py` contains `Ã—` in three arithmetic comments. Execution is unaffected, but the comments are harder to read and may indicate an editor/encoding mismatch. Replace the corrupted character with `×` or ASCII `*` and retain UTF-8 consistency.
