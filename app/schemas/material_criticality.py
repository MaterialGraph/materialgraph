from typing import Literal

from pydantic import BaseModel, ConfigDict


class MaterialCriticalityElement(BaseModel):
    element_id: int
    symbol: str
    name: str

    fraction: float | None
    fraction_known: bool
    risk_year: int | None

    abundance_score: float | None
    supply_risk_score: float | None
    toxicity_score: float | None
    recyclability_score: float | None
    geopolitical_risk_score: float | None

    criticality_known: bool
    element_criticality_score: float | None
    available_criticality_dimension_count: int
    expected_criticality_dimension_count: int
    criticality_dimension_coverage: float
    criticality_profile_complete: bool


class MaterialCriticalityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None

    criticality_score: float | None
    criticality_known: bool
    evidence_basis: str
    shared_evidence_dimensions: list[str]
    criticality_evidence_dimensions: list[str]
    aggregation_method: str
    composition_evidence_status: Literal[
        "complete",
        "partial",
        "unavailable",
    ]
    composition_fraction_coverage: float
    composition_evidence_complete: bool
    known_composition_element_count: int
    unknown_composition_element_count: int
    unknown_composition_elements: list[str]

    criticality_profile_coverage: float
    criticality_fraction_coverage: float
    criticality_complete_profile_coverage: float
    criticality_dimension_coverage: float

    known_criticality_element_count: int
    unknown_criticality_element_count: int
    complete_criticality_profile_element_count: int
    partial_criticality_profile_element_count: int
    total_element_count: int

    known_criticality_fraction: float
    unknown_criticality_fraction: float

    criticality_evidence_complete: bool
    unknown_criticality_elements: list[str]
    partial_criticality_profile_elements: list[str]

    elements: list[MaterialCriticalityElement]