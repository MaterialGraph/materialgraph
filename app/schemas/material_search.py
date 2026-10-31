from typing import Literal

from pydantic import BaseModel

# The mode a client may request; "auto" is resolved to a concrete mode
# before any search runs.
SearchRequestMode = Literal[
    "formula", "mp_id", "chemsys", "contains", "auto", "material_id"
]
# The mode a search actually ran in. Never "auto".
SearchResolvedMode = Literal[
    "formula", "mp_id", "chemsys", "contains", "material_id"
]


class MaterialSearchInterpretation(BaseModel):
    mode: SearchResolvedMode
    input: str
    elements: list[str] | None = None
    amounts: dict[str, float] | None = None
    normalized_fractions: dict[str, float] | None = None
    reduced_formula: str | None = None
    mp_id: str | None = None
    material_id: int | None = None


class MaterialSearchResult(BaseModel):
    material_id: int
    mp_id: str
    formula: str
    pretty_formula: str
    energy_above_hull: float | None = None


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


class MaterialDatasetSummaryResponse(MaterialSearchDataset):
    """The dataset block of a search response, available without a search."""


class MaterialSearchSuggestions(BaseModel):
    basis: Literal["same_chemical_system"]
    explanation: str
    results: list[MaterialSearchResult]


class MaterialSearchResponse(BaseModel):
    interpretation: MaterialSearchInterpretation
    requested_mode: SearchRequestMode
    dataset: MaterialSearchDataset
    total_matches: int
    dataset_total: int
    limit: int
    offset: int
    results: list[MaterialSearchResult]
    suggestions: MaterialSearchSuggestions | None = None
    suggestion_total: int | None = None
    message: str | None = None
    scoped_message: str | None = None


class MaterialSearchErrorDetail(BaseModel):
    """The ``detail`` of an explained 422 search error."""

    code: str
    # Null only for errors raised before an auto request was resolved.
    mode: SearchResolvedMode | None
    requested_mode: SearchRequestMode
    input: str
    explanation: str
    hint: str | None = None
