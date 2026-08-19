from app.services.discovery.edge_intelligence_service import (
    DiscoveryEdgeIntelligenceService,
)

def test_edge_intelligence_scores_alkali_substitution():
    service = DiscoveryEdgeIntelligenceService()

    result = service.build_edge_intelligence(
        transition_type="alkali_substitution",
        family="phosphate",
        preserved_framework=["Fe", "P", "O"],
        removed_elements=["Li"],
        introduced_elements=["Na"],
        scientific_reason="Li is replaced by Na while preserving phosphate chemistry.",
    )

    assert result["scientific_plausibility"] == 1.0
    assert result["edge_score"] == 100.0
    assert result["plausibility_basis"] == "internal_composition_heuristic"
    assert result["substitution_mechanism_validated"] is False
    assert "scientific_reason" in result


def test_edge_intelligence_scores_family_expansion():
    service = DiscoveryEdgeIntelligenceService()

    result = service.build_edge_intelligence(
        transition_type="family_expansion",
        family="phosphate",
        preserved_framework=["P", "O"],
        removed_elements=[],
        introduced_elements=[],
        scientific_reason="Expands within phosphate family.",
    )

    assert result["scientific_plausibility"] == 0.75
    assert result["edge_score"] == 75.0


def test_edge_intelligence_scores_unknown_transition():
    service = DiscoveryEdgeIntelligenceService()

    result = service.build_edge_intelligence(
        transition_type=None,
        family=None,
        preserved_framework=[],
        removed_elements=[],
        introduced_elements=[],
        scientific_reason="Fallback transition.",
    )

    assert result["scientific_plausibility"] == 0.5
    assert result["edge_score"] == 40.0

def test_edge_score_preserves_framework_and_exchange_distinctions():
    service = DiscoveryEdgeIntelligenceService()

    strong = service.build_edge_intelligence(
        transition_type="alkali_substitution",
        family="phosphate",
        preserved_framework=["Fe", "P", "O"],
        removed_elements=["Li"],
        introduced_elements=["Na"],
        scientific_reason="Strong evidence.",
    )

    partial = service.build_edge_intelligence(
        transition_type="alkali_substitution",
        family="phosphate",
        preserved_framework=[],
        removed_elements=["Li"],
        introduced_elements=["Na"],
        scientific_reason="Partial evidence.",
    )

    baseline = service.build_edge_intelligence(
        transition_type="alkali_substitution",
        family="phosphate",
        preserved_framework=[],
        removed_elements=[],
        introduced_elements=[],
        scientific_reason="Baseline evidence.",
    )

    assert strong["edge_score"] == 100.0
    assert partial["edge_score"] == 85.0
    assert baseline["edge_score"] == 80.0
    assert strong["edge_score"] > partial["edge_score"] > baseline["edge_score"]