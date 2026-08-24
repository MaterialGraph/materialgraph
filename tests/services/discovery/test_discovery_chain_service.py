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
        "reason": "Test transition.",
        "preserved_framework": ["O"],
    }


def test_discovery_chains_returns_valid_response(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    assert result["material_id"] == 5
    assert result["base_formula"] is not None
    assert "chains" in result
    assert isinstance(result["chains"], list)
    assert result["search_metadata"]["requested_result_limit"] == 5
    assert not result["search_metadata"][
        "scientific_completeness_guaranteed"
    ]


def test_discovery_chains_respects_max_hops(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    for chain in result["chains"]:
        assert chain["hop_count"] <= 2
        assert len(chain["transitions"]) <= 2


def test_discovery_chains_avoid_cycles(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=3,
        limit=10,
    )

    for chain in result["chains"]:
        material_ids = [
            material["material_id"]
            for material in chain["materials"]
        ]

        assert len(material_ids) == len(set(material_ids))


def test_discovery_chains_include_transition_reasons(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    for chain in result["chains"]:
        for transition in chain["transitions"]:
            assert transition["transition_type"]
            assert transition["reason"]
            assert isinstance(transition["preserved_framework"], list)


def test_discovery_chains_missing_material_returns_empty_response(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=999999,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    assert result["material_id"] == 999999
    assert result["mp_id"] is None
    assert result["base_formula"] is None
    assert result["chains"] == []
    assert result["search_metadata"]["expanded_state_count"] == 0


def test_build_chains_treats_max_hops_as_upper_bound(
    db_session,
    monkeypatch,
):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    candidates = {
        1: [_candidate(2)],
        2: [_candidate(3)],
        3: [],
    }

    monkeypatch.setattr(
        service,
        "_get_next_candidates",
        lambda material_id, **_: candidates[material_id],
    )
    monkeypatch.setattr(
        service,
        "_build_transition",
        lambda from_material, to_candidate, **_: _transition(
            from_material,
            to_candidate,
        ),
    )

    chains, metadata = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="M1",
            formula="M1",
        ),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=2,
    )

    assert [chain["hop_count"] for chain in chains] == [1, 2]
    assert [
        [material["material_id"] for material in chain["materials"]]
        for chain in chains
    ] == [[1, 2], [1, 2, 3]]
    assert metadata["expanded_state_count"] == 2


def test_build_chains_retains_dead_end_prefix(
    db_session,
    monkeypatch,
):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    monkeypatch.setattr(
        service,
        "_get_next_candidates",
        lambda material_id, **_: (
            [_candidate(2)] if material_id == 1 else []
        ),
    )
    monkeypatch.setattr(
        service,
        "_build_transition",
        lambda from_material, to_candidate, **_: _transition(
            from_material,
            to_candidate,
        ),
    )

    chains, _ = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="M1",
            formula="M1",
        ),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=3,
    )

    assert len(chains) == 1
    assert chains[0]["hop_count"] == 1


def test_build_chains_retains_prefix_with_only_invalid_continuation(
    db_session,
    monkeypatch,
):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    monkeypatch.setattr(
        service,
        "_get_next_candidates",
        lambda material_id, **_: {
            1: [_candidate(2)],
            2: [_candidate(3)],
        }.get(material_id, []),
    )

    def build_transition(from_material, to_candidate, **_):
        if from_material["material_id"] == 2:
            return None
        return _transition(from_material, to_candidate)

    monkeypatch.setattr(
        service,
        "_build_transition",
        build_transition,
    )

    chains, _ = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="M1",
            formula="M1",
        ),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=3,
    )

    assert len(chains) == 1
    assert chains[0]["hop_count"] == 1
    assert all(chain["hop_count"] <= 3 for chain in chains)


def test_response_limit_does_not_terminate_internal_search(
    db_session,
    monkeypatch,
):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    candidates = {
        1: [_candidate(2), _candidate(3)],
        2: [_candidate(4)],
        3: [],
        4: [],
    }

    monkeypatch.setattr(
        service,
        "_get_next_candidates",
        lambda material_id, **_: candidates[material_id],
    )
    monkeypatch.setattr(
        service,
        "_build_transition",
        lambda from_material, to_candidate, **_: _transition(
            from_material,
            to_candidate,
        ),
    )

    pool, metadata = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="M1",
            formula="M1",
        ),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=2,
    )

    paths = [
        [material["material_id"] for material in chain["materials"]]
        for chain in pool
    ]
    assert [1, 2, 4] in paths
    assert metadata["generated_chain_count"] == 3


def test_search_state_budget_reports_truncation(db_session, monkeypatch):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    monkeypatch.setattr(service, "SEARCH_STATE_BUDGET", 1)
    monkeypatch.setattr(
        service,
        "_get_next_candidates",
        lambda material_id, **_: [_candidate(material_id + 1)],
    )
    monkeypatch.setattr(
        service,
        "_build_transition",
        lambda from_material, to_candidate, **_: _transition(
            from_material,
            to_candidate,
        ),
    )

    _, metadata = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="M1",
            formula="M1",
        ),
        elements_map={},
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=3,
    )

    assert metadata["expanded_state_count"] == 1
    assert metadata["search_truncated"] is True


def test_soft_preference_does_not_block_later_preferred_endpoint(
    db_session,
    monkeypatch,
):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    related_materials = {
        1: [_candidate(2)],
        2: [_candidate(3)],
        3: [],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": related_materials[material_id],
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

    chains, _ = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="FePO4",
            formula="FePO4",
        ),
        elements_map={
            1: ["Fe", "P", "O"],
            2: ["Fe", "P", "O"],
            3: ["Na", "Fe", "P", "O"],
        },
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
        max_hops=2,
    )

    paths = [
        [material["material_id"] for material in chain["materials"]]
        for chain in chains
    ]

    assert [1, 2] in paths
    assert [1, 2, 3] in paths