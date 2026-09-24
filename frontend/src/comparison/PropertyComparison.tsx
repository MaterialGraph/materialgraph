import { useEffect, useState, type FormEvent } from 'react';
import { materialDetail, type MaterialDetail } from '../api';
import { ChemicalFormula } from '../ChemicalFormula';
import { arithmeticDifference, formatNumber, parseSelection, properties, type ColumnState } from './model';
import type { ComparisonLaunchContext } from './launch';

const methodology = 'Reported property values reflect independent material records, not a validated phase transformation pathway. Differences between records do not establish structural preservation, synthesis feasibility, or application performance. Matching units do not establish that the underlying methods or conditions are comparable.';

export async function loadColumn(id: number, signal: AbortSignal, report: (state: ColumnState) => void): Promise<void> {
  try {
    const material = await materialDetail(id, signal);
    if (!signal.aborted) report({ status: 'success', id, material });
  } catch (error) {
    if (!signal.aborted) report({ status: 'error', id, message: error instanceof Error ? error.message : 'Request failed.' });
  }
}

export function useComparisonColumn(id: number): ColumnState & { retry: () => void } {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<ColumnState>({ status: 'loading', id });
  useEffect(() => {
    const controller = new AbortController();
    setState({ status: 'loading', id });
    void loadColumn(id, controller.signal, setState);
    return () => controller.abort();
  }, [id, attempt]);
  return { ...state, retry: () => setAttempt(value => value + 1) };
}

type Column = ColumnState & { retry: () => void };
type Props = { source: Column; candidates: Column[]; launchContext?: string };

function identity(column: Column, role: string) {
  if (column.status !== 'success') return <><strong>{role} · Local ID {column.id}</strong><span className="comparisonState" role="status">{column.status === 'loading' ? 'Loading' : 'API Error'}</span>{column.status === 'error' && <><small>{column.message}</small><button type="button" onClick={event => { event.currentTarget.closest<HTMLElement>('[role="region"]')?.focus(); column.retry(); }}>Retry fetch</button></>}</>;
  const material = column.material;
  return <><strong>{role} · <ChemicalFormula formula={material.pretty_formula || material.formula}/></strong><small>{material.mp_id} · Local ID {material.id}</small><small>Record source: {material.source}</small></>;
}

function numericCell(column: Column, source: MaterialDetail | null, field: (typeof properties)[number]['field'], unit: string, candidate: boolean) {
  if (column.status !== 'success') return <span className="comparisonState">{column.status === 'loading' ? 'Loading' : 'API Error'}</span>;
  const value = column.material[field];
  if (value === null) return <span className="comparisonState">Unknown</span>;
  const delta = candidate ? arithmeticDifference(source, column.material, field) : null;
  return <><span className="comparisonNumber">{formatNumber(value)}</span><span className="comparisonState">Available</span>
    {candidate && <small className="comparisonDifference">Arithmetic difference from source: {delta === null ? 'Unavailable' : `${delta > 0 ? '+' : ''}${formatNumber(delta)} ${unit}`}</small>}</>;
}

export function ComparisonTable({ source, candidates, launchContext }: Props) {
  const columns = [source, ...candidates];
  const sourceMaterial = source.status === 'success' ? source.material : null;
  return <section className="panel propertyComparison" aria-label="Source-first property comparison">
    <div className="sectionTitle"><span>05 / COMPARE</span><h2>Reported properties</h2></div>
    <p className="hint">Source-relative arithmetic inspection of independently fetched material records. No candidate ranking is implied.</p>
    <div className="comparisonScroll" role="region" aria-label="Property comparison table" tabIndex={0}>
      <table><caption>Source-first property comparison. Numerical differences are candidate minus source.</caption><thead><tr><th scope="col">Property</th>{columns.map((column, index) => <th scope="col" key={index}>{identity(column, index ? 'Candidate' : 'Source')}</th>)}</tr></thead>
        <tbody>{properties.map(({ field, label, unit }) => <tr key={field}><th scope="row">{label}<small>{unit}</small></th>{columns.map((column, index) => <td key={index}>{numericCell(column, sourceMaterial, field, unit, index > 0)}</td>)}</tr>)}
          <tr><th scope="row">Stored stability classification<small>Basis not supplied by this endpoint.</small></th>{columns.map((column, index) => <td key={index}>{column.status === 'success' ? <><span>{column.material.is_stable ? 'Yes' : 'No'}</span><span className="comparisonState">Available stored classification</span></> : <span className="comparisonState">{column.status === 'loading' ? 'Loading' : 'API Error'}</span>}</td>)}</tr>
          <tr><th scope="row">Material type</th>{columns.map((column, index) => <td key={index}>{column.status === 'success' ? column.material.material_type ?? 'Unknown' : column.status === 'loading' ? 'Loading' : 'API Error'}</td>)}</tr>
          <tr><th scope="row">Elements listed</th>{columns.map((column, index) => <td key={index}>{column.status === 'success' ? column.material.elements.length ? column.material.elements.map(element => element.symbol).join(', ') : 'No elements listed' : column.status === 'loading' ? 'Loading' : 'API Error'}</td>)}</tr>
        </tbody></table>
    </div>
    <p className="comparisonMethodology">{methodology}</p>
    <div className="comparisonContext"><strong>Investigation context</strong><p>Source ID {source.id} · Selected material IDs: {candidates.map(column => column.id).join(', ')}{launchContext ? ` · ${launchContext}` : ''}. This is client request context, not scientific provenance. Values reflect current backend responses.</p></div>
  </section>;
}

function LoadedComparison({ sourceId, candidateIds, launchContext }: { sourceId: number; candidateIds: number[]; launchContext?: string }) {
  // Keys remount columns on selection change. Abort cleanup blocks stale responses.
  return candidateIds.length === 3
    ? <ThreeCandidates key={[sourceId, ...candidateIds].join(':')} sourceId={sourceId} candidateIds={candidateIds} launchContext={launchContext}/>
    : <TwoCandidates key={[sourceId, ...candidateIds].join(':')} sourceId={sourceId} candidateIds={candidateIds} launchContext={launchContext}/>;
}
function TwoCandidates({ sourceId, candidateIds, launchContext }: { sourceId: number; candidateIds: number[]; launchContext?: string }) {
  const source = useComparisonColumn(sourceId);
  const first = useComparisonColumn(candidateIds[0]);
  const second = useComparisonColumn(candidateIds[1]);
  return <ComparisonTable source={source} candidates={[first, second]} launchContext={launchContext}/>;
}
function ThreeCandidates({ sourceId, candidateIds, launchContext }: { sourceId: number; candidateIds: number[]; launchContext?: string }) {
  const source = useComparisonColumn(sourceId);
  const first = useComparisonColumn(candidateIds[0]);
  const second = useComparisonColumn(candidateIds[1]);
  const third = useComparisonColumn(candidateIds[2]);
  return <ComparisonTable source={source} candidates={[first, second, third]} launchContext={launchContext}/>;
}

export function WorkflowComparison({ launch }: { launch: ComparisonLaunchContext }) {
  const roleContext = launch.selectedMaterials.map(material => `${material.formula} (local ID ${material.id}): ${material.role}`).join('; ');
  return <LoadedComparison sourceId={launch.sourceMaterialId} candidateIds={launch.selectedMaterials.map(material => material.id)} launchContext={`${launch.investigationContext} Selected result roles: ${roleContext}`}/>;
}

export function PropertyComparisonWorkspace() {
  const [source, setSource] = useState('5');
  const [first, setFirst] = useState('6');
  const [second, setSecond] = useState('7');
  const [third, setThird] = useState('');
  const [selection, setSelection] = useState<{ sourceId: number; candidateIds: number[] } | null>(null);
  const [error, setError] = useState('');
  function submit(event: FormEvent) {
    event.preventDefault();
    try { setSelection(parseSelection(source, [first, second, third])); setError(''); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Check material IDs.'); }
  }
  return <section className="comparisonWorkspace" aria-label="Standalone comparison workspace">
    <h2>Property comparison workspace</h2><p className="hint">Enter local material IDs. This standalone workspace has no selection connection to Discovery or Objective Investigation.</p>
    <form className="comparisonLauncher" onSubmit={submit}><label>Source ID<input value={source} onChange={event => setSource(event.target.value)} inputMode="numeric"/></label><label>Candidate ID<input value={first} onChange={event => setFirst(event.target.value)} inputMode="numeric"/></label><label>Candidate ID<input value={second} onChange={event => setSecond(event.target.value)} inputMode="numeric"/></label><label>Third candidate ID (optional)<input value={third} onChange={event => setThird(event.target.value)} inputMode="numeric"/></label><button type="submit">Load comparison</button></form>
    {error && <p role="alert" className="error">{error}</p>}
    {selection && <LoadedComparison sourceId={selection.sourceId} candidateIds={selection.candidateIds}/>}
  </section>;
}
