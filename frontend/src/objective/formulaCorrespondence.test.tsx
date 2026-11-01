import { expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ObjectiveResults } from './ObjectiveInvestigation';
import type { CorrespondenceReason, FormulaCorrespondence, FormulaCorrespondenceReport, ObjectiveResponse } from './contract';
import { FormulaCorrespondencePanel, SourceAnalogNote, correspondenceDetail, correspondenceHeading, sourceAnalogText } from './FormulaCorrespondence';
import { buildObjectiveRequest, initialDraft } from './request';

// Synthetic response for display tests only (SRQ-01 PR-A3). The chain is
// LiFePO4 -> LiFe(PO3)3 -> Na3Fe(PO4)2; ranked material 10 (NaFePO4) is in no returned chain.
const text = (html: string) => html.replace(/<[^>]+>/g, ' ').replace(/&#x27;/g, "'").replace(/\s+/g, ' ');

const base: ObjectiveResponse = {
  material_id: 5, base_formula: 'LiFePO4', objective: buildObjectiveRequest(initialDraft).objective,
  objective_policy: { stable_materials: 'not_required', stability_scope: 'none', stability_evidence_policy: 'canonical_energy_primary_with_imported_flag_fallback', unknown_stability_evidence: 'not_applicable', lower_criticality: 'canonical_quality_preference', unknown_criticality_evidence: 'no_criticality_credit' },
  mode: 'balanced', constraint_policy: { avoid_elements: 'reject_introduced_penalize_inherited', prefer_elements: 'reserved_slot_and_bonus', hard_rejection_scope: 'none' },
  search_metadata: { search_policy: 'bounded_breadth_first', requested_result_limit: 5, expansion_limit_per_material: 6, search_state_budget: 200, expanded_state_count: 7, generated_chain_count: 34, returned_chain_count: 1, search_truncated: false, result_truncated: true, scientific_completeness_guaranteed: false },
  ranked_candidates: [
    { material_id: 6, formula: 'Na3Fe(PO4)2', score: 115, reasons: [], warnings: [] },
    { material_id: 8, formula: 'Na9Fe3P8O29', score: 115, reasons: [], warnings: [] },
    { material_id: 10, formula: 'NaFePO4', score: 115, reasons: [], warnings: [] },
  ],
  chains: [{ hop_count: 2, materials: [
    { material_id: 5, mp_id: 'mp-19017', pretty_formula: 'LiFePO4', formula: 'LiFePO4' },
    { material_id: 1, mp_id: 'mp-26003', pretty_formula: 'LiFe(PO3)3', formula: 'LiFe(PO3)3' },
    { material_id: 6, mp_id: 'mp-19028', pretty_formula: 'Na3Fe(PO4)2', formula: 'Na3Fe(PO4)2' },
  ], transitions: [
    { from_material_id: 5, to_material_id: 1, transition_type: 'family_expansion', reason: 'Family explanation.', shared_elements: ['Fe', 'Li', 'O', 'P'], preservation_basis: 'element_overlap', relationship_basis: 'composition_heuristic', structural_preservation_validated: false, substitution_mechanism_validated: false },
    { from_material_id: 1, to_material_id: 6, transition_type: 'alkali_substitution', reason: 'Substitution explanation.', shared_elements: ['Fe', 'O', 'P'], preservation_basis: 'element_overlap', relationship_basis: 'composition_heuristic', structural_preservation_validated: false, substitution_mechanism_validated: false },
  ], chain_reason: 'Shared-element continuity.', scientific_usefulness_score: 96, score_breakdown: null, usefulness_reason: null }],
  warnings: [], explanation: 'Backend explanation.',
};

const exact: FormulaCorrespondence = { correspondence_class: 'exact_alkali_replacement', reason: null, replaced_from: 'Li', replaced_to: 'Na' };
const report: FormulaCorrespondenceReport = {
  contract_version: '1', basis: 'stored_composition_fractions', tolerance: 1e-6,
  transitions: [{ chain_position: 1, transition_index: 1, from_material_id: 1, to_material_id: 6, correspondence: { correspondence_class: 'not_exact_replacement', reason: 'ratios_differ', replaced_from: 'Li', replaced_to: 'Na' } }],
  source_correspondence: [{ candidate_rank: 3, material_id: 10, correspondence: exact, formula_group: [] }],
  expansions: [], formula_grouping_available: false, admission_reporting_available: false,
  not_evaluated_material_ids: [8], not_evaluated_count: 1,
  limitations: ['Formula-level comparison only; crystal structure is not assessed.'],
};
const withReport: ObjectiveResponse = { ...base, formula_correspondence: report };
const render = (result: ObjectiveResponse) => renderToStaticMarkup(<ObjectiveResults result={result} submitted="{}"/>);
const card = (html: string, n: number) => html.split('class="objectiveCandidate"')[n];
const paths = (html: string) => html.split('class="objectivePaths"')[1] ?? '';

const reasons: CorrespondenceReason[] = ['ratios_differ', 'non_alkali_elements_differ', 'replacement_alkali_in_source', 'replaced_alkali_in_candidate', 'multiple_alkali_changes', 'formula_unparsed'];
const forbidden = ['validated', 'same structure', 'equivalent', 'drop-in', 'substitution mechanism'];

it('renders exactly as before when the response has no formula_correspondence key', () => {
  const html = text(render(base));
  expect(html).toContain('Different alkali metal (composition not compared)');
  expect(html).not.toContain('Formula correspondence');
  expect(html).not.toContain('Exact formula analog');
  expect(html).not.toContain('not an exact formula analog');
});

it('labels a compared chain step by its class and reason, without the "not compared" heading', () => {
  const html = text(render(withReport));
  expect(html).toContain('Different alkali metal (not an exact formula analog)');
  expect(html).toContain('Element ratios differ.');
  expect(html).toContain('Relationship 2: Different alkali metal (not an exact formula analog)');
  expect(html).toContain('Formula correspondence Element ratios differ. not_exact_replacement');
  expect(html).not.toContain('composition not compared');
  // The family-expansion step has no entry and keeps its existing label.
  expect(html).toContain('Composition family relationship');
});

it('gives every class and reason its own wording', () => {
  expect(correspondenceHeading(exact)).toBe('Exact formula analog');
  expect(correspondenceDetail(exact)).toBe('Li replaced by Na; all other element ratios unchanged.');
  const seen = new Set<string>();
  for (const reason of reasons) {
    const cls = reason === 'formula_unparsed' ? 'not_evaluated' : 'not_exact_replacement';
    const entry: FormulaCorrespondence = { correspondence_class: cls, reason, replaced_from: null, replaced_to: null };
    expect(correspondenceHeading(entry)).toBe(cls === 'not_evaluated' ? 'Different alkali metal (formula correspondence not evaluated)' : 'Different alkali metal (not an exact formula analog)');
    seen.add(correspondenceDetail(entry));
  }
  expect(seen.size).toBe(reasons.length);
});

it('notes an exact formula analog on its ranked card, even when no returned chain includes it', () => {
  const html = render(withReport);
  const nafepo4 = text(card(html, 3));
  expect(nafepo4).toContain('No returned chain includes this material.');
  expect(nafepo4).toContain('Exact formula analog of LiFePO4: Li replaced by Na; all other element ratios unchanged.');
  expect(nafepo4).toContain('it is not a returned chain step');
  expect(nafepo4).toContain('Structure not assessed.');
  // No chain-step label is invented for it.
  expect(text(paths(html))).not.toContain('Exact formula analog');
});

it('shows the not-evaluated note only for listed materials and nothing on other cards', () => {
  const html = render(withReport);
  expect(text(card(html, 2))).toContain('Formula correspondence not evaluated.');
  const first = text(card(html, 1));
  expect(first).not.toContain('Formula correspondence');
  expect(first).not.toContain('Exact formula analog');
});

it('shows no group or admission information while those flags are false', () => {
  const html = text(renderToStaticMarkup(<>
    <FormulaCorrespondencePanel report={report}/>
    <SourceAnalogNote report={report} baseFormula="LiFePO4" materialId={10}/>
  </>)).toLowerCase();
  for (const word of ['group', 'admission', 'admitted', 'excluded', 'budget']) expect(html).not.toContain(word);
});

it('renders the backend limitations and the not-evaluated count in the panel', () => {
  const html = text(renderToStaticMarkup(<FormulaCorrespondencePanel report={report}/>));
  expect(html).toContain('Formula correspondence limitations');
  expect(html).toContain(report.limitations[0]);
  expect(html).toContain('Formula correspondence not evaluated for 1 material.');
});

it('uses none of the forbidden terms in any new text', () => {
  const strings = [
    correspondenceHeading(exact), correspondenceDetail(exact), sourceAnalogText('LiFePO4', exact),
    ...reasons.flatMap(reason => { const entry: FormulaCorrespondence = { correspondence_class: 'not_exact_replacement', reason, replaced_from: null, replaced_to: null }; return [correspondenceHeading(entry), correspondenceDetail(entry)]; }),
    correspondenceHeading({ correspondence_class: 'not_evaluated', reason: 'formula_unparsed', replaced_from: null, replaced_to: null }),
    text(renderToStaticMarkup(<FormulaCorrespondencePanel report={{ ...report, limitations: [] }}/>)),
    text(renderToStaticMarkup(<SourceAnalogNote report={report} baseFormula="LiFePO4" materialId={10}/>)),
  ].join(' ').toLowerCase();
  for (const term of forbidden) expect(strings).not.toContain(term);
});
