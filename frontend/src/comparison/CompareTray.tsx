import { ChemicalFormula } from '../ChemicalFormula';
import type { SelectedMaterial } from './launch';

export function CompareTray({ id, selected, remove, compare }: { id: string; selected: SelectedMaterial[]; remove: (id: number) => void; compare: () => void }) {
  return <div className="compareTray" aria-label="Comparison selection">
    <strong>Compare · {selected.length} of 3 selected</strong>
    {selected.length > 0 && <ul>{selected.map(material => <li key={material.id}>
      <span><ChemicalFormula formula={material.formula}/> · {material.mpId ?? `Local ID ${material.id}`} <small>{material.role}</small></span>
      <button type="button" aria-label={`Remove ${material.formula}, local ID ${material.id} from comparison`} onClick={() => remove(material.id)}>Remove</button>
    </li>)}</ul>}
    <button type="button" onClick={compare} disabled={selected.length < 2}>Compare selected materials</button>
    {selected.length < 2 && <p className="hint">Select at least two materials to compare.</p>}
    {selected.length === 3 && <p id={id} className="hint">Maximum 3 candidates reached for comparison.</p>}
  </div>;
}
