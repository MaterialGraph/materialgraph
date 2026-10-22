export type Objective = {
  avoid_elements: string[];
  prefer_elements: string[];
  preserve_elements: string[];
  target_family: string | null;
  max_hops: number;
  limit: number;
  prefer_lower_criticality: boolean;
  require_stable_materials: boolean;
};

export type ObjectiveRequest = {
  objective: Objective;
  mode: 'balanced' | 'exploratory' | 'strict';
  limit: number;
};

export type ObjectiveMaterial = {
  material_id: number; mp_id: string | null; pretty_formula: string | null; formula: string;
};
export type ObjectiveTransition = {
  from_material_id: number; to_material_id: number; transition_type: string;
  reason: string; shared_elements: string[]; preservation_basis: string;
  relationship_basis: string; structural_preservation_validated: boolean;
  substitution_mechanism_validated: boolean;
  removed_elements?: string[]; introduced_elements?: string[];
};
export type ObjectiveChain = {
  hop_count: number; materials: ObjectiveMaterial[]; transitions: ObjectiveTransition[];
  chain_reason: string; scientific_usefulness_score: number | null;
  score_breakdown: Record<string, number> | null; usefulness_reason: string | null;
};
export type ObjectiveCandidate = {
  material_id: number; formula: string | null; score: number;
  /** Source identifier; absent in responses recorded before Release 1. */
  mp_id?: string | null;
  reasons: string[]; warnings: string[];
};
export type ObjectiveResponse = {
  material_id: number; base_formula: string | null; objective: Objective;
  objective_policy: {
    stable_materials: string; stability_scope: string;
    stability_evidence_policy: string; unknown_stability_evidence: string;
    lower_criticality: string; unknown_criticality_evidence: string;
  };
  mode: ObjectiveRequest['mode'];
  constraint_policy: {
    avoid_elements: 'soft_penalty' | 'hard_rejection';
    prefer_elements: 'soft_bonus'; hard_rejection_scope: 'none' | 'all_non_root_chain_materials';
  };
  search_metadata: {
    search_policy: string; requested_result_limit: number;
    expansion_limit_per_material: number; search_state_budget: number;
    expanded_state_count: number; generated_chain_count: number;
    returned_chain_count: number; search_truncated: boolean;
    result_truncated: boolean; scientific_completeness_guaranteed: false;
    /** Expansion-limit reporting (#51). Absent or null when the backend predates it. */
    expansion_limit_binding?: boolean | null;
    expansions_with_cap_discards?: number | null;
    candidates_considered_total?: number | null;
    candidates_eligible_total?: number | null;
    candidates_admitted_total?: number | null;
    candidates_discarded_by_expansion_limit_total?: number | null;
    distinct_candidates_discarded_by_expansion_limit?: number | null;
  };
  ranked_candidates: ObjectiveCandidate[]; chains: ObjectiveChain[];
  warnings: string[]; explanation: string;
  /** Absent when the backend predates objective coverage contract version 1. */
  objective_coverage?: ObjectiveCoverage;
};

export type PreferCoverageStatus = 'represented' | 'not_represented' | 'not_evaluated';
export type AvoidCoverageStatus = 'present' | 'not_observed' | 'not_evaluated';
export type MaterialElementCoverage<S> = {
  element: string; unit: 'returned_ranked_materials';
  containing_count: number; evaluated_count: number; not_evaluated_count: number; total_count: number;
  status: S; coverage_complete: boolean;
};
export type ChainElementCoverage = {
  element: string; unit: 'returned_chains_excluding_source';
  containing_chain_count: number; evaluated_chain_count: number; not_evaluated_chain_count: number; total_chain_count: number;
  chain_positions: number[]; status: AvoidCoverageStatus; coverage_complete: boolean;
};
export type ChainAvoidanceDetail = {
  chain_position: number;
  materials_with_avoided_elements: { material_id: number; chain_material_index: number; role: 'intermediate' | 'final'; avoided_elements: string[] }[];
  not_evaluated_material_ids: number[];
};
/** Backend-computed objective coverage (contract version 1). The client renders it and never re-derives it. */
export type ObjectiveCoverage = {
  contract_version: '1'; scope: 'returned_results_only'; element_evaluation_basis: 'formula_symbols_strict_parse';
  returned_ranked_material_count: number; ranked_material_pool_count: number; returned_chain_count: number;
  preferred_elements: MaterialElementCoverage<PreferCoverageStatus>[];
  avoided_elements_in_ranked_materials: MaterialElementCoverage<AvoidCoverageStatus>[];
  avoided_elements_in_returned_chains: ChainElementCoverage[];
  chain_avoidance: ChainAvoidanceDetail[];
  source_material: { material_id: number; excluded_from_counts: true; avoided_elements_present: string[] | null };
  terms_not_evaluated: ('preserve_elements' | 'target_family')[];
  mode: 'balanced' | 'exploratory' | 'strict'; avoid_policy_explanation: string; limitations: string[];
};
