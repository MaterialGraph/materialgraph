import type { CandidateResponse } from '../api';
import type { ObjectiveRequest, ObjectiveResponse } from '../objective/contract';

export type SelectedMaterial = { id: number; formula: string; mpId: string | null; role: string };
export type ComparisonLaunchContext = {
  sourceMaterialId: number;
  selectedMaterials: SelectedMaterial[];
  originWorkflow: 'discovery' | 'objective';
  investigationContext: string;
};

export function toggleComparisonSelection(current: SelectedMaterial[], material: SelectedMaterial): SelectedMaterial[] {
  if (current.some(item => item.id === material.id)) return current.filter(item => item.id !== material.id);
  return current.length === 3 ? current : [...current, material];
}

export function discoveryLaunch(result: CandidateResponse, selected: SelectedMaterial[]): ComparisonLaunchContext {
  return {
    sourceMaterialId: result.material_id, selectedMaterials: selected, originWorkflow: 'discovery',
    investigationContext: `Selected via Candidate Discovery. Applied Avoid: ${result.discovery_goal.avoid_element ?? 'none'}; applied Prefer: ${result.discovery_goal.prefer_element ?? 'none'}.`,
  };
}

export function objectiveRole(result: ObjectiveResponse, id: number): string {
  const chains = result.chains.flatMap((chain, index) => chain.materials.slice(1).some(material => material.material_id === id) ? [index + 1] : []);
  return chains.length ? `Ranked material · Included in returned composition ${chains.length === 1 ? 'chain' : 'chains'} ${chains.join(', ')}` : 'Ranked material';
}

export function objectiveLaunch(result: ObjectiveResponse, submitted: ObjectiveRequest, selected: SelectedMaterial[]): ComparisonLaunchContext {
  const objective = submitted.objective;
  return {
    sourceMaterialId: result.material_id, selectedMaterials: selected, originWorkflow: 'objective',
    investigationContext: `Selected via Objective Investigation. Submitted mode: ${submitted.mode}; Avoid: ${objective.avoid_elements.join(', ') || 'none'}; Prefer: ${objective.prefer_elements.join(', ') || 'none'}; Preserve: ${objective.preserve_elements.join(', ') || 'none'}; family: ${objective.target_family ?? 'any'}; maximum hops: ${objective.max_hops}; lower criticality preference: ${objective.prefer_lower_criticality ? 'yes' : 'no'}; require stable materials: ${objective.require_stable_materials ? 'yes' : 'no'}.`,
  };
}
