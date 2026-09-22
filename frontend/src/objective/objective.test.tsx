import { afterEach, expect, it, vi } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ApiError } from '../api';
import { ObjectiveResults, relationshipLabel, returnedRole } from './ObjectiveInvestigation';
import type { ObjectiveResponse, ObjectiveTransition } from './contract';
import { buildObjectiveRequest, exploreObjective, initialDraft } from './request';
import { errorDetails } from './useObjectiveInvestigation';

afterEach(() => vi.unstubAllGlobals());

it('posts the structured objective with both limits aligned and no query parameters', async () => {
  const request = buildObjectiveRequest({ ...initialDraft, avoid: 'li', prefer: 'Na', preserve: 'Fe, P O', family: 'phosphate' });
  expect(request.objective).toMatchObject({ avoid_elements: ['Li'], preserve_elements: ['Fe', 'P', 'O'], limit: 5 });
  expect(request.limit).toBe(5);
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ chains: [] }) });
  vi.stubGlobal('fetch', fetchMock);
  await exploreObjective(5, request);
  expect(fetchMock.mock.calls[0][0]).toBe('/api/v1/materials/5/discovery/objective/explore');
  expect(fetchMock.mock.calls[0][1]).toMatchObject({ method: 'POST', body: JSON.stringify(request) });
});

it('keeps backend validation details for the submitted objective', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: [{ loc: ['body', 'objective', 'avoid_elements', 0], msg: 'Unknown element' }] }) }));
  await expect(exploreObjective(5, buildObjectiveRequest(initialDraft))).rejects.toMatchObject({ status: 422, details: { detail: [{ msg: 'Unknown element' }] } } satisfies Partial<ApiError>);
  expect(errorDetails(new ApiError(422, 'Invalid objective', { detail: [{ loc: ['body', 'objective', 'avoid_elements', 0], msg: 'Unknown element' }] }))).toEqual(['objective → avoid_elements → 0: Unknown element']);
});

const sample: ObjectiveResponse = {
  material_id: 5, base_formula: 'LiFePO4', objective: buildObjectiveRequest(initialDraft).objective,
  objective_policy: { stable_materials: 'not_required', stability_scope: 'none', stability_evidence_policy: 'canonical_energy_primary_with_imported_flag_fallback', unknown_stability_evidence: 'not_applicable', lower_criticality: 'canonical_quality_preference', unknown_criticality_evidence: 'no_criticality_credit' },
  mode: 'balanced', constraint_policy: { avoid_elements: 'soft_penalty', prefer_elements: 'soft_bonus', hard_rejection_scope: 'none' },
  search_metadata: { search_policy: 'bounded_breadth_first', requested_result_limit: 5, expansion_limit_per_material: 6, search_state_budget: 200, expanded_state_count: 7, generated_chain_count: 34, returned_chain_count: 1, search_truncated: false, result_truncated: true, scientific_completeness_guaranteed: false },
  ranked_candidates: [{ material_id: 6, formula: 'Na3Fe(PO4)2', score: 127.25, reasons: ['Na present'], warnings: [] }, { material_id: 8, formula: 'Na9Fe3P8O29', score: 127.25, reasons: [], warnings: [] }],
  chains: [{ hop_count: 2, materials: [
    { material_id: 5, mp_id: 'mp-19017', pretty_formula: 'LiFePO4', formula: 'LiFePO4' },
    { material_id: 1, mp_id: 'mp-26003', pretty_formula: 'LiFe(PO3)3', formula: 'LiFe(PO3)3' },
    { material_id: 6, mp_id: 'mp-19028', pretty_formula: 'Na3Fe(PO4)2', formula: 'Na3Fe(PO4)2' },
  ], transitions: [
    { from_material_id: 5, to_material_id: 1, transition_type: 'family_expansion', reason: 'Original family explanation.', shared_elements: ['Fe', 'Li', 'O', 'P'], preservation_basis: 'element_overlap', relationship_basis: 'composition_heuristic', structural_preservation_validated: false, substitution_mechanism_validated: false },
    { from_material_id: 1, to_material_id: 6, transition_type: 'alkali_substitution', reason: 'Original substitution explanation.', shared_elements: ['Fe', 'O', 'P'], preservation_basis: 'element_overlap', relationship_basis: 'composition_heuristic', structural_preservation_validated: false, substitution_mechanism_validated: false },
  ], chain_reason: 'Shared-element continuity.', scientific_usefulness_score: 96, score_breakdown: null, usefulness_reason: null }],
  warnings: [], explanation: 'Backend explanation.',
};

it('derives intermediate and final roles only from returned chain membership', () => {
  expect(returnedRole(sample, 1)).toBe('Intermediate in returned chain');
  expect(returnedRole(sample, 6)).toBe('Final material in returned chain');
  expect(returnedRole(sample, 8)).toBeNull();
  const html = renderToStaticMarkup(<ObjectiveResults result={sample} submitted="{}"/>);
  expect(html).toContain('No returned chain includes this material.');
  expect(html).toContain('A missing returned chain does not establish the absence of a composition-level relationship.');
  expect(html).toContain('Some materials have the same objective rule score. Their order follows the API response.');
  expect(html).toContain('Intermediate in returned chain');
  expect(html).toContain('Returned chain:');
  expect(html).not.toContain('Returned pathways:');
  expect(renderToStaticMarkup(<ObjectiveResults result={{ ...sample, chains: [sample.chains[0], sample.chains[0]] }} submitted="{}"/>)).toContain('Returned chains:');
  expect(html).toContain('Returned composition chain 1 · 2 relationship steps');
  expect(html).toContain('Shared elements: Fe, Li, O, P');
  expect(html).toContain('Shared elements: Fe, O, P');
  expect(html).toContain('Relationship details and scoring');
  expect(html).toContain('Not validated</span>');
  expect(html).toContain('“Not validated” refers to structural preservation or a substitution mechanism for that relationship');
  expect(html.match(/class="objectiveValidation"/g)).toHaveLength(2);
  expect(html).toContain('These chains describe composition-level relationships between returned materials.');
  expect(html).toContain('<details open=""><summary>Returned reasons');
  expect(html).toContain('Search truncation: No');
  expect(html).toContain('generated chains are included in this response');
  expect(html).not.toContain('No pathway found');
});

it('presents one relationship step without implying a reaction or inventing unknown labels', () => {
  const transition: ObjectiveTransition = { ...sample.chains[0].transitions[1], transition_type: 'new_relation', shared_elements: [] };
  const chain = { ...sample.chains[0], hop_count: 1, materials: [sample.chains[0].materials[0], sample.chains[0].materials[2]], transitions: [transition] };
  const html = renderToStaticMarkup(<ObjectiveResults result={{ ...sample, chains: [chain], search_metadata: { ...sample.search_metadata, search_truncated: true, result_truncated: false } }} submitted="{}"/>);
  expect(html).toContain('Returned composition chain 1 · 1 relationship step');
  expect(html).toContain('Reported relationship: new relation');
  expect(html).toContain('Shared elements not supplied');
  expect(html).toContain('Search truncation: Yes');
  expect(html).not.toContain('→');
  expect(relationshipLabel('alkali_substitution')).toBe('Possible alkali composition substitution');
});

it('does not add validation badges or an equality note without supporting response fields', () => {
  const transition = { ...sample.chains[0].transitions[0], structural_preservation_validated: true, substitution_mechanism_validated: true };
  const chain = { ...sample.chains[0], materials: sample.chains[0].materials.slice(0, 2), transitions: [transition] };
  const result = { ...sample, ranked_candidates: [sample.ranked_candidates[0], { ...sample.ranked_candidates[1], score: 126 }], chains: [chain] };
  const html = renderToStaticMarkup(<ObjectiveResults result={result} submitted="{}"/>);
  expect(html).not.toContain('class="objectiveValidation"');
  expect(html).not.toContain('Some materials have the same objective rule score.');
  expect(html).toContain('Returned composition chain 1 · 1 relationship step');
  expect(html).toContain('Shared elements: Fe, Li, O, P');
});

it('presents zero ranked materials and zero returned pathways separately', () => {
  const html = renderToStaticMarkup(<ObjectiveResults result={{ ...sample, ranked_candidates: [], chains: [] }} submitted="{}"/>);
  expect(html).toContain('No ranked materials returned for this objective.');
  expect(html).toContain('No pathways included in this response.');
  const rankedWithoutPaths = renderToStaticMarkup(<ObjectiveResults result={{ ...sample, chains: [] }} submitted="{}"/>);
  expect(rankedWithoutPaths).toContain('No pathways included in this response.');
  expect(rankedWithoutPaths).toContain('No returned chain includes this material.');
});
