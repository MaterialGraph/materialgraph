import { ChemicalFormula } from '../ChemicalFormula';
import type { CorrespondenceReason, FormulaCorrespondence, FormulaCorrespondenceReport } from './contract';

// Renders the backend formula-correspondence report (SRQ-01 spec R7.1, contract
// version 1). No composition comparison happens in the client. When the report
// is absent (frozen requests, older backends) nothing here renders.
// Wording follows the neutral-alkali rule (S-5): it states which alkali metal
// differs and never implies that one element was exchanged for another.

const reasonText: Record<CorrespondenceReason, string> = {
  ratios_differ: 'Element ratios differ.',
  non_alkali_elements_differ: 'The materials contain different other elements.',
  replacement_alkali_in_source: 'Not a single alkali-metal change: the material before this step already contains the new alkali metal.',
  replaced_alkali_in_candidate: 'Not a single alkali-metal change: the material after this step still contains the original alkali metal.',
  multiple_alkali_changes: 'More than one alkali metal differs.',
  formula_unparsed: 'Stored composition could not be compared.',
};

export function stepCorrespondence(report: FormulaCorrespondenceReport | undefined, chainPosition: number, transitionIndex: number): FormulaCorrespondence | undefined {
  return report?.transitions.find(entry => entry.chain_position === chainPosition && entry.transition_index === transitionIndex)?.correspondence;
}

export function correspondenceHeading(correspondence: FormulaCorrespondence): string {
  if (correspondence.correspondence_class === 'exact_alkali_replacement') return 'Exact formula analog';
  if (correspondence.correspondence_class === 'not_exact_replacement') return 'Different alkali metal (not an exact formula analog)';
  return 'Different alkali metal (formula correspondence not evaluated)';
}

function alkaliChange(correspondence: FormulaCorrespondence): string {
  return correspondence.replaced_from && correspondence.replaced_to
    ? `alkali metal ${correspondence.replaced_from} → ${correspondence.replaced_to}`
    : 'one alkali metal differs';
}

const capitalise = (value: string) => value.charAt(0).toUpperCase() + value.slice(1);

export function correspondenceDetail(correspondence: FormulaCorrespondence): string {
  if (correspondence.correspondence_class === 'exact_alkali_replacement') return `${capitalise(alkaliChange(correspondence))}; all other element ratios unchanged.`;
  return correspondence.reason ? reasonText[correspondence.reason] : reasonText.formula_unparsed;
}

const independently = 'This compares formulas with the starting material directly, independently of the returned chains.';

export function sourceAnalogText(baseFormula: string | null, correspondence: FormulaCorrespondence): string {
  return `Exact formula analog of ${baseFormula || 'the starting material'}: ${alkaliChange(correspondence)}; all other element ratios unchanged. ${independently}`;
}

export const sourceNotEvaluatedText = 'Formula correspondence not evaluated.';

export function SourceAnalogNote({ report, baseFormula, materialId }: { report?: FormulaCorrespondenceReport; baseFormula: string | null; materialId: number }) {
  if (!report) return null;
  const entry = report.source_correspondence.find(item => item.material_id === materialId);
  if (entry) return <p className="objectiveCorrespondence" role="note">
    Exact formula analog of {baseFormula ? <ChemicalFormula formula={baseFormula}/> : 'the starting material'}: {alkaliChange(entry.correspondence)}; all other element ratios unchanged. {independently} <span className="objectiveStructure">Structure not assessed.</span>
  </p>;
  if (report.not_evaluated_material_ids.includes(materialId)) return <p className="hint">{sourceNotEvaluatedText}</p>;
  return null;
}

export function FormulaCorrespondencePanel({ report }: { report?: FormulaCorrespondenceReport }) {
  if (!report) return null;
  const notEvaluated = report.not_evaluated_count;
  return <section className="objectiveCoverage" aria-label="Formula correspondence">
    <h3>Formula correspondence</h3>
    <p className="hint">Stored compositions of returned materials are compared at formula level. An exact formula analog differs in one alkali metal only, with all other element ratios unchanged. Crystal structure is not assessed.</p>
    {notEvaluated > 0 && <p className="hint">Formula correspondence not evaluated for {notEvaluated} {notEvaluated === 1 ? 'material' : 'materials'}.</p>}
    <details className="coverageLimitations"><summary>Formula correspondence limitations</summary><ul>{report.limitations.map((limitation, n) => <li key={n}>{limitation}</li>)}</ul></details>
  </section>;
}
