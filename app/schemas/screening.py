from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.periodic_table import normalize_element_symbol


MAX_SCREENING_ELEMENTS = 32
ScreeningElementSymbol = Annotated[str, Field(min_length=1, max_length=2)]


class CandidateScreeningRequest(BaseModel):
    scarce_elements: list[ScreeningElementSymbol] = Field(
        default_factory=list,
        max_length=MAX_SCREENING_ELEMENTS,
    )
    avoid_elements: list[ScreeningElementSymbol] = Field(
        default_factory=list,
        max_length=MAX_SCREENING_ELEMENTS,
    )
    require_stable: bool = True
    max_energy_above_hull: float | None = None

    @field_validator("scarce_elements", "avoid_elements", mode="before")
    @classmethod
    def normalize_element_collection(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            return value
        if len(value) > MAX_SCREENING_ELEMENTS:
            raise ValueError(
                "element collection must contain at most "
                f"{MAX_SCREENING_ELEMENTS} entries"
            )

        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            if not isinstance(item, str):
                return value
            symbol = normalize_element_symbol(item)
            if symbol not in seen:
                normalized.append(symbol)
                seen.add(symbol)
        return normalized


class CandidateScreeningResult(BaseModel):
    material_id: int
    mp_id: str
    formula: str
    pretty_formula: str
    score: float
    score_before_risk_penalty: float

    material_risk_score: float | None
    risk_known: bool
    risk_profile_coverage: float
    known_risk_element_count: int
    total_element_count: int
    risk_evidence_complete: bool
    unknown_risk_elements: list[str]
    selected_risk_profile_ids: list[int] = Field(default_factory=list)
    selected_risk_profile_years: list[int] = Field(default_factory=list)
    selected_risk_profile_sources: list[str] = Field(default_factory=list)

    risk_penalty: float
    elements: list[str]
    contains_scarce_elements: bool
    contains_avoided_elements: bool
    reasons: list[str]


class CandidateScreeningEvaluation(BaseModel):
    material_id: int
    disposition: Literal[
        "eligible",
        "material_not_found",
        "filtered_unstable",
        "filtered_energy_above_hull",
        "unavailable",
    ]
    reason: str
    result: CandidateScreeningResult | None = None
