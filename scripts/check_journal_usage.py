import argparse
import logging
import shutil
from pathlib import Path


LOGGER = logging.getLogger("materialgraph.journal_monitor")
DEFAULT_JOURNAL_WARNING_BYTES = 230 * 1024 * 1024
DEFAULT_FILESYSTEM_WARNING_PERCENT = 80.0


def journal_usage_bytes(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        if not path.exists():
            continue
        for entry in path.rglob("*"):
            if not entry.is_file():
                continue
            file_stat = entry.stat()
            allocated_blocks = getattr(file_stat, "st_blocks", None)
            total += (
                allocated_blocks * 512
                if allocated_blocks is not None
                else file_stat.st_size
            )
    return total


def filesystem_used_percent(path: Path) -> float:
    usage = shutil.disk_usage(path)
    return usage.used / usage.total * 100


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--journal-warning-bytes",
        type=int,
        default=DEFAULT_JOURNAL_WARNING_BYTES,
    )
    parser.add_argument(
        "--filesystem-warning-percent",
        type=float,
        default=DEFAULT_FILESYSTEM_WARNING_PERCENT,
    )
    args = parser.parse_args()

    journal_bytes = journal_usage_bytes([
        Path("/var/log/journal"),
        Path("/run/log/journal"),
    ])
    filesystem_percent = filesystem_used_percent(Path("/"))
    threshold_exceeded = (
        journal_bytes >= args.journal_warning_bytes
        or filesystem_percent >= args.filesystem_warning_percent
    )

    logging.basicConfig(level=logging.INFO)
    LOGGER.log(
        logging.WARNING if threshold_exceeded else logging.INFO,
        "journal_usage_check status=%s journal_bytes=%d "
        "filesystem_used_percent=%.2f",
        "warning" if threshold_exceeded else "ok",
        journal_bytes,
        filesystem_percent,
    )
    return 1 if threshold_exceeded else 0


if __name__ == "__main__":
    raise SystemExit(main())
