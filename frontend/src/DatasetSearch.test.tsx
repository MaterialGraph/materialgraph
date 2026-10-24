// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { Material, MaterialSearchResponse } from './api';
import { suggestedMode } from './DatasetSearch';
import { SourcePicker } from './SourcePicker';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let host: HTMLDivElement;
let root: Root;
beforeEach(() => { host = document.createElement('div'); document.body.append(host); root = createRoot(host); });
afterEach(() => { act(() => root.unmount()); host.remove(); vi.unstubAllGlobals(); });

const loaded: Material[] = [{ id: 5, mp_id: 'mp-19017', formula: 'LiFePO4', pretty_formula: 'LiFePO4' } as Material];
const dataset = { source: 'materials_project' as const, source_release: '2026.04.13', dataset_total: 1727, provenance_note: '', composition_exclusion_count: 0 };
const response = (overrides: Partial<MaterialSearchResponse>): MaterialSearchResponse => ({
  interpretation: { mode: 'formula', input: 'NaFePO4', elements: ['Fe', 'Na', 'O', 'P'], amounts: { Na: 1, Fe: 1, P: 1, O: 4 }, normalized_fractions: null, reduced_formula: 'NaFePO4', mp_id: null },
  dataset, total_matches: 0, dataset_total: 1727, limit: 20, offset: 0, results: [], suggestions: null, message: null, ...overrides,
});

function renderPicker(select = vi.fn()) {
  act(() => root.render(<SourcePicker selected={5} select={select} items={loaded} offset={0} listError="" listLoading={false} retryList={() => {}} loadMore={() => {}}/>));
  return select;
}

async function search(mode: string, text: string) {
  const select = host.querySelector<HTMLSelectElement>('#datasetSearchMode')!;
  const input = host.querySelector<HTMLInputElement>('input[aria-label="Dataset search query"]')!;
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value')!.set!.call(select, mode);
    select.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, text);
    input.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await act(async () => { host.querySelector('.datasetSearch form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); });
}

it('finds and selects a material that is in the dataset but not loaded (M-10)', async () => {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => response({
    total_matches: 2,
    results: [
      { material_id: 10, mp_id: 'mp-19226', formula: 'NaFePO4', pretty_formula: 'NaFePO4' },
      { material_id: 384, mp_id: 'mp-1192859', formula: 'NaFePO4', pretty_formula: 'NaFePO4' },
    ],
  }) });
  vi.stubGlobal('fetch', fetchMock);
  const select = renderPicker();

  await search('formula', 'NaFePO4');

  expect(fetchMock.mock.calls[0][0]).toBe('/api/v1/materials/search?mode=formula&q=NaFePO4&limit=20&offset=0');
  expect(host.textContent).toContain('2 matches among 1727 materials in the dataset');
  expect(host.textContent).toContain('mp-1192859 · #384 · in the dataset, not yet loaded in the list');
  const button = [...host.querySelectorAll<HTMLButtonElement>('.datasetSearchResults button')].find(item => item.textContent?.includes('#384'))!;
  await act(async () => { button.click(); });
  expect(select).toHaveBeenCalledWith(384);
});

it('reports a material absent from the dataset differently from one not yet loaded', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => response({
    interpretation: { mode: 'formula', input: 'Ti2C', elements: ['C', 'Ti'], amounts: { Ti: 2, C: 1 }, normalized_fractions: null, reduced_formula: 'Ti2C', mp_id: null },
    message: 'No match in this dataset (Materials Project release 2026.04.13, 1727 materials). The material is not in this dataset; this does not mean it does not exist.',
  }) }));
  renderPicker();

  await search('formula', 'Ti2C');

  expect(host.textContent).toContain('0 matches among 1727 materials in the dataset');
  expect(host.textContent).toContain('The material is not in this dataset');
  expect(host.textContent).not.toContain('not yet loaded');
});

it('shows the backend explanation for invalid input instead of no results (M-6)', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: { code: 'invalid_formula', mode: 'formula', input: 'lifepo4', explanation: 'Element symbols are case-sensitive.' } }) }));
  renderPicker();

  await search('formula', 'lifepo4');

  expect(host.querySelector('[role="alert"]')?.textContent).toContain('Element symbols are case-sensitive.');
  expect(host.textContent).toContain('invalid_formula');
  expect(host.textContent).not.toContain('matches among');
});

it('only suggests a mode; the explicit mode is what is sent (M-1)', async () => {
  expect(suggestedMode('formula', 'mp-19017')).toBe('mp_id');
  expect(suggestedMode('formula', 'Li-Fe-P-O')).toBe('chemsys');
  expect(suggestedMode('mp_id', 'mp-19017')).toBeNull();
  expect(suggestedMode('formula', 'LiFePO4')).toBeNull();

  const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => response({}) });
  vi.stubGlobal('fetch', fetchMock);
  renderPicker();
  await search('formula', 'mp-19017');

  expect(host.textContent).toContain('This looks like a search by MP ID.');
  expect(fetchMock.mock.calls[0][0]).toContain('mode=formula');
});

it('shows the input as received beside the explanation for a 422', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 422, json: async () => ({ detail: { code: 'invalid_formula', mode: 'formula', input: 'lifepo4', explanation: 'Element symbols are case-sensitive.' } }) }));
  renderPicker();

  await search('formula', 'lifepo4');

  const alert = host.querySelector('[role="alert"]')!;
  expect(alert.querySelector('.searchInput')?.textContent).toBe('Input: lifepo4');
  expect(alert.textContent).toContain('Element symbols are case-sensitive.');
  // The displayed input is the server's echo, not a corrected version.
  expect(alert.textContent).not.toContain('LiFePO4');
});
