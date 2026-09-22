import { useState, type FormEvent } from 'react';
import { ChemicalFormula } from '../ChemicalFormula';
import type { ObjectiveCandidate, ObjectiveChain, ObjectiveResponse, ObjectiveTransition } from './contract';
import { buildObjectiveRequest, initialDraft, type ObjectiveDraft } from './request';
import { useObjectiveInvestigation } from './useObjectiveInvestigation';

export function returnedPathways(result: ObjectiveResponse, materialId: number) {
  return result.chains.flatMap((chain, index) => chain.materials.slice(1).some(material => material.material_id === materialId) ? [index] : []);
}

export function returnedRole(result: ObjectiveResponse, materialId: number): string | null {
  const roles = new Set(result.chains.flatMap(chain => chain.materials.slice(1).flatMap((material, index, nonRoot) =>
    material.material_id === materialId ? [index === nonRoot.length - 1 ? 'final' : 'intermediate'] : [])));
  if (roles.size === 2) return 'Intermediate and final material in returned chains';
  if (roles.has('final')) return 'Final material in returned chain';
  if (roles.has('intermediate')) return 'Intermediate in returned chain';
  return null;
}

function RankedMaterial({ result, candidate, index }: { result: ObjectiveResponse; candidate: ObjectiveCandidate; index: number }) {
  const paths = returnedPathways(result, candidate.material_id);
  return <li className="objectiveCandidate">
    <div className="objectiveRowHead"><div><span className="eyebrow">Ranked material {index + 1} · Local ID {candidate.material_id}</span>
      <h4><ChemicalFormula formula={candidate.formula || 'Formula unavailable'}/></h4></div>
      <div className="objectiveScore"><strong>{candidate.score.toLocaleString()}</strong><small>objective rule score</small></div></div>
    {paths.length ? <p className="hint">{returnedRole(result, candidate.material_id)} · Returned {paths.length === 1 ? 'chain' : 'chains'}: {paths.map((path, position) => <span key={path}>{position > 0 && ', '}<a href={`#objective-path-${path + 1}`}>{path + 1}</a></span>)}</p>
      : <p className="hint">No returned chain includes this material.</p>}
    {candidate.reasons.length > 0 && <details open={index === 0}><summary>Returned reasons</summary><ul>{candidate.reasons.map((reason, n) => <li key={n}>{reason}</li>)}</ul></details>}
    {candidate.warnings.map((warning, n) => <p className="warning" key={n}>{warning}</p>)}
  </li>;
}

export function relationshipLabel(type: string): string {
  if (type === 'alkali_substitution') return 'Possible alkali composition substitution';
  if (type === 'family_expansion') return 'Composition family relationship';
  return `Reported relationship: ${type.replaceAll('_', ' ')}`;
}

function Relationship({ transition }: { transition: ObjectiveTransition }) {
  return <li className="objectiveRelationship">
    <strong>{relationshipLabel(transition.transition_type)}</strong>
    {(!transition.structural_preservation_validated || !transition.substitution_mechanism_validated) && <span className="objectiveValidation">Not validated</span>}
    <small>{transition.shared_elements.length ? `Shared elements: ${transition.shared_elements.join(', ')}` : 'Shared elements not supplied'}</small>
  </li>;
}

function Pathway({ chain, index }: { chain: ObjectiveChain; index: number }) {
  return <li className="objectivePath" id={`objective-path-${index + 1}`}>
    <h4>Returned composition chain {index + 1} · {chain.transitions.length} relationship {chain.transitions.length === 1 ? 'step' : 'steps'}</h4>
    <ol className="objectivePathMaterials">{chain.materials.flatMap((material, materialIndex) => [
      <li className="objectiveMaterialRecord" key={`material-${materialIndex}`}><ChemicalFormula formula={material.pretty_formula || material.formula}/>
        <small>{material.mp_id ?? `Local ID ${material.material_id}`} · {materialIndex === 0 ? 'Source' : materialIndex === chain.materials.length - 1 ? 'Final material in returned chain' : 'Intermediate in returned chain'}</small></li>,
      ...(materialIndex < chain.transitions.length ? [<Relationship key={`relationship-${materialIndex}`} transition={chain.transitions[materialIndex]}/>] : []),
    ])}</ol>
    <p className="hint">Composition-level relationships only; reaction steps and mechanisms are not established.</p>
    <details><summary>Relationship details and scoring</summary>
      <p className="hint">Original returned chain explanation: {chain.chain_reason}</p>
      <p className="hint">Pathway usefulness rule score: {chain.scientific_usefulness_score?.toLocaleString() ?? 'Not supplied'}. This is separate from the objective rule score.</p>
      {chain.transitions.map((transition, n) => <div className="objectiveTransition" key={n}>
        <strong>Relationship {n + 1}: {relationshipLabel(transition.transition_type)}</strong>
        <p>Original returned reason: {transition.reason}</p>
        <p className="hint">Shared elements: {transition.shared_elements.length ? transition.shared_elements.join(', ') : 'None supplied'} · Basis: {transition.relationship_basis}, {transition.preservation_basis}. Structural preservation: {transition.structural_preservation_validated ? 'Reported as validated' : 'Not validated'}. Substitution mechanism: {transition.substitution_mechanism_validated ? 'Reported as validated' : 'Not validated'}.</p>
      </div>)}
      {chain.score_breakdown && <dl className="objectiveBreakdown">{Object.entries(chain.score_breakdown).map(([name, value]) => <div key={name}><dt>{name.replaceAll('_', ' ')}</dt><dd>{value.toLocaleString()}</dd></div>)}</dl>}
      {chain.usefulness_reason && <p>{chain.usefulness_reason}</p>}
    </details>
  </li>;
}

export function ObjectiveResults({ result, submitted }: { result: ObjectiveResponse; submitted: string }) {
  const metadata = result.search_metadata;
  const scores = result.ranked_candidates.map(candidate => candidate.score);
  const hasEqualScores = new Set(scores).size < scores.length;
  const hasRankedWithoutChain = result.ranked_candidates.some(candidate => returnedPathways(result, candidate.material_id).length === 0);
  const hasUnvalidatedRelationship = result.chains.some(chain => chain.transitions.some(transition => !transition.structural_preservation_validated || !transition.substitution_mechanism_validated));
  return <div className="objectiveResults">
    <div className="objectiveScope"><h3>Search scope</h3>
      <p>{metadata.returned_chain_count} of {metadata.generated_chain_count} generated chains are included in this response. The generated count is before objective filtering.</p>
      {(metadata.result_truncated || !metadata.scientific_completeness_guaranteed) && <p>The returned results are limited. Scientific completeness is not guaranteed.</p>}
      <p>Search truncation: {metadata.search_truncated ? 'Yes — search stopped at its state budget' : 'No'}. This does not establish that every scientifically relevant pathway was found.</p>
      <details><summary>Search parameters and returned policies</summary>
        <p>Mode: {result.mode}. Avoid: {result.constraint_policy.avoid_elements.replaceAll('_', ' ')}; Prefer: {result.constraint_policy.prefer_elements.replaceAll('_', ' ')}; hard rejection scope: {result.constraint_policy.hard_rejection_scope.replaceAll('_', ' ')}.</p>
        <p>Stability: {result.objective_policy.stable_materials.replaceAll('_', ' ')}; scope: {result.objective_policy.stability_scope.replaceAll('_', ' ')}. Lower criticality: {result.objective_policy.lower_criticality.replaceAll('_', ' ')}. Unknown criticality: {result.objective_policy.unknown_criticality_evidence.replaceAll('_', ' ')}.</p>
        <p>Search policy: {metadata.search_policy.replaceAll('_', ' ')}; expansion limit per material: {metadata.expansion_limit_per_material}; state budget: {metadata.search_state_budget}; expanded states: {metadata.expanded_state_count}; generated chains: {metadata.generated_chain_count}; returned chains: {metadata.returned_chain_count}; result limit applied: {metadata.result_truncated ? 'Yes' : 'No'}.</p>
        <p>Submitted structured request (client-observed):</p><pre>{submitted}</pre>
        <p>Returned explanation: {result.explanation}</p>
      </details>
    </div>
    {result.warnings.map((warning, n) => <p className="warning" key={n}>{warning}</p>)}
    <div className="objectiveColumns">
      <section><h3>Ranked materials</h3><p className="hint">Returned order and objective rule scores. A score does not measure experimental confidence.</p>
        {hasEqualScores && <p className="hint">Some materials have the same objective rule score. Their order follows the API response.</p>}
        {hasRankedWithoutChain && <p className="hint">A missing returned chain does not establish the absence of a composition-level relationship.</p>}
        {result.ranked_candidates.length ? <ol className="objectiveCandidates">{result.ranked_candidates.map((candidate, index) => <RankedMaterial key={`${candidate.material_id}-${index}`} candidate={candidate} index={index} result={result}/>)}</ol> : <p className="empty">No ranked materials returned for this objective.</p>}
      </section>
      <section><h3>Returned composition chains</h3><p className="hint">These chains describe composition-level relationships between returned materials. They do not establish that reactions proceed through these steps.</p><p className="hint">Shared-element continuity means element overlap across each consecutive relationship; it does not establish structural preservation or a validated substitution mechanism.</p>
        {hasUnvalidatedRelationship && <p className="hint">“Not validated” refers to structural preservation or a substitution mechanism for that relationship; the reported shared elements are shown separately.</p>}
        {result.chains.length ? <ol className="objectivePaths">{result.chains.map((chain, index) => <Pathway key={index} chain={chain} index={index}/>)}</ol> : <p className="empty">No pathways included in this response.</p>}
      </section>
    </div>
  </div>;
}

export function ObjectiveInvestigation({ materialId }: { materialId: number }) {
  const [draft, setDraft] = useState<ObjectiveDraft>(initialDraft);
  const [fieldError, setFieldError] = useState('');
  const { submitted, result, loading, errors, run, retry } = useObjectiveInvestigation(materialId);
  const set = <K extends keyof ObjectiveDraft>(key: K, value: ObjectiveDraft[K]) => setDraft(previous => ({ ...previous, [key]: value }));
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try { const request = buildObjectiveRequest(draft); setFieldError(''); run(request); }
    catch (error) { setFieldError(error instanceof Error ? error.message : 'Check the objective fields.'); }
  }
  return <section className="panel objectiveInvestigation" aria-label="Objective investigation">
    <div className="sectionTitle"><span>04 / INVESTIGATE</span><h2>Objective investigation</h2></div>
    <p className="hint">Set a structured composition objective for this material. These results describe ranked rules and possible pathways, not experimentally validated transformations.</p>
    <form className="objectiveForm" onSubmit={submit}>
      <label>Elements to avoid <input value={draft.avoid} onChange={e => set('avoid', e.target.value)} placeholder="e.g. Li"/><small>Comma or space separated chemical symbols</small></label>
      <label>Preferred elements <input value={draft.prefer} onChange={e => set('prefer', e.target.value)} placeholder="e.g. Na"/></label>
      <label>Elements to retain across transitions <input value={draft.preserve} onChange={e => set('preserve', e.target.value)} placeholder="e.g. Fe, P, O"/><small>Shared across each transition; this does not establish preservation of crystal structure.</small></label>
      <label>Target composition family <select value={draft.family} onChange={e => set('family', e.target.value as ObjectiveDraft['family'])}><option value="">Any</option><option value="phosphate">Phosphate (contains P and O)</option></select></label>
      <label>Investigation mode <select value={draft.mode} onChange={e => set('mode', e.target.value as ObjectiveDraft['mode'])}><option value="balanced">Balanced</option><option value="exploratory">Exploratory</option><option value="strict">Strict</option></select></label>
      <label>Maximum pathway steps <input type="number" min="1" max="3" required value={draft.hops} onChange={e => set('hops', Number(e.target.value))}/></label>
      <label>Maximum returned materials and pathways <input type="number" min="1" max="20" required value={draft.limit} onChange={e => set('limit', Number(e.target.value))}/></label>
      <div className="objectiveChecks"><label><input type="checkbox" checked={draft.lowerCriticality} onChange={e => set('lowerCriticality', e.target.checked)}/> Prefer lower criticality</label>
        <label><input type="checkbox" checked={draft.requireStable} onChange={e => set('requireStable', e.target.checked)}/> Require stable intermediate and final materials</label></div>
      <p className="hint objectiveModeHint">{draft.mode === 'strict'
        ? 'Avoided elements are excluded from intermediate and final materials in eligible chains. The source material is exempt.'
        : 'Avoided elements lower the objective score; they are not automatically excluded.'} Preferred elements add a soft bonus.</p>
      {fieldError && <p className="error" role="alert">{fieldError}</p>}
      <button type="submit" disabled={loading}>{loading ? 'Investigating…' : 'Run investigation'}</button>
    </form>
    {loading && <p role="status">Investigating this objective…</p>}
    {errors.length > 0 && <div className="error" role="alert"><p>Investigation request failed.</p><ul>{errors.map((error, n) => <li key={n}>{error}</li>)}</ul><button type="button" onClick={retry}>Retry submitted objective</button></div>}
    {!loading && result && submitted && <><p className="hint">Results for the submitted objective below. Changes to the form take effect when you run a new investigation.</p><ObjectiveResults result={result} submitted={JSON.stringify(submitted, null, 2)}/></>}
  </section>;
}
