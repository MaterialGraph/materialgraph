import argparse
import json
from pathlib import Path

from app.services.material.import_pipeline import (
    MATERIALS_PROJECT_SOURCE,
    SELECTION_CONTRACT_VERSION,
    MaterialImportPipeline,
)
from app.services.material.manifest_inspection import (
    evaluate_manifest_gates,
    inspect_material_manifest,
)
from app.services.material.pilot_contract import (
    MG_DE_005_CHEMICAL_SYSTEMS,
    MG_DE_005_MAXIMUM_ENERGY_ABOVE_HULL,
    MG_DE_005_MAXIMUM_MATERIALS,
    MG_DE_005_MINIMUM_MATERIALS,
    MG_DE_005_MINIMUM_PROPERTY_COVERAGE,
    MG_DE_005_REQUIRED_ELEMENTS,
)


DEFAULT_REQUIRED_ELEMENTS = MG_DE_005_REQUIRED_ELEMENTS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate and inspect a Materials Project manifest without "
            "network or database access."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--minimum-materials",
        type=int,
        default=MG_DE_005_MINIMUM_MATERIALS,
    )
    parser.add_argument(
        "--maximum-materials",
        type=int,
        default=MG_DE_005_MAXIMUM_MATERIALS,
    )
    parser.add_argument(
        "--required-element",
        action="append",
        dest="required_elements",
    )
    parser.add_argument(
        "--minimum-property-coverage",
        type=float,
        default=MG_DE_005_MINIMUM_PROPERTY_COVERAGE,
    )
    parser.add_argument("--require-source-complete", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.manifest.is_file():
        raise ValueError("--manifest must identify an existing file")
    if not 1 <= args.minimum_materials <= args.maximum_materials <= 10_000:
        raise ValueError("material count gates are invalid")
    if not 0 <= args.minimum_property_coverage <= 1:
        raise ValueError("--minimum-property-coverage must be between 0 and 1")
    if args.output is not None and args.output.exists():
        raise ValueError("refusing to overwrite an existing inspection report")

    inspection = inspect_material_manifest(args.manifest)
    failures = evaluate_manifest_gates(
        inspection,
        minimum_materials=args.minimum_materials,
        maximum_materials=args.maximum_materials,
        required_elements=tuple(
            args.required_elements or DEFAULT_REQUIRED_ELEMENTS
        ),
        minimum_property_coverage=args.minimum_property_coverage,
        require_source_complete=args.require_source_complete,
    )
    if inspection.source != MATERIALS_PROJECT_SOURCE:
        failures.append("source")
    if inspection.selection_contract_version != SELECTION_CONTRACT_VERSION:
        failures.append("selection_contract_version")
    if inspection.chemical_systems != tuple(
        sorted(MG_DE_005_CHEMICAL_SYSTEMS)
    ):
        failures.append("chemical_systems")
    if inspection.stable_only:
        failures.append("stable_only")
    if inspection.maximum_energy_above_hull != (
        MG_DE_005_MAXIMUM_ENERGY_ABOVE_HULL
    ):
        failures.append("maximum_energy_above_hull")
    report = {
        **inspection.to_dict(),
        "gates": {
            "minimum_materials": args.minimum_materials,
            "maximum_materials": args.maximum_materials,
            "required_elements": sorted(
                set(args.required_elements or DEFAULT_REQUIRED_ELEMENTS)
            ),
            "minimum_property_coverage": args.minimum_property_coverage,
            "require_source_complete": args.require_source_complete,
            "expected_source": MATERIALS_PROJECT_SOURCE,
            "expected_selection_contract_version": (
                SELECTION_CONTRACT_VERSION
            ),
            "expected_chemical_systems": sorted(
                MG_DE_005_CHEMICAL_SYSTEMS
            ),
            "expected_stable_only": False,
            "expected_maximum_energy_above_hull": (
                MG_DE_005_MAXIMUM_ENERGY_ABOVE_HULL
            ),
        },
        "gate_failures": failures,
        "qualified": not failures,
    }
    if args.output is not None:
        MaterialImportPipeline._write_json_atomic(args.output, report)
    print(json.dumps(report, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
