import argparse
import json
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare complete pre/post MG-DE-004 JSON responses."
    )
    parser.add_argument("--before-directory", type=Path, required=True)
    parser.add_argument("--after-directory", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    before_files = {
        path.name: path for path in args.before_directory.glob("*.json")
    }
    after_files = {
        path.name: path for path in args.after_directory.glob("*.json")
    }
    if not before_files or before_files.keys() != after_files.keys():
        raise ValueError("pre/post JSON file sets are nonempty and identical")

    mismatches = []
    for name in sorted(before_files):
        before = json.loads(before_files[name].read_text(encoding="utf-8"))
        after = json.loads(after_files[name].read_text(encoding="utf-8"))
        if before != after:
            mismatches.append(name)
        else:
            print(f"{name}=match")
    if mismatches:
        print("mismatches=" + ",".join(mismatches))
        return 1
    print(f"complete_json_comparisons={len(before_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
