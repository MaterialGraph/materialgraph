from types import SimpleNamespace

from app.schemas.sensitivity import SensitivityAnalysisRequest
from app.services.sensitivity_analysis_service import SensitivityAnalysisService


def _screening_result(
    material_id: int = 101,
    material_risk_score: float | None = 4.0,
):
    return SimpleNamespace(
        material_id=material_id,
        pretty_formula="LiFePO4",
        score=70.0,
        material_risk_score=material_risk_score,
    )


def _material_risk(
    supply_scores: list[float | None],
    geopolitical_scores: list[float | None],
):
    return SimpleNamespace(
        element_risks=[
            SimpleNamespace(
                supply_risk_score=supply,
                geopolitical_risk_score=geopolitical,
            )
            for supply, geopolitical in zip(
                supply_scores,
                geopolitical_scores,
                strict=True,
            )
        ]
    )


def test_sensitivity_analysis_returns_result(db_session):
    service = SensitivityAnalysisService(db_session)

    result = service.analyze(
        SensitivityAnalysisRequest(material_id=6)
    )

    assert result is not None
    assert result.material_id == 6
    assert result.baseline_score >= 0
    assert result.baseline_material_risk_score is not None
    assert result.baseline_supply_risk_score is not None
    assert result.baseline_geopolitical_risk_score is not None
    assert len(result.scenarios) == 4


def test_sensitivity_analysis_returns_none_for_missing_material(db_session):
    service = SensitivityAnalysisService(db_session)

    result = service.analyze(
        SensitivityAnalysisRequest(material_id=999999)
    )

    assert result is None


def test_named_risk_dimensions_use_distinct_component_baselines(db_session):
    service = SensitivityAnalysisService(db_session)
    service.screening_service = SimpleNamespace(
        screen_candidates=lambda request: [_screening_result()]
    )
    service.risk_service = SimpleNamespace(
        get_material_risk=lambda material_id: _material_risk(
            supply_scores=[2.0, 4.0],
            geopolitical_scores=[6.0, 10.0],
        )
    )

    result = service.analyze(SensitivityAnalysisRequest(material_id=101))

    assert result is not None
    assert result.baseline_supply_risk_score == 3.0
    assert result.baseline_geopolitical_risk_score == 8.0

    supply_25, supply_50, geopolitical_25, geopolitical_50 = result.scenarios

    assert supply_25.risk_dimension == "supply_risk"
    assert supply_25.baseline_component_score == 3.0
    assert supply_25.adjusted_component_score == 3.75
    assert supply_25.score_delta == -3.75
    assert supply_50.adjusted_component_score == 4.5
    assert supply_50.score_delta == -7.5

    assert geopolitical_25.risk_dimension == "geopolitical_risk"
    assert geopolitical_25.baseline_component_score == 8.0
    assert geopolitical_25.adjusted_component_score == 10.0
    assert geopolitical_25.score_delta == -10.0
    assert geopolitical_50.adjusted_component_score == 12.0
    assert geopolitical_50.score_delta == -20.0

    assert supply_25.score_delta != geopolitical_25.score_delta
    assert supply_50.score_delta != geopolitical_50.score_delta


def test_missing_supply_evidence_only_nulls_supply_scenarios(db_session):
    service = SensitivityAnalysisService(db_session)
    service.screening_service = SimpleNamespace(
        screen_candidates=lambda request: [_screening_result()]
    )
    service.risk_service = SimpleNamespace(
        get_material_risk=lambda material_id: _material_risk(
            supply_scores=[None, None],
            geopolitical_scores=[4.0, 6.0],
        )
    )

    result = service.analyze(SensitivityAnalysisRequest(material_id=101))

    assert result is not None
    assert result.baseline_supply_risk_score is None
    assert result.baseline_geopolitical_risk_score == 5.0
    assert all(
        item.adjusted_score is None
        for item in result.scenarios
        if item.risk_dimension == "supply_risk"
    )
    assert all(
        item.adjusted_score is not None
        for item in result.scenarios
        if item.risk_dimension == "geopolitical_risk"
    )
    assert result.sensitivity_level != "UNKNOWN"


def test_missing_geopolitical_evidence_only_nulls_geopolitical_scenarios(
    db_session,
):
    service = SensitivityAnalysisService(db_session)
    service.screening_service = SimpleNamespace(
        screen_candidates=lambda request: [_screening_result()]
    )
    service.risk_service = SimpleNamespace(
        get_material_risk=lambda material_id: _material_risk(
            supply_scores=[2.0, 4.0],
            geopolitical_scores=[None, None],
        )
    )

    result = service.analyze(SensitivityAnalysisRequest(material_id=101))

    assert result is not None
    assert result.baseline_supply_risk_score == 3.0
    assert result.baseline_geopolitical_risk_score is None
    assert all(
        item.adjusted_score is not None
        for item in result.scenarios
        if item.risk_dimension == "supply_risk"
    )
    assert all(
        item.adjusted_score is None
        for item in result.scenarios
        if item.risk_dimension == "geopolitical_risk"
    )


def test_entirely_unknown_component_evidence_returns_unknown_sensitivity(
    db_session,
):
    service = SensitivityAnalysisService(db_session)
    service.screening_service = SimpleNamespace(
        screen_candidates=lambda request: [
            _screening_result(material_risk_score=None)
        ]
    )
    service.risk_service = SimpleNamespace(
        get_material_risk=lambda material_id: _material_risk(
            supply_scores=[None],
            geopolitical_scores=[None],
        )
    )

    result = service.analyze(SensitivityAnalysisRequest(material_id=101))

    assert result is not None
    assert result.baseline_material_risk_score is None
    assert result.baseline_supply_risk_score is None
    assert result.baseline_geopolitical_risk_score is None
    assert result.sensitivity_level == "UNKNOWN"
    assert len(result.scenarios) == 4
    assert all(item.adjusted_component_score is None for item in result.scenarios)
    assert all(item.adjusted_score is None for item in result.scenarios)
    assert all(item.score_delta is None for item in result.scenarios)