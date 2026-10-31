"""SRQ-01 PR-0: byte-identical characterization of no-objective behaviour.

Freezes the exact response bytes of every request path that uses the shared
family ordering without the objective-aware admission branch (spec rev 3.1,
R8 and AC6). Later SRQ-01 changes to the Objective Investigation path must
leave every snapshot here unchanged.

Snapshots live in tests/fixtures/golden/srq01_pr0/ and were captured against
the offline reference dataset loaded by CI (scripts.reference_test_data, 28
curated materials). Each file holds ``response.content`` exactly as served.

Regenerating is off by default and never silent: set
``MATERIALGRAPH_REGENERATE_GOLDEN=srq01_pr0`` to rewrite the snapshots. Every
rewritten case then fails with a "snapshot written" message, so a
regeneration run can never pass; rerun without the variable to verify.
"""

import json
import os
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "golden" / "srq01_pr0"
REGENERATE_VARIABLE = "MATERIALGRAPH_REGENERATE_GOLDEN"
REGENERATE_VALUE = "srq01_pr0"

# Source materials (local IDs in the reference dataset):
#   5  LiFePO4  mp-19017   Case Study 01 source
#   10 NaFePO4  mp-19226   exact alkali analog of LiFePO4
#   28 LiMnO2   mp-754656  Q6 source
NO_OBJECTIVE = {
    "avoid_elements": [],
    "prefer_elements": [],
    "preserve_elements": [],
    "target_family": None,
    "max_hops": 2,
    "limit": 10,
    "prefer_lower_criticality": True,
    "require_stable_materials": False,
}
# Objective Explore stays on the legacy admission path when no element is
# preferred and hard Avoid is off (Balanced and Exploratory), even with Avoid,
# preserve and family constraints.
AVOID_ONLY_CS01 = {
    **NO_OBJECTIVE,
    "avoid_elements": ["Li", "Co"],
    "preserve_elements": ["Fe", "P", "O"],
    "target_family": "phosphate",
}
AVOID_ONLY_Q6 = {**NO_OBJECTIVE, "avoid_elements": ["Li"]}

# (snapshot name, method, path, query params or JSON body)
CASES = [
    # Discovery Chains API: always the legacy admission path.
    ("discovery_chains_5", "GET", "/api/v1/materials/5/discovery/chains", {}),
    ("discovery_chains_10", "GET", "/api/v1/materials/10/discovery/chains", {}),
    ("discovery_chains_28", "GET", "/api/v1/materials/28/discovery/chains", {}),
    ("discovery_chains_5_avoid_li_prefer_na", "GET", "/api/v1/materials/5/discovery/chains",
     {"avoid_element": "Li", "prefer_element": "Na", "max_hops": 2, "limit": 10}),
    # Objective Explore on the legacy admission path.
    ("objective_explore_5_balanced_no_objective", "POST", "/api/v1/materials/5/discovery/objective/explore",
     {"objective": NO_OBJECTIVE, "mode": "balanced", "limit": 10}),
    ("objective_explore_10_balanced_no_objective", "POST", "/api/v1/materials/10/discovery/objective/explore",
     {"objective": NO_OBJECTIVE, "mode": "balanced", "limit": 10}),
    ("objective_explore_28_balanced_no_objective", "POST", "/api/v1/materials/28/discovery/objective/explore",
     {"objective": NO_OBJECTIVE, "mode": "balanced", "limit": 10}),
    ("objective_explore_5_exploratory_no_objective", "POST", "/api/v1/materials/5/discovery/objective/explore",
     {"objective": NO_OBJECTIVE, "mode": "exploratory", "limit": 10}),
    ("objective_explore_5_balanced_avoid_only", "POST", "/api/v1/materials/5/discovery/objective/explore",
     {"objective": AVOID_ONLY_CS01, "mode": "balanced", "limit": 10}),
    ("objective_explore_28_exploratory_avoid_only", "POST", "/api/v1/materials/28/discovery/objective/explore",
     {"objective": AVOID_ONLY_Q6, "mode": "exploratory", "limit": 10}),
    # Objective Chains API: legacy admission, no objective.
    ("objective_chains_5_no_objective", "POST", "/api/v1/materials/5/discovery/objective/chains",
     {"objective": NO_OBJECTIVE}),
    ("objective_chains_10_no_objective", "POST", "/api/v1/materials/10/discovery/objective/chains",
     {"objective": NO_OBJECTIVE}),
    ("objective_chains_28_no_objective", "POST", "/api/v1/materials/28/discovery/objective/chains",
     {"objective": NO_OBJECTIVE}),
    # Scientific pathway analysis: built on the Objective Chains service.
    ("scientific_pathways_5_no_objective", "POST", "/api/v1/materials/5/research/scientific-pathways",
     {"objective": NO_OBJECTIVE}),
    ("scientific_pathways_28_no_objective", "POST", "/api/v1/materials/28/research/scientific-pathways",
     {"objective": NO_OBJECTIVE}),
    # Other consumers of the shared family ordering.
    ("families_5", "GET", "/api/v1/materials/5/families", {}),
    ("families_10", "GET", "/api/v1/materials/10/families", {}),
    ("families_28", "GET", "/api/v1/materials/28/families", {}),
    ("discovery_candidates_5", "GET", "/api/v1/materials/5/discovery/candidates", {}),
    ("discovery_candidates_10", "GET", "/api/v1/materials/10/discovery/candidates", {}),
    ("discovery_candidates_28", "GET", "/api/v1/materials/28/discovery/candidates", {}),
    ("discovery_graph_5", "GET", "/api/v1/materials/5/discovery/graph", {}),
    ("discovery_graph_28", "GET", "/api/v1/materials/28/discovery/graph", {}),
    ("discovery_subgraph_5", "GET", "/api/v1/materials/5/discovery/subgraph", {}),
    # 5 -> 10 is not reachable within the bounded graph (path_found false);
    # that outcome is frozen too. 5 -> 7 and 28 -> 25 are reachable.
    ("discovery_path_5_to_10", "GET", "/api/v1/materials/5/discovery/path", {"target_material_id": 10}),
    ("discovery_path_5_to_7", "GET", "/api/v1/materials/5/discovery/path", {"target_material_id": 7}),
    ("discovery_path_28_to_25", "GET", "/api/v1/materials/28/discovery/path", {"target_material_id": 25}),
    ("communities_connected_5", "GET", "/api/v1/materials/5/discovery/communities/connected", {}),
    ("communities_modularity_5", "GET", "/api/v1/materials/5/discovery/communities/modularity", {}),
    ("communities_modularity_28", "GET", "/api/v1/materials/28/discovery/communities/modularity", {}),
]


def _regenerating() -> bool:
    return os.environ.get(REGENERATE_VARIABLE) == REGENERATE_VALUE


def _request(client, method, path, payload):
    if method == "GET":
        return client.get(path, params=payload)
    return client.post(path, json=payload)


def _first_difference(expected, actual, path="$"):
    """Locate the first differing JSON path, for a readable failure."""
    if type(expected) is not type(actual):
        return path, expected, actual
    if isinstance(expected, dict):
        for key in sorted(set(expected) | set(actual)):
            if key not in expected or key not in actual:
                return f"{path}.{key}", expected.get(key, "<absent>"), actual.get(key, "<absent>")
            found = _first_difference(expected[key], actual[key], f"{path}.{key}")
            if found:
                return found
        return None
    if isinstance(expected, list):
        for index, (left, right) in enumerate(zip(expected, actual)):
            found = _first_difference(left, right, f"{path}[{index}]")
            if found:
                return found
        if len(expected) != len(actual):
            return f"{path}.length", len(expected), len(actual)
        return None
    return None if expected == actual else (path, expected, actual)


@pytest.mark.parametrize(
    ("name", "method", "path", "payload"),
    CASES,
    ids=[case[0] for case in CASES],
)
def test_no_objective_response_bytes_match_golden(client, name, method, path, payload):
    response = _request(client, method, path, payload)
    assert response.status_code == 200, response.text
    snapshot = GOLDEN_DIR / f"{name}.json"

    if _regenerating():
        GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(response.content)
        pytest.fail(
            f"snapshot written: {snapshot.name}. Review the diff, then rerun "
            f"without {REGENERATE_VARIABLE} to verify."
        )

    assert snapshot.exists(), (
        f"missing snapshot {snapshot.name}; regenerate deliberately with "
        f"{REGENERATE_VARIABLE}={REGENERATE_VALUE}"
    )
    expected = snapshot.read_bytes()
    if response.content != expected:
        difference = _first_difference(json.loads(expected), response.json())
        pytest.fail(
            f"{name}: response bytes differ from the golden snapshot "
            f"(first JSON difference: {difference}). No-objective behaviour "
            "must stay byte-identical (SRQ-01 R8, AC6)."
        )


def test_golden_snapshots_have_no_line_ending_conversion():
    """Responses are compact JSON; a CR means a checkout rewrote the bytes."""
    for snapshot in GOLDEN_DIR.glob("*.json"):
        assert b"\r" not in snapshot.read_bytes(), snapshot.name


def test_every_snapshot_belongs_to_a_case():
    """No orphaned snapshot can mask a removed case."""
    names = {case[0] for case in CASES}
    assert {snapshot.stem for snapshot in GOLDEN_DIR.glob("*.json")} == names
