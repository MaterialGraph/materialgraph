import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from app.services.material.import_pipeline import (
    MaterialDatasetContract,
    MaterialImportPipeline,
    MaterialImportScope,
)
from app.services.material.project_service import MaterialsProjectService


DEFAULT_CHEMICAL_SYSTEMS = (
    "Li-Fe-P-O",
    "Na-Fe-P-O",
    "Na-Mn-O",
    "Mg-Mn-O",
    "Li-Mn-O",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build or apply a deterministic Materials Project import manifest. "
            "Building is the default and never writes to the database."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--source-release",
        help="Authoritative Materials Project database release identifier.",
    )
    parser.add_argument(
        "--retrieved-at",
        help="Timezone-aware ISO-8601 start time for this source retrieval.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply an existing validated manifest in resumable chunks.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        help="Checkpoint path; required with --apply.",
    )
    parser.add_argument(
        "--expected-database-name",
        help="Exact database name required before manifest application.",
    )
    parser.add_argument(
        "--allow-non-test-database",
        action="store_true",
        help="Explicitly permit application outside a database named as test.",
    )
    parser.add_argument(
        "--chemical-system",
        action="append",
        dest="chemical_systems",
        help="Repeat to set build scope; defaults to the curated systems.",
    )
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--max-materials", type=int, default=1_000)
    parser.add_argument("--max-source-records", type=int, default=2_000)
    parser.add_argument("--max-pages-per-system", type=int, default=25)
    parser.add_argument("--max-fetch-attempts", type=int, default=3)
    parser.add_argument("--include-unstable", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.apply:
        if args.source_release is not None or args.retrieved_at is not None:
            raise ValueError("source provenance options are only valid when building")
        if args.checkpoint is None:
            raise ValueError("--checkpoint is required with --apply")
        if not args.expected_database_name:
            raise ValueError("--expected-database-name is required with --apply")
        if not args.manifest.is_file():
            raise ValueError("--apply requires an existing manifest file")

        from app.core.database import SessionLocal, engine
        from app.services.material.import_service import MaterialImportService

        actual_database_name = engine.url.database or ""
        if args.expected_database_name != actual_database_name:
            raise ValueError(
                "configured database does not match --expected-database-name"
            )
        if "test" not in actual_database_name.lower() and not args.allow_non_test_database:
            raise ValueError(
                "refusing to apply to a non-test database without explicit permission"
            )

        db = SessionLocal()
        try:
            result = MaterialImportPipeline.apply_manifest(
                manifest_path=args.manifest,
                checkpoint_path=args.checkpoint,
                importer=MaterialImportService(db),
            )
        finally:
            db.close()

        print(json.dumps(asdict(result), sort_keys=True))
        return 2 if result.conflicted else 0

    if args.checkpoint is not None:
        raise ValueError("--checkpoint is only valid with --apply")
    if args.expected_database_name is not None or args.allow_non_test_database:
        raise ValueError("database confirmation options are only valid with --apply")
    if not args.source_release or not args.retrieved_at:
        raise ValueError("--source-release and --retrieved-at are required when building")
    if args.manifest.exists():
        raise ValueError("refusing to overwrite an existing manifest")
    configured_env_file = os.getenv("MATERIALGRAPH_ENV_FILE")
    if configured_env_file != "":
        load_dotenv(configured_env_file or ".env")
    api_key = os.getenv("MATERIALS_PROJECT_API_KEY")
    if not api_key:
        raise ValueError("MATERIALS_PROJECT_API_KEY is not configured")

    scope = MaterialImportScope(
        chemical_systems=tuple(args.chemical_systems or DEFAULT_CHEMICAL_SYSTEMS),
        page_size=args.page_size,
        chunk_size=args.chunk_size,
        max_materials=args.max_materials,
        max_source_records=args.max_source_records,
        max_pages_per_system=args.max_pages_per_system,
        max_fetch_attempts=args.max_fetch_attempts,
        stable_only=not args.include_unstable,
    )
    pipeline = MaterialImportPipeline(
        MaterialsProjectService(
            api_key=api_key,
            database_version=args.source_release,
        ),
        on_fetch_retry=lambda chemsys, page, attempt: print(
            json.dumps(
                {
                    "event": "fetch_retry",
                    "chemical_system": chemsys,
                    "page": page,
                    "failed_attempt": attempt,
                },
                sort_keys=True,
            )
        ),
    )
    result = pipeline.build_manifest(
        scope=scope,
        dataset=MaterialDatasetContract(
            source_release=args.source_release,
            retrieved_at=args.retrieved_at,
        ),
        manifest_path=args.manifest,
    )
    print(json.dumps({**asdict(result), "path": str(result.path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
