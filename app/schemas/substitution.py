from typing import Literal

from pydantic import BaseModel, Field


class SubstitutionRequest(BaseModel):
    material_id: int
    top_n: int = 5


class SubstituteCandidate(BaseModel):
    material_id: int
    formula: str
    pretty_formula: str
    similarity_score: float
    material_risk_score: float | None
    risk_known: bool
    risk_profile_coverage: float
    risk_evidence_complete: bool
    unknown_risk_elements: list[str]
    selected_risk_profile_ids: list[int] = Field(default_factory=list)
    selected_risk_profile_years: list[int] = Field(default_factory=list)
    selected_risk_profile_sources: list[str] = Field(default_factory=list)
    stability_band: Literal[
        "stable", "near_stable", "metastable", "unstable", "unknown"
    ]
    stability_evidence_basis: Literal[
        "energy_above_hull",
        "imported_is_stable_fallback",
        "unavailable",
    ]
    stability_evidence_complete: bool
    stability_source_consistency: Literal[
        "consistent", "inconsistent", "not_comparable"
    ]
    stability_rank_contribution: float
    rank_score: float
    shared_elements: list[str]
    replacement_elements: list[str]
    removed_elements: list[str]
    explanation: str


class SubstitutionResult(BaseModel):
    source_material_id: int
    source_formula: str
    source_risk_score: float | None
    source_risk_known: bool
    source_risk_profile_coverage: float
    source_risk_evidence_complete: bool
    source_unknown_risk_elements: list[str]
    source_selected_risk_profile_ids: list[int] = Field(default_factory=list)
    source_selected_risk_profile_years: list[int] = Field(default_factory=list)
    source_selected_risk_profile_sources: list[str] = Field(default_factory=list)
    substitutes: list[SubstituteCandidate]