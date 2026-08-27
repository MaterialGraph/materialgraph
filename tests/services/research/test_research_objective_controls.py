from types import SimpleNamespace

from app.schemas.discovery import ResearchObjective
from app.services.discovery.path_ranking_service import (
    DiscoveryPathRankingService,
)
from app.services.material.quality_service import MaterialQualityService
from app.services.research.objective_exploration_service import (
    ResearchObjectiveExplorationService,
)
from app.services.research.objective_service import ResearchObjectiveService


def _chain(*material_ids: int) -> dict:
    return {
        "materials": [
            {"material_id": material_id, "formula": f"M{material_id}"}
            for material_id in material_ids
        ],
        "transitions": [],
    }


class _QualityServiceStub:
    def __init__(self, quality_by_id: dict[int, dict]):
        self.quality_by_id = quality_by_id

    def get_material_quality_bulk(self, material_ids: list[int]):
        return {
            material_id: self.quality_by_id[material_id]
            for material_id in material_ids
            if material_id in self.quality_by_id
        }


class _PathRankingStub:
    def __init__(self):
        self.calls: list[dict] = []

    def rank_path(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "scientific_usefulness_score": 0.0,
            "score_breakdown": {},
            "usefulness_reason": "Stub ranking.",
        }


def test_canonical_quality_exposes_separate_quality_components():
    service = MaterialQualityService.__new__(MaterialQualityService)
    material = SimpleNamespace(
        id=2,
        is_stable=True,
        energy_above_hull=0.0,
    )

    quality = service._build_quality_response(
        material=material,
        criticality_score=20.0,
        risk_signal={
            "risk_score": 2.0,
            "risk_known": True,
            "risk_evidence_complete": True,
        },
    )

    assert quality["stability_quality_contribution"] == 10.5
    assert quality["criticality_quality_contribution"] == 2.25
    assert quality["risk_quality_contribution"] == 2.25
    assert quality["quality_score"] == 15.0


def test_stability_requirement_is_a_hard_non_root_filter():
    service = ResearchObjectiveService.__new__(ResearchObjectiveService)
    service.quality_service = _QualityServiceStub({
        2: {"stability_band": "stable"},
        3: {"stability_band": "near_stable"},
    })
    stable_chain = _chain(1, 2)
    non_stable_chain = _chain(1, 3)

    optional = service._filter_chains(
        [stable_chain, non_stable_chain],
        ResearchObjective(require_stable_materials=False),
    )
    required = service._filter_chains(
        [stable_chain, non_stable_chain],
        ResearchObjective(require_stable_materials=True),
    )

    assert optional == [stable_chain, non_stable_chain]
    assert required == [stable_chain]


def test_stability_requirement_checks_every_hop_and_rejects_unknown():
    service = ResearchObjectiveService.__new__(ResearchObjectiveService)
    service.quality_service = _QualityServiceStub({
        2: {"stability_band": "stable"},
        3: {"stability_band": "unknown"},
    })

    result = service._filter_chains(
        [_chain(1, 2, 3), _chain(1, 4)],
        ResearchObjective(require_stable_materials=True),
    )

    assert result == []


def test_lower_criticality_control_is_forwarded_to_path_ranking():
    service = ResearchObjectiveService.__new__(ResearchObjectiveService)
    service.path_ranking_service = _PathRankingStub()

    service._rank_chains(
        [_chain(1, 2)],
        ResearchObjective(prefer_lower_criticality=False),
    )

    assert service.path_ranking_service.calls[0][
        "prefer_lower_criticality"
    ] is False


def test_path_quality_conditionally_includes_criticality():
    service = DiscoveryPathRankingService()
    service.material_quality_service = _QualityServiceStub({
        material_id: {
            "quality_score": 12.0,
            "stability_quality_contribution": 6.0,
            "risk_quality_contribution": 2.0,
            "criticality_quality_contribution": 4.0,
        }
        for material_id in (1, 2)
    })
    materials = _chain(1, 2)["materials"]

    assert service._score_material_quality(
        materials,
        prefer_lower_criticality=True,
    ) == 12.0
    assert service._score_material_quality(
        materials,
        prefer_lower_criticality=False,
    ) == 8.0
    assert service._score_material_quality(materials) == 12.0


def test_exploration_score_conditionally_includes_criticality():
    service = ResearchObjectiveExplorationService.__new__(
        ResearchObjectiveExplorationService
    )
    material = {"material_id": 2, "formula": "NaFePO4"}
    quality = {"criticality_quality_contribution": 2.25}

    preferred = service._score_material(
        material,
        [],
        ResearchObjective(prefer_lower_criticality=True),
        "balanced",
        quality,
    )
    excluded = service._score_material(
        material,
        [],
        ResearchObjective(prefer_lower_criticality=False),
        "balanced",
        quality,
    )

    assert preferred == 52.25
    assert excluded == 50.0


def test_execution_policy_discloses_effective_semantics():
    policy = ResearchObjectiveService._build_objective_policy(
        ResearchObjective(
            prefer_lower_criticality=False,
            require_stable_materials=True,
        )
    )

    assert policy["stable_materials"] == "hard_rejection"
    assert policy["stability_scope"] == "all_non_root_chain_materials"
    assert policy["unknown_stability_evidence"] == "hard_rejection"
    assert policy["lower_criticality"] == (
        "excluded_from_objective_ranking"
    )