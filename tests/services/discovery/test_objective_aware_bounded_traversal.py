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
        "reason": "Synthetic bounded-traversal transition.",
        "preserved_framework": ["O"],
    }


def test_preferred_direction_gets_bounded_exploration_opportunity(
    db_session,
    monkeypatch,
):
    """
    Contract:
    A valid preferred objective direction must have a bounded opportunity
    to enter exploration even when objective-neutral candidates ahead of
    it under family ordering outnumber the per-node expansion limit.

    PRE-FIX: expected to fail because _get_next_candidates admits the
    first EXPANSION_LIMIT family candidates without using Prefer.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    # Old family ordering places three objective-neutral candidates first.
    # Candidate 5 contains the preferred element Na but occurs after the cap.
    related_materials = {
        1: [
            _candidate(2),
            _candidate(3),
            _candidate(4),
            _candidate(5),
        ],
        2: [],
        3: [],
        4: [],
        5: [],
    }

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
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
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
        objective_aware_prefer_allocation=True,
        max_hops=1,
    )

    admitted_from_source = [
        chain["materials"][1]["material_id"]
        for chain in chains
        if chain["hop_count"] == 1
    ]

    assert 5 in admitted_from_source


def test_objective_irrelevant_dataset_growth_does_not_displace_preferred_branch(
    db_session,
    monkeypatch,
):
    """
    Dataset-growth invariance contract at source expansion.

    D0 contains an objective-relevant preferred branch that receives an
    exploration opportunity.

    D1 adds objective-irrelevant competitors ahead of that unchanged branch
    under the existing family ordering.

    The added identities:
    - do not contain the preferred element Na;
    - do not alter the source or preferred candidate;
    - do not add a new objective direction;
    - differ only by competing for bounded admission.

    Contract:
    Those additions must not remove the existing preferred branch solely by
    exhausting objective-blind per-node expansion capacity.

    PRE-FIX: expected to fail for D1.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }

    d0_family = [
        _candidate(2),
        _candidate(5),
    ]

    d1_family = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]

    def explored_source_ids(family):
        service = DiscoveryChainService(db_session)
        service.EXPANSION_LIMIT = 3

        related_materials = {
            1: family,
            2: [],
            3: [],
            4: [],
            5: [],
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
            elements_map=elements_map,
            avoid_elements=frozenset(),
            prefer_elements=frozenset({"Na"}),
            objective_aware_prefer_allocation=True,
            max_hops=1,
        )

        return [
            chain["materials"][1]["material_id"]
            for chain in chains
            if chain["hop_count"] == 1
        ]

    d0_admitted = explored_source_ids(d0_family)
    d1_admitted = explored_source_ids(d1_family)

    # Establish that the preferred branch is reachable before irrelevant growth.
    assert 5 in d0_admitted

    # Invariance contract: objective-irrelevant additions must not displace it
    # solely by exhausting the per-node admission bound.
    assert 5 in d1_admitted


def test_strict_avoid_does_not_let_avoided_candidates_exhaust_admission(
    db_session,
    monkeypatch,
):
    """
    Strict bounded-admission contract.

    Non-root family candidates containing an avoided element must not consume
    all scarce expansion capacity ahead of otherwise eligible non-avoided
    candidates merely to be rejected later by Strict mode.

    The contract applies wherever per-node bounded admission occurs, including
    intermediate nodes; this source-level fixture establishes the primary
    starvation mechanism.

    PRE-FIX: expected to fail because _get_next_candidates admits the first
    EXPANSION_LIMIT family candidates without using Avoid.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    # Candidates 2, 3, and 4 contain avoided Li and occupy the complete
    # admission budget. Candidate 5 is a valid non-Li candidate later in the
    # existing family ordering.
    related_materials = {
        1: [
            _candidate(2),
            _candidate(3),
            _candidate(4),
            _candidate(5),
        ],
        2: [],
        3: [],
        4: [],
        5: [],
    }

    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        2: ["Li", "Fe", "P", "O"],
        3: ["Li", "Fe", "P", "O"],
        4: ["Li", "Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": related_materials[material_id],
        },
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li"}),
        prefer_elements=frozenset(),
        hard_avoid_admission=True,
    )

    admitted_ids = [
        candidate["material_id"]
        for candidate in admitted
    ]

    # POST-FIX Strict contract:
    # avoided non-root candidates cannot exhaust the bounded admission budget
    # ahead of an otherwise eligible non-avoided candidate.
    assert 5 in admitted_ids


def test_preferred_direction_gets_bounded_opportunity_at_second_hop(
    db_session,
    monkeypatch,
):
    """
    Per-expanded-node objective-aware traversal contract.

    S -> I is admitted normally. At intermediate I, objective-neutral
    candidates ahead under family ordering exhaust the per-node bound before
    preferred candidate P.

    Contract:
    The preferred direction must receive a bounded exploration opportunity at
    an intermediate node just as it must at the source.

    PRE-FIX: expected to fail because the same objective-blind first-N
    admission is applied independently at I.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = {
        # S -> I
        1: [_candidate(2)],

        # At I, neutral candidates 3/4/5 exhaust the bound.
        # Preferred candidate 6 occurs immediately afterward.
        2: [
            _candidate(3),
            _candidate(4),
            _candidate(5),
            _candidate(6),
        ],
        3: [],
        4: [],
        5: [],
        6: [],
    }

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Fe", "P", "O"],
        6: ["Na", "Fe", "P", "O"],
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
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
        objective_aware_prefer_allocation=True,
        max_hops=2,
    )

    paths = [
        [
            material["material_id"]
            for material in chain["materials"]
        ]
        for chain in chains
    ]

    # Establish that the intermediate itself was explored.
    assert [1, 2] in paths

    # POST-FIX per-node contract.
    assert [1, 2, 6] in paths


def test_no_objective_preserves_existing_family_admission_order(
    db_session,
    monkeypatch,
):
    """
    Backward-compatibility baseline.

    With no Avoid or Prefer objective, bounded admission must preserve the
    existing family ordering and existing expansion behavior.

    PRE-FIX: expected to pass.
    POST-FIX: must continue to pass unless separately justified.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": related_materials,
        },
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map={
            1: ["Fe", "P", "O"],
            2: ["Fe", "P", "O"],
            3: ["Fe", "P", "O"],
            4: ["Fe", "P", "O"],
            5: ["Na", "Fe", "P", "O"],
        },
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
    )

    assert [
        candidate["material_id"]
        for candidate in admitted
    ] == [2, 3, 4]


def test_objective_does_not_displace_valid_high_overlap_candidates_without_competition(
    db_session,
    monkeypatch,
):
    """
    Negative control.

    Existing high-priority family candidates remain legitimate when the
    objective creates no competing direction requiring bounded opportunity.

    Merely supplying an objective must not arbitrarily reserve or reorder
    admission slots.

    PRE-FIX: expected to pass.
    POST-FIX: must continue to pass.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Na", "Fe", "P", "O"],
        3: ["Na", "Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": related_materials,
        },
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
        objective_aware_prefer_allocation=True,
    )

    # Preferred candidates already occupy legitimate positions inside the
    # existing bound. There is no starvation to repair, so admission remains
    # the existing deterministic first-three sequence.
    assert [
        candidate["material_id"]
        for candidate in admitted
    ] == [2, 3, 4]


def test_objective_irrelevant_growth_at_downstream_node_does_not_displace_preferred_branch(
    db_session,
    monkeypatch,
):
    """
    Dataset-growth invariance contract at a downstream expanded node.

    D0 contains an existing S -> I -> P preferred branch.

    D1 leaves S, I, P, and the objective unchanged, but adds predefined
    objective-irrelevant identities ahead of P in I's family ordering.

    Contract:
    Those additions must not remove the existing objective-relevant branch
    solely by exhausting I's bounded admission capacity.

    PRE-FIX: expected to fail for D1.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Fe", "P", "O"],
        6: ["Na", "Fe", "P", "O"],
    }

    d0_intermediate_family = [
        _candidate(3),
        _candidate(6),
    ]

    d1_intermediate_family = [
        _candidate(3),
        _candidate(4),
        _candidate(5),
        _candidate(6),
    ]

    def paths_for(intermediate_family):
        service = DiscoveryChainService(db_session)
        service.EXPANSION_LIMIT = 3

        related_materials = {
            1: [_candidate(2)],
            2: intermediate_family,
            3: [],
            4: [],
            5: [],
            6: [],
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
            elements_map=elements_map,
            avoid_elements=frozenset(),
            prefer_elements=frozenset({"Na"}),
            objective_aware_prefer_allocation=True,
            max_hops=2,
        )

        return [
            [
                material["material_id"]
                for material in chain["materials"]
            ]
            for chain in chains
        ]

    d0_paths = paths_for(d0_intermediate_family)
    d1_paths = paths_for(d1_intermediate_family)

    # Establish the unchanged preferred branch before irrelevant growth.
    assert [1, 2, 6] in d0_paths

    # Invariance must hold at downstream expansion as well as at the source.
    assert [1, 2, 6] in d1_paths


def test_objective_relevant_dataset_growth_may_compete_for_bounded_admission(
    db_session,
    monkeypatch,
):
    """
    Relevant-growth control.

    Dataset-growth invariance applies only to predefined objective-irrelevant
    additions. New candidates that themselves satisfy the preferred objective
    direction are legitimately relevant and may compete for bounded admission.

    This test captures deterministic bounded behavior without requiring the
    pre-growth admitted set to remain invariant.

    PRE-FIX: expected to pass.
    POST-FIX: must remain deterministic and bounded, but relevant additions
    are allowed to change which preferred candidates are admitted.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    # Candidate 5 is an existing preferred candidate.
    # Candidates 6 and 7 are genuinely new preferred-direction data.
    related_materials = [
        _candidate(2),
        _candidate(5),
        _candidate(6),
        _candidate(7),
    ]

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
        6: ["Na", "Fe", "P", "O"],
        7: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": related_materials,
        },
    )

    admitted_first = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
    )

    admitted_second = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
    )

    first_ids = [
        candidate["material_id"]
        for candidate in admitted_first
    ]
    second_ids = [
        candidate["material_id"]
        for candidate in admitted_second
    ]

    # Bounded and deterministic.
    assert len(first_ids) == service.EXPANSION_LIMIT
    assert second_ids == first_ids

    # This is deliberately NOT an invariance assertion about retaining every
    # previously preferred identity. Relevant new data is allowed to compete.
    assert first_ids == [2, 5, 6]


def test_production_representative_source5_preferred_direction_gets_bounded_opportunity(
    db_session,
    monkeypatch,
):
    """
    Production-representative regression for the source-5 scale interaction.

    Snapshot provenance from read-only production inspection:
      source: ID 5 / mp-19017 / LiFePO4
      total related family candidates: 839
      expansion limit: 6

      positions 1-6:
        1, 2, 3, 4, 198, 199
        all retain Li and share Fe/Li/O/P with the source

      preferred-direction gateways:
        ID 6 / mp-19028 at production family position 148
        ID 7 / mp-556540 at production family position 149
        both contain Na and do not retain Li

    The omitted production identities between positions 6 and 148 are not
    materialized here because this is an admission-boundary regression, not a
    reproduction of the complete production family dataset.

    Contract:
    A preferred objective direction that exists outside the legacy
    objective-blind first-N boundary must receive a bounded exploration
    opportunity.

    This test does NOT require ID 6 or ID 7 to rank first and does not define
    restoration of a historical sodium shortlist as algorithmic success.

    PRE-FIX: expected to fail.
    """

    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 6

    # Preserve the production-observed boundary ordering. IDs 6 and 7 represent
    # the preferred direction observed at positions 148 and 149 respectively.
    production_boundary_snapshot = [
        _candidate(1),
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(198),
        _candidate(199),
        _candidate(6),
        _candidate(7),
    ]

    elements_map = {
        5: ["Li", "Fe", "P", "O"],
        1: ["Li", "Fe", "P", "O"],
        2: ["Li", "Fe", "P", "O"],
        3: ["Li", "Fe", "P", "O"],
        4: ["Li", "Fe", "P", "O"],
        198: ["Li", "Fe", "P", "O"],
        199: ["Li", "Fe", "P", "O"],
        6: ["Na", "Fe", "P", "O"],
        7: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": production_boundary_snapshot,
        },
    )

    admitted = service._get_next_candidates(
        material_id=5,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li", "Co"}),
        prefer_elements=frozenset({"Na", "K"}),
        objective_aware_prefer_allocation=True,
    )

    admitted_ids = [
        candidate["material_id"]
        for candidate in admitted
    ]

    assert len(admitted_ids) <= service.EXPANSION_LIMIT

    # General objective-direction contract. Either production-observed Na
    # gateway can satisfy the regression; neither is required to rank first.
    assert {6, 7}.intersection(admitted_ids)


def test_no_objective_preserves_existing_bounded_chain_baseline(
    db_session,
    monkeypatch,
):
    """
    No-objective backward-compatibility characterization.

    With no Avoid or Prefer objective, freeze the legacy bounded traversal
    behavior at the chain level as well as at the admission boundary.

    POST-FIX must preserve this behavior unless an independent change is
    explicitly justified.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = {
        1: [_candidate(2), _candidate(3), _candidate(4), _candidate(5)],
        2: [],
        3: [],
        4: [],
        5: [],
    }

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Fe", "P", "O"],
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

    chains, metadata = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="FePO4",
            formula="FePO4",
        ),
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        max_hops=1,
    )

    paths = [
        [
            material["material_id"]
            for material in chain["materials"]
        ]
        for chain in chains
    ]

    assert paths == [
        [1, 2],
        [1, 3],
        [1, 4],
    ]
    assert metadata["generated_chain_count"] == 3
    assert metadata["expanded_state_count"] == 1
    assert metadata["search_truncated"] is False


def test_multiple_preferred_directions_receive_bounded_opportunity_when_capacity_allows(
    db_session,
    monkeypatch,
):
    """
    Multiple preferred directions are independently meaningful.

    With capacity for both represented preferred directions, objective-neutral
    candidates ahead in legacy family ordering must not consume every slot.

    A single candidate may satisfy more than one preferred element, but here
    Na and K are intentionally represented by separate candidates.

    PRE-FIX: expected to fail.
    """
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    family_candidates = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),  # Na direction
        _candidate(6),  # K direction
    ]

    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
        6: ["K", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": family_candidates,
        },
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na", "K"}),
        objective_aware_prefer_allocation=True,
    )

    admitted_ids = [
        candidate["material_id"]
        for candidate in admitted
    ]

    assert len(admitted_ids) <= service.EXPANSION_LIMIT
    assert 5 in admitted_ids
    assert 6 in admitted_ids


def test_preferred_allocation_cache_isolated_from_legacy_admission(
    db_session,
    monkeypatch,
):
    """Policy toggles must not reuse incompatible cached admission results."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    def admitted_ids(enabled):
        candidates = service._get_next_candidates(
            material_id=1,
            elements_map=elements_map,
            avoid_elements=frozenset(),
            prefer_elements=frozenset({"Na"}),
            objective_aware_prefer_allocation=enabled,
        )
        return [candidate["material_id"] for candidate in candidates]

    assert admitted_ids(False) == [2, 3, 4]
    assert admitted_ids(True) == [2, 3, 5]
    assert admitted_ids(False) == [2, 3, 4]
    assert admitted_ids(True) == [2, 3, 5]


def test_hard_avoid_cache_isolated_from_soft_admission(
    db_session,
    monkeypatch,
):
    """Hard Avoid must not reuse soft-admission cached candidates."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Li", "Fe", "P", "O"],
        3: ["Li", "Fe", "P", "O"],
        4: ["Li", "Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    def admitted_ids(enabled):
        candidates = service._get_next_candidates(
            material_id=1,
            elements_map=elements_map,
            avoid_elements=frozenset({"Li"}),
            prefer_elements=frozenset(),
            hard_avoid_admission=enabled,
        )
        return [candidate["material_id"] for candidate in candidates]

    assert admitted_ids(False) == [2, 3, 4]
    assert admitted_ids(True) == [5]
    assert admitted_ids(False) == [2, 3, 4]
    assert admitted_ids(True) == [5]


def test_preferred_allocation_restores_original_family_order(
    db_session,
    monkeypatch,
):
    """Reserved preferred candidates retain their family-relative order."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
        _candidate(6),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
        6: ["K", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na", "K"}),
        objective_aware_prefer_allocation=True,
    )

    admitted_ids = [
        candidate["material_id"] for candidate in admitted
    ]

    assert admitted_ids == [2, 5, 6]


def test_single_candidate_can_cover_multiple_preferred_elements(
    db_session,
    monkeypatch,
):
    """One candidate covering Na and K consumes only one reserved slot."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
        _candidate(6),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "K", "Fe", "P", "O"],
        6: ["K", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na", "K"}),
        objective_aware_prefer_allocation=True,
    )

    admitted_ids = [
        candidate["material_id"] for candidate in admitted
    ]

    assert admitted_ids == [2, 3, 5]


def test_preference_oversubscription_uses_sorted_direction_order(
    db_session,
    monkeypatch,
):
    """When capacity is insufficient, sorted preferred directions win."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 2

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Na", "Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Mg", "Fe", "P", "O"],
        5: ["K", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na", "Mg", "K"}),
        objective_aware_prefer_allocation=True,
    )

    admitted_ids = [
        candidate["material_id"] for candidate in admitted
    ]

    # K and Mg win the two available reservations.
    # Return order follows original family order, not preference order.
    assert admitted_ids == [4, 5]


def test_hard_avoid_returns_empty_when_all_neighbors_excluded(
    db_session,
    monkeypatch,
):
    """Hard Avoid never relaxes admission when all neighbors are excluded."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
    ]
    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        2: ["Li", "Fe", "P", "O"],
        3: ["Li", "Co", "P", "O"],
        4: ["Co", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li", "Co"}),
        prefer_elements=frozenset({"Na"}),
        hard_avoid_admission=True,
        objective_aware_prefer_allocation=True,
    )

    assert admitted == []


def test_prefer_elements_without_allocation_flag_preserves_legacy_admission(
    db_session,
    monkeypatch,
):
    """Prefer inputs alone must not activate objective-aware admission."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
        hard_avoid_admission=False,
        objective_aware_prefer_allocation=False,
    )

    assert [candidate["material_id"] for candidate in admitted] == [2, 3, 4]


def test_hard_avoid_without_prefer_allocation_preserves_family_order(
    db_session,
    monkeypatch,
):
    """Hard Avoid filters before the cap without reserving preferred slots."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 2

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]
    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        2: ["Li", "Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li"}),
        prefer_elements=frozenset({"Na"}),
        hard_avoid_admission=True,
        objective_aware_prefer_allocation=False,
    )

    assert [candidate["material_id"] for candidate in admitted] == [3, 4]


def test_enabled_prefer_allocation_with_empty_prefer_preserves_legacy_order(
    db_session,
    monkeypatch,
):
    """Enabled allocation with no Prefer directions preserves legacy admission."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 3

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(4),
        _candidate(5),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": related_materials},
    )

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset(),
        hard_avoid_admission=False,
        objective_aware_prefer_allocation=True,
    )

    assert [candidate["material_id"] for candidate in admitted] == [2, 3, 4]


def test_preferred_dead_end_does_not_trigger_transition_backfill(
    db_session,
    monkeypatch,
):
    """A failed preferred transition does not cause admission backfill."""
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = 2

    related_materials = [
        _candidate(2),
        _candidate(3),
        _candidate(5),
        _candidate(6),
    ]
    elements_map = {
        1: ["Fe", "P", "O"],
        2: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
        6: ["Na", "Fe", "P", "O"],
    }

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {
            "related_materials": related_materials if material_id == 1 else [],
        },
    )

    attempted_ids = []

    def build_transition(from_material, to_candidate, **kwargs):
        candidate_id = to_candidate["material_id"]
        attempted_ids.append(candidate_id)

        if candidate_id == 5:
            return None

        return _transition(from_material, to_candidate)

    monkeypatch.setattr(service, "_build_transition", build_transition)

    chains, _ = service._build_chains(
        base_material=SimpleNamespace(
            id=1,
            mp_id="mp-1",
            pretty_formula="FePO4",
            formula="FePO4",
        ),
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
        max_hops=1,
        objective_aware_prefer_allocation=True,
    )

    assert attempted_ids == [2, 5]

    generated_ids = [
        chain["materials"][1]["material_id"]
        for chain in chains
        if chain["hop_count"] == 1
    ]

    assert generated_ids == [2]
    assert 6 not in attempted_ids


def test_objective_explore_routes_admission_policies_by_mode(
    db_session,
    monkeypatch,
):
    """Objective Explore explicitly routes both policies for every mode."""
    from app.services.research.objective_exploration_service import (
        ResearchObjectiveExplorationService,
    )

    service = ResearchObjectiveExplorationService(db_session)
    objective = SimpleNamespace(
        avoid_elements=["Li"],
        prefer_lower_criticality=False,
    )
    recorded = []

    def fake_generate_chains_for_objective(**kwargs):
        recorded.append(kwargs)
        return {
            "chains": [],
            "search_metadata": {},
            "objective_policy": {},
            "base_formula": "LiFePO4",
        }

    monkeypatch.setattr(
        service.objective_service,
        "generate_chains_for_objective",
        fake_generate_chains_for_objective,
    )

    for mode, expected_hard_avoid in [
        ("strict", True),
        ("balanced", False),
        ("exploratory", False),
    ]:
        request = SimpleNamespace(
            objective=objective,
            mode=mode,
            limit=5,
        )

        result = service.explore(material_id=5, request=request)
        forwarded = recorded[-1]

        assert forwarded["material_id"] == 5
        assert forwarded["objective"] is objective
        assert forwarded["include_ranked_pool"] is True
        assert forwarded["hard_avoid_admission"] is expected_hard_avoid
        assert forwarded["objective_aware_prefer_allocation"] is True
        assert result["mode"] == mode

    assert len(recorded) == 3


def test_shared_objective_bridge_forwards_only_explicit_admission_flags(
    db_session,
    monkeypatch,
):
    """Objective inputs must not implicitly activate admission policies."""
    from app.services.research.objective_service import ResearchObjectiveService

    service = ResearchObjectiveService(db_session)
    objective = SimpleNamespace(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=[],
        target_family=None,
        require_stable_materials=False,
        prefer_lower_criticality=False,
        max_hops=2,
        limit=5,
    )

    forwarded_calls = []

    def fake_get_discovery_chains(**kwargs):
        forwarded_calls.append(kwargs)
        return {
            "material_id": 5,
            "base_formula": "LiFePO4",
            "chains": [],
            "search_metadata": {},
        }

    monkeypatch.setattr(
        service.chain_service,
        "get_discovery_chains",
        fake_get_discovery_chains,
    )

    for overrides, expected_flags in [
        ({}, (False, False)),
        (
            {
                "hard_avoid_admission": True,
                "objective_aware_prefer_allocation": True,
            },
            (True, True),
        ),
        ({}, (False, False)),
    ]:
        result = service.generate_chains_for_objective(
            material_id=5,
            objective=objective,
            **overrides,
        )

        forwarded = forwarded_calls[-1]

        assert forwarded["hard_avoid_admission"] is expected_flags[0]
        assert (
            forwarded["objective_aware_prefer_allocation"]
            is expected_flags[1]
        )
        assert forwarded["avoid_elements"] == ["Li"]
        assert forwarded["prefer_elements"] == ["Na"]
        assert forwarded["include_search_pool"] is True
        assert result["chains"] == []

    assert len(forwarded_calls) == 3


# ---------------------------------------------------------------------------
# Finding 1 (approved refinement) - Strict hard Avoid fails closed for
# candidates without MaterialElement membership.
#
# Refinement to the frozen traversal contract, explicitly approved during
# qualification: under Strict hard-Avoid admission with a non-empty Avoid
# set, a candidate whose composition is unknown cannot be shown to be free
# of avoided elements, so it must not consume bounded admission capacity.
# Balanced/Exploratory admission, Strict with an empty Avoid set, and the
# legacy flags-off path are unchanged. The final Strict filter is untouched.
# ---------------------------------------------------------------------------


def _missing_membership_service(db_session, monkeypatch, family, limit):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)
    service.EXPANSION_LIMIT = limit

    monkeypatch.setattr(
        service,
        "_get_family_result",
        lambda material_id: {"related_materials": family},
    )
    return service


def test_strict_hard_avoid_excludes_candidates_without_element_membership(
    db_session,
    monkeypatch,
):
    """
    Strict + prefer allocation: candidates 2 and 3 have no element rows.
    They must not occupy admission slots ahead of verified candidates.

    PRE-REFINEMENT: expected to fail (admits [2, 3, 6]).
    """
    family = [_candidate(i) for i in (2, 3, 4, 5, 6)]
    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        # 2 and 3 intentionally absent: no MaterialElement membership.
        4: ["Li", "Fe", "P", "O"],
        5: ["Fe", "P", "O"],
        6: ["Na", "Fe", "P", "O"],
    }
    service = _missing_membership_service(db_session, monkeypatch, family, 3)

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li"}),
        prefer_elements=frozenset({"Na"}),
        hard_avoid_admission=True,
        objective_aware_prefer_allocation=True,
    )

    assert [c["material_id"] for c in admitted] == [5, 6]
    assert list(service._admission_diagnostics.values()) == [
        {"missing_membership_excluded": 2}
    ]


def test_strict_hard_avoid_without_allocation_excludes_missing_membership(
    db_session,
    monkeypatch,
):
    """
    Strict without prefer allocation: fail-closed exclusion still applies.

    PRE-REFINEMENT: expected to fail (admits [2, 3]).
    """
    family = [_candidate(i) for i in (2, 3, 4)]
    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
    }
    service = _missing_membership_service(db_session, monkeypatch, family, 2)

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li"}),
        prefer_elements=frozenset(),
        hard_avoid_admission=True,
        objective_aware_prefer_allocation=False,
    )

    assert [c["material_id"] for c in admitted] == [3, 4]


def test_missing_membership_exclusion_is_stable_across_cache_hits(
    db_session,
    monkeypatch,
):
    """
    Repeated Strict admission returns identical results and diagnostics
    are recorded once per admission key, not re-counted on cache hits.

    PRE-REFINEMENT: expected to fail (admits [2, 4]).
    """
    family = [_candidate(i) for i in (2, 3, 4)]
    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        3: ["Li", "Fe", "P", "O"],
        4: ["Fe", "P", "O"],
    }
    service = _missing_membership_service(db_session, monkeypatch, family, 2)

    def admitted_ids():
        return [
            c["material_id"]
            for c in service._get_next_candidates(
                material_id=1,
                elements_map=elements_map,
                avoid_elements=frozenset({"Li"}),
                prefer_elements=frozenset(),
                hard_avoid_admission=True,
            )
        ]

    assert admitted_ids() == [4]
    assert admitted_ids() == [4]
    assert list(service._admission_diagnostics.values()) == [
        {"missing_membership_excluded": 1}
    ]


def test_balanced_admits_missing_membership_candidates_in_family_order(
    db_session,
    monkeypatch,
):
    """
    Balanced (hard Avoid off): unknown-composition candidates keep their
    family position and are never treated as preferred.

    PRE-REFINEMENT: expected to pass (control).
    """
    family = [_candidate(i) for i in (2, 3, 4, 5)]
    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }
    service = _missing_membership_service(db_session, monkeypatch, family, 3)

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li"}),
        prefer_elements=frozenset({"Na"}),
        hard_avoid_admission=False,
        objective_aware_prefer_allocation=True,
    )

    assert [c["material_id"] for c in admitted] == [2, 3, 5]


def test_strict_with_empty_avoid_does_not_exclude_missing_membership(
    db_session,
    monkeypatch,
):
    """
    Fail-closed exclusion exists only to enforce Avoid. With no avoided
    elements there is nothing to verify, so unknown composition is admitted.

    PRE-REFINEMENT: expected to pass (control).
    """
    family = [_candidate(i) for i in (2, 3, 4, 5)]
    elements_map = {
        1: ["Fe", "P", "O"],
        3: ["Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }
    service = _missing_membership_service(db_session, monkeypatch, family, 3)

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset(),
        prefer_elements=frozenset({"Na"}),
        hard_avoid_admission=True,
        objective_aware_prefer_allocation=True,
    )

    assert [c["material_id"] for c in admitted] == [2, 3, 5]


def test_legacy_admission_unchanged_for_missing_membership(
    db_session,
    monkeypatch,
):
    """
    Flags off: legacy objective-blind first-N admission is unchanged,
    including for unknown-composition candidates.

    PRE-REFINEMENT: expected to pass (control).
    """
    family = [_candidate(i) for i in (2, 3, 4, 5)]
    elements_map = {
        1: ["Li", "Fe", "P", "O"],
        3: ["Li", "Fe", "P", "O"],
        4: ["Fe", "P", "O"],
        5: ["Na", "Fe", "P", "O"],
    }
    service = _missing_membership_service(db_session, monkeypatch, family, 3)

    admitted = service._get_next_candidates(
        material_id=1,
        elements_map=elements_map,
        avoid_elements=frozenset({"Li"}),
        prefer_elements=frozenset({"Na"}),
    )

    assert [c["material_id"] for c in admitted] == [2, 3, 4]
