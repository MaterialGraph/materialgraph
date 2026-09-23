import { afterEach, expect, it, vi } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { materialDetail, type MaterialDetail } from '../api';
import { ComparisonTable, loadColumn } from './PropertyComparison';
import { arithmeticDifference, formatNumber, parseSelection, type ColumnState } from './model';

const source: MaterialDetail = { id: 5, mp_id: 'mp-19017', formula: 'LiFePO4', pretty_formula: 'LiFePO4', material_type: null,
  band_gap: 3.9224, energy_above_hull: 0, formation_energy_per_atom: -2.479896, density: 3.683146,
  is_stable: true, source: 'materials_project', elements: [{ id: 1, symbol: 'Li', name: 'Lithium' }] };
const first: MaterialDetail = { ...source, id: 6, mp_id: 'mp-19028', formula: 'Na3Fe(PO4)2', pretty_formula: 'Na3Fe(PO4)2',
  band_gap: 1.6304, formation_energy_per_atom: -2.4820996, density: 3.174671, elements: [{ id: 2, symbol: 'Na', name: 'Sodium' }] };
const second: MaterialDetail = { ...source, id: 7, mp_id: 'mp-556540', formula: 'Na3Fe3(PO4)4', pretty_formula: 'Na3Fe3(PO4)4', band_gap: null, is_stable: false };
const third: MaterialDetail = { ...source, id: 1, mp_id: 'mp-26003', formula: 'LiFe(PO3)3', pretty_formula: 'LiFe(PO3)3', band_gap: 4.067, elements: [] };
const retry = vi.fn();
const loaded = (material: MaterialDetail) => ({ status: 'success', id: material.id, material, retry } as const);
const error = (id: number) => ({ status: 'error', id, message: 'Material not found.', retry } as const);
const view = (a: ColumnState & { retry: () => void }, b: Array<ColumnState & { retry: () => void }>) => renderToStaticMarkup(<ComparisonTable source={a} candidates={b}/>);
afterEach(() => { vi.unstubAllGlobals(); vi.clearAllMocks(); });

it('renders source and two independent candidates with neutral differences and methodology', () => {
  const html = view(loaded(source), [loaded(first), loaded(second)]);
  expect(html).toContain('Source ·');
  expect(html.match(/Candidate ·/g)).toHaveLength(2);
  expect(html).toContain('mp-19017');
  expect(html).toContain('Arithmetic difference from source: -2.292 eV');
  expect(html).toContain('<span class="comparisonState">Unknown</span>');
  expect(html).toContain('Matching units do not establish that the underlying methods or conditions are comparable.');
  expect(html).toContain('Basis not supplied by this endpoint.');
  expect(html).toContain('Yes');
  expect(html).toContain('No');
  expect(html).toContain('Unknown');
  expect(html).toContain('0</span><span class="comparisonState">Available');
  expect(html).not.toMatch(/\b(winner|tie|recommended|better|worse)\b/i);
});

it('renders three candidates and listed-elements absence without claiming empty composition', () => {
  const html = view(loaded(source), [loaded(first), loaded(second), loaded(third)]);
  expect(html.match(/Candidate ·/g)).toHaveLength(3);
  expect(html).toContain('No elements listed');
  expect(html).toContain('Arithmetic difference from source: +0.1446 eV');
  expect(html).toContain('Arithmetic difference from source: -2.292 eV');
});

it('keeps successful columns when one candidate fails and suppresses differences without source', () => {
  const partial = view(loaded(source), [error(6), loaded(third)]);
  expect(partial).toContain('API Error');
  expect(partial).toContain('Retry fetch');
  expect(partial).toContain('mp-26003');
  expect(partial).toContain('Arithmetic difference from source: +0.1446 eV');
  const failedSource = view(error(5), [loaded(first), loaded(third)]);
  expect(failedSource).toContain('mp-19028');
  expect(failedSource).toContain('Arithmetic difference from source: Unavailable');
  expect(failedSource).not.toContain('Arithmetic difference from source: -2.292 eV');
  expect(view(loaded(source), [loaded(first), loaded(third)])).not.toContain('API Error');
});

it('preserves raw values for arithmetic, zero, null and presentation rounding', () => {
  expect(arithmeticDifference(source, first, 'band_gap')).toBeCloseTo(-2.292);
  expect(arithmeticDifference(source, second, 'band_gap')).toBeNull();
  expect(arithmeticDifference(source, first, 'energy_above_hull')).toBe(0);
  expect(formatNumber(3.9223999999999997)).toBe('3.9224');
  expect(formatNumber(-0.000001)).toBe('0');
  expect(formatNumber(arithmeticDifference(source, first, 'formation_energy_per_atom')!)).toBe('-0.0022');
});

it('bounds distinct local IDs without merging workflow selections', () => {
  expect(parseSelection('5', ['6', '7', ''])).toEqual({ sourceId: 5, candidateIds: [6, 7] });
  expect(parseSelection('5', ['6', '7', '1'])).toEqual({ sourceId: 5, candidateIds: [6, 7, 1] });
  expect(() => parseSelection('5', ['', '7', ''])).toThrow();
  expect(() => parseSelection('5', ['6', '6', ''])).toThrow();
  expect(() => parseSelection('5', ['6', '7', '1', '8'])).toThrow();
});

it('uses independent abortable detail requests, and a failed fetch can be retried', async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce({ ok: false, status: 404 })
    .mockResolvedValueOnce({ ok: true, json: async () => first });
  vi.stubGlobal('fetch', fetchMock);
  const signal = new AbortController().signal;
  await expect(materialDetail(6, signal)).rejects.toMatchObject({ status: 404 });
  await expect(materialDetail(6, signal)).resolves.toEqual(first);
  expect(fetchMock).toHaveBeenCalledTimes(2);
  expect(fetchMock.mock.calls[1]).toEqual(['/api/v1/materials/6/detail', { signal }]);
});

it('recovers one failed column without changing other column states', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce({ ok: false, status: 404 })
    .mockResolvedValueOnce({ ok: true, json: async () => first }));
  const report = vi.fn();
  await loadColumn(6, new AbortController().signal, report);
  expect(report).toHaveBeenLastCalledWith(expect.objectContaining({ status: 'error', id: 6 }));
  await loadColumn(6, new AbortController().signal, report);
  expect(report).toHaveBeenLastCalledWith({ status: 'success', id: 6, material: first });
});

it('does not report an older response after its comparison selection was aborted', async () => {
  let resolveOld!: (value: unknown) => void;
  const oldResponse = new Promise(resolve => { resolveOld = resolve; });
  const fetchMock = vi.fn().mockReturnValueOnce(oldResponse)
    .mockResolvedValueOnce({ ok: true, json: async () => second });
  vi.stubGlobal('fetch', fetchMock);
  const oldController = new AbortController();
  const report = vi.fn();
  const oldTask = loadColumn(6, oldController.signal, report);
  oldController.abort();
  await loadColumn(7, new AbortController().signal, report);
  resolveOld({ ok: true, json: async () => first });
  await oldTask;
  expect(report).toHaveBeenCalledTimes(1);
  expect(report).toHaveBeenCalledWith({ status: 'success', id: 7, material: second });
});
