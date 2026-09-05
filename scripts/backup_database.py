#!/usr/bin/env python3
"""Create and remotely verify a MaterialGraph PostgreSQL logical backup."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

import psycopg
from dotenv import dotenv_values
from sqlalchemy.engine import make_url


LOGGER = logging.getLogger("materialgraph.backup")
DEFAULT_APPLICATION_ENV = Path("/opt/materialgraph/.env")
DEFAULT_STATE_DIRECTORY = Path("/var/lib/materialgraph-backup")
REQUIRED_COMMANDS = ("pg_dump", "pg_restore", "aws", "git")


class BackupError(RuntimeError):
    """Raised when a backup cannot be completed and verified safely."""


def required_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise BackupError(f"required setting is absent: {name}")
    return value


def safe_prefix(value: str) -> str:
    prefix = value.strip().strip("/")
    if not prefix or any(part in {"", ".", ".."} for part in prefix.split("/")):
        raise BackupError("MATERIALGRAPH_BACKUP_PREFIX is invalid")
    return prefix


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(
    command: list[str],
    *,
    environment: dict[str, str] | None = None,
    capture_output: bool = True,
    timeout: int = 1_500,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=capture_output,
            text=True,
            env=environment,
            timeout=timeout,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise BackupError(f"command failed: {Path(command[0]).name}") from exc


def database_environment(database_url: str) -> dict[str, str]:
    url = make_url(database_url)
    required = (url.host, url.database, url.username, url.password)
    if not all(required):
        raise BackupError("database backup connection is incomplete")

    environment = os.environ.copy()
    environment.update(
        {
            "PGHOST": str(url.host),
            "PGPORT": str(url.port or 5432),
            "PGDATABASE": str(url.database),
            "PGUSER": str(url.username),
            "PGPASSWORD": str(url.password),
            "PGSSLMODE": "require",
            "PGCHANNELBINDING": "require",
            "PGCONNECT_TIMEOUT": "15",
        }
    )
    return environment


def load_database_url(path: Path) -> str:
    values = dotenv_values(path)
    for key in ("DATABASE_MIGRATION_URL", "DATABASE_URL"):
        value = values.get(key)
        if value and value.strip():
            return value.strip()
    raise BackupError(f"database URL is absent from {path}")


@contextmanager
def exclusive_lock(path: Path) -> Iterator[None]:
    import fcntl

    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BackupError("another backup run is active") from exc
        yield


def connection_parameters(pg_environment: dict[str, str]) -> dict[str, Any]:
    return {
        "host": pg_environment["PGHOST"],
        "port": int(pg_environment["PGPORT"]),
        "dbname": pg_environment["PGDATABASE"],
        "user": pg_environment["PGUSER"],
        "password": pg_environment["PGPASSWORD"],
        "sslmode": pg_environment["PGSSLMODE"],
        "channel_binding": "require",
        "connect_timeout": int(pg_environment["PGCONNECT_TIMEOUT"]),
    }


def collect_database_manifest(connection: psycopg.Connection[Any]) -> dict[str, Any]:
    with connection.cursor() as cursor:
        cursor.execute("SHOW server_version")
        postgres_version = cursor.fetchone()[0]
        cursor.execute("SELECT version_num FROM alembic_version ORDER BY version_num")
        alembic_revisions = [row[0] for row in cursor.fetchall()]
        cursor.execute(
            """
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
            """
        )
        table_names = [row[0] for row in cursor.fetchall()]
        table_counts: dict[str, int] = {}
        for table_name in table_names:
            query = psycopg.sql.SQL("SELECT count(*) FROM {}").format(
                psycopg.sql.Identifier(table_name)
            )
            cursor.execute(query)
            table_counts[table_name] = cursor.fetchone()[0]

        representative_ids: dict[str, list[str]] = {}
        for table_name in ("materials", "elements", "applications"):
            if table_name not in table_names:
                continue
            cursor.execute(
                psycopg.sql.SQL("SELECT id::text FROM {} ORDER BY id LIMIT 3").format(
                    psycopg.sql.Identifier(table_name)
                )
            )
            representative_ids[table_name] = [row[0] for row in cursor.fetchall()]

    return {
        "postgres_version": postgres_version,
        "alembic_revisions": alembic_revisions,
        "table_counts": table_counts,
        "representative_ids": representative_ids,
    }


def git_commit(project_root: Path) -> str:
    return run(["git", "-C", str(project_root), "rev-parse", "HEAD"]).stdout.strip()


def upload_object(
    path: Path,
    *,
    bucket: str,
    key: str,
    region: str,
    sha256: str,
) -> None:
    response = run(
        [
            "aws",
            "s3api",
            "put-object",
            "--bucket",
            bucket,
            "--key",
            key,
            "--body",
            str(path),
            "--server-side-encryption",
            "AES256",
            "--metadata",
            f"sha256={sha256}",
            "--region",
            region,
            "--output",
            "json",
        ]
    )
    parsed = json.loads(response.stdout)
    if parsed.get("ServerSideEncryption") != "AES256":
        raise BackupError(f"S3 did not confirm SSE-S3 for {key}")


def remote_object_size(*, bucket: str, key: str, region: str) -> int:
    response = run(
        [
            "aws",
            "s3api",
            "list-objects-v2",
            "--bucket",
            bucket,
            "--prefix",
            key,
            "--max-items",
            "2",
            "--region",
            region,
            "--output",
            "json",
        ]
    )
    matches = [
        item
        for item in json.loads(response.stdout).get("Contents", [])
        if item.get("Key") == key
    ]
    if len(matches) != 1:
        raise BackupError(f"remote object verification failed: {key}")
    if not matches[0].get("LastModified"):
        raise BackupError(f"remote creation time is absent: {key}")
    return int(matches[0]["Size"])


def execute_backup() -> None:
    for command in REQUIRED_COMMANDS:
        if shutil.which(command) is None:
            raise BackupError(f"required command is unavailable: {command}")

    bucket = required_setting("MATERIALGRAPH_BACKUP_BUCKET")
    region = os.environ.get("MATERIALGRAPH_BACKUP_REGION", "ap-south-1").strip()
    prefix = safe_prefix(os.environ.get("MATERIALGRAPH_BACKUP_PREFIX", "production"))
    application_env = Path(
        os.environ.get("MATERIALGRAPH_APPLICATION_ENV", DEFAULT_APPLICATION_ENV)
    )
    state_directory = Path(
        os.environ.get("MATERIALGRAPH_BACKUP_STATE_DIRECTORY", DEFAULT_STATE_DIRECTORY)
    )
    project_root = Path(os.environ.get("MATERIALGRAPH_PROJECT_ROOT", "/opt/materialgraph"))

    database_url = load_database_url(application_env)
    pg_environment = database_environment(database_url)
    created_at = datetime.now(UTC)
    backup_id = created_at.strftime("%Y%m%dT%H%M%SZ")
    object_prefix = f"{prefix}/{backup_id}"

    with exclusive_lock(state_directory / "backup.lock"):
        with tempfile.TemporaryDirectory(prefix="run-", dir=state_directory) as temporary_directory:
            work_directory = Path(temporary_directory)
            dump_path = work_directory / "database.dump"
            manifest_path = work_directory / "manifest.json"

            with psycopg.connect(**connection_parameters(pg_environment)) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY"
                    )
                    cursor.execute("SELECT pg_export_snapshot()")
                    snapshot_id = cursor.fetchone()[0]
                run(
                    [
                        "pg_dump",
                        "--format=custom",
                        "--compress=9",
                        "--no-owner",
                        "--no-privileges",
                        "--snapshot",
                        snapshot_id,
                        "--file",
                        str(dump_path),
                    ],
                    environment=pg_environment,
                )
                source = collect_database_manifest(connection)
            os.chmod(dump_path, 0o600)
            if dump_path.stat().st_size == 0:
                raise BackupError("pg_dump produced an empty archive")
            run(["pg_restore", "--list", str(dump_path)])

            dump_sha256 = sha256_file(dump_path)
            manifest = {
                "format_version": 1,
                "backup_id": backup_id,
                "created_at_utc": created_at.isoformat(),
                "application_commit": git_commit(project_root),
                "archive": {
                    "format": "postgresql-custom",
                    "filename": dump_path.name,
                    "bytes": dump_path.stat().st_size,
                    "sha256": dump_sha256,
                },
                "source": source,
            }
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.chmod(manifest_path, 0o600)
            manifest_sha256 = sha256_file(manifest_path)

            objects = (
                (dump_path, f"{object_prefix}/database.dump", dump_sha256),
                (manifest_path, f"{object_prefix}/manifest.json", manifest_sha256),
            )
            for path, key, checksum in objects:
                upload_object(path, bucket=bucket, key=key, region=region, sha256=checksum)
                remote_size = remote_object_size(
                    bucket=bucket,
                    key=key,
                    region=region,
                )
                if remote_size != path.stat().st_size:
                    raise BackupError(f"remote size mismatch: {key}")

            LOGGER.info(
                "backup_verified backup_id=%s archive_bytes=%d archive_sha256=%s table_count=%d",
                backup_id,
                dump_path.stat().st_size,
                dump_sha256,
                len(source["table_counts"]),
            )


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    os.umask(0o077)
    try:
        execute_backup()
    except Exception as exc:  # systemd must receive a failure for every unsafe outcome
        LOGGER.error("backup_failed category=%s", type(exc).__name__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
