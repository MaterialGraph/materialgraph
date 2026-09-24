import type { MaterialDetail } from '../api';

export type ColumnState =
  | { status: 'loading'; id: number }
  | { status: 'success'; id: number; material: MaterialDetail }
  | { status: 'error'; id: number; message: string; code?: number };

export const properties = [
  { field: 'band_gap', label: 'Band gap', unit: 'eV' },
  { field: 'energy_above_hull', label: 'Energy above hull', unit: 'eV/atom' },
  { field: 'formation_energy_per_atom', label: 'Formation energy per atom', unit: 'eV/atom' },
  { field: 'density', label: 'Density', unit: 'g/cm³' },
] as const;
export type Property = (typeof properties)[number]['field'];

// Presentation rounds to at most four fractional digits. Arithmetic uses raw API numbers.
export function formatNumber(value: number): string {
  const rounded = Number(value.toFixed(4));
  return Object.is(rounded, -0) ? '0' : rounded.toLocaleString('en-US', { maximumFractionDigits: 4 });
}

export function arithmeticDifference(source: MaterialDetail | null, candidate: MaterialDetail | null, field: Property): number | null {
  const a = source?.[field];
  const b = candidate?.[field];
  return typeof a === 'number' && Number.isFinite(a) && typeof b === 'number' && Number.isFinite(b) ? b - a : null;
}

export function parseSelection(source: string, candidates: string[]): { sourceId: number; candidateIds: number[] } {
  if (candidates.length !== 3) throw new Error('Enter two or three candidate IDs.');
  const values = [source, candidates[0], candidates[1], ...(candidates[2]?.trim() ? [candidates[2]] : [])];
  if (values.length < 3 || values.length > 4 || values.some(value => !/^[1-9]\d*$/.test(value.trim()) || !Number.isSafeInteger(Number(value.trim())))) {
    throw new Error('Enter a source ID and two or three positive integer candidate IDs.');
  }
  const ids = values.map(value => Number(value.trim()));
  if (new Set(ids).size !== ids.length) throw new Error('Each material ID must be distinct.');
  return { sourceId: ids[0], candidateIds: ids.slice(1) };
}
