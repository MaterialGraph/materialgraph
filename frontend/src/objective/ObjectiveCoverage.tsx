import type { AvoidCoverageStatus, ChainAvoidanceDetail, ChainElementCoverage, MaterialElementCoverage, ObjectiveCoverage, PreferCoverageStatus } from './contract';

// Renders backend-computed objective coverage (contract version 1) verbatim.
// No formula parsing or status derivation happens in the client.

const preferLabel: Record<PreferCoverageStatus, string> = {
  represented: 'Represented', not_represented: 'Not represented', not_evaluated: 'Not evaluated',
};
const avoidLabel: Record<AvoidCoverageStatus, string> = {
  present: 'Present', not_observed: 'Not observed', not_evaluated: 'Not evaluated',
};

const materials = (n: number) => `returned ranked ${n === 1 ? 'material' : 'materials'}`;
const chains = (n: number) => `returned ${n === 1 ? 'chain' : 'chains'}`;
const notEvaluatedNote = (n: number, unit: string) => n > 0 ? ` ${n} ${unit} not evaluated (formula missing or not parseable).` : '';

export function preferText(entry: MaterialElementCoverage<PreferCoverageStatus>): string {
  const base = `Prefer ${entry.element} — `;
  if (entry.status === 'not_evaluated') return `${base}Not evaluated: no returned ranked material could be evaluated.`;
  const counted = entry.status === 'represented'
    ? `Represented in ${entry.containing_count} of ${entry.evaluated_count} evaluated ${materials(entry.evaluated_count)}.`
    : `Not represented in ${entry.evaluated_count} evaluated ${materials(entry.evaluated_count)}.`;
  return base + counted + notEvaluatedNote(entry.not_evaluated_count, entry.not_evaluated_count === 1 ? 'material' : 'materials');
}

export function avoidMaterialText(entry: MaterialElementCoverage<AvoidCoverageStatus>): string {
  const base = `Avoid ${entry.element} (ranked materials) — `;
  if (entry.status === 'not_evaluated') return `${base}Not evaluated: no returned ranked material could be evaluated.`;
  const counted = entry.status === 'present'
    ? `Present in ${entry.containing_count} of ${entry.evaluated_count} evaluated ${materials(entry.evaluated_count)}.`
    : `Not observed in ${entry.evaluated_count} evaluated ${materials(entry.evaluated_count)}.`;
  return base + counted + notEvaluatedNote(entry.not_evaluated_count, entry.not_evaluated_count === 1 ? 'material' : 'materials');
}

export function avoidChainText(entry: ChainElementCoverage): string {
  const base = `Avoid ${entry.element} (returned chains, source excluded) — `;
  if (entry.status === 'not_evaluated') return `${base}Not evaluated: no returned chain could be fully evaluated.`;
  const counted = entry.status === 'present'
    ? `Present in ${entry.containing_chain_count} of ${entry.total_chain_count} ${chains(entry.total_chain_count)}.`
    : `Not observed in ${entry.evaluated_chain_count} evaluated ${chains(entry.evaluated_chain_count)}.`;
  return base + counted + notEvaluatedNote(entry.not_evaluated_chain_count, entry.not_evaluated_chain_count === 1 ? 'chain' : 'chains');
}

function sourceText(coverage: ObjectiveCoverage): string {
  const present = coverage.source_material.avoided_elements_present;
  const id = `local ID ${coverage.source_material.material_id}`;
  if (present === null) return `The source material (${id}) composition was not evaluated. It is excluded from pathway counts.`;
  if (present.length) return `The source material (${id}) contains ${present.join(', ')}. It is excluded from pathway counts.`;
  return `The source material (${id}) is excluded from pathway counts.`;
}

const termLabel: Record<ObjectiveCoverage['terms_not_evaluated'][number], string> = {
  preserve_elements: 'elements to retain', target_family: 'target composition family',
};

function ChainLinks({ positions }: { positions: number[] }) {
  return <>{positions.map((position, n) => <span key={position}>{n > 0 && ', '}<a href={`#objective-path-${position}`}>{position}</a></span>)}</>;
}

export function ObjectiveCoveragePanel({ coverage }: { coverage?: ObjectiveCoverage }) {
  if (!coverage) {
    return <section className="objectiveCoverage" aria-label="Objective coverage in returned results">
      <h3>Objective coverage in returned results</h3>
      <p className="hint">Objective coverage is not available from this backend version. Inspect the ranked materials and returned chains below.</p>
    </section>;
  }
  const chainsWithAvoided = coverage.avoided_elements_in_returned_chains.filter(entry => entry.status === 'present');
  const nothingRequested = !coverage.preferred_elements.length && !coverage.avoided_elements_in_ranked_materials.length;
  return <section className="objectiveCoverage" aria-label="Objective coverage in returned results">
    <h3>Objective coverage in returned results</h3>
    <p className="hint">Counts {coverage.returned_ranked_material_count} {materials(coverage.returned_ranked_material_count)} and {coverage.returned_chain_count} {chains(coverage.returned_chain_count)}. Element presence is read from reported formulas.</p>
    <p className="objectiveCoverageMode">{coverage.avoid_policy_explanation}</p>
    {chainsWithAvoided.map(entry => <p className="warning" role="note" key={entry.element}>
      Returned {entry.chain_positions.length === 1 ? 'chain' : 'chains'} <ChainLinks positions={entry.chain_positions}/> {entry.chain_positions.length === 1 ? 'includes a material' : 'include materials'} containing avoided element {entry.element} (source material excluded).
    </p>)}
    {nothingRequested && <p className="hint">No preferred or avoided elements were requested.</p>}
    {coverage.preferred_elements.length > 0 && <><h4>Preferred elements</h4><ul className="objectiveCoverageList">
      {coverage.preferred_elements.map(entry => <li key={entry.element}><span className="objectiveCoverageStatus">{preferLabel[entry.status]}</span> {preferText(entry)}</li>)}
    </ul></>}
    {coverage.avoided_elements_in_ranked_materials.length > 0 && <><h4>Avoided elements</h4><ul className="objectiveCoverageList">
      {coverage.avoided_elements_in_ranked_materials.map(entry => <li key={`m-${entry.element}`}><span className="objectiveCoverageStatus">{avoidLabel[entry.status]}</span> {avoidMaterialText(entry)}</li>)}
      {coverage.avoided_elements_in_returned_chains.map(entry => <li key={`c-${entry.element}`}><span className="objectiveCoverageStatus">{avoidLabel[entry.status]}</span> {avoidChainText(entry)}{entry.chain_positions.length > 0 && <> Chains: <ChainLinks positions={entry.chain_positions}/>.</>}</li>)}
    </ul></>}
    <p className="hint">{sourceText(coverage)}</p>
    {coverage.terms_not_evaluated.length > 0 && <p className="hint">Not evaluated in this summary: {coverage.terms_not_evaluated.map(term => termLabel[term]).join(', ')}.</p>}
    <details><summary>Coverage limitations</summary><ul>{coverage.limitations.map((limitation, n) => <li key={n}>{limitation}</li>)}</ul></details>
  </section>;
}

export function ChainAvoidanceNote({ detail }: { detail?: ChainAvoidanceDetail }) {
  if (!detail) return null;
  const flagged = detail.materials_with_avoided_elements;
  return <>
    {flagged.length > 0 && <p className="objectiveChainAvoidance" role="note">Contains avoided {flagged.flatMap(m => m.avoided_elements).filter((e, i, all) => all.indexOf(e) === i).length === 1 ? 'element' : 'elements'} in {flagged.map(m => `${m.role} material (local ID ${m.material_id}): ${m.avoided_elements.join(', ')}`).join('; ')}. Source material excluded.</p>}
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
