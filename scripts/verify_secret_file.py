import argparse
import os
import stat
from pathlib import Path
from typing import Protocol


class SecretFileError(RuntimeError):
    """Raised when a secret file does not meet the deployment boundary."""


class FileMetadata(Protocol):
    st_mode: int
    st_uid: int
    st_nlink: int


def verify_secret_metadata(
    file_stat: FileMetadata,
    effective_uid: int,
    expected_mode: int = 0o600,
) -> None:
    if not stat.S_ISREG(file_stat.st_mode):
        raise SecretFileError("secret path must be a regular file")
    if file_stat.st_uid != effective_uid:
        raise SecretFileError("secret file must be owned by the service user")
    if stat.S_IMODE(file_stat.st_mode) != expected_mode:
        raise SecretFileError("secret file mode must be exactly 600")
    if file_stat.st_nlink != 1:
        raise SecretFileError("secret file must have exactly one hard link")


def verify_secret_file(path: Path, expected_mode: int = 0o600) -> None:
    file_stat = path.lstat()
    effective_uid = getattr(os, "geteuid", lambda: file_stat.st_uid)()
    verify_secret_metadata(file_stat, effective_uid, expected_mode)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify secret-file metadata without reading its contents."
    )
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    try:
        verify_secret_file(args.path)
    except (OSError, SecretFileError):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
