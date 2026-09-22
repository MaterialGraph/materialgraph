import { expect, it } from 'vitest';
import type { Candidate } from './api';
import { factorExplanation, factorLabel, presentCandidate } from './candidatePresentation';

const candidate: Candidate = {
  material_id: 6, mp_id: 'mp-19028', pretty_formula: 'Na3Fe(PO4)2', formula: 'Na3Fe(PO4)2',
  discovery_score: 125, score_breakdown: { family_bonus: 40, substitution_bonus: 35 },
  discovery_path: ['alkali_substitution', 'shared_chemistry', 'phosphate_related', 'oxide_related'],
  explanation: 'Na3Fe(PO4)2: composition-heuristic relationship; shares Fe, O, P chemistry with LiFePO4; composition-level alkali-substitution hypothesis from Li to Na; a substitution mechanism is not validated; both materials contain phosphorus and oxygen; structural framework similarity is not validated; both materials contain oxygen; oxide structure similarity is not validated.',
  substitution_path: null,
};

it('summarizes a composition hypothesis without asserting structural preservation or duplicating element overlap', () => {
  const presentation = presentCandidate(candidate, 'LiFePO4');
  expect(presentation.hypothesis).toContain('possible Li-to-Na alkali substitution');
  expect(presentation.hypothesis).toContain('Shared elements: Fe, O, P');
  expect(presentation.hypothesis).toContain('based on composition alone');
  expect(presentation.hypothesis).not.toContain('structural');
  expect(presentation.signals.map(signal => signal.key)).toEqual(['alkali_substitution', 'shared_chemistry']);
  expect(presentation.caveats).toEqual([
    'A substitution mechanism has not been demonstrated.',
    'Composition-based signals do not establish structural similarity, synthesis feasibility, or performance.',
  ]);
});

it('falls back to an honest generic hypothesis when no structured relationship is available', () => {
  const presentation = presentCandidate({ ...candidate, discovery_path: [], explanation: 'A candidate.' }, 'LiFePO4');
  expect(presentation.hypothesis).toContain('Composition-based rules');
  expect(presentation.caveats).toContain('Composition-based signals do not establish structural similarity, synthesis feasibility, or performance.');
  expect(factorExplanation('unknown_rule', candidate, { avoid_element: null, prefer_element: null })).toContain('A scoring rule');
  expect(factorLabel('avoided_element_present_penalty')).toBe('Avoided element present');
});

it('uses returned preference signals to label absent and present elements', () => {
  const goal = { avoid_element: 'Li', prefer_element: 'Na' };
  const absent = presentCandidate({ ...candidate, discovery_path: ['avoided_element_removed', 'preferred_element'] }, 'LiFePO4', goal);
  expect(absent.signals.map(signal => signal.label)).toEqual(['Li absent', 'Na present']);
  const present = presentCandidate({ ...candidate, discovery_path: ['contains_avoided_element'] }, 'LiFePO4', goal);
  expect(present.signals.map(signal => signal.label)).toEqual(['Contains Li (avoided)']);
});

it('does not invent element identities when optional preference context is missing', () => {
  const presentation = presentCandidate({ ...candidate, mp_id: null, pretty_formula: null, explanation: '', discovery_path: ['preferred_element'] }, '');
  expect(presentation.signals).toEqual([]);
  expect(presentation.hypothesis).toContain('Composition-based');
});
