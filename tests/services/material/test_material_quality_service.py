from types import SimpleNamespace


def test_material_quality_service_returns_quality_metadata(db_session):
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService(db_session)

    result = service.get_material_quality(5)

    assert result["material_id"] == 5
    assert "stability_score" in result
    assert "stability_band" in result
    assert "stability_evidence_basis" in result
    assert "stability_evidence_complete" in result
    assert "stability_source_consistency" in result
    assert "stability_quality_contribution" in result
    assert "energy_above_hull" in result
    assert "criticality_score" in result
    assert "criticality_composition_evidence_status" in result
    assert "criticality_composition_fraction_coverage" in result
    assert "criticality_composition_evidence_complete" in result
    assert "risk_score" in result
    assert "risk_known" in result
    assert "risk_profile_coverage" in result
    assert "risk_complete_profile_coverage" in result
    assert "risk_dimension_coverage" in result
    assert "known_risk_element_count" in result
    assert "total_element_count" in result
    assert "risk_evidence_complete" in result
    assert "unknown_risk_elements" in result
    assert "partial_risk_profile_elements" in result
    assert "risk_evidence_basis" in result
    assert "risk_evidence_dimensions" in result
    assert "risk_aggregation_method" in result
    assert "quality_score" in result

    assert isinstance(result["stability_score"], float)
    assert result["risk_score"] is None or isinstance(result["risk_score"], float)
    assert isinstance(result["risk_known"], bool)
    assert isinstance(result["risk_profile_coverage"], float)
    assert isinstance(result["quality_score"], float)


def test_material_quality_service_returns_empty_quality_for_missing_material(
    db_session,
):
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService(db_session)

    result = service.get_material_quality(999999)

    assert result == {
        "material_id": 999999,
        "stability_score": 0.0,
        "stability_band": "unknown",
        "stability_evidence_basis": "unavailable",
        "stability_evidence_complete": False,
        "stability_source_consistency": "not_comparable",
        "stability_quality_contribution": 0.0,
        "energy_above_hull": None,
        "criticality_score": None,
        "criticality_quality_contribution": 0.0,
        "criticality_composition_evidence_status": "unavailable",
        "criticality_composition_fraction_coverage": 0.0,
        "criticality_composition_evidence_complete": False,
        "risk_score": None,
        "risk_quality_contribution": 0.0,
        "risk_known": False,
        "risk_profile_coverage": 0.0,
        "risk_complete_profile_coverage": 0.0,
        "risk_dimension_coverage": 0.0,
        "known_risk_element_count": 0,
        "complete_risk_profile_element_count": 0,
        "partial_risk_profile_element_count": 0,
        "total_element_count": 0,
        "risk_evidence_complete": False,
        "unknown_risk_elements": [],
        "partial_risk_profile_elements": [],
        "risk_evidence_basis": None,
        "risk_evidence_dimensions": [],
        "risk_aggregation_method": None,
        "quality_score": 0.0,
    }


def test_unknown_risk_does_not_receive_low_risk_quality_bonus():
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService.__new__(MaterialQualityService)
    service.QUALITY_SCORE_MAX = 15.0

    score = service._calculate_quality_score(
        is_stable=True,
        energy_above_hull=0.0,
        criticality_score=31.0,
        risk_score=None,
        risk_known=False,
        risk_evidence_complete=False,
    )

    assert score == 11.7


def test_known_low_risk_receives_low_risk_quality_bonus():
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService.__new__(MaterialQualityService)
    service.QUALITY_SCORE_MAX = 15.0

    score = service._calculate_quality_score(
        is_stable=True,
        energy_above_hull=0.0,
        criticality_score=31.0,
        risk_score=1.5,
        risk_known=True,
        risk_evidence_complete=True,
    )

    assert score == 13.95


def test_partial_low_risk_evidence_does_not_receive_quality_bonus():
    """Partial risk evidence must not unlock a favorable risk-quality bonus."""
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService.__new__(MaterialQualityService)
    service.QUALITY_SCORE_MAX = 15.0

    material = SimpleNamespace(
        id=123,
        is_stable=True,
        energy_above_hull=0.0,
    )
    risk_signal = {
        "material_id": 123,
        "risk_score": 1.5,
        "risk_known": True,
        "risk_profile_coverage": 0.25,
        "risk_complete_profile_coverage": 0.0,
        "risk_dimension_coverage": 0.0833,
        "known_risk_element_count": 1,
        "complete_risk_profile_element_count": 0,
        "partial_risk_profile_element_count": 1,
        "total_element_count": 4,
        "known_risk_elements": ["Li"],
        "unknown_risk_elements": ["Fe", "O", "P"],
        "partial_risk_profile_elements": ["Li"],
        "evidence_basis": "latest_element_risk_profile",
        "risk_evidence_dimensions": [
            "supply_risk_score",
            "geopolitical_risk_score",
            "toxicity_score",
        ],
        "aggregation_method": (
            "mean_available_dimensions_then_equal_mean_calculable_elements"
        ),
        "risk_evidence_complete": False,
    }

    result = service._build_quality_response(
        material=material,
        criticality_score=31.0,
        risk_signal=risk_signal,
    )

    assert result["risk_known"] is True
    assert result["risk_profile_coverage"] == 0.25
    assert result["risk_complete_profile_coverage"] == 0.0
    assert result["risk_dimension_coverage"] == 0.0833
    assert result["known_risk_element_count"] == 1
    assert result["total_element_count"] == 4
    assert result["risk_evidence_complete"] is False
    assert result["unknown_risk_elements"] == ["Fe", "O", "P"]
    assert result["partial_risk_profile_elements"] == ["Li"]
    assert result["risk_evidence_basis"] == "latest_element_risk_profile"

    # Corrected MG-AUD-008 behavior:
    # partial evidence does not qualify for a favorable risk bonus.
    assert result["quality_score"] == 11.7


def test_quality_does_not_double_count_inconsistent_stability_fields():
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService.__new__(MaterialQualityService)
    service.QUALITY_SCORE_MAX = 15.0

    score = service._calculate_quality_score(
        is_stable=True,
        energy_above_hull=0.2,
        criticality_score=None,
        risk_score=None,
        risk_known=False,
        risk_evidence_complete=False,
    )

    assert score == 0.0


def test_quality_uses_stable_flag_only_when_energy_is_missing():
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService.__new__(MaterialQualityService)
    service.QUALITY_SCORE_MAX = 15.0

    score = service._calculate_quality_score(
        is_stable=True,
        energy_above_hull=None,
        criticality_score=None,
        risk_score=None,
        risk_known=False,
        risk_evidence_complete=False,
    )

    assert score == 5.25