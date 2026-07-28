from app.services.discovery.k_best_path_service import DiscoveryKBestPathService

def test_k_best_path_service_returns_paths(db_session):
    service = DiscoveryKBestPathService(db_session)

    result = service.get_k_best_paths(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        k=3,
    )

    assert result["start_material_id"] == 5
    assert result["target_material_id"] == 7
    assert result["k"] == 3
    assert "paths" in result
    assert isinstance(result["paths"], list)
    assert result["paths"]
    assert isinstance(result["search_truncated"], bool)


def test_k_best_paths_are_ranked_by_scientific_usefulness(db_session):
    service = DiscoveryKBestPathService(db_session)

    result = service.get_k_best_paths(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        k=3,
    )

    scores = [
        path["scientific_usefulness_score"]
        for path in result["paths"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_k_best_path_service_respects_k_limit(db_session):
    service = DiscoveryKBestPathService(db_session)

    result = service.get_k_best_paths(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        k=1,
    )

    assert len(result["paths"]) <= 1

def test_k_shortest_paths_are_ordered_by_hop_count(db_session):
    service = DiscoveryKBestPathService(db_session)

    result = service.get_k_shortest_paths(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        k=5,
    )

    hop_counts = [path["hop_count"] for path in result["paths"]]

    assert result["algorithm"] == "k_shortest_paths"
    assert hop_counts == sorted(hop_counts)


def test_k_best_uses_metadata_from_actual_incoming_edge(db_session):
    service = DiscoveryKBestPathService(db_session)
    adjacency = {
        1: [
            {
                "material_id": 3,
                "mp_id": "mp-from-1",
                "pretty_formula": "Wrong",
            },
            {
                "material_id": 2,
                "mp_id": "mp-2",
                "pretty_formula": "Intermediate",
            },
        ],
        2: [
            {
                "material_id": 3,
                "mp_id": "mp-from-2",
                "pretty_formula": "Correct",
            }
        ],
    }

    materials = service._materials_for_path(
        path_ids=[1, 2, 3],
        adjacency=adjacency,
        start_material_id=1,
    )

    assert materials[-1]["mp_id"] == "mp-from-2"
    assert materials[-1]["pretty_formula"] == "Correct"


def test_k_best_transitions_use_canonical_validated_metadata(db_session):
    service = DiscoveryKBestPathService(db_session)
    adjacency = {
        1: [
            {
                "material_id": 2,
                "discovery_path": ["misleading_raw_path"],
                "validated_transition": {
                    "transition_type": "family_expansion",
                    "family": "phosphate",
                    "preserved_framework": ["Fe", "O", "P"],
                    "preservation_basis": "element_overlap",
                    "structural_preservation_validated": False,
                    "removed_elements": ["Li"],
                    "introduced_elements": ["Na"],
                    "reason": "Canonical validator reason.",
                },
            }
        ]
    }

    transitions = service._transitions_for_path(
        path_ids=[1, 2],
        adjacency=adjacency,
    )

    assert transitions == [
        {
            "source_material_id": 1,
            "target_material_id": 2,
            "transition_type": "family_expansion",
            "family": "phosphate",
            "preserved_framework": ["Fe", "O", "P"],
            "preservation_basis": "element_overlap",
            "structural_preservation_validated": False,
            "removed_elements": ["Li"],
            "introduced_elements": ["Na"],
            "scientific_reason": "Canonical validator reason.",
        }
    ]


def test_simple_path_enumeration_enforces_path_budget(
    db_session,
    monkeypatch,
):
    service = DiscoveryKBestPathService(db_session)
    monkeypatch.setattr(service, "INTERNAL_PATH_LIMIT", 2)
    adjacency = {
        1: [
            {"material_id": 2},
            {"material_id": 3},
            {"material_id": 4},
        ],
        2: [{"material_id": 9}],
        3: [{"material_id": 9}],
        4: [{"material_id": 9}],
    }

    paths, search_truncated = service._enumerate_simple_paths(
        start_material_id=1,
        target_material_id=9,
        adjacency=adjacency,
        max_hops=2,
    )

    assert paths == [[1, 2, 9], [1, 3, 9]]
    assert search_truncated is True


def test_simple_path_enumeration_enforces_state_budget(
    db_session,
    monkeypatch,
):
    service = DiscoveryKBestPathService(db_session)
    monkeypatch.setattr(service, "INTERNAL_STATE_LIMIT", 2)
    adjacency = {
        1: [
            {"material_id": 2},
            {"material_id": 3},
            {"material_id": 4},
        ]
    }

    paths, search_truncated = service._enumerate_simple_paths(
        start_material_id=1,
        target_material_id=99,
        adjacency=adjacency,
        max_hops=2,
    )

    assert paths == []
    assert search_truncated is True


def test_k_best_ranks_only_paths_within_internal_budget(
    db_session,
    monkeypatch,
):
    service = DiscoveryKBestPathService(db_session)
    monkeypatch.setattr(service, "INTERNAL_PATH_LIMIT", 2)
    adjacency = {
        1: [
            {
                "material_id": material_id,
                "validated_transition": {
                    "transition_type": "family_expansion",
                    "reason": "validated",
                },
            }
            for material_id in (2, 3, 4)
        ],
        2: [
            {
                "material_id": 9,
                "validated_transition": {
                    "transition_type": "family_expansion",
                    "reason": "validated",
                },
            }
        ],
        3: [
            {
                "material_id": 9,
                "validated_transition": {
                    "transition_type": "family_expansion",
                    "reason": "validated",
                },
            }
        ],
        4: [
            {
                "material_id": 9,
                "validated_transition": {
                    "transition_type": "family_expansion",
                    "reason": "validated",
                },
            }
        ],
    }
    monkeypatch.setattr(
        service.graph_builder,
        "build_adjacency",
        lambda **kwargs: adjacency,
    )
    ranking_calls = []

    def rank_path(**kwargs):
        ranking_calls.append(kwargs)
        return {
            "scientific_usefulness_score": 50.0,
            "score_breakdown": {},
            "usefulness_reason": "bounded",
        }

    monkeypatch.setattr(
        service.path_ranking_service,
        "rank_path",
        rank_path,
    )

    result = service.get_k_best_paths(
        start_material_id=1,
        target_material_id=9,
        max_hops=2,
        k=5,
    )

    assert len(ranking_calls) == 2
    assert result["total_path_count"] == 2
    assert result["search_truncated"] is True