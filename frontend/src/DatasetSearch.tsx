import { useState, type FormEvent } from 'react';
import { ApiError, searchMaterials, type MaterialSearchResponse, type SearchMode, type SearchResult } from './api';
import { ChemicalFormula } from './ChemicalFormula';

const modeLabels: Record<SearchMode, string> = {
  formula: 'Formula',
  mp_id: 'MP ID',
  chemsys: 'Chemical system',
  contains: 'Contains elements',
};

const placeholders: Record<SearchMode, string> = {
  formula: 'e.g. LiFePO4 (case-sensitive)',
  mp_id: 'e.g. mp-19017',
  chemsys: 'e.g. Li-Fe-P-O (exactly these elements)',
  contains: 'e.g. Na, Fe (at least these elements)',
};

/** Suggests a mode for the typed text. It never switches mode or rewrites the query. */
export function suggestedMode(mode: SearchMode, text: string): SearchMode | null {
  const value = text.trim();
  if (mode !== 'mp_id' && /^mp-\d+$/.test(value)) return 'mp_id';
  if (mode === 'formula' && /^[A-Z][a-z]?(-[A-Z][a-z]?)+$/.test(value)) return 'chemsys';
  return null;
}

type State =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; message: string; code?: string }
  | { status: 'done'; response: MaterialSearchResponse; results: SearchResult[] };

function interpretationText(response: MaterialSearchResponse): string {
  const { interpretation } = response;
  if (interpretation.mode === 'mp_id') return `MP ID ${interpretation.mp_id}`;
  if (interpretation.mode === 'formula') return `formula ${interpretation.reduced_formula} (elements: ${(interpretation.elements ?? []).join(', ')})`;
  if (interpretation.mode === 'chemsys') return `exactly the elements ${(interpretation.elements ?? []).join(', ')}`;
  return `at least the elements ${(interpretation.elements ?? []).join(', ')}`;
}

export function DatasetSearch({ select, loadedIds }: { select: (id: number) => void; loadedIds: Set<number> }) {
  const [mode, setMode] = useState<SearchMode>('formula');
  const [query, setQuery] = useState('');
  const [state, setState] = useState<State>({ status: 'idle' });
  const suggestion = suggestedMode(mode, query);

  async function run(offset: number) {
    const previous = state.status === 'done' && offset > 0 ? state.results : [];
    setState({ status: 'loading' });
    try {
      const response = await searchMaterials(mode, query, offset);
      setState({ status: 'done', response, results: [...previous, ...response.results] });
    } catch (error) {
      if (error instanceof ApiError) {
        const detail = error.details as { code?: string } | undefined;
        setState({ status: 'error', message: error.message, code: detail?.code });
      } else setState({ status: 'error', message: 'Search failed.' });
    }
  }
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (query.trim()) void run(0); }

  return <section className="datasetSearch" aria-label="Search the full dataset">
    <form onSubmit={submit}>
      <label htmlFor="datasetSearchMode">Search the full dataset by</label>
      <div className="inline">
        <select id="datasetSearchMode" value={mode} onChange={event => setMode(event.target.value as SearchMode)}>
          {(Object.keys(modeLabels) as SearchMode[]).map(key => <option key={key} value={key}>{modeLabels[key]}</option>)}
        </select>
        <input aria-label="Dataset search query" maxLength={100} value={query} onChange={event => setQuery(event.target.value)} placeholder={placeholders[mode]}/>
        <button type="submit" disabled={state.status === 'loading'}>Search</button>
      </div>
      {suggestion && <p className="hint">This looks like a search by {modeLabels[suggestion]}. <button type="button" className="textButton" onClick={() => setMode(suggestion)}>Use {modeLabels[suggestion]} mode</button></p>}
    </form>
    {state.status === 'loading' && <p role="status">Searching the full dataset…</p>}
    {state.status === 'error' && <p className="error" role="alert">{state.message}{state.code && <small> ({state.code})</small>}</p>}
    {state.status === 'done' && <div className="datasetSearchResults">
      <p className="hint">Interpreted as {interpretationText(state.response)}. {state.response.total_matches} {state.response.total_matches === 1 ? 'match' : 'matches'} among {state.response.dataset_total} materials in the dataset.</p>
      {state.response.message && <p>{state.response.message}</p>}
      {state.results.length > 0 && <div className="materialList">{state.results.map(item => <button key={item.material_id} onClick={() => select(item.material_id)}>
        <strong><ChemicalFormula formula={item.pretty_formula || item.formula}/></strong>
        <small>{item.mp_id} · #{item.material_id}{!loadedIds.has(item.material_id) && ' · in the dataset, not yet loaded in the list'}</small>
      </button>)}</div>}
      {state.results.length < state.response.total_matches && <button type="button" className="secondary" onClick={() => void run(state.results.length)}>Show more matches</button>}
      {state.response.suggestions && <div className="datasetSearchSuggestions"><p className="hint">{state.response.suggestions.explanation}</p>
        <div className="materialList">{state.response.suggestions.results.map(item => <button key={item.material_id} onClick={() => select(item.material_id)}>
          <strong><ChemicalFormula formula={item.pretty_formula || item.formula}/></strong><small>Same elements, different proportions · {item.mp_id} · #{item.material_id}</small>
        </button>)}</div></div>}
    </div>}
  </section>;
}
