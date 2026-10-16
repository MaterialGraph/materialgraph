import { expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { ObjectiveResults, modeHint } from './ObjectiveInvestigation';
import { ObjectiveCoveragePanel, avoidChainCell, avoidMaterialCell, materialAvoidanceLabel, preferCell } from './ObjectiveCoverage';
import { CompareTray } from '../comparison/CompareTray';
import type { ObjectiveCoverage, ObjectiveResponse } from './contract';
import cs01Fixture from './fixtures/cs01-objective-explore-coverage-v1.json';

// Frozen production Case Study 01 response plus backend-computed coverage (contract v1).
const cs01 = cs01Fixture as unknown as ObjectiveResponse;
const coverage = cs01.objective_coverage as ObjectiveCoverage;
const text = (html: string) => html.replace(/<[^>]+>/g, ' ').replace(/&#x27;/g, "'").replace(/\s+/g, ' ');
const rowsOf = (html: string) => html.split('<tr>').slice(2).map(text);

it('renders one matrix row per requested element with backend counts (golden Case Study 01)', () => {
  const html = renderToStaticMarkup(<ObjectiveCoveragePanel coverage={coverage}/>);
  expect(html).toContain('<table class="coverageTable">');
  expect(text(html)).toContain('Returned ranked materials (5)');
  expect(text(html)).toContain('Returned chains (5, source excluded)');
  const rows = rowsOf(html);
  expect(rows).toHaveLength(4);
  expect(rows[0]).toMatch(/Na Prefer ✓ Represented 5\/5 — Not assessed for chains/);
  expect(rows[1]).toMatch(/K Prefer ✕ Not represented 0\/5 — Not assessed for chains/);
  expect(rows[2]).toMatch(/Li Avoid – Not observed 0\/5 ⚠ Present 3\/5 chains 3 4 5/);
  expect(rows[3]).toMatch(/Co Avoid – Not observed 0\/5 – Not observed 0\/5/);
});

it('keeps backend explanation, source disclosure, unevaluated terms and limitations', () => {
  const html = text(renderToStaticMarkup(<ObjectiveCoveragePanel coverage={coverage}/>));
  expect(html).toContain(coverage.avoid_policy_explanation);
  expect(html).toContain('Source material (local ID 5) contains Li — excluded from chain counts.');
  expect(html).toContain('Not evaluated in this summary: elements to retain, target composition family.');
  for (const limitation of coverage.limitations) expect(html).toContain(limitation);
});

it('uses text labels and tones, never colour alone, and never claims satisfaction', () => {
  const html = renderToStaticMarkup(<ObjectiveCoveragePanel coverage={coverage}/>);
  expect(html).toContain('class="coverageStatus coverageStatus-positive"');
  expect(html).toContain('class="coverageStatus coverageStatus-caution"');
  for (const label of ['Represented', 'Not represented', 'Not observed', 'Present']) expect(html).toContain(label);
  expect(html.toLowerCase()).not.toContain('satisf');
  expect(html.toLowerCase()).not.toContain('final candidate');
});

it('links the Present chain cell to the affected returned chains only', () => {
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
  expect(preferCell({ element: 'K', unit: 'returned_ranked_materials', containing_count: 0, evaluated_count: 4, not_evaluated_count: 1, total_count: 5, status: 'not_represented', coverage_complete: false }))
    .toEqual({ icon: '✕', label: 'Not represented', tone: 'neutral', count: '0/4', notEvaluated: 1 });
  expect(avoidMaterialCell({ element: 'Li', unit: 'returned_ranked_materials', containing_count: 0, evaluated_count: 0, not_evaluated_count: 2, total_count: 2, status: 'not_evaluated', coverage_complete: false }))
    .toEqual({ icon: '?', label: 'Not evaluated', tone: 'unknown', count: null, notEvaluated: 2 });
  expect(avoidChainCell({ element: 'Li', unit: 'returned_chains_excluding_source', containing_chain_count: 1, evaluated_chain_count: 3, not_evaluated_chain_count: 2, total_chain_count: 5, chain_positions: [2], status: 'present', coverage_complete: false }))
    .toEqual({ icon: '⚠', label: 'Present', tone: 'caution', count: '1/5', notEvaluated: 2 });
  const partial: ObjectiveCoverage = { ...coverage, preferred_elements: [{ ...coverage.preferred_elements[1], evaluated_count: 4, not_evaluated_count: 1, coverage_complete: false }] };
  expect(text(renderToStaticMarkup(<ObjectiveCoveragePanel coverage={partial}/>))).toContain('Not represented 0/4 +1 not evaluated');
  expect(materialAvoidanceLabel({ chain_position: 1, materials_with_avoided_elements: [], not_evaluated_material_ids: [9] }, 9)).toBe('Composition not evaluated');
});

it('renders empty results and objectives without Avoid/Prefer without inventing statuses', () => {
  const empty: ObjectiveCoverage = { ...coverage, returned_ranked_material_count: 0, returned_chain_count: 0, preferred_elements: [], avoided_elements_in_ranked_materials: [], avoided_elements_in_returned_chains: [], chain_avoidance: [], terms_not_evaluated: [] };
  const html = text(renderToStaticMarkup(<ObjectiveCoveragePanel coverage={empty}/>));
  expect(html).toContain('No preferred or avoided elements were requested.');
  expect(html).not.toMatch(/Represented|Not observed|Present/);
});

it('shows the backend Strict explanation and the unevaluated-source wording', () => {
  const strict: ObjectiveCoverage = { ...coverage, mode: 'strict', avoid_policy_explanation: 'Strict backend explanation.', source_material: { material_id: 5, excluded_from_counts: true, avoided_elements_present: null } };
  const html = text(renderToStaticMarkup(<ObjectiveCoveragePanel coverage={strict}/>));
  expect(html).toContain('Strict backend explanation.');
  expect(html).toContain('Source material (local ID 5): composition not evaluated; excluded from chain counts.');
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

it('keeps each compare-tray selection and its Remove button on one row', () => {
  const html = renderToStaticMarkup(<CompareTray id="t" selected={[
    { id: 6, formula: 'Na3Fe(PO4)2', mpId: 'mp-19028', role: 'Ranked material · Included in returned composition chains 1, 2, 3, 4, 5' },
    { id: 7, formula: 'Na3Fe3(PO4)4', mpId: null, role: 'Ranked material' },
  ]} remove={() => {}} compare={() => {}}/>);
  const items = html.split('<li>').slice(1);
  expect(items).toHaveLength(2);
  items.forEach(item => expect(item).toMatch(/^<span>.*<\/span><button type="button"[^>]*>Remove<\/button><\/li>/));
});
