import argparse
import json
from dataclasses import asdict
from pathlib import Path

from app.services.material.benchmark_fixture import (
    build_representative_fixture_manifest,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the deterministic offline MG-DE-004 fixture manifest."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--target-materials", type=int, default=1_000)
    parser.add_argument("--chunk-size", type=int, default=100)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = build_representative_fixture_manifest(
        manifest_path=args.manifest,
        target_materials=args.target_materials,
        chunk_size=args.chunk_size,
    )
    print(json.dumps({**asdict(result), "path": str(result.path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
