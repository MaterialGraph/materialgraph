from pydantic import BaseModel


class ElementRiskSummary(BaseModel):
    symbol: str
    risk_profile_id: int
    risk_year: int
    risk_source: str
    risk_score: float
    supply_risk_score: float | None = None
    geopolitical_risk_score: float | None = None
    toxicity_score: float | None = None
    available_risk_dimension_count: int
    expected_risk_dimension_count: int
    risk_dimension_coverage: float
    risk_profile_complete: bool


class MaterialRiskRead(BaseModel):
    material_id: int
    formula: str
    pretty_formula: str
    material_risk_score: float | None
    evidence_basis: str
    shared_evidence_dimensions: list[str]
    risk_evidence_dimensions: list[str]
    aggregation_method: str
    selected_profile_ids: list[int]
    selected_profile_years: list[int]
    selected_profile_sources: list[str]
    risk_profile_coverage: float
    risk_complete_profile_coverage: float
    risk_dimension_coverage: float
    risk_evidence_complete: bool
    element_risks: list[ElementRiskSummary]