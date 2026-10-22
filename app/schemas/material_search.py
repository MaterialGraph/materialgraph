from typing import Literal

from pydantic import BaseModel

SearchMode = Literal["formula", "mp_id", "chemsys", "contains"]


class MaterialSearchInterpretation(BaseModel):
    mode: SearchMode
    input: str
    elements: list[str] | None = None
    amounts: dict[str, float] | None = None
    normalized_fractions: dict[str, float] | None = None
    reduced_formula: str | None = None
    mp_id: str | None = None


class MaterialSearchResult(BaseModel):
    material_id: int
    mp_id: str
    formula: str
    pretty_formula: str


class CompositionExclusion(BaseModel):
    material_id: int
    mp_id: str
    reason: str


class MaterialSearchDataset(BaseModel):
    source: Literal["materials_project"] = "materials_project"
    source_release: str | None = None
    dataset_total: int
    provenance_note: str
    composition_exclusions: list[CompositionExclusion]
    composition_exclusion_count: int


class MaterialSearchSuggestions(BaseModel):
    basis: Literal["same_chemical_system"]
    explanation: str
    results: list[MaterialSearchResult]


class MaterialSearchResponse(BaseModel):
    interpretation: MaterialSearchInterpretation
    dataset: MaterialSearchDataset
    total_matches: int
    dataset_total: int
    limit: int
    offset: int
    results: list[MaterialSearchResult]
    suggestions: MaterialSearchSuggestions | None = None
    message: str | None = None
