import argparse
import json
import os
from pathlib import Path

from app.services.material.neon_qualification import (
    APPROVED_MANIFEST_FILE_SHA256,
    NeonQualificationBudget,
    approved_manifest_file_sha256,
    sanitized_url_summary,
)
from app.services.material.production_rollout import (
    ProductionBaseline,
    ProductionExpectedOutcome,
    ProductionResourceIdentity,
    ProductionRollbackBoundary,
    ProductionRolloutAuthorization,
    evaluate_production_rollout_document,
    evaluate_production_rollout_contract,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an offline MG-DE-009 production rollout contract."
    )
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pooled-url-env", default="DATABASE_URL")
    parser.add_argument("--direct-url-env", default="DATABASE_MIGRATION_URL")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    pooled_url = os.environ.get(args.pooled_url_env, "")
    direct_url = os.environ.get(args.direct_url_env, "")
    document_issues = evaluate_production_rollout_document(contract)
    if document_issues:
        if args.output.exists():
            raise RuntimeError("refusing to overwrite an existing validation report")
        result = {
            "schema_version": 1,
            "valid": False,
            "issues": document_issues,
            "network_access_performed": False,
            "database_writes_performed": False,
            "production_execution_authorized": False,
        }
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, sort_keys=True))
        return 2

    target = ProductionResourceIdentity(**contract["production_target"])
    baseline = ProductionBaseline(**contract["expected_baseline"])
    expected_outcome = ProductionExpectedOutcome(
        **contract.get("expected_outcome", {})
    )
    authorization = ProductionRolloutAuthorization(
        **contract.get("authorization", {})
    )
    rollback = ProductionRollbackBoundary(
        **contract.get("rollback_boundary", {})
    )
    budget = NeonQualificationBudget(**contract.get("budget", {}))
    issues = evaluate_production_rollout_contract(
        target=target,
        baseline=baseline,
        expected_outcome=expected_outcome,
        authorization=authorization,
        rollback=rollback,
        pooled_url=pooled_url,
        direct_url=direct_url,
        manifest=manifest,
        budget=budget,
    )

    manifest_file_sha256 = approved_manifest_file_sha256(args.manifest)
    if manifest_file_sha256 != APPROVED_MANIFEST_FILE_SHA256:
        issues.append("manifest_file_sha256")
    issues = list(dict.fromkeys(issues))

    if args.output.exists():
        raise RuntimeError("refusing to overwrite an existing validation report")

    result = {
        "schema_version": 1,
        "valid": not issues,
        "issues": issues,
        "production_target": contract["production_target"],
        "expected_baseline": contract["expected_baseline"],
        "expected_outcome": contract.get("expected_outcome", {}),
        "authorization": contract.get("authorization", {}),
        "rollback_boundary": contract.get("rollback_boundary", {}),
        "budget": contract.get("budget", {}),
        "manifest_file_sha256": manifest_file_sha256,
        "manifest_payload_digest": manifest.get("manifest_sha256"),
        "pooled_url": sanitized_url_summary(pooled_url),
        "direct_url": sanitized_url_summary(direct_url),
        "network_access_performed": False,
        "database_writes_performed": False,
        "migration_performed": False,
        "backup_performed": False,
        "restore_performed": False,
        "service_restart_performed": False,
        "production_execution_authorized": False,
    }
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if not issues else 2


if __name__ == "__main__":
    raise SystemExit(main())
