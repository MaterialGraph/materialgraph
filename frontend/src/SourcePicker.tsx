import { useState } from 'react';
import type { Material } from './api';
import { ChemicalFormula } from './ChemicalFormula';
type Props = { selected: number; select: (id: number) => void; items: Material[]; offset: number; listError: string; listLoading: boolean; retryList: () => void; loadMore: () => void };
export function SourcePicker({ selected, select, items, offset, listError, listLoading, retryList, loadMore }: Props) {
  const [search, setSearch] = useState('');
  const filtered = items.filter(item => `${item.pretty_formula} ${item.formula} ${item.mp_id} ${item.id}`.toLowerCase().includes(search.toLowerCase()));
  return <>
      <aside className="panel picker"><div className="sectionTitle"><span>01 / SELECT</span><h2>Materials</h2></div><label htmlFor="search">Filter loaded materials</label><input id="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Formula, source ID, or local ID"/><p className="hint">Showing the first {items.length} identities in internal ID order. Load more to extend this list.</p>
        {listError && <div role="alert" className="error">{listError} <button onClick={() => retryList()}>Retry</button></div>}
        <div className="materialList">{filtered.map(item => <button key={item.id} className={selected === item.id ? 'active' : ''} onClick={() => select(item.id)}><strong><ChemicalFormula formula={item.pretty_formula || item.formula}/></strong><small>{item.mp_id} · #{item.id}</small></button>)}</div>
        {items.length === 0 && !listLoading && !listError && <p>No materials in this page.</p>}{filtered.length === 0 && items.length > 0 && <p>No matches among loaded materials. Load more or select by ID below.</p>}
        <button className="secondary" disabled={listLoading || items.length < offset + 100} onClick={() => loadMore()}>{listLoading ? 'Loading materials…' : 'Load more materials'}</button>
        <form onSubmit={e => { e.preventDefault(); const input = new FormData(e.currentTarget).get('id'); const id = Number(input); if (Number.isSafeInteger(id) && id > 0) select(id); }}><label htmlFor="directId">Know the local material ID?</label><div className="inline"><input id="directId" name="id" type="number" min="1" required placeholder="e.g. 5"/><button type="submit">Open</button></div></form>
      </aside>
  </>;
}
