from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.periodic_table import normalize_element_symbol


MAX_RESEARCH_OBJECTIVE_ELEMENTS = 32
ElementSymbol = Annotated[str, Field(min_length=1, max_length=2)]


class DiscoveryGoal(BaseModel):
    avoid_element: str | None = None
    prefer_element: str | None = None


class DiscoveryConstraintPolicy(BaseModel):
    avoid_element: Literal["soft_penalty"] = "soft_penalty"
    prefer_element: Literal["soft_bonus"] = "soft_bonus"


class SubstitutionPath(BaseModel):
    from_formula: str
    to_formula: str
    path_type: str
    replaced_elements: list[str]
    introduced_elements: list[str]
    shared_elements: list[str] = Field(default_factory=list)
    preserved_framework: list[str]
    preservation_basis: str = "element_overlap"
    structural_preservation_validated: bool = False
    relationship_basis: Literal["composition_heuristic"] = (
        "composition_heuristic"
    )
    substitution_mechanism_validated: bool = False
    reason: str


class DiscoveryCandidate(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str
    discovery_score: float
    score_breakdown: dict[str, float]
    discovery_path: list[str]
    substitution_path: SubstitutionPath | None = None
    explanation: str


class DiscoveryCandidatesResponse(BaseModel):
    material_id: int
    mp_id: str | None = None
    base_formula: str | None = None
    discovery_goal: DiscoveryGoal
    constraint_policy: DiscoveryConstraintPolicy
    discovery_warnings: list[str] = []
    candidates: list[DiscoveryCandidate]

class DiscoveryChainGoal(DiscoveryGoal):
    max_hops: int = Field(default=2, ge=1, le=3)
    limit: int = Field(default=5, ge=1, le=20)


class DiscoveryChainMaterial(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str


class DiscoveryChainTransition(BaseModel):
    from_material_id: int
    to_material_id: int
    from_formula: str
    to_formula: str
    transition_type: str
    family: str | None = None
    reason: str
    shared_elements: list[str] = Field(default_factory=list)
    preserved_framework: list[str]
    preservation_basis: str = "element_overlap"
    structural_preservation_validated: bool = False
    relationship_basis: Literal["composition_heuristic"] = (
        "composition_heuristic"
    )
    substitution_mechanism_validated: bool = False
    removed_elements: list[str]
    introduced_elements: list[str]


class DiscoveryChain(BaseModel):
    hop_count: int
    materials: list[DiscoveryChainMaterial]
    transitions: list[DiscoveryChainTransition]
    chain_reason: str

    scientific_usefulness_score: float | None = None
    score_breakdown: dict[str, float] | None = None
    usefulness_reason: str | None = None


class DiscoverySearchMetadata(BaseModel):
    search_policy: Literal["bounded_breadth_first"] = "bounded_breadth_first"
    requested_result_limit: int
    expansion_limit_per_material: int
    search_state_budget: int
    expanded_state_count: int
    generated_chain_count: int
    returned_chain_count: int
    search_truncated: bool
    result_truncated: bool
    scientific_completeness_guaranteed: Literal[False] = False


class DiscoveryChainsResponse(BaseModel):
    material_id: int
    mp_id: str | None = None
    base_formula: str | None = None
    discovery_goal: DiscoveryChainGoal
    search_metadata: DiscoverySearchMetadata
    chains: list[DiscoveryChain]

class ResearchObjective(BaseModel):
    avoid_elements: list[ElementSymbol] = Field(
        default_factory=list,
        max_length=MAX_RESEARCH_OBJECTIVE_ELEMENTS,
    )
    prefer_elements: list[ElementSymbol] = Field(
        default_factory=list,
        max_length=MAX_RESEARCH_OBJECTIVE_ELEMENTS,
    )
    preserve_elements: list[ElementSymbol] = Field(
        default_factory=list,
        max_length=MAX_RESEARCH_OBJECTIVE_ELEMENTS,
    )
    target_family: str | None = None
    max_hops: int = Field(default=2, ge=1, le=3)
    limit: int = Field(default=5, ge=1, le=20)
    prefer_lower_criticality: bool = True
    require_stable_materials: bool = False

    @field_validator(
        "avoid_elements",
        "prefer_elements",
        "preserve_elements",
        mode="before",
    )
    @classmethod
    def normalize_element_collection(cls, value: object) -> object:
        if not isinstance(value, (list, tuple)):
            return value
        if len(value) > MAX_RESEARCH_OBJECTIVE_ELEMENTS:
            raise ValueError(
                "element collection must contain at most "
                f"{MAX_RESEARCH_OBJECTIVE_ELEMENTS} entries"
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


class ResearchObjectiveChainRequest(BaseModel):
    objective: ResearchObjective


class ResearchObjectiveExecutionPolicy(BaseModel):
    stable_materials: Literal["hard_rejection", "not_required"]
    stability_scope: Literal["all_non_root_chain_materials", "none"]
    stability_evidence_policy: Literal[
        "canonical_energy_primary_with_imported_flag_fallback"
    ]
    unknown_stability_evidence: Literal[
        "hard_rejection",
        "not_applicable",
    ]
    lower_criticality: Literal[
        "canonical_quality_preference",
        "excluded_from_objective_ranking",
    ]
    unknown_criticality_evidence: Literal["no_criticality_credit"]


class ResearchObjectiveChainResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    objective_policy: ResearchObjectiveExecutionPolicy
    search_metadata: DiscoverySearchMetadata
    chains: list[DiscoveryChain]
