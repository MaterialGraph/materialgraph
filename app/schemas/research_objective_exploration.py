from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.discovery import (
    DiscoveryChain,
    DiscoveryChainMaterial,
    DiscoveryChainTransition,
    DiscoverySearchMetadata,
    ResearchObjective,
)


EvidenceReadiness = Literal["strong", "moderate", "limited"]
ConfidenceLevel = Literal["high", "medium", "low"]
ObjectiveSatisfactionStatus = Literal["complete", "partial", "unmatched"]
QualityLabel = Literal["strong", "moderate", "weak", "unknown"]
ScoreDimension = Literal[
    "shared_element_continuity",
    "objective_alignment",
    "transition_plausibility",
    "path_efficiency",
    "material_quality",
]


class ResearchObjectiveExplorationRequest(BaseModel):
    objective: ResearchObjective
    mode: Literal["balanced", "exploratory", "strict"] = "balanced"
    limit: int = Field(default=5, ge=1, le=20)


class ResearchObjectiveCandidate(BaseModel):
    material_id: int
    formula: str | None = None
    score: float
    reasons: list[str]
    warnings: list[str]


class ResearchObjectiveConstraintPolicy(BaseModel):
    avoid_elements: Literal["soft_penalty", "hard_rejection"]
    prefer_elements: Literal["soft_bonus"] = "soft_bonus"
    hard_rejection_scope: Literal["none", "all_non_root_chain_materials"]


class ResearchObjectiveExplorationResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    mode: Literal["balanced", "exploratory", "strict"]
    constraint_policy: ResearchObjectiveConstraintPolicy
    search_metadata: DiscoverySearchMetadata
    ranked_candidates: list[ResearchObjectiveCandidate]
    chains: list[DiscoveryChain]
    warnings: list[str]
    explanation: str


class QualitySummary(BaseModel):
    average_quality_score: float
    overall_quality: QualityLabel
    highest_risk_material: str | None = None
    lowest_quality_material: str | None = None


class ConfidenceExplanation(BaseModel):
    level: ConfidenceLevel
    reasons: list[str]
    confidence_scope: Literal[
        "deterministic_pathway_ranking_not_external_validation"
    ] = "deterministic_pathway_ranking_not_external_validation"


class MaterialQualityEvidence(BaseModel):
    material_id: int
    stability_score: float = 0.0
    energy_above_hull: float | None = None
    criticality_score: float | None = None
    risk_score: float | None = None
    risk_known: bool = False
    risk_profile_coverage: float = 0.0
    risk_complete_profile_coverage: float = 0.0
    risk_dimension_coverage: float = 0.0
    known_risk_element_count: int = 0
    complete_risk_profile_element_count: int = 0
    partial_risk_profile_element_count: int = 0
    total_element_count: int = 0
    risk_evidence_complete: bool = False
    unknown_risk_elements: list[str] = Field(default_factory=list)
    partial_risk_profile_elements: list[str] = Field(default_factory=list)
    risk_evidence_basis: str | None = None
    risk_evidence_dimensions: list[str] = Field(default_factory=list)
    risk_aggregation_method: str | None = None
    quality_score: float = 0.0


class ScientificFacts(BaseModel):
    transition_types: list[str]
    shared_elements: list[str] = Field(default_factory=list)
    preserved_framework: list[str]
    preservation_basis: Literal["element_overlap"] = "element_overlap"
    structural_preservation_validated: Literal[False] = False
    removed_elements: list[str]
    introduced_elements: list[str]
    material_quality: list[MaterialQualityEvidence]


class SupportingSignal(BaseModel):
    statement: str
    source_service: str
    derived_from: str
    confidence: Literal["high", "moderate"]
    evidence_origin: Literal["internal_deterministic"] = "internal_deterministic"
    scientific_validation_status: Literal["unvalidated"] = "unvalidated"
    confidence_scope: Literal[
        "deterministic_rule_match_not_external_validation"
    ] = "deterministic_rule_match_not_external_validation"


class MissingEvidence(BaseModel):
    statement: str
    reason: str
    researcher_action: str
    evidence_origin: Literal["external"] = "external"
    availability_status: Literal["not_integrated"] = "not_integrated"


class WeakAssumption(BaseModel):
    assumption: str
    based_on: str
    requires_validation: Literal[True] = True


class ValidationPriority(BaseModel):
    priority: int
    action: str
    reason: str


class EvidenceSummary(BaseModel):
    supporting_signals: list[SupportingSignal]
    missing_evidence: list[MissingEvidence]
    weak_assumptions: list[WeakAssumption]
    validation_priorities: list[ValidationPriority]
    support_basis: Literal["internal_deterministic_signals"] = (
        "internal_deterministic_signals"
    )
    external_evidence_integrated: Literal[False] = False
    external_evidence_status: Literal["not_integrated"] = "not_integrated"
    evidence_readiness_scope: Literal[
        "internal_research_prioritization_only"
    ] = "internal_research_prioritization_only"
    evidence_readiness: EvidenceReadiness
    decision_boundary: str = (
        "Evidence readiness describes deterministic internal support for "
        "research prioritization, not external scientific validation."
    )


class ScientificPathway(BaseModel):
    hop_count: int
    materials: list[DiscoveryChainMaterial]
    transitions: list[DiscoveryChainTransition]
    chain_reason: str | None = None


class ObjectiveSatisfaction(BaseModel):
    requested_avoid_elements: list[str] = Field(default_factory=list)
    matched_avoid_elements: list[str] = Field(default_factory=list)
    unmatched_avoid_elements: list[str] = Field(default_factory=list)
    requested_prefer_elements: list[str] = Field(default_factory=list)
    matched_prefer_elements: list[str] = Field(default_factory=list)
    unmatched_prefer_elements: list[str] = Field(default_factory=list)
    avoid_coverage: float = 0.0
    prefer_coverage: float = 0.0
    overall_coverage: float = 0.0
    status: ObjectiveSatisfactionStatus
    interpretation: str
    endpoint_matched_avoid_elements: list[str] = Field(default_factory=list)
    endpoint_unmatched_avoid_elements: list[str] = Field(default_factory=list)
    endpoint_matched_prefer_elements: list[str] = Field(default_factory=list)
    endpoint_unmatched_prefer_elements: list[str] = Field(default_factory=list)
    endpoint_avoid_coverage: float = 0.0
    endpoint_prefer_coverage: float = 0.0
    endpoint_overall_coverage: float = 0.0
    endpoint_status: ObjectiveSatisfactionStatus
    endpoint_interpretation: str


class ScientificPathwayScoreBreakdown(BaseModel):
    shared_element_continuity: float
    objective_alignment: float
    transition_plausibility: float
    path_efficiency: float
    material_quality: float


class ScientificPathwayOpportunity(BaseModel):
    evidence_summary: EvidenceSummary | None = None
    pathway_id: str
    position: int
    rank: int
    pathway: ScientificPathway
    scientific_usefulness_score: float
    score_breakdown: ScientificPathwayScoreBreakdown
    scientific_facts: ScientificFacts
    objective_satisfaction: ObjectiveSatisfaction
    quality_summary: QualitySummary
    strengths: list[str]
    trade_offs: list[str]
    risks: list[str]
    assumptions: list[str]
    confidence: ConfidenceExplanation
    recommended_next_investigation: str
    researcher_decision_required: bool


class EndpointMaterialReference(BaseModel):
    material_id: int | None = None
    formula: str | None = None
    pretty_formula: str | None = None
    mp_id: str | None = None


class PathwayReference(BaseModel):
    pathway_id: str
    position: int
    rank: int | None = None
    endpoint_material: EndpointMaterialReference | None = None


class TopRankedPathway(PathwayReference):
    scientific_usefulness_score: float
    why_it_ranks_highest: list[str]


class ComparativeStrength(PathwayReference):
    strengths: list[str]


class ComparativeTradeOff(PathwayReference):
    trade_offs: list[str]
    risks: list[str]


class ComparativeResearchGap(PathwayReference):
    missing_evidence: list[MissingEvidence]


class PathwayEvidenceReadiness(PathwayReference):
    evidence_readiness: EvidenceReadiness


class ComparativeEvidenceReadiness(BaseModel):
    pathways: list[PathwayEvidenceReadiness]
    highest_readiness_status: Literal["unique", "tie", "unavailable"]
    highest_readiness_pathways: list[PathwayEvidenceReadiness]
    highest_readiness_pathway_id: str | None = None
    highest_readiness_pathway_position: int | None = None
    highest_readiness_pathway_rank: int | None = None
    highest_readiness: EvidenceReadiness | None = None


class ComparativeAssumption(PathwayReference):
    pathway_assumptions: list[str]
    weak_assumptions: list[WeakAssumption]


class ScoreDimensionComparison(BaseModel):
    dimension: ScoreDimension
    higher_score: float
    lower_score: float
    difference: float
    explanation: str


class LowerRankedAdvantage(BaseModel):
    dimension: ScoreDimension
    higher_ranked_score: float
    lower_ranked_score: float
    difference: float
    explanation: str


class EvidenceReadinessPairComparison(BaseModel):
    higher_ranked_pathway_readiness: EvidenceReadiness
    lower_ranked_pathway_readiness: EvidenceReadiness
    same_readiness: bool


class EndpointMaterialComparison(BaseModel):
    first_pathway_endpoint: EndpointMaterialReference | None = None
    second_pathway_endpoint: EndpointMaterialReference | None = None
    higher_ranked_endpoint: EndpointMaterialReference | None = None
    lower_ranked_endpoint: EndpointMaterialReference | None = None
    same_endpoint: bool


class PairwisePathwayComparison(BaseModel):
    first_pathway_id: str
    second_pathway_id: str
    first_pathway_position: int
    second_pathway_position: int
    first_pathway_rank: int | None = None
    second_pathway_rank: int | None = None
    higher_ranked_pathway_rank: int | None = None
    lower_ranked_pathway_rank: int | None = None
    score_difference: float
    comparison_type: Literal["tie", "score_difference"]
    tie_reason: str | None = None
    endpoint_material_comparison: EndpointMaterialComparison
    why_higher_ranked: list[ScoreDimensionComparison]
    lower_ranked_pathway_advantages: list[LowerRankedAdvantage]
    evidence_readiness_comparison: EvidenceReadinessPairComparison


class ComparativeElementHighlight(BaseModel):
    element: str
    role: Literal[
        "introduced_element",
        "removed_element",
        "preserved_framework",
    ]
    role_semantics: str
    structural_preservation_validated: bool | None = None
    pathway_ids: list[str]
    pathway_count: int
    appears_in_pathway_ranks: list[int]
    potential_signal: str
    researcher_action: str
    requires_validation: Literal[True] = True


class PathwayComparison(BaseModel):
    comparison_count: int = 0
    top_ranking_status: Literal["unique", "tie", "unavailable"] = "unavailable"
    top_score: float | None = None
    top_ranked_pathway: TopRankedPathway | None = None
    top_ranked_pathways: list[TopRankedPathway] = Field(default_factory=list)
    comparative_strengths: list[ComparativeStrength] = Field(default_factory=list)
    comparative_trade_offs: list[ComparativeTradeOff] = Field(default_factory=list)
    comparative_research_gaps: list[ComparativeResearchGap] = Field(
        default_factory=list
    )
    comparative_evidence_readiness: ComparativeEvidenceReadiness
    comparative_assumptions: list[ComparativeAssumption] = Field(default_factory=list)
    pairwise_comparisons: list[PairwisePathwayComparison] = Field(default_factory=list)
    comparative_element_highlights: list[ComparativeElementHighlight] = Field(
        default_factory=list
    )
    researcher_decision_required: Literal[True] = True
    decision_boundary: str


class EndpointEvidence(BaseModel):
    endpoint_quality_score: float | None = None
    endpoint_stability_score: float | None = None
    endpoint_energy_above_hull: float | None = None
    endpoint_criticality_score: float | None = None
    endpoint_risk_score: float | None = None
    endpoint_risk_known: bool = False
    endpoint_risk_profile_coverage: float = 0.0
    endpoint_risk_complete_profile_coverage: float = 0.0
    endpoint_risk_dimension_coverage: float = 0.0
    endpoint_risk_evidence_complete: bool = False
    endpoint_partial_risk_profile_elements: list[str] = Field(default_factory=list)
    endpoint_unknown_risk_elements: list[str] = Field(default_factory=list)
    evidence_readiness: EvidenceReadiness


class EndpointRecord(BaseModel):
    pathway_rank: int | None = None
    endpoint_material: EndpointMaterialReference | None = None
    endpoint_evidence: EndpointEvidence
    requires_validation: Literal[True] = True


class GroupedEndpointEvidence(BaseModel):
    endpoint_quality_score: float | None = None
    endpoint_stability_score: float | None = None
    endpoint_energy_above_hull_band: str
    endpoint_energy_above_hull_band_rank: int
    endpoint_criticality_band: str
    endpoint_criticality_band_rank: int
    endpoint_risk_band: str
    endpoint_risk_band_rank: int
    endpoint_risk_score_eligible: bool
    endpoint_risk_known: bool
    endpoint_risk_profile_coverage: float
    endpoint_risk_complete_profile_coverage: float
    endpoint_risk_dimension_coverage: float
    endpoint_risk_evidence_complete: bool
    evidence_readiness: EvidenceReadiness


class EndpointPriorityGroup(BaseModel):
    endpoint_sensitive_group_rank: int
    shared_endpoint_evidence: GroupedEndpointEvidence
    pathways: list[EndpointRecord]
    reason: str


class SinglePathwayEndpointGroup(BaseModel):
    scientific_usefulness_score: float
    pathway_count: int
    differentiation_status: Literal["single_pathway"]
    tie_preserved: Literal[False]
    reason: str
    endpoint_records: list[EndpointRecord]


class PreservedTieEndpointGroup(BaseModel):
    scientific_usefulness_score: float
    pathway_count: int
    differentiation_status: Literal["tie_preserved"]
    tie_preserved: Literal[True]
    reason: str
    endpoint_records: list[EndpointRecord]


class DifferentiatedEndpointGroup(BaseModel):
    scientific_usefulness_score: float
    pathway_count: int
    differentiation_status: Literal["endpoint_differentiated"]
    tie_preserved: Literal[False]
    reason: str
    ordering_policy: Literal["lexicographic"]
    ordering_dimensions: list[str]
    endpoint_priority_groups: list[EndpointPriorityGroup]


EndpointRankingGroup = (
    SinglePathwayEndpointGroup
    | PreservedTieEndpointGroup
    | DifferentiatedEndpointGroup
)


class EndpointSensitiveRanking(BaseModel):
    ranking_basis: Literal["endpoint_specific_existing_evidence"]
    ordering_policy: Literal["lexicographic"]
    ordering_dimensions: list[str]
    evidence_grouping_policy: dict[str, str]
    score_preserved: Literal[True]
    original_score_field: Literal["scientific_usefulness_score"]
    endpoint_sensitive_score_added: Literal[False]
    differentiated_group_count: int
    preserved_tie_group_count: int
    groups: list[EndpointRankingGroup]
    researcher_decision_required: Literal[True]
    decision_boundary: str


class ScientificPathwayAnalysisResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    pathway_opportunities: list[ScientificPathwayOpportunity]
    endpoint_sensitive_ranking: EndpointSensitiveRanking | None = None
    pathway_comparison: PathwayComparison
    researcher_decision_required: Literal[True]
    decision_boundary: str