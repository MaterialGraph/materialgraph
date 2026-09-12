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
    st_gid: int
    st_nlink: int


def verify_secret_metadata(
    file_stat: FileMetadata,
    expected_uid: int,
    expected_gid: int,
    expected_mode: int = 0o600,
) -> None:
    if not stat.S_ISREG(file_stat.st_mode):
        raise SecretFileError("secret path must be a regular file")
    if file_stat.st_uid != expected_uid:
        raise SecretFileError("secret file has an unexpected owner")
    if file_stat.st_gid != expected_gid:
        raise SecretFileError("secret file has an unexpected group")
    if stat.S_IMODE(file_stat.st_mode) != expected_mode:
        raise SecretFileError(
            f"secret file mode must be exactly {expected_mode:o}"
        )
    if file_stat.st_nlink != 1:
        raise SecretFileError("secret file must have exactly one hard link")


def verify_secret_file(
    path: Path,
    expected_mode: int = 0o600,
    expected_uid: int | None = None,
    expected_gid: int | None = None,
) -> None:
    file_stat = path.lstat()
    if expected_uid is None:
        expected_uid = getattr(os, "geteuid", lambda: file_stat.st_uid)()
    if expected_gid is None:
        expected_gid = getattr(os, "getegid", lambda: file_stat.st_gid)()
    verify_secret_metadata(
        file_stat,
        expected_uid,
        expected_gid,
        expected_mode,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify secret-file metadata without reading its contents."
    )
    parser.add_argument("path", type=Path)
    parser.add_argument("--owner-uid", type=int, default=None)
    parser.add_argument(
        "--mode",
        type=lambda value: int(value, 8),
        default=0o600,
    )
    args = parser.parse_args()

    try:
        verify_secret_file(
            args.path,
            expected_mode=args.mode,
            expected_uid=args.owner_uid,
        )
    except (OSError, SecretFileError):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
