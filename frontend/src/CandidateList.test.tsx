import { expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import type { CandidateResponse, MaterialDetail } from './api';
import { CandidateList } from './CandidateList';

const detail: MaterialDetail = {
  id: 5, mp_id: 'mp-19017', formula: 'LiFePO4', pretty_formula: 'LiFePO4', material_type: null,
  band_gap: null, energy_above_hull: null, formation_energy_per_atom: null, density: null,
  is_stable: true, source: 'materials_project', elements: [],
};
const result: CandidateResponse = {
  material_id: 5, base_formula: 'LiFePO4',
  discovery_goal: { avoid_element: 'Li', prefer_element: 'Na' },
  constraint_policy: { avoid_element: 'soft_penalty', prefer_element: 'soft_bonus' },
  discovery_warnings: [],
  candidates: [
    { material_id: 6, mp_id: 'mp-19028', formula: 'Na3Fe(PO4)2', pretty_formula: null,
      discovery_score: 25, score_breakdown: { avoided_element_removed_bonus: 25 },
      discovery_path: ['avoided_element_removed', 'preferred_element'], explanation: 'Unchanged API explanation.', substitution_path: null },
    { material_id: 2, mp_id: null, formula: 'LiFe(PO3)4', pretty_formula: null,
      discovery_score: -10, score_breakdown: { avoided_element_present_penalty: -50 },
      discovery_path: ['contains_avoided_element'], explanation: 'Original scientific text.', substitution_path: null },
  ],
};
const noop = () => {};

it('keeps backend order and explains a negative rule score without judging scientific value', () => {
  const html = renderToStaticMarkup(<CandidateList select={noop} detail={detail} avoid="Li" setAvoid={noop} prefer="Na" setPrefer={noop} result={result} candidateError="" candidateLoading={false} searchCandidates={noop}/>);
  expect(html.indexOf('mp-19028')).toBeLessThan(html.indexOf('source ID unavailable'));
  expect(html).toContain('Contains Li (avoided)');
  expect(html).toContain('-10');
  expect(html).toContain('Full discovery explanation');
  expect(html).toContain('Discover candidates');
  const negativeFirst = renderToStaticMarkup(<CandidateList select={noop} detail={detail} avoid="Li" setAvoid={noop} prefer="Na" setPrefer={noop} result={{ ...result, candidates: [...result.candidates].reverse() }} candidateError="" candidateLoading={false} searchCandidates={noop}/>);
  expect(negativeFirst).toContain('not negative scientific value');
});

it('shows missing optional candidate context without inventing a signal or a factor', () => {
  const missing: CandidateResponse = {
    ...result, candidates: [{ ...result.candidates[1], discovery_path: [], score_breakdown: {}, explanation: '' }],
  };
  const html = renderToStaticMarkup(<CandidateList select={noop} detail={detail} avoid="" setAvoid={noop} prefer="" setPrefer={noop} result={missing} candidateError="" candidateLoading={false} searchCandidates={noop}/>);
  expect(html).toContain('source ID unavailable');
  expect(html).toContain('No individual matching signals were provided.');
  expect(html).toContain('No factor breakdown was provided.');
});
