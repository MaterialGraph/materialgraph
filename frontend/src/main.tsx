import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { candidates, listMaterials, materialDetail, type Material, type MaterialDetail, type CandidateResponse } from './api';
import './style.css';

function value(number: number | null, unit = '') {
  return number === null ? 'Unknown — no value supplied' : `${number.toLocaleString(undefined, { maximumFractionDigits: 4 })}${unit}`;
}
function App() {
  const initial = Number(new URLSearchParams(location.search).get('material'));
  const [selected, setSelected] = useState(Number.isSafeInteger(initial) && initial > 0 ? initial : 0);
  const [items, setItems] = useState<Material[]>([]);
  const [offset, setOffset] = useState(0);
  const [listRetry, setListRetry] = useState(0);
  const [detailRetry, setDetailRetry] = useState(0);
  const [listError, setListError] = useState('');
  const [listLoading, setListLoading] = useState(false);
  const [detail, setDetail] = useState<MaterialDetail | null>(null);
  const [detailError, setDetailError] = useState('');
  const [detailLoading, setDetailLoading] = useState(false);
  const [avoid, setAvoid] = useState('');
  const [prefer, setPrefer] = useState('');
  const [result, setResult] = useState<CandidateResponse | null>(null);
  const [candidateError, setCandidateError] = useState('');
  const [candidateLoading, setCandidateLoading] = useState(false);
  const [request, setRequest] = useState<{ id: number; avoid: string; prefer: string; sequence: number } | null>(null);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    setListLoading(true); setListError('');
    listMaterials(offset, controller.signal).then(page => setItems(previous => offset ? [...previous, ...page] : page))
      .catch(error => { if (!controller.signal.aborted) setListError(error.message); })
      .finally(() => { if (!controller.signal.aborted) setListLoading(false); });
    return () => controller.abort();
  }, [offset, listRetry]);
  useEffect(() => {
    if (!selected) return;
    const controller = new AbortController();
    setDetail(null); setResult(null); setRequest(null); setDetailError(''); setDetailLoading(true);
    materialDetail(selected, controller.signal).then(setDetail)
      .catch(error => { if (!controller.signal.aborted) setDetailError(error.message); })
      .finally(() => { if (!controller.signal.aborted) setDetailLoading(false); });
    return () => controller.abort();
  }, [selected, detailRetry]);
  useEffect(() => {
    if (!request) return;
    const controller = new AbortController();
    setResult(null); setCandidateError(''); setCandidateLoading(true);
    candidates(request.id, request.avoid, request.prefer, controller.signal).then(setResult)
      .catch(error => { if (!controller.signal.aborted) setCandidateError(error.message); })
      .finally(() => { if (!controller.signal.aborted) setCandidateLoading(false); });
    return () => controller.abort();
  }, [request]);
  function select(id: number) {
    setSelected(id);
    const url = new URL(location.href); url.searchParams.set('material', String(id)); history.replaceState(null, '', url);
  }
  const filtered = items.filter(item => `${item.pretty_formula} ${item.formula} ${item.mp_id} ${item.id}`.toLowerCase().includes(search.toLowerCase()));
  return <div className="shell">
    <header><div className="brand">Material<span>Graph</span><small>Research workspace / 01</small></div><div className="headerNote">MATERIAL EXPLORER <span>·</span> READ ONLY</div></header>
    <div className="intro"><p className="eyebrow">EXPLORE THE MATERIAL LANDSCAPE</p><h1>Start with a material.<br/><em>Follow the evidence.</em></h1><p>Select a source identity, inspect available properties, then explore explainable candidates. Scores describe encoded rules, not experimental validation.</p></div>
    <main className="layout">
      <aside className="panel picker"><div className="sectionTitle"><span>01 / SELECT</span><h2>Materials</h2></div><label htmlFor="search">Filter loaded materials</label><input id="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Formula, source ID, or local ID"/><p className="hint">Showing the first {items.length} identities in internal ID order. Load more to extend this list.</p>
        {listError && <div role="alert" className="error">{listError} <button onClick={() => setListRetry(n => n + 1)}>Retry</button></div>}
        <div className="materialList">{filtered.map(item => <button key={item.id} className={selected === item.id ? 'active' : ''} onClick={() => select(item.id)}><strong>{item.pretty_formula || item.formula}</strong><small>{item.mp_id} · #{item.id}</small></button>)}</div>
        {items.length === 0 && !listLoading && !listError && <p>No materials in this page.</p>}{filtered.length === 0 && items.length > 0 && <p>No matches among loaded materials. Load more or select by ID below.</p>}
        <button className="secondary" disabled={listLoading || items.length < offset + 100} onClick={() => setOffset(items.length)}>{listLoading ? 'Loading materials…' : 'Load more materials'}</button>
        <form onSubmit={e => { e.preventDefault(); const input = new FormData(e.currentTarget).get('id'); const id = Number(input); if (Number.isSafeInteger(id) && id > 0) select(id); }}><label htmlFor="directId">Know the local material ID?</label><div className="inline"><input id="directId" name="id" type="number" min="1" required placeholder="e.g. 5"/><button type="submit">Open</button></div></form>
      </aside>
      <section className="workspace">
        {!selected && <div className="panel welcome"><span className="eyebrow">A PLACE TO BEGIN</span><h2>Select a material to open its workspace.</h2><p>Each source identity stays distinct, even when two materials share a formula.</p></div>}
        {selected > 0 && <div className="panel details"><div className="sectionTitle"><span>02 / INSPECT</span><h2>Material identity</h2></div>
          {detailLoading && <p role="status">Loading material details…</p>}{detailError && <div role="alert" className="error">{detailError} <button onClick={() => setDetailRetry(n => n + 1)}>Retry</button></div>}
          {detail && <><div className="identity"><div><h3>{detail.pretty_formula || detail.formula}</h3><p>Source ID: {detail.mp_id} · Local ID: {detail.id}</p></div><span className="tag">{detail.source}</span></div><p className="hint">Reported fields from the material record. This endpoint does not supply field-level provenance, evidence quality, or measurement conditions. “Stable” is a stored flag; inspect energy above hull separately.</p><dl className="properties"><div><dt>Formula</dt><dd>{detail.formula}</dd></div><div><dt>Type</dt><dd>{detail.material_type ?? 'Unknown'}</dd></div><div><dt>Band gap</dt><dd>{value(detail.band_gap, ' eV')}</dd></div><div><dt>Energy above hull</dt><dd>{value(detail.energy_above_hull, ' eV/atom')}</dd></div><div><dt>Formation energy</dt><dd>{value(detail.formation_energy_per_atom, ' eV/atom')}</dd></div><div><dt>Density</dt><dd>{value(detail.density, ' g/cm³')}</dd></div><div><dt>Stored stability flag</dt><dd>{detail.is_stable ? 'Yes' : 'No'} · evidence basis not supplied here</dd></div><div><dt>Elements</dt><dd>{detail.elements.length ? detail.elements.map(e => `${e.symbol} (${e.name})`).join(', ') : 'None listed'}</dd></div></dl></>}
        </div>}
        {detail && <div className="panel discovery"><div className="sectionTitle"><span>03 / EXPLORE</span><h2>Discovery candidates</h2></div><p className="hint">Optional element preferences adjust scores. Avoid is a soft penalty, not an exclusion; prefer is a soft bonus. Results can include the selected element even when avoided.</p>
          <form className="filters" onSubmit={e => { e.preventDefault(); setRequest({ id: selected, avoid, prefer, sequence: (request?.sequence ?? 0) + 1 }); }}><label>Avoid element <input value={avoid} onChange={e => setAvoid(e.target.value)} maxLength={3} placeholder="e.g. Li"/></label><label>Prefer element <input value={prefer} onChange={e => setPrefer(e.target.value)} maxLength={3} placeholder="e.g. Na"/></label><button type="submit" disabled={candidateLoading}>{candidateLoading ? 'Searching…' : 'Find candidates →'}</button></form>
          {candidateLoading && <p role="status">Ranking candidates using current backend rules…</p>}{candidateError && <div role="alert" className="error">{candidateError} <button onClick={() => setRequest({ id: selected, avoid, prefer, sequence: (request?.sequence ?? 0) + 1 })}>Retry</button></div>}
          {result && <><p className="hint">{result.candidates.length} returned identities · backend order preserved. Dataset and methodology versions, evidence coverage, and completeness status are not supplied by this endpoint.</p>{result.discovery_warnings.map((warning, i) => <p className="warning" key={i} role="status">{warning}</p>)}{!result.candidates.length && <div className="empty">No candidates returned within this request. This does not establish that no alternatives exist.</div>}
            <ol className="candidateList">{result.candidates.map((candidate, index) => <li key={candidate.material_id} className="candidate"><div className="candidateHead"><div><span className="eyebrow">ITEM {index + 1} · SOURCE {candidate.mp_id ?? 'UNKNOWN'}</span><h3>{candidate.pretty_formula || candidate.formula}</h3></div><div className="score"><strong>{candidate.discovery_score.toLocaleString()}</strong><small>rule score</small></div></div><p>{candidate.explanation}</p><details><summary>Inspect score and reasoning</summary><dl className="breakdown">{Object.entries(candidate.score_breakdown).map(([name, amount]) => <div key={name}><dt>{name.replaceAll('_', ' ')}</dt><dd>{amount.toLocaleString()}</dd></div>)}</dl>{candidate.discovery_path.length > 0 && <p>Backend relationship signals: {candidate.discovery_path.map(signal => signal.replaceAll('_', ' ')).join(', ')}. These labels are not a verified transformation pathway.</p>}{candidate.substitution_path && <p>{candidate.substitution_path.reason} Composition heuristic; structural preservation and substitution mechanism are not validated.</p>}<p className="hint">Internal ranking does not establish synthesis feasibility, performance, or novelty.</p><button className="textButton" onClick={() => select(candidate.material_id)}>Inspect this material →</button></details></li>)}</ol></>}
        </div>}
      </section>
    </main><footer>MaterialGraph · Evidence and limits stay visible.</footer>
  </div>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
