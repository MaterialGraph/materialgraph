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
};
export type ObjectiveChain = {
  hop_count: number; materials: ObjectiveMaterial[]; transitions: ObjectiveTransition[];
  chain_reason: string; scientific_usefulness_score: number | null;
  score_breakdown: Record<string, number> | null; usefulness_reason: string | null;
};
export type ObjectiveCandidate = {
  material_id: number; formula: string | null; score: number;
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
  };
  ranked_candidates: ObjectiveCandidate[]; chains: ObjectiveChain[];
  warnings: string[]; explanation: string;
};
