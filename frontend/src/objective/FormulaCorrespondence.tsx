import { ChemicalFormula } from '../ChemicalFormula';
import type { CorrespondenceReason, FormulaCorrespondence, FormulaCorrespondenceReport } from './contract';

// Renders the backend formula-correspondence report (SRQ-01 spec R7.1, contract
// version 1). No composition comparison happens in the client. When the report
// is absent (frozen requests, older backends) nothing here renders.

const reasonText: Record<CorrespondenceReason, string> = {
  ratios_differ: 'Element ratios differ.',
  non_alkali_elements_differ: 'The materials contain different other elements.',
  replacement_alkali_in_source: 'Not compared as a one-alkali replacement: the material before this step already contains the new alkali metal.',
  replaced_alkali_in_candidate: 'Not compared as a one-alkali replacement: the material after this step still contains the original alkali metal.',
  multiple_alkali_changes: 'More than one alkali metal changes; not a one-alkali replacement.',
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

function replacement(correspondence: FormulaCorrespondence): string {
  return correspondence.replaced_from && correspondence.replaced_to
    ? `${correspondence.replaced_from} replaced by ${correspondence.replaced_to}`
    : 'One alkali metal replaced';
}

export function correspondenceDetail(correspondence: FormulaCorrespondence): string {
  if (correspondence.correspondence_class === 'exact_alkali_replacement') return `${replacement(correspondence)}; all other element ratios unchanged.`;
  return correspondence.reason ? reasonText[correspondence.reason] : reasonText.formula_unparsed;
}

export function sourceAnalogText(baseFormula: string | null, correspondence: FormulaCorrespondence): string {
  return `Exact formula analog of ${baseFormula || 'the starting material'}: ${replacement(correspondence)}; all other element ratios unchanged. This compares formulas with the starting material directly; it is not a returned chain step.`;
}

export const sourceNotEvaluatedText = 'Formula correspondence not evaluated.';

export function SourceAnalogNote({ report, baseFormula, materialId }: { report?: FormulaCorrespondenceReport; baseFormula: string | null; materialId: number }) {
  if (!report) return null;
  const entry = report.source_correspondence.find(item => item.material_id === materialId);
  if (entry) return <p className="objectiveCorrespondence" role="note">
    Exact formula analog of {baseFormula ? <ChemicalFormula formula={baseFormula}/> : 'the starting material'}: {replacement(entry.correspondence)}; all other element ratios unchanged. This compares formulas with the starting material directly; it is not a returned chain step. <span className="objectiveStructure">Structure not assessed.</span>
  </p>;
  if (report.not_evaluated_material_ids.includes(materialId)) return <p className="hint">{sourceNotEvaluatedText}</p>;
  return null;
}

export function FormulaCorrespondencePanel({ report }: { report?: FormulaCorrespondenceReport }) {
  if (!report) return null;
  const notEvaluated = report.not_evaluated_count;
  return <section className="objectiveCoverage" aria-label="Formula correspondence">
    <h3>Formula correspondence</h3>
    <p className="hint">Stored compositions of returned materials are compared at formula level. An exact formula analog has one alkali metal replaced and all other element ratios unchanged. Crystal structure is not assessed.</p>
    {notEvaluated > 0 && <p className="hint">Formula correspondence not evaluated for {notEvaluated} {notEvaluated === 1 ? 'material' : 'materials'}.</p>}
    <details className="coverageLimitations"><summary>Formula correspondence limitations</summary><ul>{report.limitations.map((limitation, n) => <li key={n}>{limitation}</li>)}</ul></details>
  </section>;
}
