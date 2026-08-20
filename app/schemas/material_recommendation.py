from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.material_common import (
    CriticalityDirection,
    MaterialRelationshipSummary,
    MaterialRiskSummary,
)


class MaterialRecommendationRead(MaterialRiskSummary, MaterialRelationshipSummary):
    similarity_score: float
    criticality_delta: float | None
    criticality_direction: CriticalityDirection
    recommendation_score: float
    recommendation_reason: str


class MaterialRecommendationRankingPolicy(BaseModel):
    prefer_lower_criticality: bool
    criticality_delta_multiplier: float
    candidate_pool: Literal["all_similar_materials_before_limit"]
    final_tie_breaker: Literal["material_id_asc"]


class MaterialRecommendationResponse(MaterialRiskSummary):
    model_config = ConfigDict(from_attributes=True)

    ranking_policy: MaterialRecommendationRankingPolicy
    candidate_pool_count: int
    returned_count: int
    recommendations: list[MaterialRecommendationRead]


class MaterialScenarioRead(MaterialRecommendationRead):
    scenario_score: float
    scenario_delta: float
    scenario_reason: str


class MaterialRecommendationScenario(BaseModel):
    element: str
    supply_risk_multiplier: float
    avoid_element: str | None = None
    prefer_element: str | None = None
    limit: int


class MaterialScenarioRecommendationResponse(MaterialRiskSummary):
    model_config = ConfigDict(from_attributes=True)

    scenario: MaterialRecommendationScenario
    ranking_policy: MaterialRecommendationRankingPolicy
    candidate_pool_count: int
    returned_count: int
    recommendations: list[MaterialScenarioRead]