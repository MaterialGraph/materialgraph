from dataclasses import dataclass
import os
from pathlib import Path
import stat

import pytest

from scripts.verify_secret_file import (
    SecretFileError,
    verify_secret_file,
    verify_secret_metadata,
)


@dataclass
class Metadata:
    st_mode: int = stat.S_IFREG | 0o600
    st_uid: int = 1000
    st_nlink: int = 1


def test_accepts_valid_metadata():
    verify_secret_metadata(Metadata(), effective_uid=1000)


@pytest.mark.skipif(os.name == "nt", reason="POSIX mode integration")
def test_accepts_owner_only_regular_file(tmp_path: Path):
    secret_file = tmp_path / "runtime.env"
    secret_file.write_text("placeholder=true\n", encoding="utf-8")
    secret_file.chmod(0o600)

    verify_secret_file(secret_file)


@pytest.mark.parametrize("mode", [0o400, 0o640, 0o644, 0o660, 0o664])
def test_rejects_mode_other_than_600(mode: int):
    with pytest.raises(SecretFileError, match="mode must be exactly 600"):
        verify_secret_metadata(
            Metadata(st_mode=stat.S_IFREG | mode),
            effective_uid=1000,
        )


def test_rejects_non_regular_metadata():
    with pytest.raises(SecretFileError, match="regular file"):
        verify_secret_metadata(
            Metadata(st_mode=stat.S_IFLNK | 0o600),
            effective_uid=1000,
        )


def test_rejects_wrong_owner():
    with pytest.raises(SecretFileError, match="owned by the service user"):
        verify_secret_metadata(Metadata(st_uid=1001), effective_uid=1000)


def test_rejects_multiple_hard_links():
    with pytest.raises(SecretFileError, match="exactly one hard link"):
        verify_secret_metadata(Metadata(st_nlink=2), effective_uid=1000)
