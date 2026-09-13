from pathlib import Path

from scripts.check_journal_usage import journal_usage_bytes


def test_journal_usage_sums_only_files(tmp_path: Path):
    persistent = tmp_path / "persistent"
    volatile = tmp_path / "volatile"
    persistent.mkdir()
    volatile.mkdir()
    (persistent / "system.journal").write_bytes(b"a" * 17)
    (volatile / "runtime.journal").write_bytes(b"b" * 23)

    assert journal_usage_bytes([persistent, volatile]) == 40


def test_journal_usage_ignores_missing_directories(tmp_path: Path):
    assert journal_usage_bytes([tmp_path / "missing"]) == 0
