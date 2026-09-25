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

const scope = 'These ranked materials come from a selected cohort of material identities in battery-relevant chemical systems. They do not represent a comprehensive search of materials space.';

it('shows an eligible-chain reason alongside no returned chain without rewriting backend text', () => {
  const reason = 'Appears in an eligible composition chain with relationship type alkali_substitution.';
  const result = {
    ...sample,
    ranked_candidates: sample.ranked_candidates.map(candidate => candidate.material_id === 8
      ? { ...candidate, reasons: [reason] }
      : candidate),
  };
  const html = renderToStaticMarkup(<ObjectiveResults result={result} submitted="{}"/>);
  expect(html).toContain(reason);
  expect(html).toContain('No returned chain includes this material.');
  expect(html).toContain('A missing returned chain does not establish the absence of a composition-level relationship.');
  expect(html).toContain('Returned composition chain 1 · 2 relationship steps');
});

it('places cohort coverage beneath the ranked-material heading for populated and empty results', () => {
  for (const ranked_candidates of [sample.ranked_candidates, []]) {
    const html = renderToStaticMarkup(<ObjectiveResults result={{ ...sample, ranked_candidates }} submitted="{}"/>);
    expect(html).toContain(`<h3>Ranked materials</h3><p class="hint">${scope}</p>`);
    expect(html.indexOf(scope)).toBeLessThan(html.indexOf('Returned order and objective rule scores.'));
    expect(html).toContain('Search scope');
    expect(html).toContain('The returned results are limited. Scientific completeness is not guaranteed.');
    expect(html).toContain('Search truncation: No');
    expect(html).toContain('This does not establish that every scientifically relevant pathway was found.');
  }
  const populated = renderToStaticMarkup(<ObjectiveResults result={sample} submitted="{}"/>);
  expect(populated.indexOf(scope)).toBeLessThan(populated.indexOf('Ranked material 1'));
  expect(populated).toContain('No returned chain includes this material.');
  expect(populated).toContain('A missing returned chain does not establish the absence of a composition-level relationship.');
});

it('derives intermediate and final roles only from returned chain membership', () => {
  expect(returnedRole(sample, 1)).toBe('Intermediate in returned chain');
  expect(returnedRole(sample, 6)).toBe('Final material in returned chain');
  expect(returnedRole(sample, 8)).toBeNull();
  const html = renderToStaticMarkup(<ObjectiveResults result={sample} submitted="{}"/>);
  expect(html).toContain('No returned chain includes this material.');
  expect(html).toContain('A missing returned chain does not establish the absence of a composition-level relationship.');
  expect(html).toContain('Some materials have the same objective rule score. Their order follows the API response.');
  expect(html).toContain('class="objectiveRole">Intermediate</span>');
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
  expect(html).toContain('Reported composition relationship');
  expect(html).toContain('<code>new_relation</code>');
  expect(html).not.toContain('Reported relationship: new relation');
  expect(html).toContain('Shared elements not supplied');
  expect(html).toContain('Search truncation: Yes');
  expect(html).not.toContain('→');
  expect(relationshipLabel('alkali_substitution')).toBe('Possible alkali composition substitution');
});

it('keeps chain position, metadata, and score scopes explicit', () => {
  const chain = { ...sample.chains[0], score_breakdown: { transition_plausibility: 20 } };
  const html = renderToStaticMarkup(<ObjectiveResults result={{ ...sample, chains: [chain] }} submitted="{}"/>);
  expect(html).toContain('mp-19017 <span class="objectiveRole">Source</span>');
  expect(html).toContain('mp-26003 <span class="objectiveRole">Intermediate</span>');
  expect(html).toContain('mp-19028 <span class="objectiveRole">Final</span>');
  expect(html).toContain('Possible alkali composition substitution');
  expect(html).toContain('Composition family relationship');
  expect(html).toContain('<code>alkali_substitution</code>');
  expect(html).toContain('Composition heuristic <code>composition_heuristic</code>');
  expect(html).toContain('Element overlap <code>element_overlap</code>');
  expect(html).toContain('Structural preservation</dt><dd>Not validated');
  expect(html).toContain('Substitution mechanism</dt><dd>Not validated');
  expect(html).toContain('Shared elements</dt><dd>Fe, O, P');
  expect(html).toContain('Chain usefulness rule score: 96');
  expect(html).toContain('Whole-chain score breakdown');
  expect(html).toContain('Relationship type weighting');
  expect(html).not.toContain('Transition Plausibility');
  expect(html).not.toContain('Relationship usefulness rule score');
  expect(html).toContain('Shared-element continuity describes a composition-level relationship. It does not establish structural preservation or a validated substitution mechanism.');
  expect(html).toContain('No returned chain includes this material.');
  expect(html).toContain('A missing returned chain does not establish the absence of a composition-level relationship.');
});

it('separates relationship facts, the whole-chain score, and verbatim backend explanations', () => {
  const transition = {
    ...sample.chains[0].transitions[1],
    reason: 'Backend Li -> Na wording; preserve exactly.',
    removed_elements: ['Li'], introduced_elements: ['Na'],
  };
  const chain = {
    ...sample.chains[0],
    transitions: [sample.chains[0].transitions[0], transition],
    chain_reason: 'This discovery chain follows family_expansion -> alkali_substitution.',
    usefulness_reason: 'Composition-chain rule score evidence: reported relationship types: alkali_substitution.',
    scientific_usefulness_score: 93.75,
    score_breakdown: {
      shared_element_continuity: 30, objective_alignment: 18.75,
      transition_plausibility: 20, path_efficiency: 10, material_quality: 15,
    },
  };
  const html = renderToStaticMarkup(<ObjectiveResults result={{ ...sample, chains: [chain] }} submitted="{}"/>);
  expect(html.indexOf('Chain usefulness rule score: 93.75')).toBeLessThan(html.indexOf('<summary>Relationship details and scoring'));
  expect(html).toContain('<section class="objectiveDetailSection" aria-label="Relationship details">');
  expect(html).toContain('Relationship 2: Possible alkali composition substitution');
  expect(html).toContain('Composition heuristic <code>composition_heuristic</code>');
  expect(html).toContain('Element overlap <code>element_overlap</code>');
  expect(html).toContain('Structural preservation</dt><dd>Not validated');
  expect(html).toContain('Substitution mechanism</dt><dd>Not validated');
  expect(html).toContain('Shared elements</dt><dd>Fe, O, P');
  expect(html).toContain('Elements absent in next composition</dt><dd>Li');
  expect(html).toContain('Elements present only in next composition</dt><dd>Na');
  expect(html).toContain('<h5>Whole-chain score breakdown</h5>');
  for (const [label, key, value, maximum] of [
    ['Shared-element overlap', 'shared_element_continuity', '30', '30'],
    ['Endpoint objective alignment', 'objective_alignment', '18.75', '25'],
    ['Relationship type weighting', 'transition_plausibility', '20', '20'],
    ['Chain structure component', 'path_efficiency', '10', '10'],
    ['Endpoint/bottleneck material quality', 'material_quality', '15', '15'],
  ]) expect(html).toContain(`${label} <code>${key}</code></th><td>${value}</td><td>${maximum}</td>`);
  expect(html).toContain('Chain usefulness rule score</th><td>93.75</td><td>100</td>');
  expect(html).toContain('<details class="objectiveTechnical"><summary>Backend technical explanations</summary>');
  expect(html).toContain('Backend chain explanation:</strong> This discovery chain follows family_expansion -&gt; alkali_substitution.');
  expect(html).toContain('Backend transition reason:</strong> Backend Li -&gt; Na wording; preserve exactly.');
  expect(html).toContain('Backend score explanation:</strong> Composition-chain rule score evidence: reported relationship types: alkali_substitution.');
  expect(html).not.toContain('Original returned reason');
  expect(html).not.toContain('Path Efficiency');
  expect(html).toContain('No returned chain includes this material.');
  expect(html).toContain('A missing returned chain does not establish the absence of a composition-level relationship.');
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
