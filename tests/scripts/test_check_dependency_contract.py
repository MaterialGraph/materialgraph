from pathlib import Path

import pytest

from scripts.check_dependency_contract import (
    input_pins,
    lock_pins,
    snapshot_pins,
    validate_contracts,
    validate_snapshot,
)


def test_repository_dependency_contract_is_complete_and_hashed():
    root = Path(__file__).resolve().parents[2]

    for stem in ("production", "audit"):
        direct = input_pins(root / f"requirements-{stem}.in")
        locked = lock_pins(root / f"requirements-{stem}.lock")

        assert direct.items() <= locked.items()

    production, errors = validate_contracts()

    assert errors == []
    assert production["pillow"] == "12.3.0"
    assert production["pydantic-settings"] == "2.14.2"
    assert production["starlette"] == "1.3.1"


def test_lock_parser_rejects_an_unhashed_requirement(tmp_path):
    lock = tmp_path / "requirements.lock"
    lock.write_text("example==1.0\n", encoding="utf-8")

    with pytest.raises(ValueError, match="has no SHA-256 hash"):
        lock_pins(lock)


def test_lock_parser_rejects_external_requirement_url(tmp_path):
    lock = tmp_path / "requirements.lock"
    lock.write_text(
        "example==1.0 --hash=sha256:" + "a" * 64 + "\nhttps://example.test/x\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsafe external requirement"):
        lock_pins(lock)


def test_developer_snapshot_mirrors_the_test_lock():
    root = Path(__file__).resolve().parents[2]
    snapshot = snapshot_pins(root / "requirements.txt")
    test_locked = lock_pins(root / "requirements-test.lock")

    assert validate_snapshot(snapshot, test_locked) == []
    assert snapshot["httpx2"] == test_locked["httpx2"]
    assert "pip" not in snapshot


def test_developer_snapshot_rejects_drift_and_unreviewed_extras(tmp_path):
    locked = {"anyio": "4.15.1", "pip": "26.2.1"}

    assert validate_snapshot({"anyio": "4.15.1"}, locked) == []
    assert validate_snapshot({"anyio": "4.15.1", "ruff": "0.15.15"}, locked) == []

    drift = validate_snapshot({"anyio": "4.13.0"}, locked)
    assert drift and "anyio==4.15.1 differs" in drift[0]

    missing = validate_snapshot({}, locked)
    assert missing and "anyio==4.15.1 differs or is missing" in missing[0]

    stray = validate_snapshot({"anyio": "4.15.1", "httpcore": "1.0.9"}, locked)
    assert stray and "httpcore==1.0.9 is not in" in stray[0]


def test_developer_snapshot_parser_accepts_markers_only(tmp_path):
    snapshot = tmp_path / "requirements.txt"
    snapshot.write_text(
        "# comment\nuvloop==0.22.1; sys_platform != \"win32\"\nruff==0.15.15\n",
        encoding="utf-8",
    )
    assert snapshot_pins(snapshot) == {"uvloop": "0.22.1", "ruff": "0.15.15"}

    snapshot.write_text("-e git+https://example.test/x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="expected name==version"):
        snapshot_pins(snapshot)
