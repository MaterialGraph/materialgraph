"""SRQ-01 PR-0 part 2: local-ID permutation harness for AC3 (H1) and AC4 (H2).

Objective-aware Objective Explore requests (spec rev 3.3, 4.0) are run on the
CI reference dataset under the baseline local IDs and under permutations of
them (tests/support/id_permutation.py). Results are compared by MP ID only.

H1: the set of candidates admitted at each expansion, observed by spying on
    DiscoveryChainService._get_next_candidates (test-side only).
H2: the order of equally scored ranked candidates and chains.

Where the current code depends on local IDs, the invariance test is marked
xfail(strict=True): it fails today and turns into an XPASS error once PR-B
removes the dependence, so the marker must then be removed deliberately.
Frozen request paths (4.0) are not tested here; the golden suite covers them.
"""

from __future__ import annotations

from functools import cache
from unittest.mock import patch

import pytest
from sqlalchemy import select, text

from app.models.material import Material
from app.schemas.research_objective_exploration import ResearchObjectiveExplorationRequest
from app.services.discovery.chain_service import DiscoveryChainService
from app.services.research.objective_exploration_service import ResearchObjectiveExplorationService
from tests.support.id_permutation import BASELINE, REVERSED, permutation, permuted_reference_session

PERMUTATIONS = (REVERSED, 1, 2, 3)
H1_H2_DEPENDENCE = "SRQ-01 H1/H2: current local-ID dependence; PR-B must fix"
# A crash is not an expected failure: only a failed invariance assertion is.
LOCAL_ID_DEPENDENCE = pytest.mark.xfail(strict=True, raises=AssertionError, reason=H1_H2_DEPENDENCE)

_BASE_OBJECTIVE = {
    "avoid_elements": [],
    "prefer_elements": [],
    "preserve_elements": [],
    "target_family": None,
    "max_hops": 2,
    "limit": 20,
    "prefer_lower_criticality": True,
    "require_stable_materials": False,
}
# name -> (source MP ID, objective, mode). All three are objective-aware.
REQUESTS = {
    "cs01_source5_balanced": (
        "mp-19017",
        {**_BASE_OBJECTIVE, "avoid_elements": ["Li", "Co"], "prefer_elements": ["Na", "K"],
         "preserve_elements": ["Fe", "P", "O"], "target_family": "phosphate"},
        "balanced",
    ),
    "q6_source28_balanced": (
        "mp-754656",
        {**_BASE_OBJECTIVE, "avoid_elements": ["Li"], "prefer_elements": ["Na"]},
        "balanced",
    ),
    "strict_source5_avoid_li": (
        "mp-19017",
        {**_BASE_OBJECTIVE, "avoid_elements": ["Li"]},
        "strict",
    ),
}


@cache
def _observe(request_name: str, seed) -> dict:
    """Run one request under one permutation; return MP-ID-keyed results."""
    source, objective, mode = REQUESTS[request_name]
    with permuted_reference_session(seed) as (session, _mapping):
        mp_by_id = dict(session.execute(select(Material.id, Material.mp_id)).all())
        id_by_mp = {mp_id: material_id for material_id, mp_id in mp_by_id.items()}
        admitted: dict[str, frozenset[str]] = {}
        original = DiscoveryChainService._get_next_candidates

        def spy(self, material_id, *args, **kwargs):
            result = original(self, material_id, *args, **kwargs)
            admitted[mp_by_id[material_id]] = frozenset(
                mp_by_id[candidate["material_id"]] for candidate in result
            )
            return result

        request = ResearchObjectiveExplorationRequest(objective=objective, mode=mode, limit=20)
        with patch.object(DiscoveryChainService, "_get_next_candidates", spy):
            response = ResearchObjectiveExplorationService(session).explore(id_by_mp[source], request)

        return {
            "admitted": admitted,
            "ranked": [
                (mp_by_id[candidate["material_id"]], candidate["score"])
                for candidate in response["ranked_candidates"]
            ],
            "chains": [
                (
                    "/".join(mp_by_id[material["material_id"]] for material in chain["materials"]),
                    chain["scientific_usefulness_score"],
                )
                for chain in response["chains"]
            ],
        }


def _differences(request_name: str, key: str) -> dict:
    baseline = _observe(request_name, BASELINE)[key]
    return {
        seed: (baseline, observed)
        for seed in PERMUTATIONS
        if (observed := _observe(request_name, seed)[key]) != baseline
    }


# Harness ---------------------------------------------------------------------

def test_permutation_is_seed_controlled_and_bijective():
    ids = list(range(1, 29))
    assert permutation(ids, BASELINE) == {i: i for i in ids}
    assert permutation(ids, REVERSED) == {i: 29 - i for i in ids}
    for seed in (1, 2, 3):
        mapping = permutation(ids, seed)
        assert mapping == permutation(ids, seed)
        assert sorted(mapping.values()) == ids
        assert mapping != {i: i for i in ids}


@pytest.mark.parametrize("seed", PERMUTATIONS)
def test_permuted_dataset_keeps_every_reference_and_restores_ids(seed):
    query = text(
        "SELECT m.mp_id, e.symbol FROM materials m "
        "JOIN material_elements me ON me.material_id = m.id "
        "JOIN elements e ON e.id = me.element_id ORDER BY 1, 2"
    )
    with permuted_reference_session(BASELINE) as (session, _):
        expected = session.execute(query).all()
        expected_ids = dict(session.execute(select(Material.mp_id, Material.id)).all())
    with permuted_reference_session(seed) as (session, mapping):
        assert session.execute(query).all() == expected
        assert dict(session.execute(select(Material.mp_id, Material.id)).all()) == {
            mp_id: mapping[material_id] for mp_id, material_id in expected_ids.items()
        }
        constraints = session.execute(text(
            "SELECT count(*) FROM pg_constraint "
            "WHERE contype = 'f' AND confrelid = 'materials'::regclass"
        )).scalar_one()
        assert constraints >= 4  # every FK re-added and re-validated
    # The context manager has also asserted the rollback; check it here too.
    with permuted_reference_session(BASELINE) as (session, _):
        assert dict(session.execute(select(Material.mp_id, Material.id)).all()) == expected_ids


# H1: admitted candidates (AC3) -------------------------------------------------

@pytest.mark.parametrize(
    "request_name",
    [
        pytest.param("cs01_source5_balanced", marks=LOCAL_ID_DEPENDENCE),
        pytest.param("q6_source28_balanced", marks=LOCAL_ID_DEPENDENCE),
        # No dependence observed: only five candidates are eligible at every
        # expansion, below the cap of six, so admission has no competition.
        "strict_source5_avoid_li",
    ],
)
def test_h1_admitted_candidates_do_not_depend_on_local_ids(request_name):
    assert _differences(request_name, "admitted") == {}


# H2: order of equally scored results (AC4) -------------------------------------

@pytest.mark.parametrize("request_name", list(REQUESTS))
def test_ranked_candidate_set_and_scores_do_not_depend_on_local_ids(request_name):
    """Precondition for reading the H2 tests: only the order differs today."""
    baseline = sorted(_observe(request_name, BASELINE)["ranked"])
    for seed in PERMUTATIONS:
        assert sorted(_observe(request_name, seed)["ranked"]) == baseline, seed


@pytest.mark.parametrize("request_name", list(REQUESTS))
@LOCAL_ID_DEPENDENCE
def test_h2_equally_scored_candidates_keep_their_order(request_name):
    assert _differences(request_name, "ranked") == {}


@pytest.mark.parametrize(
    "request_name",
    # Case Study 01's chain set changes with admission (H1), so its chain
    # order is not an independent H2 observation and is not tested here.
    ["q6_source28_balanced", "strict_source5_avoid_li"],
)
@LOCAL_ID_DEPENDENCE
def test_h2_equally_scored_chains_keep_their_order(request_name):
    assert _differences(request_name, "chains") == {}
