from pydantic import BaseModel, Field


class SensitivityAnalysisRequest(BaseModel):
    material_id: int


class SensitivityScenarioResult(BaseModel):
    scenario: str
    risk_dimension: str
    baseline_component_score: float | None
    adjusted_component_score: float | None
    adjusted_material_risk_score: float | None
    material_risk_delta: float | None
    adjusted_score: float | None
    score_delta: float | None


class SensitivityAnalysisResult(BaseModel):
    material_id: int
    formula: str
    baseline_score: float
    baseline_material_risk_score: float | None
    baseline_supply_risk_score: float | None
    baseline_geopolitical_risk_score: float | None
    selected_risk_profile_ids: list[int] = Field(default_factory=list)
    selected_risk_profile_years: list[int] = Field(default_factory=list)
    selected_risk_profile_sources: list[str] = Field(default_factory=list)
    sensitivity_level: str
    scenarios: list[SensitivityScenarioResult]