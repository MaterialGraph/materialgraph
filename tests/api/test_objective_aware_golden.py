"""SRQ-01 PR-A: objective-aware Objective Explore responses.

The baseline snapshots in tests/fixtures/golden/srq01_pra/ were captured before
the formula-correspondence report existed (spec rev 3.7, 4.0). Each response
minus the new ``formula_correspondence`` key, serialized exactly as the API
serializes JSON, must still equal its baseline byte for byte. The full current
responses are frozen separately under srq01_pra/full/.

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


def _serialize(data) -> bytes:
    """Starlette's JSONResponse rendering, so bytes compare like for like."""
    return json.dumps(
        data, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":"),
    ).encode("utf-8")


@pytest.mark.parametrize(("name", "source", "body"), CASES, ids=[case[0] for case in CASES])
def test_response_without_the_report_matches_the_pre_integration_baseline(client, name, source, body):
    response = client.post(EXPLORE.format(source), json=body)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "formula_correspondence" in data
    baseline = GOLDEN_DIR / f"{name}.json"
    assert baseline.exists(), baseline.name
    expected = baseline.read_bytes()

    # The response minus the new key, serialized like the API, equals the
    # pre-integration bytes.
    data.pop("formula_correspondence")
    assert _serialize(data) == expected, (
        f"{name}: the response changed beyond the additive formula_correspondence key"
    )
    # On the served bytes themselves: the new key is the model's last field,
    # so the response is the baseline with only that member appended.
    prefix = expected[:-1] + b',"formula_correspondence":'
    assert response.content.startswith(prefix), name
    assert response.content.endswith(b"}}"), name


@pytest.mark.parametrize(("name", "source", "body"), CASES, ids=[case[0] for case in CASES])
def test_full_objective_aware_response_bytes_match_golden(client, name, source, body):
    response = client.post(EXPLORE.format(source), json=body)
    assert response.status_code == 200, response.text
    _check(GOLDEN_DIR / "full" / f"{name}.json", response.content)


def test_snapshots_have_no_line_ending_conversion():
    for snapshot in GOLDEN_DIR.rglob("*.json"):
        assert b"\r" not in snapshot.read_bytes(), snapshot.name
        json.loads(snapshot.read_bytes())
