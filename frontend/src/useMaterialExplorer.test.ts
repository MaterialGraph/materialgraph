import { expect, it } from 'vitest';
import { initialMaterialId } from './useMaterialExplorer';

it('opens the local material ID from the existing URL entry point', () => {
  expect(initialMaterialId('?material=5')).toBe(5);
  expect(initialMaterialId('?material=5&other=value')).toBe(5);
  expect(initialMaterialId('?material=mp-19017')).toBe(0);
  expect(initialMaterialId('?material=-1')).toBe(0);
  expect(initialMaterialId('')).toBe(0);
});
