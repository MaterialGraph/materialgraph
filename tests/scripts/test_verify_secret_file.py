import os
from pathlib import Path

import pytest

from scripts.verify_secret_file import SecretFileError, verify_secret_file


def test_accepts_owner_only_regular_file(tmp_path: Path):
    secret_file = tmp_path / "runtime.env"
    secret_file.write_text("placeholder=true\n", encoding="utf-8")
    secret_file.chmod(0o600)

    verify_secret_file(secret_file)


@pytest.mark.parametrize("mode", [0o400, 0o640, 0o644, 0o660, 0o664])
def test_rejects_mode_other_than_600(tmp_path: Path, mode: int):
    secret_file = tmp_path / "runtime.env"
    secret_file.write_text("placeholder=true\n", encoding="utf-8")
    secret_file.chmod(mode)

    with pytest.raises(SecretFileError, match="mode must be exactly 600"):
        verify_secret_file(secret_file)


@pytest.mark.skipif(os.name == "nt", reason="Windows symlinks require privileges")
def test_rejects_symbolic_link(tmp_path: Path):
    secret_file = tmp_path / "runtime.env"
    secret_file.write_text("placeholder=true\n", encoding="utf-8")
    secret_file.chmod(0o600)
    link = tmp_path / "runtime-link.env"
    link.symlink_to(secret_file)

    with pytest.raises(SecretFileError, match="regular file"):
        verify_secret_file(link)


def test_rejects_multiple_hard_links(tmp_path: Path):
    secret_file = tmp_path / "runtime.env"
    secret_file.write_text("placeholder=true\n", encoding="utf-8")
    secret_file.chmod(0o600)
    os.link(secret_file, tmp_path / "runtime-copy.env")

    with pytest.raises(SecretFileError, match="exactly one hard link"):
        verify_secret_file(secret_file)
