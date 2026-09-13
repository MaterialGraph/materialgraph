from pathlib import Path

import pytest

from scripts.check_dependency_contract import (
    input_pins,
    lock_pins,
    validate_contracts,
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
