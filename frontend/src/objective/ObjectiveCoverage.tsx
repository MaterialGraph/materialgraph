import type { AvoidCoverageStatus, ChainAvoidanceDetail, ChainElementCoverage, MaterialElementCoverage, ObjectiveCoverage, PreferCoverageStatus } from './contract';

// Renders backend-computed objective coverage (contract version 1) as a compact
// matrix. No formula parsing or status derivation happens in the client.

type Tone = 'positive' | 'caution' | 'neutral' | 'unknown';
type Cell = { icon: string; label: string; tone: Tone; count: string | null; notEvaluated: number };

const preferStyle: Record<PreferCoverageStatus, { icon: string; label: string; tone: Tone }> = {
  represented: { icon: '✓', label: 'Represented', tone: 'positive' },
  not_represented: { icon: '✕', label: 'Not represented', tone: 'neutral' },
  not_evaluated: { icon: '?', label: 'Not evaluated', tone: 'unknown' },
};
const avoidStyle: Record<AvoidCoverageStatus, { icon: string; label: string; tone: Tone }> = {
  present: { icon: '⚠', label: 'Present', tone: 'caution' },
  not_observed: { icon: '–', label: 'Not observed', tone: 'neutral' },
  not_evaluated: { icon: '?', label: 'Not evaluated', tone: 'unknown' },
};

export function preferCell(entry: MaterialElementCoverage<PreferCoverageStatus>): Cell {
  const style = preferStyle[entry.status];
  return { ...style, count: entry.status === 'not_evaluated' ? null : `${entry.containing_count}/${entry.evaluated_count}`, notEvaluated: entry.not_evaluated_count };
}

export function avoidMaterialCell(entry: MaterialElementCoverage<AvoidCoverageStatus>): Cell {
  const style = avoidStyle[entry.status];
  return { ...style, count: entry.status === 'not_evaluated' ? null : `${entry.containing_count}/${entry.evaluated_count}`, notEvaluated: entry.not_evaluated_count };
}

export function avoidChainCell(entry: ChainElementCoverage): Cell {
  const style = avoidStyle[entry.status];
  const count = entry.status === 'not_evaluated' ? null
    : entry.status === 'present' ? `${entry.containing_chain_count}/${entry.total_chain_count}`
    : `0/${entry.evaluated_chain_count}`;
  return { ...style, count, notEvaluated: entry.not_evaluated_chain_count };
}

function ChainLinks({ positions }: { positions: number[] }) {
  return <>{positions.map((position, n) => <span key={position}>{n > 0 && ' '}<a href={`#objective-path-${position}`} aria-label={`Returned chain ${position}`}>{position}</a></span>)}</>;
}

function CoverageCell({ cell, chains }: { cell: Cell; chains?: number[] }) {
  return <td>
    <span className={`coverageStatus coverageStatus-${cell.tone}`}><span aria-hidden="true">{cell.icon}</span> {cell.label}</span>
    {cell.count && <span className="coverageCount">{cell.count}</span>}
    {chains && chains.length > 0 && <span className="coverageChains">chains <ChainLinks positions={chains}/></span>}
    {cell.notEvaluated > 0 && <span className="coverageIncomplete">+{cell.notEvaluated} not evaluated</span>}
  </td>;
}

function sourceText(coverage: ObjectiveCoverage): string {
  const present = coverage.source_material.avoided_elements_present;
  const id = `local ID ${coverage.source_material.material_id}`;
  if (present === null) return `Source material (${id}): composition not evaluated; excluded from chain counts.`;
  if (present.length) return `Source material (${id}) contains ${present.join(', ')} — excluded from chain counts.`;
  return `Source material (${id}) is excluded from chain counts.`;
}

const termLabel: Record<ObjectiveCoverage['terms_not_evaluated'][number], string> = {
  preserve_elements: 'elements to retain', target_family: 'target composition family',
};

const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;

export function ObjectiveCoveragePanel({ coverage }: { coverage?: ObjectiveCoverage }) {
  if (!coverage) {
    return <section className="objectiveCoverage" aria-label="Objective coverage in returned results">
      <h3>Objective coverage in returned results</h3>
      <p className="hint">Objective coverage is not available from this backend version. Inspect the ranked materials and returned chains below.</p>
    </section>;
  }
  const chainByElement = new Map(coverage.avoided_elements_in_returned_chains.map(entry => [entry.element, entry]));
  const rows = [
    ...coverage.preferred_elements.map(entry => ({ key: `prefer-${entry.element}`, element: entry.element, goal: 'Prefer', ranked: preferCell(entry), chain: null as ChainElementCoverage | null })),
    ...coverage.avoided_elements_in_ranked_materials.map(entry => ({ key: `avoid-${entry.element}`, element: entry.element, goal: 'Avoid', ranked: avoidMaterialCell(entry), chain: chainByElement.get(entry.element) ?? null })),
  ];
  return <section className="objectiveCoverage" aria-label="Objective coverage in returned results">
    <h3>Objective coverage in returned results</h3>
    <p className="objectiveCoverageMode">{coverage.avoid_policy_explanation}</p>
    {rows.length === 0 ? <p className="hint">No preferred or avoided elements were requested.</p> :
      <div className="coverageTableWrap"><table className="coverageTable">
        <caption className="visuallyHidden">Objective coverage by element. Counts {plural(coverage.returned_ranked_material_count, 'returned ranked material', 'returned ranked materials')} and {plural(coverage.returned_chain_count, 'returned chain', 'returned chains')}; the source material is excluded from chain counts.</caption>
        <thead><tr>
          <th scope="col">Element</th><th scope="col">Goal</th>
          <th scope="col">Returned ranked materials <span className="coverageDenominator">({coverage.returned_ranked_material_count})</span></th>
          <th scope="col">Returned chains <span className="coverageDenominator">({coverage.returned_chain_count}, source excluded)</span></th>
        </tr></thead>
        <tbody>{rows.map(row => <tr key={row.key}>
          <th scope="row">{row.element}</th>
          <td className="coverageGoal">{row.goal}</td>
          <CoverageCell cell={row.ranked}/>
          {row.chain ? <CoverageCell cell={avoidChainCell(row.chain)} chains={row.chain.chain_positions}/>
            : <td className="coverageNotApplicable"><span aria-hidden="true">—</span><span className="visuallyHidden">Not assessed for chains</span></td>}
        </tr>)}</tbody>
      </table></div>}
    <p className="coverageFootnote">{sourceText(coverage)}{coverage.terms_not_evaluated.length > 0 && <> Not evaluated in this summary: {coverage.terms_not_evaluated.map(term => termLabel[term]).join(', ')}.</>} Element presence is read from reported formulas.</p>
    <details className="coverageLimitations"><summary>Coverage limitations</summary><ul>{coverage.limitations.map((limitation, n) => <li key={n}>{limitation}</li>)}</ul></details>
  </section>;
}

export function ChainAvoidanceNote({ detail }: { detail?: ChainAvoidanceDetail }) {
  if (!detail) return null;
  const flagged = detail.materials_with_avoided_elements;
  const elements = [...new Set(flagged.flatMap(m => m.avoided_elements))];
  return <>
    {flagged.length > 0 && <p className="objectiveChainAvoidance" role="note"><span aria-hidden="true">⚠ </span>Contains avoided {elements.length === 1 ? 'element' : 'elements'} in {flagged.map(m => `${m.role} material (local ID ${m.material_id}): ${m.avoided_elements.join(', ')}`).join('; ')}. Source material excluded.</p>}
    {detail.not_evaluated_material_ids.length > 0 && <p className="hint">Composition not evaluated for local ID {detail.not_evaluated_material_ids.join(', ')}.</p>}
  </>;
}

export function materialAvoidanceLabel(detail: ChainAvoidanceDetail | undefined, materialId: number): string | null {
  if (!detail) return null;
  const hit = detail.materials_with_avoided_elements.find(m => m.material_id === materialId);
  if (hit) return `Contains avoided ${hit.avoided_elements.length === 1 ? 'element' : 'elements'}: ${hit.avoided_elements.join(', ')}`;
  if (detail.not_evaluated_material_ids.includes(materialId)) return 'Composition not evaluated';
  return null;
}
