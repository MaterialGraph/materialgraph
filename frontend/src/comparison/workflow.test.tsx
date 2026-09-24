// @vitest-environment jsdom
import { act, useState } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { CandidateResponse, MaterialDetail } from '../api';
import { CandidateList } from '../CandidateList';
import { ObjectiveResults } from '../objective/ObjectiveInvestigation';
import type { ObjectiveResponse } from '../objective/contract';
import { buildObjectiveRequest, initialDraft } from '../objective/request';
import { WorkflowComparison } from './PropertyComparison';
import { discoveryLaunch, objectiveLaunch, objectiveRole, toggleComparisonSelection, type ComparisonLaunchContext, type SelectedMaterial } from './launch';
import { CompareTray } from './CompareTray';
import { App } from '../main';
import { serializeComparison } from './routing';

const noop = () => {};
const source: MaterialDetail = { id: 5, mp_id: 'mp-19017', formula: 'LiFePO4', pretty_formula: 'LiFePO4', source: 'materials_project', material_type: null, band_gap: 3, energy_above_hull: 0, formation_energy_per_atom: -2, density: 3, is_stable: true, elements: [] };
const discovery: CandidateResponse = {
  material_id: 5, base_formula: 'LiFePO4', discovery_goal: { avoid_element: 'Li', prefer_element: 'Na' },
  constraint_policy: { avoid_element: 'soft_penalty', prefer_element: 'soft_bonus' }, discovery_warnings: [],
  candidates: [6, 7, 8, 9].map(id => ({ material_id: id, mp_id: `mp-${id}`, formula: `Na${id}FePO4`, pretty_formula: null, discovery_score: 100 - id, score_breakdown: {}, discovery_path: [], explanation: '', substitution_path: null })),
};
const submitted = buildObjectiveRequest({ ...initialDraft, avoid: 'Li', prefer: 'Na', preserve: 'Fe P O', family: 'phosphate' });
const objective: ObjectiveResponse = {
  material_id: 5, base_formula: 'LiFePO4', objective: submitted.objective, mode: submitted.mode,
  objective_policy: { stable_materials: '', stability_scope: '', stability_evidence_policy: '', unknown_stability_evidence: '', lower_criticality: '', unknown_criticality_evidence: '' },
  constraint_policy: { avoid_elements: 'soft_penalty', prefer_elements: 'soft_bonus', hard_rejection_scope: 'none' },
  search_metadata: { search_policy: '', requested_result_limit: 5, expansion_limit_per_material: 6, search_state_budget: 200, expanded_state_count: 5, generated_chain_count: 2, returned_chain_count: 1, search_truncated: false, result_truncated: false, scientific_completeness_guaranteed: false },
  ranked_candidates: [6, 8, 9].map(id => ({ material_id: id, formula: `Na${id}FePO4`, score: 127.25, reasons: [], warnings: [] })),
  chains: [{ hop_count: 2, materials: [5, 1, 6].map(id => ({ material_id: id, mp_id: `mp-${id}`, formula: `Formula${id}`, pretty_formula: null })), transitions: [], chain_reason: '', scientific_usefulness_score: null, score_breakdown: null, usefulness_reason: null }], warnings: [], explanation: '',
};

let host: HTMLDivElement;
let root: Root;
beforeEach(() => { host = document.createElement('div'); document.body.append(host); root = createRoot(host); (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true; });
afterEach(async () => { await act(async () => root.unmount()); host.remove(); history.replaceState(null,'','/'); vi.unstubAllGlobals(); });
async function render(view: React.ReactNode) { await act(async () => root.render(view)); }
async function click(button: Element | null) { expect(button).not.toBeNull(); await act(async () => (button as HTMLButtonElement).click()); }
function selectButtons() { return [...host.querySelectorAll<HTMLButtonElement>('.compareSelect')]; }
function compareButton() { return [...host.querySelectorAll<HTMLButtonElement>('.compareTray > button')][0]; }

it('keeps Discovery inspection separate from comparison, enforces the limit, and launches from applied response context', async () => {
  let inspected = 0;
  let launch: ComparisonLaunchContext | null = null;
  function Discovery() {
    const [draft, setDraft] = useState('Li');
    return <CandidateList select={id => { inspected = id; }} detail={source} avoid={draft} setAvoid={setDraft} prefer="Na" setPrefer={noop} result={discovery} candidateError="" candidateLoading={false} searchCandidates={noop} onCompare={value => { launch = value; }}/>;
  }
  await render(<Discovery/>);
  expect(host.querySelector('.discoveryRail > .discoveryList')).not.toBeNull();
  expect(host.querySelector('.discoveryRail > .compareTray')).not.toBeNull();
  expect(host.textContent).toContain('0 of 3 selected');
  expect(compareButton().disabled).toBe(true);
  await click(host.querySelectorAll('.candidateRow')[1]);
  expect(host.textContent).toContain('0 of 3 selected');
  expect(host.querySelectorAll('.candidateRow.active')).toHaveLength(1);
  await click(selectButtons()[0]);
  expect(host.querySelector('.candidateRow.active')?.textContent).toContain('Na7FePO4');
  expect(compareButton().disabled).toBe(true);
  await click(selectButtons()[1]);
  expect(host.textContent).toContain('2 of 3 selected');
  expect(compareButton().disabled).toBe(false);
  await click(selectButtons()[2]);
  expect(selectButtons()[3].disabled).toBe(true);
  expect(selectButtons()[3].getAttribute('aria-describedby')).toBe('discovery-selection-limit');
  expect(host.textContent).toContain('Maximum 3 candidates reached for comparison.');
  await click(host.querySelector('.compareTray li button'));
  expect(selectButtons()[3].disabled).toBe(false);
  expect(host.querySelectorAll('.candidateRow')).toHaveLength(4);
  await click(selectButtons()[3]);
  expect(compareButton().disabled).toBe(false);
  await click(host.querySelector('input'));
  await act(async () => { const input = host.querySelector('input')!; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, 'Co'); input.dispatchEvent(new Event('input', { bubbles: true })); });
  await click(compareButton());
  expect(launch).toMatchObject({ sourceMaterialId: 5, originWorkflow: 'discovery', selectedMaterials: [{ id: 7 }, { id: 8 }, { id: 9 }] });
  expect((launch as ComparisonLaunchContext | null)?.investigationContext).toContain('Applied Avoid: Li');
  expect(inspected).toBe(0);
});

it('derives Objective roles from actual returned chains, never selects chain-only members, and keeps workflows isolated', async () => {
  let discoverySet: SelectedMaterial[] = [];
  let objectiveSet: SelectedMaterial[] = [];
  let launched: ComparisonLaunchContext | null = null;
  function Harness() {
    const [discoverySelected, setDiscoverySelected] = useState<SelectedMaterial[]>([]);
    const [objectiveSelected, setObjectiveSelected] = useState<SelectedMaterial[]>([]);
    const [showObjective, setShowObjective] = useState(false);
    discoverySet = discoverySelected; objectiveSet = objectiveSelected;
    return <><button id="switch" onClick={() => setShowObjective(value => !value)}>Switch</button>
      <div hidden={showObjective}><CandidateList select={noop} detail={source} avoid="Li" setAvoid={noop} prefer="Na" setPrefer={noop} result={discovery} candidateError="" candidateLoading={false} searchCandidates={noop} onCompare={value => { launched = value; }}/></div>
      <div hidden={!showObjective}><ObjectiveResults result={objective} submitted={JSON.stringify(submitted)} comparison={objectiveSelected} toggle={material => setObjectiveSelected(previous => toggleComparisonSelection(previous, material))}/>
        <CompareTray id="objective-selection-limit" selected={objectiveSelected} remove={id => setObjectiveSelected(previous => previous.filter(item => item.id !== id))} compare={() => { launched = objectiveLaunch(objective, submitted, objectiveSelected); }}/></div>
      <button id="discovery-state" onClick={() => setDiscoverySelected(previous => toggleComparisonSelection(previous, { id: 7, formula: 'Na7FePO4', mpId: 'mp-7', role: 'Discovery candidate' }))}>Select Discovery</button></>;
  }
  await render(<Harness/>);
  await click(host.querySelector('#discovery-state'));
  await click(host.querySelector('#switch'));
  expect(objectiveSet).toHaveLength(0);
  expect(host.querySelectorAll('.objectiveCandidate .compareSelect')).toHaveLength(3);
  const controls = [...host.querySelectorAll<HTMLButtonElement>('.objectiveCandidate .compareSelect')];
  await click(controls[0]); await click(controls[1]);
  expect(objectiveSet.map(item => item.id)).toEqual([6, 8]);
  expect(objectiveSet[0].role).toContain('Included in returned composition chain 1');
  expect(objectiveSet[1].role).toBe('Ranked material');
  expect(objectiveSet.some(item => item.id === 1)).toBe(false);
  expect(objectiveRole(objective, 9)).toBe('Ranked material');
  expect(discoverySet.map(item => item.id)).toEqual([7]);
  await click(host.querySelectorAll('.compareTray > button')[1]);
  expect(launched).toMatchObject({ sourceMaterialId: 5, originWorkflow: 'objective', selectedMaterials: [{ id: 6 }, { id: 8 }] });
  expect((launched as ComparisonLaunchContext | null)?.investigationContext).toContain('Submitted mode: balanced');
  await click(host.querySelector('#switch'));
  expect(discoverySet.map(item => item.id)).toEqual([7]);
});

it('keeps an existing selection at the limit and makes room after removal', () => {
  const items = [6, 7, 8, 9].map(id => ({ id, formula: `Na${id}FePO4`, mpId: null, role: 'Ranked material' }));
  const three = items.slice(0, 3).reduce(toggleComparisonSelection, [] as SelectedMaterial[]);
  expect(toggleComparisonSelection(three, items[3])).toEqual(three);
  expect(toggleComparisonSelection(toggleComparisonSelection(three, items[0]), items[3]).map(item => item.id)).toEqual([7, 8, 9]);
  expect(objectiveRole({ ...objective, chains: [] }, 6)).toBe('Ranked material');
  expect(discoveryLaunch(discovery, three).sourceMaterialId).toBe(5);
});

it('loads fresh detail records for a launched comparison instead of using discovery properties', async () => {
  const requests: string[] = [];
  vi.stubGlobal('fetch', vi.fn(async (url: string) => {
    requests.push(url);
    const id = Number(url.match(/materials\/(\d+)\/detail/)?.[1]);
    return { ok: true, json: async () => ({ ...source, id, band_gap: id === 5 ? 3 : 0 }) };
  }));
  await render(<WorkflowComparison launch={discoveryLaunch(discovery, [6, 7].map(id => ({ id, formula: `Na${id}FePO4`, mpId: `mp-${id}`, role: 'Discovery candidate' })))}/>);
  expect(requests).toEqual(['/api/v1/materials/5/detail', '/api/v1/materials/6/detail', '/api/v1/materials/7/detail']);
  expect(host.textContent).toContain('0');
  expect(host.textContent).toContain('Discovery candidate');
});

it('returns to the originating workflow with its selection and focus intact', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url: string) => {
    if (url.includes('discovery/candidates')) return { ok: true, json: async () => discovery };
    if (url.includes('/materials?')) return { ok: true, json: async () => [source] };
    const id = Number(url.match(/materials\/(\d+)\/detail/)?.[1]);
    return { ok: true, json: async () => ({ ...source, id }) };
  }));
  await render(<App/>);
  await click(host.querySelector('.materialList button'));
  await click(host.querySelector('.filters button'));
  await click(selectButtons()[0]); await click(selectButtons()[1]);
  await click(compareButton());
  expect(host.querySelector('.layout')?.hasAttribute('hidden')).toBe(true);
  expect(host.textContent).toContain('Comparison from Candidate Discovery');
  expect(document.activeElement?.textContent).toBe('Comparison from Candidate Discovery');
  await click(host.querySelector('.workflowComparison > button'));
  await act(async () => { await new Promise(resolve => requestAnimationFrame(resolve)); });
  expect(host.querySelector('.layout')?.hasAttribute('hidden')).toBe(false);
  expect(host.textContent).toContain('2 of 3 selected');
  expect(document.activeElement?.querySelector('.discovery')).not.toBeNull();
});

it('launches Objective from its submitted request and restores only its own selection on return', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url: string) => {
    if (url.includes('/discovery/objective/explore')) return { ok: true, json: async () => objective };
    if (url.includes('/materials?')) return { ok: true, json: async () => [source] };
    const id = Number(url.match(/materials\/(\d+)\/detail/)?.[1]);
    return { ok: true, json: async () => ({ ...source, id }) };
  }));
  await render(<App/>);
  await click(host.querySelector('.materialList button'));
  await click(host.querySelector('.objectiveForm button[type="submit"]'));
  expect(host.querySelector('.objectiveColumns > section:first-child > .compareTray')).not.toBeNull();
  await act(async () => { const input = host.querySelector<HTMLInputElement>('.objectiveForm input')!; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, 'Co'); input.dispatchEvent(new Event('input', { bubbles: true })); });
  const objectiveControls = [...host.querySelectorAll<HTMLButtonElement>('.objectiveCandidate .compareSelect')];
  expect(objectiveControls).toHaveLength(3);
  await click(objectiveControls[0]); await click(objectiveControls[1]);
  expect(host.textContent).toContain('Included in returned composition chain 1');
  expect(host.textContent).toContain('2 of 3 selected');
  await click(host.querySelector('.objectiveInvestigation .compareTray > button'));
  expect(host.textContent).toContain('Comparison from Objective Investigation');
  expect(host.textContent).toContain('Submitted mode: balanced');
  expect(host.querySelector('.comparisonContext')?.textContent).toContain('Avoid: none');
  expect(host.querySelector('.comparisonContext')?.textContent).not.toContain('Avoid: Co');
  expect(host.textContent).toContain('Ranked material · Included in returned composition chain 1');
  await click(host.querySelector('.workflowComparison > button'));
  await act(async () => { await new Promise(resolve => requestAnimationFrame(resolve)); });
  expect(host.querySelector('.objectiveInvestigation .compareTray')?.textContent).toContain('2 of 3 selected');
  expect(host.querySelector('.discovery .compareTray')).toBeNull();
});

it('cold-restores Discovery with fresh details and prefilled inputs without rerunning research', async () => {
  const calls: string[] = [];
  history.replaceState(null,'',serializeComparison({source:5,candidates:[6,8],workflow:'discovery',context:{kind:'discovery',avoid_element:'Li',prefer_element:'Na',limit:10,include_substitution_paths:false}}));
  vi.stubGlobal('fetch',vi.fn(async (url: string) => { calls.push(url); if (url.includes('/materials?')) return {ok:true,json:async()=>[source]}; const id=Number(url.match(/materials\/(\d+)\/detail/)?.[1]); return {ok:true,json:async()=>({...source,id,band_gap:id === 6 ? 0 : 4})}; }));
  await render(<App/>);
  expect(calls.filter(url=>url.includes('/detail'))).toEqual(['/api/v1/materials/5/detail','/api/v1/materials/6/detail','/api/v1/materials/8/detail']);
  expect(calls.some(url=>url.includes('/discovery/'))).toBe(false);
  expect(host.textContent).toContain('Property values are fetched again and may have changed');
  expect(host.textContent).toContain('current result membership has not been checked');
  expect(host.querySelector('.comparisonContext')?.textContent).toContain('Applied Avoid: Li');
  await click(host.querySelector('.workflowComparison > button'));
  expect(host.querySelector<HTMLInputElement>('.filters input')?.value).toBe('Li');
  expect(host.querySelector('.discovery .compareTray')).toBeNull();
  expect(host.textContent).toContain('No investigation results are contained in this link');
  expect(calls.some(url=>url.includes('/discovery/'))).toBe(false);
});

it('cold-restores Objective without prior roles and opens prefilled unsent request', async () => {
  history.replaceState(null,'',serializeComparison({source:5,candidates:[6,8],workflow:'objective',context:{kind:'objective',request:{...submitted,objective:{...submitted.objective,limit:7}}}}));
  const calls:string[]=[];
  vi.stubGlobal('fetch',vi.fn(async (url:string)=>{calls.push(url);if(url.includes('/materials?')) return {ok:true,json:async()=>[source]};const id=Number(url.match(/materials\/(\d+)\/detail/)?.[1]);return {ok:true,json:async()=>({...source,id})};}));
  await render(<App/>);
  expect(host.textContent).toContain('previous rank and chain membership unavailable');
  expect(host.textContent).not.toContain('Included in returned composition chain');
  expect(host.querySelector('.comparisonContext')?.textContent).toContain('"limit":5');
  await click(host.querySelector('.workflowComparison > button'));
  expect(host.querySelector<HTMLInputElement>('.objectiveForm input')?.value).toBe('Li');
  expect(host.querySelector<HTMLInputElement>('input[value="7"]')?.value).toBe('7');
  expect(host.querySelector('.objectiveCandidates')).toBeNull();
  expect(calls.some(url=>url.includes('/discovery/objective/'))).toBe(false);
});

it('treats source 404 as restoration failure and candidate 404 as material not found', async () => {
  history.replaceState(null,'',serializeComparison({source:5,candidates:[6,8],workflow:'discovery',context:null}));
  vi.stubGlobal('fetch',vi.fn(async (url:string)=>url.includes('/materials?') ? {ok:true,json:async()=>[]} : url.includes('/materials/5/') ? {ok:false,status:404} : {ok:true,json:async()=>({...source,id:6})}));
  await render(<App/>);
  expect(host.textContent).toContain('Source restoration failure');
  expect(host.querySelector('.propertyComparison')).toBeNull();
  expect(host.textContent).toContain('Investigation context unavailable');
});

it('shows invalid comparison without material fetches', async () => {
  history.replaceState(null,'','/?view=compare&v=1&source=05&candidates=6,8&workflow=discovery');
  const calls:string[]=[];
  vi.stubGlobal('fetch',vi.fn(async (url:string)=>{calls.push(url);return {ok:true,json:async()=>[]};}));
  await render(<App/>);
  expect(host.textContent).toContain('Invalid comparison link');
  expect(calls.some(url=>url.includes('/detail'))).toBe(false);
});

it('navigates in-app Back and Forward while preserving the actual Discovery selection', async () => {
  vi.stubGlobal('fetch',vi.fn(async (url:string)=>{
    if(url.includes('discovery/candidates')) return {ok:true,json:async()=>discovery};
    if(url.includes('/materials?')) return {ok:true,json:async()=>[source]};
    const id=Number(url.match(/materials\/(\d+)\/detail/)?.[1]);return {ok:true,json:async()=>({...source,id})};
  }));
  await render(<App/>);
  await click(host.querySelector('.materialList button'));
  await click(host.querySelector('.filters button'));
  await click(selectButtons()[0]);await click(selectButtons()[1]);await click(compareButton());
  const comparisonUrl=location.search;
  expect(comparisonUrl).toContain('view=compare');
  await act(async()=>{history.replaceState(null,'','/?material=5');dispatchEvent(new PopStateEvent('popstate'));});
  expect(host.querySelector('.layout')?.hasAttribute('hidden')).toBe(false);
  expect(host.querySelector('.discovery .compareTray')?.textContent).toContain('2 of 3 selected');
  await act(async()=>{history.replaceState(null,'',`/${comparisonUrl}`);dispatchEvent(new PopStateEvent('popstate'));});
  expect(host.querySelector('.workflowComparison')).not.toBeNull();
  expect(host.textContent).toContain('Discovery candidate');
});

it('copies the canonical absolute URL, reporting clipboard failure honestly', async () => {
  history.replaceState(null,'',serializeComparison({source:5,candidates:[6,8],workflow:'discovery',context:null}));
  vi.stubGlobal('fetch',vi.fn(async (url:string)=>url.includes('/materials?') ? {ok:true,json:async()=>[]} : {ok:true,json:async()=>({...source,id:Number(url.match(/materials\/(\d+)\/detail/)?.[1])})}));
  const copy=vi.fn(async()=>{});
  vi.stubGlobal('navigator',Object.assign(Object.create(navigator),{clipboard:{writeText:copy}}));
  await render(<App/>);
  await click([...host.querySelectorAll('.workflowComparison > button')][1]);
  expect(copy).toHaveBeenCalledWith(`${location.origin}${location.pathname}${location.search}`);
  expect(host.textContent).toContain('Comparison link copied.');
  copy.mockRejectedValueOnce(Error('Clipboard denied'));
  await click([...host.querySelectorAll('.workflowComparison > button')][1]);
  expect(host.textContent).toContain('Could not copy comparison link.');
});

it('retains missing candidate columns distinctly from Unknown properties', async () => {
  history.replaceState(null,'',serializeComparison({source:5,candidates:[6,8],workflow:'discovery',context:null}));
  vi.stubGlobal('fetch',vi.fn(async (url:string)=>{
    if(url.includes('/materials?')) return {ok:true,json:async()=>[]};
    if(url.includes('/materials/6/')) return {ok:false,status:404};
    if(url.includes('/materials/8/')) return {ok:false,status:503,headers:{get:()=>null}};
    return {ok:true,json:async()=>({...source,band_gap:null})};
  }));
  await render(<App/>);
  expect(host.querySelector('.propertyComparison')).not.toBeNull();
  expect(host.textContent).toContain('Material not found');
  expect(host.textContent).toContain('API Error');
  expect(host.textContent).toContain('Unknown');
  expect(host.querySelectorAll('.propertyComparison thead th')).toHaveLength(4);
});
