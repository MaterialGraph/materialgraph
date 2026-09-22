import { postJson } from '../api';
import type { ObjectiveRequest, ObjectiveResponse } from './contract';

export const exploreObjective = (materialId: number, request: ObjectiveRequest, signal?: AbortSignal) =>
  postJson<ObjectiveResponse>(`/materials/${materialId}/discovery/objective/explore`, request, signal);

export type ObjectiveDraft = {
  avoid: string; prefer: string; preserve: string; family: '' | 'phosphate';
  mode: ObjectiveRequest['mode']; hops: number; limit: number;
  lowerCriticality: boolean; requireStable: boolean;
};

export const initialDraft: ObjectiveDraft = {
  avoid: '', prefer: '', preserve: '', family: '', mode: 'balanced', hops: 2, limit: 5,
  lowerCriticality: true, requireStable: false,
};

export function buildObjectiveRequest(draft: ObjectiveDraft): ObjectiveRequest {
  function elements(value: string, label: string): string[] {
    const tokens = value.split(/[\s,]+/).filter(Boolean);
    if (tokens.length > 32 || tokens.some(token => !/^[A-Za-z]{1,2}$/.test(token))) {
      throw new Error(`${label}: enter up to 32 chemical symbols separated by commas or spaces.`);
    }
    return [...new Set(tokens.map(token => token[0].toUpperCase() + token.slice(1).toLowerCase()))];
  }
  if (!Number.isInteger(draft.hops) || draft.hops < 1 || draft.hops > 3) {
    throw new Error('Maximum pathway steps must be between 1 and 3.');
  }
  if (!Number.isInteger(draft.limit) || draft.limit < 1 || draft.limit > 20) {
    throw new Error('Maximum returned results must be between 1 and 20.');
  }
  return {
    objective: {
      avoid_elements: elements(draft.avoid, 'Elements to avoid'),
      prefer_elements: elements(draft.prefer, 'Preferred elements'),
      preserve_elements: elements(draft.preserve, 'Elements to retain'),
      target_family: draft.family || null, max_hops: draft.hops, limit: draft.limit,
      prefer_lower_criticality: draft.lowerCriticality,
      require_stable_materials: draft.requireStable,
    },
    mode: draft.mode, limit: draft.limit,
  };
}
