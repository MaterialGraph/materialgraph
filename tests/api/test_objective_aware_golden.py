"""SRQ-01 PR-A: baseline of objective-aware Objective Explore responses.

Freezes today's objective-aware responses (spec rev 3.7, 4.0) on the CI
reference dataset before the formula-correspondence report is added, so the
integration can be shown to change nothing else.

Snapshots live in tests/fixtures/golden/srq01_pra/. Regeneration is off by
default and never silent: set ``MATERIALGRAPH_REGENERATE_GOLDEN=srq01_pra``;
every rewritten case then fails with a "snapshot written" message.
"""

import json
import os
from pathlib import Path

import pytest

GOLDEN_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "golden" / "srq01_pra"
REGENERATE_VARIABLE = "MATERIALGRAPH_REGENERATE_GOLDEN"
REGENERATE_VALUE = "srq01_pra"
EXPLORE = "/api/v1/materials/{}/discovery/objective/explore"

_BASE = {
    "avoid_elements": [],
    "prefer_elements": [],
    "preserve_elements": [],
    "target_family": None,
    "max_hops": 2,
    "limit": 10,
    "prefer_lower_criticality": True,
    "require_stable_materials": False,
}

# (snapshot name, source material ID, request body). All are objective-aware.
CASES = [
    ("cs01_source5_balanced", 5, {
        "objective": {**_BASE, "avoid_elements": ["Li", "Co"], "prefer_elements": ["Na", "K"],
                      "preserve_elements": ["Fe", "P", "O"], "target_family": "phosphate"},
        "mode": "balanced", "limit": 10,
    }),
    ("q6_source28_balanced", 28, {
        "objective": {**_BASE, "avoid_elements": ["Li"], "prefer_elements": ["Na"]},
        "mode": "balanced", "limit": 10,
    }),
    ("strict_source5_avoid_li", 5, {
        "objective": {**_BASE, "avoid_elements": ["Li"]},
        "mode": "strict", "limit": 10,
    }),
]


def _regenerating() -> bool:
    return os.environ.get(REGENERATE_VARIABLE) == REGENERATE_VALUE


def _check(snapshot: Path, content: bytes) -> None:
    if _regenerating():
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(content)
        pytest.fail(
            f"snapshot written: {snapshot.name}. Review the diff, then rerun "
            f"without {REGENERATE_VARIABLE} to verify."
        )
    assert snapshot.exists(), (
        f"missing snapshot {snapshot.name}; regenerate deliberately with "
        f"{REGENERATE_VARIABLE}={REGENERATE_VALUE}"
    )
    expected = snapshot.read_bytes()
    if content != expected:
        pytest.fail(f"{snapshot.name}: response bytes differ from the golden snapshot")


@pytest.mark.parametrize(("name", "source", "body"), CASES, ids=[case[0] for case in CASES])
def test_objective_aware_response_bytes_match_baseline(client, name, source, body):
    response = client.post(EXPLORE.format(source), json=body)
    assert response.status_code == 200, response.text
    _check(GOLDEN_DIR / f"{name}.json", response.content)


def test_baseline_snapshots_have_no_line_ending_conversion():
    for snapshot in GOLDEN_DIR.glob("*.json"):
        assert b"\r" not in snapshot.read_bytes(), snapshot.name
        json.loads(snapshot.read_bytes())
