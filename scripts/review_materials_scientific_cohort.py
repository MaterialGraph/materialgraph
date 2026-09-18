import argparse
import json
from pathlib import Path

from app.services.material.cohort_review import (
    evaluate_review_integrity,
    review_scientific_cohort,
)
from app.services.material.import_pipeline import (
    MATERIALS_PROJECT_SOURCE,
    MaterialImportPipeline,
)

MG_DE_006_MANIFEST_SHA256 = (
    "902109235f7d3da057537b73e240130b5a9e4d847852e39c52f43e2798b8a9b9"
)
MG_DE_006_SELECTION_CONTRACT = "materials-project-selection-v3"
MG_DE_006_ACCEPTED = 1_727


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Produce an offline scientific-cohort review report without "
            "network or database access."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sparse-system-threshold", type=int, default=5)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.manifest.is_file():
        raise ValueError("--manifest must identify an existing file")
    if args.output.exists():
        raise ValueError("refusing to overwrite an existing review report")
    if not 1 <= args.sparse_system_threshold <= 100:
        raise ValueError("--sparse-system-threshold must be between 1 and 100")

    review = review_scientific_cohort(
        args.manifest,
        sparse_system_threshold=args.sparse_system_threshold,
    )
    failures = evaluate_review_integrity(
        review,
        expected_manifest_sha256=MG_DE_006_MANIFEST_SHA256,
        expected_source=MATERIALS_PROJECT_SOURCE,
        expected_selection_contract_version=MG_DE_006_SELECTION_CONTRACT,
        expected_accepted=MG_DE_006_ACCEPTED,
    )
    report = {
        **review.to_dict(),
        "integrity_gate_failures": failures,
        "ready_for_scientific_decision": not failures,
        "scientific_decision": "pending_independent_review",
        "database_import_authorized": False,
    }
    MaterialImportPipeline._write_json_atomic(args.output, report)
    print(json.dumps(report, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
