from pydantic import BaseModel, Field


class ScenarioRankingRequest(BaseModel):
    scenario_name: str
    top_n: int = Field(default=10, ge=1, le=20)


class ScenarioRankingResult(BaseModel):
    rank: int
    scenario_name: str
    material_id: int
    mp_id: str
    formula: str
    pretty_formula: str
    score: float
    material_risk_score: float | None
    risk_penalty: float
    reasons: list[str]
    ranking_explanation: list[str]