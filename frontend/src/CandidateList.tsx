import type { CandidateResponse, MaterialDetail } from './api';
import { ChemicalFormula, FormulaInText } from './ChemicalFormula';
import { factorExplanation, factorLabel, presentCandidate } from './candidatePresentation';
type Props = { selected: number; select: (id: number) => void; detail: MaterialDetail | null; avoid: string; setAvoid: (value: string) => void; prefer: string; setPrefer: (value: string) => void; result: CandidateResponse | null; candidateError: string; candidateLoading: boolean; searchCandidates: () => void };
export function CandidateList({ select, detail, avoid, setAvoid, prefer, setPrefer, result, candidateError, candidateLoading, searchCandidates }: Props) {
  return <>

        {detail && <div className="panel discovery"><div className="sectionTitle"><span>03 / EXPLORE</span><h2>Discovery candidates</h2></div><p className="hint">Avoid applies a soft score penalty; Prefer applies a soft score bonus. Results may still include avoided elements.</p>
          <form className="filters" onSubmit={e => { e.preventDefault(); searchCandidates(); }}><label>Avoid element <input value={avoid} onChange={e => setAvoid(e.target.value)} maxLength={3} placeholder="e.g. Li"/></label><label>Prefer element <input value={prefer} onChange={e => setPrefer(e.target.value)} maxLength={3} placeholder="e.g. Na"/></label><button type="submit" disabled={candidateLoading}>{candidateLoading ? 'Searching…' : 'Find candidates →'}</button></form>
          {candidateLoading && <p role="status">Loading ranked candidates…</p>}{candidateError && <div role="alert" className="error">{candidateError} <button onClick={() => searchCandidates()}>Retry</button></div>}
          {result && <><p className="hint">{result.candidates.length} candidates returned in backend ranking order. This response does not provide dataset or method versions, evidence coverage, or a completeness assessment.</p>{result.discovery_warnings.map((warning, i) => <p className="warning" key={i} role="status">{warning}</p>)}{!result.candidates.length && <div className="empty">No candidates were returned for this request. Other candidates may still exist.</div>}
            <ol className="candidateList">{result.candidates.map((candidate, index) => {
              const presentation = presentCandidate(candidate, result.base_formula || detail.pretty_formula || detail.formula);
              return <li key={candidate.material_id} className="candidate">
                <div className="candidateHead"><div><span className="eyebrow">CANDIDATE {index + 1} · MATERIALS PROJECT {candidate.mp_id ?? 'ID NOT PROVIDED'}</span><h3><ChemicalFormula formula={candidate.pretty_formula || candidate.formula}/></h3></div><div className="score"><strong>{candidate.discovery_score.toLocaleString()}</strong><small>rule points</small></div></div>
                <div className="candidateZone"><h4>Composition-based hypothesis</h4><p><FormulaInText text={presentation.hypothesis} formula={result.base_formula || detail.pretty_formula || detail.formula}/></p></div>
                <div className="candidateZone"><h4>Ranking signals</h4><div className="signalPills">{presentation.signals.map(signal => <span key={signal.key} className="signalPill">{signal.label}</span>)}</div>
                  <p className="hint">Score factors · open each factor for its explanation</p>
                  <div className="factorPreview">{Object.entries(candidate.score_breakdown).map(([name, amount]) => <details key={name} className="factorPill"><summary><span>{factorLabel(name)}</span> <strong>{amount > 0 ? '+' : ''}{amount.toLocaleString()}</strong></summary><p>{factorExplanation(name, candidate, result.discovery_goal)}</p></details>)}</div>
                </div>
                <div className="candidateZone caveats"><h4>Scientific limits</h4><ul>{presentation.caveats.map(caveat => <li key={caveat}>{caveat}</li>)}</ul></div>
                <details className="originalExplanation"><summary>Full API explanation</summary><p>{candidate.explanation}</p>{candidate.substitution_path && <p>{candidate.substitution_path.reason}</p>}</details>
                <button className="textButton" onClick={() => select(candidate.material_id)}>Inspect this material →</button>
              </li>;
            })}</ol>
            <p className="rankingNote">Rule points reflect deterministic composition heuristics, not confidence or validated performance. Candidate relationships do not establish a substitution mechanism, structural preservation, or synthesis feasibility.</p></>}
        </div>}
  </>;
}
