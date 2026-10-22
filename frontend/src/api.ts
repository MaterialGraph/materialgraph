export interface Material {
  id: number; mp_id: string; formula: string; pretty_formula: string;
  material_type: string | null; band_gap: number | null;
  energy_above_hull: number | null; formation_energy_per_atom: number | null;
  density: number | null; is_stable: boolean; source: string;
}
export interface MaterialDetail extends Material {
  elements: { id: number; symbol: string; name: string }[];
}
export interface Candidate {
  material_id: number; mp_id: string | null; pretty_formula: string | null;
  formula: string; discovery_score: number; score_breakdown: Record<string, number>;
  discovery_path: string[]; explanation: string;
  substitution_path: { reason: string; relationship_basis: string;
    structural_preservation_validated: boolean; substitution_mechanism_validated: boolean } | null;
}
export interface CandidateResponse {
  material_id: number; base_formula: string | null;
  discovery_goal: { avoid_element: string | null; prefer_element: string | null };
  constraint_policy: { avoid_element: string; prefer_element: string };
  discovery_warnings: string[]; candidates: Candidate[];
}
export class ApiError extends Error {
  constructor(readonly status: number, message: string, readonly details?: unknown) { super(message); }
}
const base = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '');
async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try { response = await fetch(`${base}${path}`, { signal }); }
  catch (error) { if (signal?.aborted) throw error; throw new ApiError(0, 'Cannot reach the API. Check the local backend connection.'); }
  if (!response.ok) {
    let message = `Request failed (${response.status}).`;
    if (response.status >= 500 && !response.headers?.get('content-type')?.includes('application/json')) {
      message = 'API unavailable or returned a non-JSON error. Check the local backend and Vite proxy.';
    }
    if (response.status === 404) message = 'Material not found.';
    if (response.status === 422) message = 'Invalid element symbol. Enter a valid chemical symbol.';
    if (response.status === 429) message = 'Too many requests. Please try again shortly.';
    throw new ApiError(response.status, message);
  }
  return response.json() as Promise<T>;
}
export { get as getJson };
export const listMaterials = (offset: number, signal?: AbortSignal) =>
  get<Material[]>(`/materials?limit=100&offset=${offset}`, signal);
export const materialDetail = (id: number, signal?: AbortSignal) =>
  get<MaterialDetail>(`/materials/${id}/detail`, signal);
export function candidates(id: number, avoid: string, prefer: string, signal?: AbortSignal) {
  const params = new URLSearchParams({ limit: '10', include_substitution_paths: 'false' });
  if (avoid.trim()) params.set('avoid_element', avoid.trim());
  if (prefer.trim()) params.set('prefer_element', prefer.trim());
  return get<CandidateResponse>(`/materials/${id}/discovery/candidates?${params}`, signal);
}

/** Full-dataset search (contract M). The mode is always explicit. */
export type SearchMode = 'formula' | 'mp_id' | 'chemsys' | 'contains';
export type SearchResult = { material_id: number; mp_id: string; formula: string; pretty_formula: string };
export type MaterialSearchResponse = {
  interpretation: { mode: SearchMode; input: string; elements: string[] | null; amounts: Record<string, number> | null; normalized_fractions: Record<string, number> | null; reduced_formula: string | null; mp_id: string | null };
  dataset: { source: 'materials_project'; source_release: string | null; dataset_total: number; provenance_note: string; composition_exclusion_count: number };
  total_matches: number; dataset_total: number; limit: number; offset: number;
  results: SearchResult[];
  suggestions: { basis: 'same_chemical_system'; explanation: string; results: SearchResult[] } | null;
  message: string | null;
};
export type SearchQueryProblem = { code: string; mode: SearchMode; input: string; explanation: string };

export async function searchMaterials(mode: SearchMode, q: string, offset = 0, signal?: AbortSignal): Promise<MaterialSearchResponse> {
  const params = new URLSearchParams({ mode, q, limit: '20', offset: String(offset) });
  let response: Response;
  try { response = await fetch(`${base}/materials/search?${params}`, { signal }); }
  catch (error) { if (signal?.aborted) throw error; throw new ApiError(0, 'Cannot reach the API. Check the local backend connection.'); }
  if (response.status === 422) {
    const payload = await response.json().catch(() => null) as { detail?: unknown } | null;
    const detail = payload?.detail;
    // Backend explanations are shown as given; the query is never corrected client-side.
    if (detail && typeof detail === 'object' && 'explanation' in detail) throw new ApiError(422, String((detail as SearchQueryProblem).explanation), detail);
    throw new ApiError(422, 'The search request was not valid.', payload);
  }
  if (!response.ok) throw new ApiError(response.status, response.status === 429 ? 'Too many requests. Please try again shortly.' : `Search failed (${response.status}).`);
  return response.json() as Promise<MaterialSearchResponse>;
}

export async function postJson<T>(path: string, body: unknown, signal?: AbortSignal): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${base}${path}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body), signal,
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new ApiError(0, 'Cannot reach the API. Check the local backend connection.');
  }
  if (!response.ok) {
    if (response.status === 422) {
      const payload: unknown = await response.json().catch(() => null);
      throw new ApiError(422, 'Check the objective fields and try again.', payload);
    }
    if (response.status === 404) throw new ApiError(404, 'Material not found.');
    if (response.status === 429) throw new ApiError(429, 'Too many requests. Please try again shortly.');
    throw new ApiError(response.status, response.status >= 500
      ? 'The investigation API is unavailable. Please try again.'
      : `Request failed (${response.status}).`);
  }
  return response.json() as Promise<T>;
}
