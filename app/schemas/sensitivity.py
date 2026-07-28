from pydantic import BaseModel


class SensitivityAnalysisRequest(BaseModel):
    material_id: int


class SensitivityScenarioResult(BaseModel):
    scenario: str
    adjusted_score: float | None
    score_delta: float | None


class SensitivityAnalysisResult(BaseModel):
    material_id: int
    formula: str
    baseline_score: float
    baseline_material_risk_score: float | None
    sensitivity_level: str
    scenarios: list[SensitivityScenarioResult]