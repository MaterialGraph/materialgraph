"""SRQ-01 PR-0 part 2: local-ID permutation harness for AC3 (H1) and AC4 (H2).

Objective-aware Objective Explore requests (spec rev 3.3, 4.0) are run on the
CI reference dataset under the baseline local IDs and under permutations of
them (tests/support/id_permutation.py). Results are compared by MP ID only.

H1: the set of candidates admitted at each expansion, observed by spying on
    DiscoveryChainService._get_next_candidates (test-side only).
H2: the order of equally scored ranked candidates and chains.

PR-0 encoded the observed local-ID dependence as seven strict xfails. PR-B1
(spec rev 3.11, R5/R6: MP-ID ordering on objective-aware requests) removed it,
and the markers were removed deliberately once each test genuinely passed.
Frozen request paths (4.0) are not tested here; the golden suite covers them.
"""

from __future__ import annotations

import json
from functools import cache
from unittest.mock import patch

import pytest
from sqlalchemy import select, text

from app.models.material import Material
from app.schemas.research_objective_exploration import ResearchObjectiveExplorationRequest
from app.services.discovery import chain_service as chain_service_module
from app.services.discovery.chain_service import DiscoveryChainService
from app.services.research import objective_exploration_service as explore_module
from app.services.research.formula_correspondence_report import mp_id_sort_key
from app.services.research.objective_exploration_service import ResearchObjectiveExplorationService
from tests.support.id_permutation import BASELINE, REVERSED, permutation, permuted_reference_session

PERMUTATIONS = (REVERSED, 1, 2, 3)

# Synthetic Na-Fe-P-O records (AC3). Added inside the rolled-back permutation
# transaction before the permutation, so their local IDs are permuted too.
# With the five reference Na-Fe-P-O materials they give eight Li-free
# candidates for LiFePO4, all sharing Fe, O and P: more than the cap of six.
SYNTHETIC_NA_FE_P_O = [
    (101, "mp-19100", {"Na": 2, "Fe": 1, "P": 2, "O": 7}),
    (102, "mp-30000", {"Na": 4, "Fe": 3, "P": 4, "O": 15}),
    (103, "mp-600000", {"Na": 1, "Fe": 2, "P": 3, "O": 10}),
]


def _formula(amounts: dict) -> str:
    return "".join(f"{symbol}{'' if amount == 1 else amount}" for symbol, amount in amounts.items())


def _add_synthetic_na_fe_p_o(connection) -> None:
    element_ids = dict(connection.execute(text("SELECT symbol, id FROM elements")).all())
    for material_id, mp_id, amounts in SYNTHETIC_NA_FE_P_O:
        formula = _formula(amounts)
        connection.execute(text(
            "INSERT INTO materials (id, mp_id, formula, pretty_formula, energy_above_hull, "
            "is_stable, source, raw_data) VALUES (:id, :mp_id, :formula, :formula, 0.0, true, "
            "'materials_project', CAST(:raw AS json))"
        ), {"id": material_id, "mp_id": mp_id, "formula": formula,
            "raw": json.dumps({"composition": {k: float(v) for k, v in amounts.items()}})})
        total = sum(amounts.values())
        for symbol, amount in amounts.items():
            connection.execute(text(
                "INSERT INTO material_elements (material_id, element_id, fraction, fraction_known) "
                "VALUES (:material_id, :element_id, :fraction, true)"
            ), {"material_id": material_id, "element_id": element_ids[symbol], "fraction": amount / total})


SETUPS = {"strict_source5_avoid_li_more_than_cap": _add_synthetic_na_fe_p_o}

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
    # Same request with eight eligible candidates at the source expansion.
    "strict_source5_avoid_li_more_than_cap": (
        "mp-19017",
        {**_BASE_OBJECTIVE, "avoid_elements": ["Li"]},
        "strict",
    ),
}


@cache
def _observe(request_name: str, seed) -> dict:
    """Run one request under one permutation; return MP-ID-keyed results."""
    source, objective, mode = REQUESTS[request_name]
    with permuted_reference_session(seed, setup=SETUPS.get(request_name)) as (session, _mapping):
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
        "cs01_source5_balanced",
        "q6_source28_balanced",
        # Only five candidates are eligible here, below the cap of six, so
        # this case alone cannot detect admission dependence.
        "strict_source5_avoid_li",
        # AC3: eight eligible candidates compete for six slots.
        "strict_source5_avoid_li_more_than_cap",
    ],
)
def test_h1_admitted_candidates_do_not_depend_on_local_ids(request_name):
    assert _differences(request_name, "admitted") == {}


def test_synthetic_strict_case_really_exceeds_the_cap():
    """The AC3 case is only meaningful if admission actually discards candidates."""
    admitted = _observe("strict_source5_avoid_li_more_than_cap", BASELINE)["admitted"]["mp-19017"]
    eligible = {"mp-19028", "mp-556540", "mp-761065", "mp-752506", "mp-19226",
                "mp-19100", "mp-30000", "mp-600000"}
    assert len(eligible) > DiscoveryChainService.EXPANSION_LIMIT
    assert len(admitted) == DiscoveryChainService.EXPANSION_LIMIT
    # All eight share Fe, O and P with LiFePO4, so the numeric MP ID decides.
    assert admitted == frozenset(sorted(eligible, key=lambda mp: mp_id_sort_key(mp, 0))[:6])


# H2: order of equally scored results (AC4) -------------------------------------

@pytest.mark.parametrize("request_name", list(REQUESTS))
def test_ranked_candidate_set_and_scores_do_not_depend_on_local_ids(request_name):
    """Precondition for reading the H2 tests: only the order could differ."""
    baseline = sorted(_observe(request_name, BASELINE)["ranked"])
    for seed in PERMUTATIONS:
        assert sorted(_observe(request_name, seed)["ranked"]) == baseline, seed


@pytest.mark.parametrize("request_name", list(REQUESTS))
def test_h2_equally_scored_candidates_keep_their_order(request_name):
    assert _differences(request_name, "ranked") == {}


@pytest.mark.parametrize(
    "request_name",
    # cs01 (AC4): its chain set depended on admission (H1) before PR-B1, so
    # its chain order became an independent observation only once H1 held.
    ["cs01_source5_balanced", "q6_source28_balanced", "strict_source5_avoid_li",
     "strict_source5_avoid_li_more_than_cap"],
)
def test_h2_equally_scored_chains_keep_their_order(request_name):
    assert _differences(request_name, "chains") == {}


# R5 fallback: never used on the reference data --------------------------------

@pytest.mark.parametrize("request_name", ["cs01_source5_balanced", "q6_source28_balanced",
                                          "strict_source5_avoid_li"])
def test_no_ordering_decision_uses_the_local_id_fallback(monkeypatch, db_session, request_name):
    """Every objective-aware ordering key must come from a numeric MP ID."""
    calls = []

    def recording_key(mp_id, material_id):
        calls.append(mp_id)
        return mp_id_sort_key(mp_id, material_id)

    for module in (chain_service_module, explore_module):
        monkeypatch.setattr(module, "mp_id_sort_key", recording_key)
    source, objective, mode = REQUESTS[request_name]
    id_by_mp = dict(db_session.execute(select(Material.mp_id, Material.id)).all())
    request = ResearchObjectiveExplorationRequest(objective=objective, mode=mode, limit=20)
    ResearchObjectiveExplorationService(db_session).explore(id_by_mp[source], request)

    assert calls, "no objective-aware ordering key was computed"
    fallback = [mp_id for mp_id in calls if mp_id_sort_key(mp_id, 0)[0] != 0]
    assert fallback == [], f"local-ID fallback used for {sorted(set(map(str, fallback)))}"
