import pytest
from pydantic import ValidationError

from app.schemas.research_objective_exploration import (
    ConfidenceExplanation,
    EndpointSensitiveRanking,
    EvidenceSummary,
    PathwayComparison,
    ScientificPathway,
    ScientificPathwayAnalysisResponse,
    ScientificPathwayScoreBreakdown,
)
from app.services.research.comparative_research_intelligence_service import (
    ComparativeResearchIntelligenceService,
)
from app.services.research.endpoint_sensitive_research_ranking_service import (
    EndpointSensitiveResearchRankingService,
)


def test_evidence_readiness_rejects_values_outside_public_contract():
    with pytest.raises(ValidationError):
        EvidenceSummary.model_validate(
            {
                "supporting_signals": [],
                "missing_evidence": [],
                "weak_assumptions": [],
                "validation_priorities": [],
                "evidence_readiness": "excellent",
            }
        )


def test_pathway_confidence_is_scoped_and_constrained():
    confidence = ConfidenceExplanation.model_validate(
        {
            "level": "high",
            "reasons": ["Strong deterministic score."],
        }
    )

    assert confidence.confidence_scope == (
        "deterministic_pathway_ranking_not_external_validation"
    )

    with pytest.raises(ValidationError):
        ConfidenceExplanation.model_validate(
            {"level": "experimentally_validated", "reasons": []}
        )


def test_scientific_score_breakdown_requires_canonical_dimensions():
    with pytest.raises(ValidationError):
        ScientificPathwayScoreBreakdown.model_validate(
            {
                "shared_element_continuity": 20.0,
                "objective_alignment": 25.0,
                "transition_plausibility": 15.0,
                "path_efficiency": 10.0,
            }
        )


def test_scientific_pathway_rejects_untyped_material_payload():
    with pytest.raises(ValidationError):
        ScientificPathway.model_validate(
            {
                "hop_count": 0,
                "materials": [{"formula": "LiFePO4"}],
                "transitions": [],
            }
        )


def test_empty_comparison_conforms_to_typed_contract():
    result = ComparativeResearchIntelligenceService().compare_opportunities([])

    comparison = PathwayComparison.model_validate(result)

    assert comparison.top_ranking_status == "unavailable"
    assert comparison.comparative_evidence_readiness.highest_readiness is None


def test_empty_endpoint_ranking_conforms_to_typed_contract():
    result = EndpointSensitiveResearchRankingService().rank_opportunities([])

    ranking = EndpointSensitiveRanking.model_validate(result)

    assert ranking.groups == []
    assert ranking.score_preserved is True


def test_analysis_openapi_schema_uses_concrete_nested_models():
    schema = ScientificPathwayAnalysisResponse.model_json_schema()
    properties = schema["properties"]

    assert properties["pathway_comparison"] == {
        "$ref": "#/$defs/PathwayComparison"
    }
    assert properties["pathway_opportunities"]["items"] == {
        "$ref": "#/$defs/ScientificPathwayOpportunity"
    }
    assert schema["$defs"]["EvidenceSummary"]["properties"][
        "evidence_readiness"
    ]["enum"] == ["strong", "moderate", "limited"]