from pydantic import BaseModel


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
    substitutes: list[SubstituteCandidate]