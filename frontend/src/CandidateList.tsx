import { useEffect, useState } from 'react';
import type { CandidateResponse, MaterialDetail } from './api';
import { ChemicalFormula, FormulaInText } from './ChemicalFormula';
import { factorExplanation, factorLabel, presentCandidate } from './candidatePresentation';
import { CompareTray } from './comparison/CompareTray';
import { discoveryLaunch, toggleComparisonSelection, type ComparisonLaunchContext, type SelectedMaterial } from './comparison/launch';
import { routeFromDiscovery, type ComparisonRoute } from './comparison/routing';

type Props = {
  select: (id: number) => void; detail: MaterialDetail | null;
  avoid: string; setAvoid: (value: string) => void;
  prefer: string; setPrefer: (value: string) => void;
  result: CandidateResponse | null; candidateError: string;
  candidateLoading: boolean; searchCandidates: () => void;
  onCompare?: (launch: ComparisonLaunchContext, route: ComparisonRoute) => void;
};

export function CandidateList({ select, detail, avoid, setAvoid, prefer, setPrefer, result, candidateError, candidateLoading, searchCandidates, onCompare }: Props) {
  const [inspectedId, setInspectedId] = useState<number | null>(null);
  const [comparison, setComparison] = useState<SelectedMaterial[]>([]);
  useEffect(() => { setComparison([]); }, [result]);
  if (!detail) return null;
  const inspected = result?.candidates.find(candidate => candidate.material_id === inspectedId) ?? result?.candidates[0];
  const sourceFormula = result?.base_formula || detail.pretty_formula || detail.formula;
  const presentation = inspected && result ? presentCandidate(inspected, sourceFormula, result.discovery_goal) : null;

  return <section className="panel discovery" aria-label="Discovery results">
    <div className="sectionTitle"><span>03 / EXPLORE</span><h2>Discovery results</h2></div>
    <p className="hint">Avoid applies a soft score penalty; Prefer applies a soft score bonus. Results may still include avoided elements.</p>
    <form className="filters" onSubmit={event => { event.preventDefault(); searchCandidates(); }}>
      <label>Avoid element <input value={avoid} onChange={event => setAvoid(event.target.value)} maxLength={3} placeholder="e.g. Li"/></label>
      <label>Prefer element <input value={prefer} onChange={event => setPrefer(event.target.value)} maxLength={3} placeholder="e.g. Na"/></label>
      <button type="submit" disabled={candidateLoading}>{candidateLoading ? 'Discovering…' : 'Discover candidates'}</button>
    </form>
    {candidateLoading && <p role="status">Loading discovery results…</p>}
    {candidateError && <div role="alert" className="error">{candidateError} <button onClick={searchCandidates}>Retry</button></div>}
    {result && <>
      <p className="hint">{result.candidates.length} candidates returned in ranking order. Dataset and method versions, evidence coverage, and completeness are not provided with these results.</p>
      {result.discovery_warnings.map((warning, index) => <p className="warning" key={index} role="status">{warning}</p>)}
      {!result.candidates.length && <div className="empty">No candidates were returned for this request. Other candidates may still exist.</div>}
      {!!inspected && presentation && <div className="discoveryWorkspace">
        <div className="discoveryRail">
        <div className="discoveryList" aria-label="Ranked candidates">
          <ol className="candidateList">{result.candidates.map((candidate, index) => {
            const inspectedRow = candidate.material_id === inspected.material_id;
            const selectedForComparison = comparison.some(item => item.id === candidate.material_id);
            const candidateSignals = presentCandidate(candidate, sourceFormula, result.discovery_goal).signals;
            const avoided = candidateSignals.find(signal => signal.key === 'contains_avoided_element');
            return <li key={candidate.material_id}>
              <button className={`candidateRow${inspectedRow ? ' active' : ''}`} aria-current={inspectedRow ? 'true' : undefined} onClick={() => setInspectedId(candidate.material_id)}>
                <span className="eyebrow">Candidate {index + 1} · {candidate.mp_id ?? 'source ID unavailable'}</span>
                <span className="rowIdentity"><strong><ChemicalFormula formula={candidate.pretty_formula || candidate.formula}/></strong><span>{candidate.discovery_score.toLocaleString()} <small>rule score</small></span></span>
                {avoided && <span className="rowNote">{avoided.label}</span>}
              </button>
              {onCompare && candidate.material_id !== detail.id && <button type="button" className="compareSelect" aria-pressed={selectedForComparison} aria-label={`${selectedForComparison ? 'Remove' : 'Select'} ${candidate.pretty_formula || candidate.formula}, local ID ${candidate.material_id} ${selectedForComparison ? 'from' : 'for'} comparison`}
                disabled={comparison.length === 3 && !selectedForComparison} aria-describedby={comparison.length === 3 && !selectedForComparison ? 'discovery-selection-limit' : undefined}
                onClick={() => setComparison(previous => toggleComparisonSelection(previous, { id: candidate.material_id, formula: candidate.pretty_formula || candidate.formula, mpId: candidate.mp_id, role: 'Discovery candidate' }))}>
                {selectedForComparison ? 'Selected for comparison' : 'Select for comparison'}
              </button>}
            </li>;
          })}</ol>
        </div>
        {onCompare && <CompareTray id="discovery-selection-limit" selected={comparison} remove={id => setComparison(previous => previous.filter(item => item.id !== id))} compare={() => { if (comparison.length >= 2) { const launch = discoveryLaunch(result, comparison); onCompare(launch, routeFromDiscovery(launch, result)); } }}/>}
        </div>
        <article className="investigationDossier" aria-label="Candidate investigation" key={inspected.material_id}>
          <div className="dossierIdentity"><p className="eyebrow">Investigation · {inspected.mp_id ?? 'source ID unavailable'}</p><h3><ChemicalFormula formula={inspected.pretty_formula || inspected.formula}/></h3><p className="hint">Deterministic rule score: {inspected.discovery_score.toLocaleString()}.{inspected.discovery_score < 0 && ' A negative score reflects rule penalties, not negative scientific value.'}</p></div>
          <div className="researchSummary">
            <h4>Research hypothesis</h4><p><FormulaInText text={presentation.hypothesis} formula={sourceFormula}/></p>
            <aside><h4>Scientific limitations</h4><ul>{presentation.caveats.map(caveat => <li key={caveat}>{caveat}</li>)}</ul></aside>
          </div>
          <div className="dossierDetails">
            <section><h4>Why this candidate?</h4>
              {presentation.signals.length ? <ul className="signalList">{presentation.signals.map(signal => <li key={signal.key}>{signal.label}</li>)}</ul> : <p className="hint">No individual matching signals were provided.</p>}
            </section>
            <section><h4>How the rule score was calculated</h4>
              {Object.entries(inspected.score_breakdown).length ? <dl className="scoreFactors">{Object.entries(inspected.score_breakdown).map(([name, amount]) => <div key={name}><dt>{factorLabel(name)}</dt><dd>{amount > 0 ? '+' : ''}{amount.toLocaleString()}</dd><p>{factorExplanation(name, inspected, result.discovery_goal)}</p></div>)}</dl> : <p className="hint">No factor breakdown was provided.</p>}
            </section>
            <details className="originalExplanation"><summary>Full discovery explanation</summary><p>{inspected.explanation}</p>{inspected.substitution_path && <p>{inspected.substitution_path.reason}</p>}</details>
            <button className="textButton" onClick={() => select(inspected.material_id)}>Explore material →</button>
          </div>
        </article>
      </div>}
      <p className="rankingNote">Rule scores are deterministic composition heuristics, not confidence or validated performance. Candidate relationships do not establish a substitution mechanism, structural preservation, synthesis feasibility, or application performance.</p>
    </>}
  </section>;
}
