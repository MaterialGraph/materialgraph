from app.services.research.research_evidence_intelligence_service import (
    ResearchEvidenceIntelligenceService,
)


def _sample_opportunity() -> dict:
    return {
        "score_breakdown": {
            "shared_element_continuity": 30.0,
            "objective_alignment": 25.0,
            "transition_plausibility": 18.5,
            "path_efficiency": 7.5,
            "material_quality": 13.95,
        },
        "scientific_facts": {
            "transition_types": ["alkali_substitution", "family_expansion"],
            "preserved_framework": ["Fe", "O", "P"],
            "removed_elements": ["Li"],
            "introduced_elements": ["Na"],
            "material_quality": [
                {
                    "material_id": 5,
                    "stability_score": 100.0,
                    "energy_above_hull": 0.0,
                    "criticality_score": 36.5,
                    "risk_score": 2.833,
                    "quality_score": 13.95,
                }
            ],
        },
        "quality_summary": {
            "average_quality_score": 13.95,
            "overall_quality": "strong",
            "highest_risk_material": "LiFePO4",
            "lowest_quality_material": "LiFePO4",
        },
    }


def test_research_evidence_summary_contains_required_sections():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    assert "supporting_signals" in evidence
    assert "missing_evidence" in evidence
    assert "weak_assumptions" in evidence
    assert "validation_priorities" in evidence
    assert "evidence_readiness" in evidence
    assert evidence["support_basis"] == "internal_deterministic_signals"
    assert evidence["external_evidence_integrated"] is False
    assert evidence["external_evidence_status"] == "not_integrated"
    assert evidence["evidence_readiness_scope"] == (
        "internal_research_prioritization_only"
    )
    assert "not scientific validation" in evidence["decision_boundary"]


def test_supporting_signals_are_attributed():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    signal = evidence["supporting_signals"][0]

    assert "statement" in signal
    assert "source_service" in signal
    assert "derived_from" in signal
    assert "confidence" in signal
    assert signal["evidence_origin"] == "internal_deterministic"
    assert signal["scientific_validation_status"] == "unvalidated"
    assert signal["confidence_scope"] == (
        "deterministic_rule_match_not_external_validation"
    )


def test_missing_evidence_is_explainable():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary({})

    missing = evidence["missing_evidence"][0]

    assert "statement" in missing
    assert "reason" in missing
    assert "researcher_action" in missing
    assert missing["evidence_origin"] == "external"
    assert missing["availability_status"] == "not_integrated"

    assert any(
        "Experimental synthesis evidence" in item["statement"]
        for item in evidence["missing_evidence"]
    )

    assert any(
        "Scientific literature support" in item["statement"]
        for item in evidence["missing_evidence"]
    )


def test_weak_assumptions_are_structured():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    assumption = evidence["weak_assumptions"][0]

    assert "assumption" in assumption
    assert "based_on" in assumption
    assert "requires_validation" in assumption


def test_validation_priorities_are_structured():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    priority = evidence["validation_priorities"][0]

    assert "priority" in priority
    assert "action" in priority
    assert "reason" in priority


def test_research_evidence_readiness_is_valid():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    assert evidence["evidence_readiness"] in {
        "limited",
        "moderate",
        "strong",
    }


def test_external_evidence_gaps_cap_strong_internal_support_at_moderate():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())

    assert len(evidence["supporting_signals"]) >= 5
    assert evidence["missing_evidence"]
    assert evidence["evidence_readiness"] == "moderate"
    assert evidence["evidence_readiness_scope"] == (
        "internal_research_prioritization_only"
    )


def test_high_confidence_is_scoped_to_internal_rule_support():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary(_sample_opportunity())
    high_confidence_signals = [
        signal
        for signal in evidence["supporting_signals"]
        if signal["confidence"] == "high"
    ]

    assert high_confidence_signals
    assert all(
        signal["evidence_origin"] == "internal_deterministic"
        and signal["scientific_validation_status"] == "unvalidated"
        and signal["confidence_scope"]
        == "deterministic_rule_match_not_external_validation"
        for signal in high_confidence_signals
    )


def test_weak_internal_support_remains_limited():
    service = ResearchEvidenceIntelligenceService()

    evidence = service.build_evidence_summary({})

    assert evidence["evidence_readiness"] == "limited"


def test_strong_readiness_requires_no_external_evidence_gaps():
    service = ResearchEvidenceIntelligenceService()

    readiness = service._evidence_readiness(
        supporting_signals=[{} for _ in range(5)],
        weak_assumptions=[{}],
        missing_evidence=[],
    )

    assert readiness == "strong"


def test_enrich_opportunity_adds_evidence_summary():
    service = ResearchEvidenceIntelligenceService()

    opportunity = {
        "rank": 1,
        "score_breakdown": {},
        "scientific_facts": {},
        "quality_summary": {},
    }

    enriched = service.enrich_opportunity(opportunity)

    assert "evidence_summary" in enriched
    assert enriched["rank"] == 1