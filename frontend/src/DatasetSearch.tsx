import { useEffect, useRef, useState, type FormEvent } from 'react';
import {
  ApiError, browseMaterials, datasetSummary, searchMaterials, SEARCH_PAGE_SIZE,
  type DatasetSummary, type Material, type MaterialSearchResponse, type SearchQueryProblem,
  type SearchRequestMode, type SearchResolvedMode, type SearchResult,
} from './api';
import { ChemicalFormula } from './ChemicalFormula';

export const modeLabels: Record<SearchRequestMode, string> = {
  auto: 'Auto',
  formula: 'Formula',
  chemsys: 'Chemical system',
  contains: 'Contains elements',
  mp_id: 'MP ID',
  material_id: 'Local ID',
};

const placeholders: Record<SearchRequestMode, string> = {
  auto: 'Formula, Li-Fe-P-O, mp-19017 or #5',
  formula: 'e.g. LiFePO4 (case-sensitive)',
  chemsys: 'e.g. Li-Fe-P-O (exactly these elements)',
  contains: 'e.g. Na, Fe (at least these elements)',
  mp_id: 'e.g. mp-19017',
  material_id: 'e.g. 5 or #5',
};

const compositionModes = new Set(['formula', 'chemsys', 'contains']);

type Draft = { query: string; mode: SearchRequestMode };
/** The last submitted search, or null for browsing the whole dataset. */
type Committed = Draft | null;
type Pages = { rows: SearchResult[]; response: MaterialSearchResponse | null; lastPageSize: number };
type Problem = { message: string; code?: string; input?: string; hint?: string | null; mode?: SearchResolvedMode | null; requestedMode?: SearchRequestMode };

const initialDraft: Draft = { query: '', mode: 'auto' };
const noPages: Pages = { rows: [], response: null, lastPageSize: 0 };

/** Energy above hull as given by the API, at three decimals; never styled by value. */
export function formatEnergy(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return 'Energy above hull: not supplied';
  let text: string;
  if (value === 0) text = '0.000';
  else if (value > 0) text = value < 0.0005 ? '<0.001' : value.toFixed(3);
  else text = value > -0.0005 ? '>−0.001' : `−${(-value).toFixed(3)}`;
  return `Energy above hull: ${text} eV/atom`;
}

export function interpretationText(response: MaterialSearchResponse): string {
  const { interpretation } = response;
  if (interpretation.mode === 'material_id') return `local material ID ${interpretation.material_id}`;
  if (interpretation.mode === 'mp_id') return `MP ID ${interpretation.mp_id}`;
  if (interpretation.mode === 'formula') return `formula ${interpretation.reduced_formula} (elements: ${(interpretation.elements ?? []).join(', ')})`;
  if (interpretation.mode === 'chemsys') return `exactly the elements ${(interpretation.elements ?? []).join(', ')}`;
  return `at least the elements ${(interpretation.elements ?? []).join(', ')}`;
}

function countText(response: MaterialSearchResponse): string {
  return `${response.total_matches} ${response.total_matches === 1 ? 'match' : 'matches'} among ${response.dataset_total} materials in the dataset.`;
}

function toProblem(error: unknown): Problem {
  if (error instanceof ApiError) {
    const detail = error.details as Partial<SearchQueryProblem> | undefined;
    if (error.status === 422 && detail && typeof detail === 'object' && 'explanation' in detail) {
      return { message: error.message, code: detail.code, input: detail.input, hint: detail.hint, mode: detail.mode, requestedMode: detail.requested_mode };
    }
    return { message: error.message };
  }
  return { message: 'Search failed.' };
}

const toRow = (item: Material): SearchResult => ({
  material_id: item.id, mp_id: item.mp_id, formula: item.formula,
  pretty_formula: item.pretty_formula, energy_above_hull: item.energy_above_hull,
});

function Provenance({ dataset }: { dataset: DatasetSummary }) {
  return <p className="hint">Values computed by Materials Project. {dataset.provenance_note}{' '}
    {dataset.source_release
      ? `Most recent recorded import: Materials Project release ${dataset.source_release}.`
      : 'The Materials Project release is not recorded in this database.'}</p>;
}

type RowProps = { item: SearchResult; selected: number; select: (id: number) => void; rowRef?: (node: HTMLButtonElement | null) => void };
function MaterialRow({ item, selected, select, rowRef }: RowProps) {
  const active = item.material_id === selected;
  return <button type="button" ref={rowRef} className={active ? 'materialRow active' : 'materialRow'} aria-current={active ? 'true' : undefined} onClick={() => select(item.material_id)}>
    <strong><ChemicalFormula formula={item.pretty_formula || item.formula}/></strong>
    <small>{item.mp_id} · #{item.material_id}</small>
    <small className="energy">{formatEnergy(item.energy_above_hull)}</small>
  </button>;
}

type Active = { id: number; controller: AbortController };

export function DatasetSearch({ selected, select }: { selected: number; select: (id: number) => void }) {
  const [draft, setDraft] = useState<Draft>(initialDraft);
  const [committed, setCommitted] = useState<Committed>(null);
  const [pages, setPages] = useState<Pages>(noPages);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [error, setError] = useState<Problem | null>(null);
  const [pageStatus, setPageStatus] = useState<'idle' | 'loading' | 'error'>('idle');
  const [pageError, setPageError] = useState('');
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [summaryStatus, setSummaryStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [focusIndex, setFocusIndex] = useState<number | null>(null);
  const counter = useRef(0);
  const listRequest = useRef<Active | null>(null);
  const summaryRequest = useRef<Active | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const rows = useRef<(HTMLButtonElement | null)[]>([]);

  function begin(slot: { current: Active | null }): Active {
    slot.current?.controller.abort();
    const next = { id: ++counter.current, controller: new AbortController() };
    slot.current = next;
    return next;
  }

  async function fetchPage(target: Committed, offset: number) {
    const request = begin(listRequest);
    if (offset === 0) { setStatus('loading'); setError(null); setPageStatus('idle'); }
    else { setPageStatus('loading'); setPageError(''); }
    try {
      const page = target
        ? await searchMaterials(target.mode, target.query, offset, request.controller.signal).then(response => ({ rows: response.results, response }))
        : await browseMaterials(offset, request.controller.signal).then(items => ({ rows: items.map(toRow), response: null }));
      if (listRequest.current?.id !== request.id) return;
      setPages(previous => offset === 0
        ? { rows: page.rows, response: page.response, lastPageSize: page.rows.length }
        : { rows: [...previous.rows, ...page.rows], response: previous.response, lastPageSize: page.rows.length });
      if (offset === 0) setStatus('ready');
      else { setPageStatus('idle'); setFocusIndex(offset); }
    } catch (failure) {
      // An aborted or superseded request is never shown.
      if (request.controller.signal.aborted || listRequest.current?.id !== request.id) return;
      if (offset === 0) { setStatus('error'); setError(toProblem(failure)); }
      else { setPageStatus('error'); setPageError(toProblem(failure).message); }
    }
  }

  async function fetchSummary() {
    const request = begin(summaryRequest);
    setSummary(null); setSummaryStatus('loading');
    try {
      const next = await datasetSummary(request.controller.signal);
      if (summaryRequest.current?.id !== request.id) return;
      setSummary(next); setSummaryStatus('ready');
    } catch {
      if (request.controller.signal.aborted || summaryRequest.current?.id !== request.id) return;
      setSummaryStatus('error');
    }
  }

  function browse() {
    setCommitted(null); setDraft(initialDraft); setPages(noPages);
    void fetchPage(null, 0);
    void fetchSummary();
  }

  useEffect(() => {
    void fetchPage(null, 0);
    void fetchSummary();
    return () => { listRequest.current?.controller.abort(); summaryRequest.current?.controller.abort(); };
    // Initial entry into browse only; later requests are started by user actions.
  }, []);

  useEffect(() => {
    if (focusIndex === null) return;
    rows.current[focusIndex]?.focus();
    setFocusIndex(null);
  }, [focusIndex, pages]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    input.current?.focus();
    if (!draft.query.trim()) { browse(); return; }
    const next = { ...draft };
    setCommitted(next); setPages(noPages);
    void fetchPage(next, 0);
  }

  function showMore() {
    if (pageStatus !== 'idle') return;
    void fetchPage(committed, pages.rows.length);
  }
  /** Refetches the failed page of the committed search at the same offset. */
  function retryPage() {
    if (pageStatus === 'error') void fetchPage(committed, pages.rows.length);
  }

  const response = pages.response;
  const stale = committed !== null && (draft.query !== committed.query || draft.mode !== committed.mode);
  const total = committed ? response?.total_matches : summary?.dataset_total;
  const hasMore = status === 'ready' && (committed
    ? response !== null && pages.rows.length < response.total_matches
    : pages.lastPageSize === SEARCH_PAGE_SIZE && (summary === null || pages.rows.length < summary.dataset_total));
  const showing = pages.rows.length > 0 ? `Showing 1–${pages.rows.length}${total !== undefined ? ` of ${total}` : ''}` : '';
  const announcement = status === 'loading'
    ? (committed ? 'Searching the full dataset…' : 'Loading materials…')
    : status === 'ready' && committed && response ? `Interpreted as ${interpretationText(response)}. ${countText(response)}` : '';
  rows.current = [];

  return <section className="datasetSearch" aria-label="Search the full dataset">
    <form onSubmit={submit} className="datasetSearchForm">
      <label htmlFor="datasetSearchQuery">Search the full dataset</label>
      <input id="datasetSearchQuery" ref={input} aria-label="Dataset search query" maxLength={100} value={draft.query}
        onChange={event => setDraft({ ...draft, query: event.target.value })} placeholder={placeholders[draft.mode]}/>
      <div className="datasetSearchControls">
        <select id="datasetSearchMode" aria-label="Search mode" value={draft.mode} onChange={event => setDraft({ ...draft, mode: event.target.value as SearchRequestMode })}>
          {(Object.keys(modeLabels) as SearchRequestMode[]).map(key => <option key={key} value={key}>{modeLabels[key]}</option>)}
        </select>
        <button type="submit">Search</button>
      </div>
    </form>
    <div className="datasetSearchHeader">
      <p className="visuallyHidden" role="status" aria-live="polite">{announcement}</p>
      {committed && status === 'ready' && response && <>
        <p className="hint" aria-hidden="true">Interpreted as {interpretationText(response)}. {countText(response)}</p>
        <p className="hint">Ordered by local ID.</p>
        <Provenance dataset={response.dataset}/>
        {compositionModes.has(response.interpretation.mode) && response.dataset.composition_exclusion_count > 0 &&
          <p className="hint">{response.dataset.composition_exclusion_count} materials could not be searched by composition; MP ID and local ID search still find them.</p>}
      </>}
      {!committed && status !== 'error' && <>
        <p className="hint">All materials in the dataset, ordered by local ID.{showing && ` ${showing}`}</p>
        {summaryStatus === 'ready' && summary && <Provenance dataset={summary}/>}
        {summaryStatus === 'error' && <div className="error summaryError" role="alert">Dataset information unavailable <button type="button" onClick={() => void fetchSummary()}>Retry</button></div>}
      </>}
      {committed && <p className="hint">{status === 'ready' && showing && `${showing}. `}<button type="button" className="textButton" onClick={browse}>Clear search</button></p>}
      {stale && <p className="hint stale">These results belong to the previous search: <code>{committed.query}</code> ({modeLabels[committed.mode]}).</p>}
    </div>
    {status === 'error' && error && <div className="error" role="alert">
      {/* The input as the server received it, shown beside the explanation; never rewritten. */}
      {error.input !== undefined && <p className="searchInput">Input: <code>{error.input}</code></p>}
      <p>{error.message}{error.code && <small> ({error.code})</small>}</p>
      {error.requestedMode === 'auto' && error.mode && <p className="searchHint">Searched as {modeLabels[error.mode]} (detected automatically).</p>}
      {error.hint && <p className="searchHint">{error.hint}</p>}
      {!error.code && <button type="button" onClick={() => void fetchPage(committed, 0)}>Retry</button>}
    </div>}
    <div className="datasetSearchScroll">
      {status === 'ready' && committed && response && response.total_matches === 0 && response.scoped_message && <p className="scopedMessage">{response.scoped_message}</p>}
      {status === 'ready' && !committed && pages.rows.length === 0 && <p className="hint">No materials in the dataset.</p>}
      {pages.rows.length > 0 && <div className="materialList">{pages.rows.map((item, index) =>
        <MaterialRow key={item.material_id} item={item} selected={selected} select={select} rowRef={node => { rows.current[index] = node; }}/>)}</div>}
      {pageStatus === 'error' && <div className="error" role="alert">{pageError} <button type="button" onClick={retryPage}>Retry</button></div>}
      {hasMore && pageStatus !== 'error' && <button type="button" className="secondary" disabled={pageStatus === 'loading'} onClick={showMore}>{pageStatus === 'loading' ? 'Loading…' : 'Show more'}</button>}
      {status === 'ready' && response?.suggestions && <div className="datasetSearchSuggestions">
        <p className="suggestionLabel">Same elements, different proportions</p>
        <p className="hint">{response.suggestions.explanation}</p>
        {response.suggestion_total !== null && response.suggestion_total > response.suggestions.results.length &&
          <p className="hint">Showing {response.suggestions.results.length} of {response.suggestion_total}</p>}
        <div className="materialList">{response.suggestions.results.map(item =>
          <MaterialRow key={item.material_id} item={item} selected={selected} select={select}/>)}</div>
      </div>}
    </div>
  </section>;
}
