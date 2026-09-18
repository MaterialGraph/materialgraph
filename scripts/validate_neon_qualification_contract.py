import argparse
import json
import os
from pathlib import Path

from app.services.material.neon_qualification import (
    APPROVED_MANIFEST_FILE_SHA256,
    NeonProductionIdentity,
    NeonQualificationBudget,
    NeonResourceIdentity,
    approved_manifest_file_sha256,
    evaluate_neon_qualification_contract,
    sanitized_url_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an offline MG-DE-008 Neon qualification contract."
    )
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pooled-url-env", default="DATABASE_URL")
    parser.add_argument(
        "--direct-url-env", default="DATABASE_MIGRATION_URL"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    pooled_url = os.environ.get(args.pooled_url_env, "")
    direct_url = os.environ.get(args.direct_url_env, "")

    resource = NeonResourceIdentity(**contract["qualification_resource"])
    production = NeonProductionIdentity(**contract["production_denylist"])
    budget = NeonQualificationBudget(**contract.get("budget", {}))
    issues = evaluate_neon_qualification_contract(
        resource=resource,
        production=production,
        pooled_url=pooled_url,
        direct_url=direct_url,
        manifest=manifest,
        budget=budget,
    )
    manifest_file_sha256 = approved_manifest_file_sha256(args.manifest)
    if manifest_file_sha256 != APPROVED_MANIFEST_FILE_SHA256:
        issues.append("manifest_file_sha256")

    if args.output.exists():
        raise RuntimeError("refusing to overwrite an existing validation report")

    result = {
        "schema_version": 1,
        "valid": not issues,
        "issues": issues,
        "qualification_resource": contract["qualification_resource"],
        "budget": contract.get("budget", {}),
        "manifest_file_sha256": manifest_file_sha256,
        "manifest_payload_digest": manifest.get("manifest_sha256"),
        "pooled_url": sanitized_url_summary(pooled_url),
        "direct_url": sanitized_url_summary(direct_url),
        "network_access_performed": False,
        "database_writes_performed": False,
        "resource_creation_performed": False,
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
