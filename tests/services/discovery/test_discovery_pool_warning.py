"""The Discovery result-limit warning states the candidate pool by source (R1-fix-839).

Each source's figure is what it supplied before deduplication; the total is
the deduplicated pool before the final result limit; recommendation and
scenario candidates are named only when requested, with their per-request
cap, and an enabled source that supplied nothing is said to have supplied
nothing.
"""

import re

import pytest

from app.services.discovery.candidate_service import DiscoveryCandidateService
from app.services.discovery.warning_service import DiscoveryWarningService
from app.services.material.family_service import MaterialFamilyService
from app.services.material.recommendation_service import MaterialRecommendationService

SOURCE = 5
CANDIDATES = "/api/v1/materials/5/discovery/candidates"
FLAG_COMBINATIONS = [
    pytest.param({}, False, False, id="route-defaults"),
    pytest.param({"include_recommendations": "true"}, True, False, id="recommendations-only"),
    pytest.param({"include_scenarios": "true"}, False, True, id="scenarios-only"),
    pytest.param({"include_recommendations": "true", "include_scenarios": "true"}, True, True,
                 id="both"),
]


def _expected_pool(db, limit, recommendations, scenarios, avoid="Li", prefer="Na"):
    """Recompute each source's supplied IDs from the underlying services."""
    cap = min(limit * 3, 20)
    family, _ = MaterialFamilyService(db).get_material_families_with_elements(SOURCE)
    pool = {"composition": [m["material_id"] for m in family["related_materials"]]}
    service = MaterialRecommendationService(db)
    if recommendations:
        result = service.get_recommendations(material_id=SOURCE, limit=cap, prefer_lower_criticality=False)
        pool["recommendation"] = [m["material_id"] for m in result["recommendations"]]
    if scenarios and (avoid or prefer):
        result = service.get_scenario_recommendations(
            material_id=SOURCE, element=avoid or prefer, supply_risk_multiplier=1.0,
            avoid_element=avoid, prefer_element=prefer, limit=cap, prefer_lower_criticality=False)
        pool["scenario"] = [m["material_id"] for m in result["recommendations"]]
    return pool, cap


def _limit_warning(data):
    found = [w for w in data["discovery_warnings"] if w.startswith("Results were limited")]
    assert len(found) == 1, data["discovery_warnings"]
    return found[0]


@pytest.mark.parametrize(("flags", "recommendations", "scenarios"), FLAG_COMBINATIONS)
def test_route_states_the_pool_for_each_flag_combination(client, db_session, flags, recommendations,
                                                         scenarios):
    limit = 2
    response = client.get(CANDIDATES, params={"avoid_element": "Li", "prefer_element": "Na",
                                              "limit": limit, **flags})
    assert response.status_code == 200
    warning = _limit_warning(response.json())

    pool, cap = _expected_pool(db_session, limit, recommendations, scenarios)
    distinct = set().union(*pool.values())
    assert SOURCE not in distinct
    assert warning.startswith(
        f"Results were limited to {limit} candidates from {len(distinct)} distinct candidates "
        "before the final result limit was applied: composition-related materials supplied "
        f"{len(pool['composition'])} candidates (the source material excluded); ")
    for name, enabled in (("recommendation", recommendations), ("scenario", scenarios)):
        if not enabled:
            assert f"{name} candidates were not requested" in warning
        elif pool[name]:
            assert (f"{name} candidates supplied {len(pool[name])} candidates "
                    f"(this source is capped at {cap} for this request)") in warning
        else:
            assert f"{name} candidates were enabled but none were generated" in warning
    supplied = sum(len(ids) for ids in pool.values())
    assert ("counted once in the total" in warning) == (supplied > len(distinct))


def test_route_defaults_name_composition_only(client):
    """The route defaults (both optional sources off) are what the frontend and the
    production captures use."""
    data = client.get(CANDIDATES, params={"avoid_element": "Li", "prefer_element": "Na",
                                          "limit": 2}).json()
    warning = _limit_warning(data)

    assert "recommendation candidates were not requested" in warning
    assert "scenario candidates were not requested" in warning
    assert "capped at" not in warning
    assert "counted once" not in warning


def test_stated_total_is_the_deduplicated_pool_before_the_final_limit(db_session):
    limit = 2
    service = DiscoveryCandidateService(db_session)
    seen = {}
    build = service.warning_service.build_warnings

    def spy(**kwargs):
        seen.update(kwargs)
        return build(**kwargs)

    service.warning_service.build_warnings = spy
    result = service.get_discovery_candidates(material_id=SOURCE, avoid_element="Li", prefer_element="Na",
                                              limit=limit, include_substitution_paths=False)
    pool, _ = _expected_pool(db_session, limit, True, True)
    distinct = set().union(*pool.values())

    assert seen["total_candidate_count"] == len(distinct)
    assert len(result["candidates"]) == limit < len(distinct)
    assert f"from {len(distinct)} distinct candidates" in _limit_warning(result)


def test_overlapping_sources_are_counted_once_in_the_total(db_session):
    limit = 2
    pool, _ = _expected_pool(db_session, limit, True, True)
    distinct = set().union(*pool.values())
    supplied = sum(len(ids) for ids in pool.values())
    assert supplied > len(distinct), "fixture should have candidates supplied by several sources"

    result = DiscoveryCandidateService(db_session).get_discovery_candidates(
        material_id=SOURCE, avoid_element="Li", prefer_element="Na", limit=limit,
        include_substitution_paths=False)
    warning = _limit_warning(result)

    assert f"from {len(distinct)} distinct candidates" in warning
    assert f"composition-related materials supplied {len(pool['composition'])} candidates" in warning
    assert f"recommendation candidates supplied {len(pool['recommendation'])} candidates" in warning
    assert f"scenario candidates supplied {len(pool['scenario'])} candidates" in warning
    assert warning.endswith("A candidate supplied by more than one source is counted once in the total.")


def test_source_material_is_in_no_source(db_session):
    pool, _ = _expected_pool(db_session, 50, True, True)
    assert all(SOURCE not in ids for ids in pool.values())

    result = DiscoveryCandidateService(db_session).get_discovery_candidates(
        material_id=SOURCE, avoid_element="Li", prefer_element="Na", limit=50,
        include_substitution_paths=False)
    assert SOURCE not in [c["material_id"] for c in result["candidates"]]


def test_enabled_source_supplying_nothing_is_stated(db_session):
    service = DiscoveryCandidateService(db_session)
    service.recommendation_service.get_recommendations = lambda **kwargs: {
        "material_id": SOURCE, "mp_id": "mp-19017", "recommendations": []}
    warning = _limit_warning(service.get_discovery_candidates(
        material_id=SOURCE, avoid_element="Li", prefer_element="Na", limit=1,
        include_scenarios=False, include_substitution_paths=False))

    assert ("recommendation candidates were enabled but none were generated for this request;"
            in warning)
    assert "scenario candidates were not requested" in warning


def test_scenarios_enabled_without_an_element_supply_nothing(client):
    data = client.get(CANDIDATES, params={"limit": 1, "include_scenarios": "true"}).json()
    warning = _limit_warning(data)

    assert ("scenario candidates were enabled but none were generated for this request, "
            "because no avoided or preferred element was given") in warning


def test_per_source_cap_is_distinct_from_the_final_limit(client, db_session):
    limit = 2
    data = client.get(CANDIDATES, params={"avoid_element": "Li", "prefer_element": "Na", "limit": limit,
                                          "include_recommendations": "true"}).json()
    warning = _limit_warning(data)
    pool, cap = _expected_pool(db_session, limit, True, False)

    assert cap == 6 != limit
    assert len(data["candidates"]) == limit
    assert 0 < len(pool["recommendation"]) <= cap
    assert re.search(rf"limited to {limit} candidates", warning)
    assert f"capped at {cap} for this request" in warning


def test_warning_without_a_basis_states_only_the_distinct_total():
    warnings = DiscoveryWarningService().build_warnings(
        candidates=[{"formula": "NaFePO4"}], avoid_element=None, prefer_element=None,
        limit=10, total_candidate_count=839)

    assert warnings == ["Results were limited to 10 candidates from 839 distinct candidates "
                        "before the final result limit was applied."]
