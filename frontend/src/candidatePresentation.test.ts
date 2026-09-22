import { expect, it } from 'vitest';
import type { Candidate } from './api';
import { factorExplanation, presentCandidate } from './candidatePresentation';

const candidate: Candidate = {
  material_id: 6, mp_id: 'mp-19028', pretty_formula: 'Na3Fe(PO4)2', formula: 'Na3Fe(PO4)2',
  discovery_score: 125, score_breakdown: { family_bonus: 40, substitution_bonus: 35 },
  discovery_path: ['alkali_substitution', 'shared_chemistry', 'phosphate_related', 'oxide_related'],
  explanation: 'Na3Fe(PO4)2: composition-heuristic relationship; shares Fe, O, P chemistry with LiFePO4; composition-level alkali-substitution hypothesis from Li to Na; a substitution mechanism is not validated; both materials contain phosphorus and oxygen; structural framework similarity is not validated; both materials contain oxygen; oxide structure similarity is not validated.',
  substitution_path: null,
};

it('summarizes a composition hypothesis without asserting structural preservation or duplicating element overlap', () => {
  const presentation = presentCandidate(candidate, 'LiFePO4');
  expect(presentation.hypothesis).toContain('alkali substitution from Li to Na');
  expect(presentation.hypothesis).toContain('Both contain Fe, O, P');
  expect(presentation.hypothesis).not.toContain('framework');
  expect(presentation.signals.map(signal => signal.key)).toEqual(['alkali_substitution', 'shared_chemistry']);
  expect(presentation.caveats).toContain('A shared structural framework has not been validated.');
});

it('falls back to an honest generic hypothesis when no structured relationship is available', () => {
  const presentation = presentCandidate({ ...candidate, discovery_path: [], explanation: 'A candidate.' }, 'LiFePO4');
  expect(presentation.hypothesis).toContain('composition-level candidate');
  expect(presentation.caveats).toContain('These composition-level signals do not confirm a structural relationship.');
  expect(factorExplanation('unknown_rule', candidate, { avoid_element: null, prefer_element: null })).toContain('Backend scoring factor');
});
