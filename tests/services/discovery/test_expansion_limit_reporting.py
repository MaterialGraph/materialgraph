"""Expansion-limit reporting (#51; Release 1 item R1-3, contract B-3).

The per-material expansion limit is reported separately from
``search_truncated``, which keeps its budget-only meaning. Recording is
additive: admission and generated chains are unchanged.
"""

from types import SimpleNamespace


def _candidate(material_id):
    return {
        "material_id": material_id,
        "mp_id": f"mp-{material_id}",
        "pretty_formula": f"M{material_id}",
        "formula": f"M{material_id}",
    }


def _transition(from_material, to_candidate):
    return {
        "from_material_id": from_material["material_id"],
        "to_material_id": to_candidate["material_id"],
        "transition_type": "shared_chemistry",
        "reason": "Synthetic transition.",
        "preserved_framework": ["O"],
    }


def _service(db_session, monkeypatch, related, *, limit):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = limit
    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": [
                _candidate(item) for item in related.get(material_id, [])
            ],
        },
    )
    monkeypatch.setattr(
        service,
        "_build_transition",
        lambda from_material, to_candidate, **_: _transition(
            from_material,
            to_candidate,
        ),
    )
    return service


def _base():
    return SimpleNamespace(
        id=1,
        mp_id="mp-1",
        pretty_formula="M1",
        formula="M1",
    )


def _paths(chains):
    return [
        [material["material_id"] for material in chain["materials"]]
        for chain in chains
    ]


def test_binding_cap_is_reported_while_search_truncated_stays_false(
    db_session,
    monkeypatch,
):
    service = _service(
        db_session,
        monkeypatch,
        {1: [2, 3, 4, 5]},
        limit=3,
    )

    chains, metadata = service._build_chains(
        base_material=_base(),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=1,
    )

    # Admission is unchanged: the first three family candidates.
    assert _paths(chains) == [[1, 2], [1, 3], [1, 4]]
    assert metadata["search_truncated"] is False
    assert metadata["expansion_limit_binding"] is True
    assert metadata["candidates_considered_total"] == 4
    assert metadata["candidates_eligible_total"] == 4
    assert metadata["candidates_admitted_total"] == 3
    assert metadata["candidates_discarded_by_expansion_limit_total"] == 1
    assert metadata["expansions_with_cap_discards"] == 1
    assert metadata["distinct_candidates_discarded_by_expansion_limit"] == 1


def test_non_binding_cap_reports_no_discards(db_session, monkeypatch):
    service = _service(db_session, monkeypatch, {1: [2, 3]}, limit=3)

    _, metadata = service._build_chains(
        base_material=_base(),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=1,
    )

    assert metadata["expansion_limit_binding"] is False
    assert metadata["candidates_discarded_by_expansion_limit_total"] == 0
    assert metadata["expansions_with_cap_discards"] == 0
    assert metadata["distinct_candidates_discarded_by_expansion_limit"] == 0


def test_cache_hit_expansions_are_counted_and_distinct_count_dedupes(
    db_session,
    monkeypatch,
):
    # Materials 2 and 3 are each expanded twice (once directly, once as a
    # second hop), so the second expansion of each is an admission-cache hit.
    service = _service(
        db_session,
        monkeypatch,
        {1: [2, 3], 2: [3, 8, 9, 10], 3: [2, 8, 9, 10], 8: []},
        limit=2,
    )

    _, metadata = service._build_chains(
        base_material=_base(),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=3,
    )

    # Discards: 9 and 10 at each of the four expansions of material 2 or 3.
    assert metadata["candidates_discarded_by_expansion_limit_total"] == 8
    assert metadata["expansions_with_cap_discards"] == 4
    assert metadata["distinct_candidates_discarded_by_expansion_limit"] == 2
    assert metadata["expansion_limit_binding"] is True


def test_strict_exclusions_are_not_counted_as_cap_discards(
    db_session,
    monkeypatch,
):
    service = _service(db_session, monkeypatch, {1: [2, 3, 4]}, limit=2)
    elements_map = {
        1: ["Fe", "O", "P"],
        2: ["Fe", "Li", "O", "P"],
        3: ["Fe", "Na", "O", "P"],
        4: ["Fe", "O", "P"],
    }

    chains, metadata = service._build_chains(
        base_material=_base(),
        elements_map=elements_map,
        avoid_elements=frozenset({"Li"}),
        prefer_elements=frozenset(),
        max_hops=1,
        hard_avoid_admission=True,
    )

    assert _paths(chains) == [[1, 3], [1, 4]]
    assert metadata["candidates_considered_total"] == 3
    assert metadata["candidates_eligible_total"] == 2
    assert metadata["candidates_admitted_total"] == 2
    assert metadata["candidates_discarded_by_expansion_limit_total"] == 0
    assert metadata["expansion_limit_binding"] is False


def test_reporting_does_not_change_admission(db_session, monkeypatch):
    service = _service(
        db_session,
        monkeypatch,
        {1: [2, 3, 4, 5]},
        limit=3,
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
    )
    repeated = service._get_next_candidates(
        material_id=1,
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
    )

    assert [c["material_id"] for c in admitted] == [2, 3, 4]
    assert repeated is admitted


def test_chains_api_exposes_expansion_limit_fields(client):
    response = client.get(
        "/api/v1/materials/5/discovery/chains"
        "?avoid_element=Li&prefer_element=Na&max_hops=2&limit=5"
    )

    assert response.status_code == 200
    metadata = response.json()["search_metadata"]

    assert isinstance(metadata["expansion_limit_binding"], bool)
    considered = metadata["candidates_considered_total"]
    eligible = metadata["candidates_eligible_total"]
    admitted = metadata["candidates_admitted_total"]
    discarded = metadata["candidates_discarded_by_expansion_limit_total"]
    assert considered >= eligible >= admitted
    assert discarded == eligible - admitted
    assert metadata["expansion_limit_binding"] is (discarded > 0)
    assert (
        metadata["distinct_candidates_discarded_by_expansion_limit"]
        <= discarded
    )
