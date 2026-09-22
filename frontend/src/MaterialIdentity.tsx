import type { MaterialDetail } from './api';
import { ChemicalFormula } from './ChemicalFormula';
function value(number: number | null, unit = '') {
  return number === null ? 'Unknown — no value supplied' : `${number.toLocaleString(undefined, { maximumFractionDigits: 4 })}${unit}`;
}
type Props = { selected: number; detail: MaterialDetail | null; detailLoading: boolean; detailError: string; retryDetail: () => void };
export function MaterialIdentity({ selected, detail, detailLoading, detailError, retryDetail }: Props) {
  return <>
        {selected > 0 && <div className="panel details"><div className="sectionTitle"><span>02 / INSPECT</span><h2>Material identity</h2></div>
          {detailLoading && <p role="status">Loading material details…</p>}{detailError && <div role="alert" className="error">{detailError} <button onClick={() => retryDetail()}>Retry</button></div>}
          {detail && <><div className="identity"><div><h3><ChemicalFormula formula={detail.pretty_formula || detail.formula}/></h3><p>Source ID: {detail.mp_id} · Local ID: {detail.id}</p></div><span className="tag">{detail.source}</span></div><p className="hint">Reported fields from the material record. This endpoint does not supply field-level provenance, evidence quality, or measurement conditions. “Stable” is a stored flag; inspect energy above hull separately.</p><dl className="properties"><div><dt>Formula</dt><dd><ChemicalFormula formula={detail.formula}/></dd></div><div><dt>Type</dt><dd>{detail.material_type ?? 'Unknown'}</dd></div><div><dt>Band gap</dt><dd>{value(detail.band_gap, ' eV')}</dd></div><div><dt>Energy above hull</dt><dd>{value(detail.energy_above_hull, ' eV/atom')}</dd></div><div><dt>Formation energy</dt><dd>{value(detail.formation_energy_per_atom, ' eV/atom')}</dd></div><div><dt>Density</dt><dd>{value(detail.density, ' g/cm³')}</dd></div><div><dt>Stored stability flag</dt><dd>{detail.is_stable ? 'Yes' : 'No'} · evidence basis not supplied here</dd></div><div><dt>Elements</dt><dd>{detail.elements.length ? detail.elements.map(e => `${e.symbol} (${e.name})`).join(', ') : 'None listed'}</dd></div></dl></>}
        </div>}
  </>;
}
