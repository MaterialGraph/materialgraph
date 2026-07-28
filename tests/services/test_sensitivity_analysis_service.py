from types import SimpleNamespace

from app.schemas.sensitivity import SensitivityAnalysisRequest
from app.services.sensitivity_analysis_service import SensitivityAnalysisService


def test_sensitivity_analysis_returns_result(db_session):
    service = SensitivityAnalysisService(db_session)

    result = service.analyze(
        SensitivityAnalysisRequest(material_id=6)
    )

    assert result is not None
    assert result.material_id == 6
    assert result.baseline_score >= 0
    assert result.baseline_material_risk_score is not None
    assert result.baseline_material_risk_score >= 0
    assert len(result.scenarios) == 4


def test_sensitivity_analysis_returns_none_for_missing_material(db_session):
    service = SensitivityAnalysisService(db_session)

    result = service.analyze(
        SensitivityAnalysisRequest(material_id=999999)
    )

    assert result is None


def test_unknown_baseline_risk_returns_unknown_sensitivity(db_session):
    service = SensitivityAnalysisService(db_session)
    service.screening_service = SimpleNamespace(
        screen_candidates=lambda request: [
            SimpleNamespace(
                material_id=101,
                pretty_formula="NaFePO4",
                score=70.0,
                material_risk_score=None,
            )
        ]
    )

    result = service.analyze(
        SensitivityAnalysisRequest(material_id=101)
    )

    assert result is not None
    assert result.baseline_material_risk_score is None
    assert result.sensitivity_level == "UNKNOWN"
    assert len(result.scenarios) == 4
    assert all(item.adjusted_score is None for item in result.scenarios)
    assert all(item.score_delta is None for item in result.scenarios)