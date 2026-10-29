// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { DatasetSummary, Material, MaterialSearchResponse, SearchResult } from './api';
import { formatEnergy } from './DatasetSearch';
import { SourcePicker } from './SourcePicker';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

// Vitest serves CSS imports (including ?raw) as empty strings, so the stylesheet
// is read from disk. The project has no Node typings; the builtin is reached untyped.
type Fs = { readFileSync: (path: string, encoding: 'utf8') => string };
const nodeProcess = (globalThis as unknown as { process: { cwd: () => string; getBuiltinModule: (name: string) => Fs } }).process;
const css = nodeProcess.getBuiltinModule('node:fs').readFileSync(`${nodeProcess.cwd()}/src/style.css`, 'utf8');

// jsdom lacks native dialog methods; the App test mounts PilotOrientation.
if (!HTMLDialogElement.prototype.showModal) {
  Object.defineProperty(HTMLDialogElement.prototype, 'showModal', { configurable: true, value(this: HTMLDialogElement) { this.setAttribute('open', ''); } });
  Object.defineProperty(HTMLDialogElement.prototype, 'close', { configurable: true, value(this: HTMLDialogElement) { this.removeAttribute('open'); } });
}

let host: HTMLDivElement;
let root: Root;
beforeEach(() => { host = document.createElement('div'); document.body.append(host); root = createRoot(host); stubFetch(); });
afterEach(() => { act(() => root.unmount()); host.remove(); history.replaceState(null, '', '/'); vi.unstubAllGlobals(); });

// Fixtures -------------------------------------------------------------------

const summary: DatasetSummary = {
  source: 'materials_project', source_release: '2026.04.13', dataset_total: 1727,
  provenance_note: '1699 records carry release provenance; 28 curated records predate provenance tracking.',
  composition_exclusions: [], composition_exclusion_count: 0,
};
const material = (id: number): Material => ({
  id, mp_id: `mp-${1000 + id}`, formula: `Fe${id}O`, pretty_formula: `Fe${id}O`, material_type: null, band_gap: null,
  energy_above_hull: id === 2 ? null : 0.01 * id, formation_energy_per_atom: null, density: null, is_stable: false, source: 'materials_project',
});
const materials = (from: number, count: number) => Array.from({ length: count }, (_, i) => material(from + i));
const result = (id: number, extra: Partial<SearchResult> = {}): SearchResult => ({
  material_id: id, mp_id: `mp-${1000 + id}`, formula: `Fe${id}O`, pretty_formula: `Fe${id}O`, energy_above_hull: 0.012, ...extra,
});
const response = (overrides: Partial<MaterialSearchResponse> = {}): MaterialSearchResponse => ({
  interpretation: { mode: 'formula', input: 'NaFePO4', elements: ['Fe', 'Na', 'O', 'P'], amounts: { Na: 1, Fe: 1, P: 1, O: 4 }, normalized_fractions: null, reduced_formula: 'NaFePO4', mp_id: null, material_id: null },
  requested_mode: 'auto', dataset: summary, total_matches: 0, dataset_total: 1727, limit: 50, offset: 0, results: [],
  suggestions: null, suggestion_total: null, message: null, scoped_message: null, ...overrides,
});

// A fetch whose responses the test releases one by one. By default it ignores
// abort signals, so a late response really arrives and must be discarded.
type Call = { url: string; signal?: AbortSignal; reply: (body: unknown, status?: number) => Promise<void>; fail: () => Promise<void> };
let calls: Call[];
async function flush() { await act(async () => { for (let i = 0; i < 5; i++) await new Promise(resolve => setTimeout(resolve, 0)); }); }
function stubFetch({ honourAbort = false } = {}) {
  calls = [];
  vi.stubGlobal('fetch', vi.fn((url: string, init?: RequestInit) => new Promise((resolve, reject) => {
    if (honourAbort) init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    calls.push({
      url, signal: init?.signal ?? undefined,
      reply: async (body, status = 200) => { resolve({ ok: status < 400, status, headers: new Headers({ 'content-type': 'application/json' }), json: async () => body }); await flush(); },
      fail: async () => { reject(new TypeError('Failed to fetch')); await flush(); },
    });
  })));
}
const browseCalls = () => calls.filter(call => call.url.includes('/materials?'));
const summaryCalls = () => calls.filter(call => call.url.includes('/dataset-summary'));
const searchCalls = () => calls.filter(call => call.url.includes('/materials/search'));
const lastSearch = () => new URL(searchCalls().at(-1)!.url, 'http://test').searchParams;

async function renderPicker(select = vi.fn(), selected = 5) {
  await act(async () => root.render(<SourcePicker selected={selected} select={select}/>));
  return select;
}
async function startBrowse(rows = materials(1, 50), select = vi.fn(), selected = 5) {
  await renderPicker(select, selected);
  await browseCalls()[0].reply(rows);
  await summaryCalls()[0].reply(summary);
  return select;
}
const queryInput = () => host.querySelector<HTMLInputElement>('input[aria-label="Dataset search query"]')!;
const modeSelect = () => host.querySelector<HTMLSelectElement>('#datasetSearchMode')!;
async function type(text: string) {
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(queryInput(), text);
    queryInput().dispatchEvent(new Event('input', { bubbles: true }));
  });
}
async function chooseMode(mode: string) {
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')!.set!.call(modeSelect(), mode);
    modeSelect().dispatchEvent(new Event('change', { bubbles: true }));
  });
}
async function submit() { await act(async () => { host.querySelector('.datasetSearch form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); }); }
async function search(text: string, mode = 'auto') { await chooseMode(mode); await type(text); await submit(); }
const button = (label: string) => [...host.querySelectorAll<HTMLButtonElement>('button')].find(item => item.textContent === label);
async function click(target: HTMLElement | undefined) { expect(target).toBeDefined(); await act(async () => target!.click()); }
const rowIds = () => [...host.querySelectorAll('.datasetSearchScroll > .materialList .materialRow small:first-of-type')].map(item => item.textContent);
const liveRegion = () => host.querySelector('[role="status"]')!.textContent;

// Transitions ---------------------------------------------------------------

it('enters browse on first render: page 1 of 50 and the dataset summary', async () => {
  await startBrowse();
  expect(browseCalls().map(call => call.url)).toEqual(['/api/v1/materials?limit=50&offset=0']);
  expect(summaryCalls().map(call => call.url)).toEqual(['/api/v1/materials/dataset-summary']);
  expect(host.textContent).toContain('All materials in the dataset, ordered by local ID. Showing 1–50 of 1727');
  expect(host.textContent).toContain(`Values computed by Materials Project. ${summary.provenance_note}`);
  expect(host.querySelectorAll('.materialRow')).toHaveLength(50);
});

it('offers the six modes, defaults to Auto and keeps the requested mode after an auto search', async () => {
  await startBrowse();
  expect([...modeSelect().options].map(option => [option.value, option.textContent])).toEqual([
    ['auto', 'Auto'], ['formula', 'Formula'], ['chemsys', 'Chemical system'], ['contains', 'Contains elements'], ['mp_id', 'MP ID'], ['material_id', 'Local ID'],
  ]);
  expect(modeSelect().value).toBe('auto');
  await search('5');
  await searchCalls()[0].reply(response({ interpretation: { ...response().interpretation, mode: 'material_id', input: '5', elements: null, amounts: null, reduced_formula: null, material_id: 5 }, total_matches: 1, results: [result(5)] }));
  expect(host.textContent).toContain('Interpreted as local material ID 5.');
  expect(modeSelect().value).toBe('auto');
});

it('submits the draft: aborts browse, clears pages, announces the interpretation and keeps focus in the input', async () => {
  await renderPicker();
  const browse = browseCalls()[0];
  await search('NaFePO4');
  expect(browse.signal?.aborted).toBe(true);
  expect(lastSearch().toString()).toBe('mode=auto&q=NaFePO4&limit=50&offset=0');
  expect(host.querySelectorAll('.materialRow')).toHaveLength(0);
  expect(liveRegion()).toBe('Searching the full dataset…');
  await searchCalls()[0].reply(response({ total_matches: 2, results: [result(10), result(384)] }));
  expect(liveRegion()).toContain('Interpreted as formula NaFePO4 (elements: Fe, Na, O, P). 2 matches among 1727 materials in the dataset.');
  expect(host.textContent).toContain('Ordered by local ID.');
  expect(host.textContent).toContain('Showing 1–2 of 2');
  expect(document.activeElement).toBe(queryInput());
});

it('editing the input or mode changes only the draft and marks the results stale', async () => {
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply(response({ total_matches: 1, results: [result(1)] }));
  const count = calls.length;
  await type('Co');
  await chooseMode('formula');
  expect(calls.length).toBe(count);
  expect(host.querySelector('.stale')?.textContent).toBe('These results belong to the previous search: Fe (Auto).');
  await type('Fe'); await chooseMode('auto');
  expect(host.querySelector('.stale')).toBeNull();
});

it('Show more pages the committed query, never the edited draft (Release 1 regression)', async () => {
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply(response({ total_matches: 120, results: Array.from({ length: 50 }, (_, i) => result(i + 1)) }));
  await type('Co'); await chooseMode('formula');
  await click(button('Show more'));
  expect(lastSearch().toString()).toBe('mode=auto&q=Fe&limit=50&offset=50');
  expect(button('Loading…')?.disabled).toBe(true);
  await searchCalls()[1].reply(response({ total_matches: 120, offset: 50, results: Array.from({ length: 50 }, (_, i) => result(i + 51)) }));
  expect(host.querySelectorAll('.materialRow')).toHaveLength(100);
  // Focus moves to the first newly loaded row.
  expect(document.activeElement?.textContent).toContain('#51');
});

it('Show more in browse appends the next page at the loaded count', async () => {
  await startBrowse();
  await click(button('Show more'));
  expect(browseCalls()[1].url).toBe('/api/v1/materials?limit=50&offset=50');
  await browseCalls()[1].reply(materials(51, 50));
  expect(host.textContent).toContain('Showing 1–100 of 1727');
  expect(document.activeElement?.textContent).toContain('#51');
});

it('a later-page failure keeps loaded pages; Retry refetches the same offset', async () => {
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply(response({ total_matches: 120, results: Array.from({ length: 50 }, (_, i) => result(i + 1)) }));
  await click(button('Show more'));
  await searchCalls()[1].fail();
  expect(host.querySelectorAll('.materialRow')).toHaveLength(50);
  expect(host.querySelector('.datasetSearchScroll [role="alert"]')?.textContent).toContain('Cannot reach the API.');
  expect(button('Show more')).toBeUndefined();
  await type('Co');
  await click(button('Retry'));
  expect(lastSearch().toString()).toBe('mode=auto&q=Fe&limit=50&offset=50');
  await searchCalls()[2].reply(response({ total_matches: 120, results: Array.from({ length: 50 }, (_, i) => result(i + 51)) }));
  expect(host.querySelectorAll('.materialRow')).toHaveLength(100);
  expect(host.querySelector('[role="alert"]')).toBeNull();
});

it('a first-page failure shows the error and no rows', async () => {
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].fail();
  expect(host.querySelector('[role="alert"]')?.textContent).toContain('Cannot reach the API. Check the local backend connection.');
  expect(host.querySelectorAll('.materialRow')).toHaveLength(0);
});

it('the Search button stays enabled while loading and supersedes the current request', async () => {
  await startBrowse();
  await search('Fe');
  expect(button('Search')?.disabled).toBe(false);
  const first = searchCalls()[0];
  await search('Co');
  expect(first.signal?.aborted).toBe(true);
  await searchCalls()[1].reply(response({ interpretation: { ...response().interpretation, reduced_formula: 'Co', elements: ['Co'] }, total_matches: 1, results: [result(27)] }));
  // The superseded response arrives late and is discarded.
  await first.reply(response({ total_matches: 1, results: [result(26)] }));
  expect(rowIds()).toEqual(['mp-1027 · #27']);
  expect(host.textContent).toContain('formula Co');
});

it('discards a late page response after a new search', async () => {
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply(response({ total_matches: 120, results: Array.from({ length: 50 }, (_, i) => result(i + 1)) }));
  await click(button('Show more'));
  const page = searchCalls()[1];
  await search('Co');
  expect(page.signal?.aborted).toBe(true);
  await searchCalls()[2].reply(response({ total_matches: 1, results: [result(300)] }));
  await page.reply(response({ total_matches: 120, results: Array.from({ length: 50 }, (_, i) => result(i + 51)) }));
  expect(rowIds()).toEqual(['mp-1300 · #300']);
});

it('discards a late summary response and applies only the current one', async () => {
  await startBrowse();
  await submit();
  const late = summaryCalls()[1];
  await submit();
  expect(late.signal?.aborted).toBe(true);
  await browseCalls()[2].reply(materials(1, 50));
  await summaryCalls()[2].reply(summary);
  await late.reply({ ...summary, dataset_total: 9999, provenance_note: 'stale note' });
  expect(host.textContent).toContain('Showing 1–50 of 1727');
  expect(host.textContent).not.toContain('9999');
  expect(host.textContent).not.toContain('stale note');
});

it('an aborted request is never shown as an error', async () => {
  stubFetch({ honourAbort: true });
  await renderPicker();
  await search('Fe');
  await search('Co');
  expect(host.querySelector('[role="alert"]')).toBeNull();
  await searchCalls()[1].reply(response({ total_matches: 0, scoped_message: 'No material with reduced formula Co in this dataset.' }));
  expect(host.querySelector('[role="alert"]')).toBeNull();
});

it('Clear search and empty submit return to browse, refetch the summary and leave the selection unchanged', async () => {
  const select = await startBrowse(materials(1, 50), vi.fn(), 7);
  await search('Fe');
  await searchCalls()[0].reply(response({ total_matches: 1, results: [result(1)] }));
  await click(button('Clear search'));
  expect(queryInput().value).toBe('');
  expect(modeSelect().value).toBe('auto');
  expect(browseCalls()).toHaveLength(2);
  expect(summaryCalls()).toHaveLength(2);
  await browseCalls()[1].reply(materials(1, 50));
  await summaryCalls()[1].reply(summary);
  expect(host.textContent).toContain('All materials in the dataset');
  expect(host.querySelector('.materialRow.active')?.textContent).toContain('#7');

  await search('Fe');
  const inFlight = searchCalls()[1];
  await type('   ');
  await submit();
  expect(inFlight.signal?.aborted).toBe(true);
  expect(browseCalls()).toHaveLength(3);
  expect(summaryCalls()).toHaveLength(3);
  expect(select).not.toHaveBeenCalled();
});

it('a summary failure keeps browse rows and offers a summary-only Retry, with no total shown', async () => {
  await renderPicker();
  await browseCalls()[0].reply(materials(1, 50));
  await summaryCalls()[0].reply({ detail: 'boom' }, 500);
  expect(host.querySelectorAll('.materialRow')).toHaveLength(50);
  expect(host.querySelector('.summaryError')?.textContent).toContain('Dataset information unavailable');
  expect(host.textContent).toContain('Showing 1–50');
  expect(host.textContent).not.toContain('1727');
  expect(host.textContent).not.toContain('Values computed by Materials Project');
  const count = calls.length;
  await click(host.querySelector<HTMLButtonElement>('.summaryError button')!);
  expect(calls.length).toBe(count + 1);
  expect(calls.at(-1)!.url).toBe('/api/v1/materials/dataset-summary');
  await summaryCalls()[1].reply(summary);
  expect(host.textContent).toContain('Showing 1–50 of 1727');
});

it('browse rows failing is a first-page error', async () => {
  await renderPicker();
  await browseCalls()[0].fail();
  await summaryCalls()[0].reply(summary);
  expect(host.querySelector('[role="alert"]')?.textContent).toContain('Cannot reach the API.');
  expect(host.querySelectorAll('.materialRow')).toHaveLength(0);
});

// Header ----------------------------------------------------------------------

it('renders provenance_note as returned and says when the release is not recorded', async () => {
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply(response({ dataset: { ...summary, source_release: null }, total_matches: 1, results: [result(1)] }));
  expect(host.textContent).toContain(`Values computed by Materials Project. ${summary.provenance_note}`);
  expect(host.textContent).toContain('The Materials Project release is not recorded in this database.');
  expect(host.textContent).not.toContain('2026.04.13');
});

it('states composition exclusions only on composition-mode searches with a non-zero count', async () => {
  const excluded = { ...summary, composition_exclusion_count: 3 };
  const line = '3 materials could not be searched by composition; MP ID and local ID search still find them.';
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply(response({ dataset: excluded, total_matches: 1, results: [result(1)] }));
  expect(host.textContent).toContain(line);
  await search('mp-1001');
  await searchCalls()[1].reply(response({ interpretation: { ...response().interpretation, mode: 'mp_id', mp_id: 'mp-1001', elements: null }, dataset: excluded, total_matches: 1, results: [result(1)] }));
  expect(host.textContent).not.toContain('could not be searched by composition');
  await search('Fe');
  await searchCalls()[2].reply(response({ total_matches: 1, results: [result(1)] }));
  expect(host.textContent).not.toContain('could not be searched by composition');
});

// Rows ------------------------------------------------------------------------

it.each([
  [null, 'Energy above hull: not supplied'],
  [undefined, 'Energy above hull: not supplied'],
  [0, 'Energy above hull: 0.000 eV/atom'],
  [-0, 'Energy above hull: 0.000 eV/atom'],
  [0.0004, 'Energy above hull: <0.001 eV/atom'],
  [0.0005, 'Energy above hull: 0.001 eV/atom'],
  [0.0123, 'Energy above hull: 0.012 eV/atom'],
  [1.5, 'Energy above hull: 1.500 eV/atom'],
  [-0.0123, 'Energy above hull: −0.012 eV/atom'],
  [-0.0004, 'Energy above hull: >−0.001 eV/atom'],
])('formats energy above hull %s as %s', (value, text) => {
  expect(formatEnergy(value)).toBe(text);
});

it('rows show formula, identifiers and energy, and mark the selected material', async () => {
  await startBrowse();
  const rows = [...host.querySelectorAll<HTMLButtonElement>('.materialRow')];
  expect(rows[0].querySelector('sub')?.textContent).toBe('1');
  expect(rows[0].textContent).toContain('mp-1001 · #1');
  expect(rows[0].textContent).toContain('Energy above hull: 0.010 eV/atom');
  expect(rows[1].textContent).toContain('Energy above hull: not supplied');
  expect(rows.filter(row => row.getAttribute('aria-current') === 'true').map(row => row.textContent)).toEqual([rows[4].textContent]);
  expect(rows.every(row => row.type === 'button')).toBe(true);
});

it('finds and selects a material that is in the dataset (present; M-10)', async () => {
  const select = await startBrowse();
  await search('NaFePO4', 'formula');
  expect(lastSearch().toString()).toBe('mode=formula&q=NaFePO4&limit=50&offset=0');
  await searchCalls()[0].reply(response({ requested_mode: 'formula', total_matches: 2, results: [result(10, { mp_id: 'mp-19226' }), result(384, { mp_id: 'mp-1192859' })] }));
  expect(host.textContent).toContain('2 matches among 1727 materials in the dataset');
  expect(host.textContent).not.toContain('not yet loaded');
  await click([...host.querySelectorAll<HTMLButtonElement>('.materialRow')].find(item => item.textContent?.includes('#384')));
  expect(select).toHaveBeenCalledWith(384);
  expect(queryInput().value).toBe('NaFePO4');
  expect(host.querySelectorAll('.materialRow')).toHaveLength(2);
});

it('reports a material absent from the dataset with the scoped message (absent)', async () => {
  await startBrowse();
  await search('Ti2C');
  const scoped = 'No material with reduced formula Ti2C in this dataset (Materials Project release 2026.04.13, 1727 materials). Absence here does not mean the material does not exist.';
  await searchCalls()[0].reply(response({
    interpretation: { ...response().interpretation, input: 'Ti2C', elements: ['C', 'Ti'], reduced_formula: 'Ti2C' },
    message: 'No match in this dataset. The material is not in this dataset; this does not mean it does not exist.', scoped_message: scoped,
  }));
  expect(host.textContent).toContain('0 matches among 1727 materials in the dataset');
  expect(host.querySelector('.scopedMessage')?.textContent).toBe(scoped);
  expect(host.textContent).not.toContain('No match in this dataset.');
  expect(host.textContent).not.toContain('not yet loaded');
  expect(host.querySelectorAll('.materialRow')).toHaveLength(0);
});

it('shows the backend explanation, hint and input for invalid input (invalid; M-6)', async () => {
  await startBrowse();
  await search('lifepo4');
  await searchCalls()[0].reply({ detail: { code: 'invalid_formula', mode: 'formula', requested_mode: 'auto', input: 'lifepo4', explanation: 'Element symbols are case-sensitive.', hint: 'Accepted inputs: a local material ID (5 or #5).' } }, 422);
  const alert = host.querySelector('[role="alert"]')!;
  expect(alert.textContent).toContain('Element symbols are case-sensitive.');
  expect(alert.textContent).toContain('Accepted inputs: a local material ID (5 or #5).');
  expect(alert.textContent).toContain('invalid_formula');
  // The displayed input is the server's echo, not a corrected version.
  expect(alert.querySelector('.searchInput')?.textContent).toBe('Input: lifepo4');
  expect(alert.textContent).not.toContain('LiFePO4');
  expect(host.textContent).not.toContain('matches among');
});

it('reports a list-shaped 422 as an invalid request', async () => {
  await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply({ detail: [{ loc: ['query', 'mode'], msg: 'bad' }] }, 422);
  expect(host.querySelector('[role="alert"]')?.textContent).toContain('The search request was not valid.');
});

it('labels suggestions and states how many exist beyond those shown', async () => {
  await startBrowse();
  await search('Li20O');
  await searchCalls()[0].reply(response({
    scoped_message: 'No material with reduced formula Li20O in this dataset.',
    suggestions: { basis: 'same_chemical_system', explanation: 'These materials have the same elements in different proportions.', results: Array.from({ length: 10 }, (_, i) => result(i + 1)) },
    suggestion_total: 12,
  }));
  const block = host.querySelector('.datasetSearchSuggestions')!;
  expect(block.textContent).toContain('Same elements, different proportions');
  expect(block.textContent).toContain('Showing 10 of 12');
  expect(block.querySelectorAll('.materialRow')).toHaveLength(10);
  expect(block.textContent).toContain('Energy above hull: 0.012 eV/atom');
});

// Selection contract ------------------------------------------------------------

it('never changes the selection on a new query, page, mode change or edit', async () => {
  const select = await startBrowse();
  await search('Fe');
  await searchCalls()[0].reply(response({ total_matches: 120, results: Array.from({ length: 50 }, (_, i) => result(i + 1)) }));
  await click(button('Show more'));
  await searchCalls()[1].reply(response({ total_matches: 120, results: Array.from({ length: 50 }, (_, i) => result(i + 51)) }));
  await chooseMode('formula'); await type('Co');
  await submit();
  expect(select).not.toHaveBeenCalled();
});

it('a main-workspace detail 404 shows the error and marks no other material as selected', async () => {
  history.replaceState(null, '', '/?material=999');
  vi.stubGlobal('fetch', vi.fn(async (url: string) => {
    if (url.includes('/materials?')) return { ok: true, status: 200, json: async () => materials(1, 50) };
    if (url.includes('/dataset-summary')) return { ok: true, status: 200, json: async () => summary };
    return { ok: false, status: 404, headers: new Headers(), json: async () => ({ detail: 'Material not found' }) };
  }));
  const { App } = await import('./main');
  await act(async () => root.render(<App/>));
  await flush();
  expect([...host.querySelectorAll('[role="alert"]')].some(item => item.textContent?.includes('Material not found.'))).toBe(true);
  expect(host.querySelectorAll('.materialRow')).toHaveLength(50);
  expect(host.querySelector('.materialRow.active, .materialRow[aria-current]')).toBeNull();
});

// Layout (rules only: jsdom does not lay out) ----------------------------------

it('stacks the full-width input above the mode select and Search button', async () => {
  await startBrowse();
  const form = host.querySelector('.datasetSearchForm')!;
  expect([...form.children].map(child => child.tagName)).toEqual(['LABEL', 'INPUT', 'DIV']);
  const controls = form.querySelector('.datasetSearchControls')!;
  expect([...controls.children].map(child => child.tagName)).toEqual(['SELECT', 'BUTTON']);
  expect(host.querySelectorAll('.datasetSearchScroll')).toHaveLength(1);
  expect(host.querySelector('.datasetSearchScroll')!.contains(host.querySelector('.materialList'))).toBe(true);
  expect(host.querySelector('#search, #directId')).toBeNull();
});

it('sizes the input for at least 24 characters at the minimum content width', () => {
  const rule = (selector: string) => css.match(new RegExp(`${selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\{([^}]*)\\}`))?.[1] ?? '';
  const input = rule('.datasetSearchForm input');
  expect(input).toContain('width:100%');
  expect(input).toContain('font-size:15px');
  expect(input).toContain('padding:10px 8px');
  // 228px content - 2px border - 16px padding = 210px of text; 24 characters at
  // 15px are about 24 * 0.55em = 198px in system-ui.
  expect(228 - 2 - 16).toBeGreaterThanOrEqual(Math.ceil(24 * 0.55 * 15));
  expect(rule('.datasetSearchScroll')).toContain('overflow:auto');
  expect(rule('.picker')).toContain('max-height:calc(100vh - 28px)');
  expect(css).toContain('@media(max-width:850px){.datasetSearchScroll{max-height:60vh}}');
  expect(css).not.toContain('max-height:420px');
});

