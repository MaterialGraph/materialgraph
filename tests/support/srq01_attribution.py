"""SRQ-01 PR-B1 change attribution harness (test-side only; not a test module).

Runs each objective-aware request on the CI reference dataset under five
configurations of the three PR-B1 ordering points, switched by test-side
monkeypatching only (no app change):

    0_baseline    all three off (pre-PR-B1 behaviour)
    1_admission   admission ordering only (R5a)
    2_ranked      ranked-candidate tie key only (R5b/R6)
    3_chains      chain tie key only (R5b)
    4_all         all three on (the current branch)

Supplementary, only to test explanations of changes no single configuration
produces: 5_admission_and_chains (1 and 3 together).

Before any attribution is trusted, configuration 0 must reproduce the
pre-PR-B1 snapshots and configuration 4 the current ones (ranked candidates
with reasons, and returned chains with scores).

    python -m tests.support.srq01_attribution <output directory> <pre-PR-B1 commit>

writes one JSON file per request and prints the attribution summary.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from sqlalchemy.orm import Session

from app.core.database import engine
from app.schemas.research_objective_exploration import ResearchObjectiveExplorationRequest
from app.services.research.objective_exploration_service import ResearchObjectiveExplorationService
from app.services.research.objective_service import ResearchObjectiveService
from tests.api.test_objective_aware_golden import CASES

SNAPSHOTS = Path("tests/fixtures/golden/srq01_pra/full")


@dataclass(frozen=True)
class Config:
    admission: bool
    ranked: bool
    chains: bool


CONFIGS = {
    "0_baseline": Config(False, False, False),
    "1_admission": Config(True, False, False),
    "2_ranked": Config(False, True, False),
    "3_chains": Config(False, False, True),
    "4_all": Config(True, True, True),
}
# Supplementary pair, used only to test combination explanations.
SUPPLEMENTARY = {"5_admission_and_chains": Config(True, False, True)}
SINGLE = ("1_admission", "2_ranked", "3_chains")


def _path(chain: dict) -> str:
    return "/".join(material["mp_id"] for material in chain["materials"])


def run(db: Session, source: int, body: dict, config: Config) -> dict:
    """One objective-aware explore request with the given ordering points on."""
    original_generate = ResearchObjectiveService.generate_chains_for_objective
    original_rank = ResearchObjectiveExplorationService._rank_candidates_from_chains
    pools: list[list[dict]] = []

    def generate(self, *args, **kwargs):
        kwargs["objective_aware_ordering"] = config.admission
        kwargs["chain_tie_key"] = (
            ResearchObjectiveExplorationService.chain_tie_key if config.chains else None
        )
        return original_generate(self, *args, **kwargs)

    def rank(self, *args, **kwargs):
        pools.append(kwargs["chains"])
        if not config.ranked:
            kwargs["source_material_id"] = None
        return original_rank(self, *args, **kwargs)

    request = ResearchObjectiveExplorationRequest(**body)
    with patch.object(ResearchObjectiveService, "generate_chains_for_objective", generate), \
            patch.object(ResearchObjectiveExplorationService, "_rank_candidates_from_chains", rank):
        response = ResearchObjectiveExplorationService(db).explore(source, request)
    (pool,) = pools
    return {
        "ranked": [
            {"mp_id": candidate["mp_id"], "score": candidate["score"], "reasons": candidate["reasons"]}
            for candidate in response["ranked_candidates"]
        ],
        "chains": [
            {"path": _path(chain), "score": chain["scientific_usefulness_score"],
             "score_breakdown": chain["score_breakdown"]}
            for chain in response["chains"]
        ],
        "pool": [
            {"path": _path(chain), "score": chain["scientific_usefulness_score"],
             "score_breakdown": chain["score_breakdown"]}
            for chain in pool
        ],
    }


def _snapshot(name: str, revision: str | None) -> dict:
    path = SNAPSHOTS / f"{name}.json"
    raw = (
        path.read_bytes() if revision is None
        else subprocess.run(["git", "show", f"{revision}:{path.as_posix()}"],
                            capture_output=True, check=True).stdout
    )
    data = json.loads(raw)
    return {
        "ranked": [{"mp_id": c["mp_id"], "score": c["score"], "reasons": c["reasons"]}
                   for c in data["ranked_candidates"]],
        "chains": [{"path": _path(c), "score": c["scientific_usefulness_score"]}
                   for c in data["chains"]],
    }


def _comparable(result: dict) -> dict:
    return {"ranked": result["ranked"],
            "chains": [{"path": c["path"], "score": c["score"]} for c in result["chains"]]}


def _score_check(base: list[dict], other: list[dict], key: str) -> list:
    """AC8b: items present in both keep the same score (and breakdown)."""
    def index(items):
        return {item[key]: (item["score"], item.get("score_breakdown")) for item in items}
    a, b = index(base), index(other)
    return [{key: k, "baseline": a[k], "changed": b[k]} for k in sorted(a.keys() & b.keys()) if a[k] != b[k]]


def attribute(results: dict) -> dict:
    base, full = results["0_baseline"], results["4_all"]
    ranked_changes = []
    for position, (before, after) in enumerate(zip(base["ranked"], full["ranked"]), start=1):
        if before["mp_id"] == after["mp_id"]:
            continue
        explained_by = [name for name in SINGLE
                        if results[name]["ranked"][position - 1]["mp_id"] == after["mp_id"]]
        ranked_changes.append({"position": position, "before": before["mp_id"], "after": after["mp_id"],
                               "score": after["score"], "single_configurations": explained_by})

    returned = {name: [c["path"] for c in result["chains"]] for name, result in results.items()}
    pools = {name: {c["path"] for c in result["pool"]} for name, result in results.items()}
    chain_changes = []
    for path in sorted(set(returned["4_all"]) ^ set(returned["0_baseline"])):
        added = path in returned["4_all"]
        in_both_pools = path in pools["0_baseline"] and path in pools["4_all"]
        explained_by = [name for name in SINGLE if (path in returned[name]) == added]
        chain_changes.append({
            "path": path,
            "change": "added" if added else "dropped",
            "kind": "crossed the limit boundary" if in_both_pools else "generation changed (eligible pool)",
            "single_configurations": explained_by,
            "in_eligible_pool_of": [name for name in pools if path in pools[name]],
            "returned_in": [name for name in returned if path in returned[name]],
        })
    reordered = [
        {"path": path, "position_before": returned["0_baseline"].index(path) + 1,
         "position_after": returned["4_all"].index(path) + 1,
         "single_configurations": [
             name for name in SINGLE
             if path in returned[name]
             and returned[name].index(path) == returned["4_all"].index(path)
         ]}
        for path in returned["4_all"]
        if path in returned["0_baseline"]
        and returned["0_baseline"].index(path) != returned["4_all"].index(path)
    ]

    reason_changes = []
    base_pool = pools["0_baseline"]
    full_pool = pools["4_all"]
    base_reasons = {c["mp_id"]: c["reasons"] for c in base["ranked"]}
    for candidate in full["ranked"]:
        before = base_reasons.get(candidate["mp_id"])
        if before is None or before == candidate["reasons"]:
            continue
        added = [r for r in candidate["reasons"] if r not in before]
        removed = [r for r in before if r not in candidate["reasons"]]
        gained = sorted(p for p in full_pool - base_pool if candidate["mp_id"] in p.split("/")[1:])
        lost = sorted(p for p in base_pool - full_pool if candidate["mp_id"] in p.split("/")[1:])
        if not added and not removed:
            classification = "order only: reasons follow eligible-chain order, which changed"
        else:
            classification = "follows from eligible-chain changes"
        unexplained = (added and not gained) or (removed and not lost)
        reason_changes.append({
            "mp_id": candidate["mp_id"], "added": added, "removed": removed,
            "eligible_chains_gained": gained, "eligible_chains_lost": lost,
            "classification": "UNEXPLAINED" if unexplained else classification,
        })

    unexplained = (
        [c for c in ranked_changes if not c["single_configurations"]]
        + [c for c in chain_changes if not c["single_configurations"]]
        + [c for c in reordered if not c["single_configurations"]]
        + [c for c in reason_changes if c["classification"] == "UNEXPLAINED"]
    )
    return {
        "ranked_position_changes": ranked_changes,
        "chain_membership_changes": chain_changes,
        "chain_reorderings_within_returned": reordered,
        "reason_changes": reason_changes,
        "ac8b_score_check": {
            name: {"ranked": _score_check(base["ranked"], result["ranked"], "mp_id"),
                   "returned_chains": _score_check(base["chains"], result["chains"], "path"),
                   "eligible_pool": _score_check(base["pool"], result["pool"], "path")}
            for name, result in results.items() if name != "0_baseline"
        },
        "not_explained_by_a_single_configuration": unexplained,
    }


def main(output: Path, pre_b1_revision: str) -> int:
    output.mkdir(parents=True, exist_ok=True)
    failures = 0
    with Session(engine) as db:
        for name, source, body in CASES:
            results = {config: run(db, source, body, settings)
                       for config, settings in {**CONFIGS, **SUPPLEMENTARY}.items()}
            validation = {
                "0_baseline_matches_pre_pr_b1_snapshot":
                    _comparable(results["0_baseline"]) == _snapshot(name, pre_b1_revision),
                "4_all_matches_current_snapshot":
                    _comparable(results["4_all"]) == _snapshot(name, None),
            }
            report = {
                "request": {"name": name, "source_material_id": source, "body": body},
                "pre_pr_b1_revision": pre_b1_revision,
                "validation": validation,
                "configurations": {k: {"admission": v.admission, "ranked": v.ranked, "chains": v.chains}
                                   for k, v in {**CONFIGS, **SUPPLEMENTARY}.items()},
                "results": results,
                "attribution": attribute(results),
            }
            (output / f"{name}.json").write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            unexplained = report["attribution"]["not_explained_by_a_single_configuration"]
            ok = all(validation.values()) and not unexplained
            failures += not ok
            print(f"{name}: validation {validation}; unexplained {len(unexplained)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), sys.argv[2]))
