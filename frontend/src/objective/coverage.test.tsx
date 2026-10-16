import { expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ObjectiveResults, modeHint } from './ObjectiveInvestigation';
import { ObjectiveCoveragePanel, avoidChainText, avoidMaterialText, materialAvoidanceLabel, preferText } from './ObjectiveCoverage';
import type { ObjectiveCoverage, ObjectiveResponse } from './contract';
import cs01Fixture from './fixtures/cs01-objective-explore-coverage-v1.json';

// Frozen production Case Study 01 response plus backend-computed coverage (contract v1).
const cs01 = cs01Fixture as unknown as ObjectiveResponse;
const coverage = cs01.objective_coverage as ObjectiveCoverage;
const text = (html: string) => html.replace(/<[^>]+>/g, '').replace(/&#x27;/g, "'").replace(/\s+/g, ' ');

it('renders the golden Case Study 01 coverage exactly from backend values', () => {
  const html = text(renderToStaticMarkup(<ObjectiveCoveragePanel coverage={coverage}/>));
  expect(html).toContain('Prefer Na — Represented in 5 of 5 evaluated returned ranked materials.');
  expect(html).toContain('Prefer K — Not represented in 5 evaluated returned ranked materials.');
  expect(html).toContain('Avoid Li (ranked materials) — Not observed in 5 evaluated returned ranked materials.');
  expect(html).toContain('Avoid Co (ranked materials) — Not observed in 5 evaluated returned ranked materials.');
  expect(html).toContain('Avoid Li (returned chains, source excluded) — Present in 3 of 5 returned chains.');
  expect(html).toContain('Avoid Co (returned chains, source excluded) — Not observed in 5 evaluated returned chains.');
  expect(html).toContain('Returned chains 3, 4, 5 include materials containing avoided element Li (source material excluded).');
  expect(html).toContain('The source material (local ID 5) contains Li. It is excluded from pathway counts.');
  expect(html).toContain(coverage.avoid_policy_explanation);
  expect(html).toContain('Not evaluated in this summary: elements to retain, target composition family.');
  for (const limitation of coverage.limitations) expect(html).toContain(limitation);
});

it('uses text status labels, never colour alone, and never claims satisfaction', () => {
  const html = renderToStaticMarkup(<ObjectiveCoveragePanel coverage={coverage}/>);
  for (const label of ['Represented', 'Not represented', 'Not observed', 'Present']) {
    expect(html).toContain(`<span class="objectiveCoverageStatus">${label}</span>`);
  }
  expect(html.toLowerCase()).not.toContain('satisf');
  expect(html.toLowerCase()).not.toContain('final candidate');
});

it('links the warning to the affected returned chains', () => {
  const html = renderToStaticMarkup(<ObjectiveCoveragePanel coverage={coverage}/>);
  for (const position of [3, 4, 5]) expect(html).toContain(`href="#objective-path-${position}"`);
  expect(html).not.toContain('href="#objective-path-1"');
});

it('marks avoided-element materials only in the chains the backend flags (#55)', () => {
  const html = renderToStaticMarkup(<ObjectiveResults result={cs01} submitted="{}"/>);
  const paths = html.split('class="objectivePath"').slice(1);
  expect(paths).toHaveLength(5);
  paths.slice(0, 2).forEach(path => expect(path).not.toContain('objectiveAvoidance'));
  paths.slice(2).forEach(path => {
    expect(path).toContain('<span class="objectiveAvoidance">Contains avoided element: Li</span>');
    expect(text(path)).toMatch(/Contains avoided element in intermediate material \(local ID [123]\): Li\. Source material excluded\./);
  });
  // The source (LiFePO4) is never flagged even though it contains Li.
  paths.forEach(path => expect(path.split('Source</span>')[1]?.startsWith('<span class="objectiveAvoidance">')).toBe(false));
});

it('places the coverage panel between search scope and the result columns', () => {
  const html = renderToStaticMarkup(<ObjectiveResults result={cs01} submitted="{}"/>);
  expect(html.indexOf('Search scope')).toBeLessThan(html.indexOf('Objective coverage in returned results'));
  expect(html.indexOf('Objective coverage in returned results')).toBeLessThan(html.indexOf('<h3>Ranked materials</h3>'));
});

it('shows an explicit fallback when the backend predates objective coverage', () => {
  const legacy: ObjectiveResponse = { ...cs01, objective_coverage: undefined };
  const html = text(renderToStaticMarkup(<ObjectiveResults result={legacy} submitted="{}"/>));
  expect(html).toContain('Objective coverage is not available from this backend version.');
  expect(html).not.toContain('Represented');
  expect(html).not.toContain('Contains avoided element');
});

it('distinguishes incomplete coverage from confirmed absence', () => {
  expect(preferText({ element: 'K', unit: 'returned_ranked_materials', containing_count: 0, evaluated_count: 4, not_evaluated_count: 1, total_count: 5, status: 'not_represented', coverage_complete: false }))
    .toBe('Prefer K — Not represented in 4 evaluated returned ranked materials. 1 material not evaluated (formula missing or not parseable).');
  expect(avoidMaterialText({ element: 'Li', unit: 'returned_ranked_materials', containing_count: 0, evaluated_count: 0, not_evaluated_count: 2, total_count: 2, status: 'not_evaluated', coverage_complete: false }))
    .toBe('Avoid Li (ranked materials) — Not evaluated: no returned ranked material could be evaluated.');
  expect(avoidChainText({ element: 'Li', unit: 'returned_chains_excluding_source', containing_chain_count: 1, evaluated_chain_count: 3, not_evaluated_chain_count: 2, total_chain_count: 5, chain_positions: [2], status: 'present', coverage_complete: false }))
    .toBe('Avoid Li (returned chains, source excluded) — Present in 1 of 5 returned chains. 2 chains not evaluated (formula missing or not parseable).');
  expect(materialAvoidanceLabel({ chain_position: 1, materials_with_avoided_elements: [], not_evaluated_material_ids: [9] }, 9)).toBe('Composition not evaluated');
});

it('renders empty results and objectives without Avoid/Prefer without inventing statuses', () => {
  const empty: ObjectiveCoverage = { ...coverage, returned_ranked_material_count: 0, returned_chain_count: 0, preferred_elements: [], avoided_elements_in_ranked_materials: [], avoided_elements_in_returned_chains: [], chain_avoidance: [], terms_not_evaluated: [] };
  const html = text(renderToStaticMarkup(<ObjectiveCoveragePanel coverage={empty}/>));
  expect(html).toContain('Counts 0 returned ranked materials and 0 returned chains.');
  expect(html).toContain('No preferred or avoided elements were requested.');
  expect(html).not.toMatch(/Represented|Not observed|Present in/);
});

it('shows the backend Strict explanation and the unevaluated-source wording', () => {
  const strict: ObjectiveCoverage = { ...coverage, mode: 'strict', avoid_policy_explanation: 'Strict backend explanation.', source_material: { material_id: 5, excluded_from_counts: true, avoided_elements_present: null } };
  const html = text(renderToStaticMarkup(<ObjectiveCoveragePanel coverage={strict}/>));
  expect(html).toContain('Strict backend explanation.');
  expect(html).toContain('The source material (local ID 5) composition was not evaluated. It is excluded from pathway counts.');
});

it('gives Balanced and Exploratory distinct, accurate form hints', () => {
  expect(modeHint.balanced).not.toBe(modeHint.exploratory);
  expect(modeHint.exploratory).toContain('smaller score penalty than Balanced');
  for (const mode of ['balanced', 'exploratory'] as const) {
    expect(modeHint[mode]).toContain('soft preference');
    expect(modeHint[mode]).toContain('may still contain them');
  }
  expect(modeHint.strict).toContain('The source material is exempt.');
});
