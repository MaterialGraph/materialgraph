import { expect, it, vi } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { MaterialIdentity } from './MaterialIdentity';
import type { MaterialDetail } from './api';

const detail: MaterialDetail = {
  id: 5, mp_id: 'mp-19017', formula: 'LiFePO4', pretty_formula: 'LiFePO4',
  material_type: null, band_gap: 3.9, energy_above_hull: 0,
  formation_energy_per_atom: -2.48, density: 3.68, is_stable: true,
  source: 'materials_project', elements: [],
};
const view = (material: MaterialDetail | null) => renderToStaticMarkup(
  <MaterialIdentity selected={5} detail={material} detailLoading={false} detailError="" retryDetail={vi.fn()}/>,
);

it('credits a fetched Materials Project record with accessible links and a readable source', () => {
  const html = view(detail);
  expect(html).toContain('Material record data: Materials Project (CC BY 4.0). MaterialGraph calculates the discovery, objective, chain, and comparison analysis shown here.');
  expect(html).toContain('<span class="tag">Materials Project</span>');
  expect(html).toContain('href="https://materialsproject.org/"');
  expect(html).toContain('href="https://creativecommons.org/licenses/by/4.0/"');
  expect(html).toContain('href="https://materialsproject.org/about/cite"');
  expect(html.match(/class="materialsAttribution"/g)).toHaveLength(1);
});

it('does not infer Materials Project provenance from a source ID or missing details', () => {
  expect(view({ ...detail, source: 'other_provider' })).toContain('<span class="tag">other_provider</span>');
  expect(view({ ...detail, source: 'other_provider' })).not.toContain('materialsAttribution');
  expect(view(null)).not.toContain('materialsAttribution');
});
