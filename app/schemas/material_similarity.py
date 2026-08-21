from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.schemas.material_common import (
    CriticalityDirection,
    MaterialRelationshipSummary,
    MaterialRiskSummary,
)


class StabilityEvidenceSummary(BaseModel):
    stability_band: Literal[
        "stable",
        "near_stable",
        "metastable",
        "unstable",
        "unknown",
    ]
    stability_evidence_basis: Literal[
        "energy_above_hull",
        "imported_is_stable_fallback",
        "unavailable",
    ]
    stability_evidence_complete: bool
    stability_source_consistency: Literal[
        "consistent",
        "inconsistent",
        "not_comparable",
    ]
    stability_score_contribution: float


class SimilarMaterialRead(
    StabilityEvidenceSummary,
    MaterialRiskSummary,
    MaterialRelationshipSummary,
):
    similarity_score: float
    reason_summary: str
    criticality_delta: float | None
    criticality_direction: CriticalityDirection


class SimilarityRankingPolicy(BaseModel):
    primary: Literal["similarity_score_desc"]
    criticality_tie_breaker: Literal[
        "known_then_smallest_absolute_delta"
    ]
    final_tie_breaker: Literal["material_id_asc"]
    candidate_pool: Literal["all_structured_neighbors_before_limit"]
    stability_policy: Literal["single_energy_primary_signal"]


class MaterialSimilarityResponse(MaterialRiskSummary):
    model_config = ConfigDict(from_attributes=True)

    ranking_policy: SimilarityRankingPolicy
    candidate_pool_count: int
    returned_count: int
    similar_materials: list[SimilarMaterialRead]