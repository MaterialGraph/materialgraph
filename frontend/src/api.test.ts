import { afterEach, expect, it, vi } from 'vitest';
import { ApiError, candidates, materialDetail } from './api';

afterEach(() => vi.unstubAllGlobals());

it('requests a material detail by local ID and keeps missing properties unknown', async () => {
  const payload = { id: 5, band_gap: null, elements: [] };
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => payload });
  vi.stubGlobal('fetch', fetchMock);
  expect(await materialDetail(5)).toEqual(payload);
  expect(fetchMock.mock.calls[0][0]).toBe('/api/v1/materials/5/detail');
});

it('sends only explicitly chosen soft element filters', async () => {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ candidates: [] }) });
  vi.stubGlobal('fetch', fetchMock);
  await candidates(5, 'Li', '  ');
  const url = new URL(fetchMock.mock.calls[0][0], 'http://localhost');
  expect(url.searchParams.get('avoid_element')).toBe('Li');
  expect(url.searchParams.has('prefer_element')).toBe(false);
  expect(url.searchParams.get('include_substitution_paths')).toBe('false');
  expect(url.searchParams.get('limit')).toBe('10');
});

it('distinguishes a missing material from a transport failure', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 404 }));
  await expect(materialDetail(999)).rejects.toMatchObject({ status: 404, message: 'Material not found.' });
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
  await expect(materialDetail(5)).rejects.toBeInstanceOf(ApiError);
  await expect(materialDetail(5)).rejects.toMatchObject({ status: 0 });
});

it('explains a proxy failure without treating it as a scientific result', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: false, status: 500, headers: { get: () => 'text/plain' },
  }));
  await expect(materialDetail(5)).rejects.toMatchObject({
    status: 500,
    message: 'API unavailable or returned a non-JSON error. Check the local backend and Vite proxy.',
  });
});
