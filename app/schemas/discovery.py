from typing import Literal

from pydantic import BaseModel, Field


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
    avoid_elements: list[str] = []
    prefer_elements: list[str] = []
    preserve_elements: list[str] = []
    target_family: str | None = None
    max_hops: int = Field(default=2, ge=1, le=3)
    limit: int = Field(default=5, ge=1, le=20)
    prefer_lower_criticality: bool = True
    require_stable_materials: bool = False


class ResearchObjectiveChainRequest(BaseModel):
    objective: ResearchObjective


class ResearchObjectiveChainResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    search_metadata: DiscoverySearchMetadata
    chains: list[DiscoveryChain]
