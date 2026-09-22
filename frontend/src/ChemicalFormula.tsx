import React from 'react';

export function ChemicalFormula({ formula }: { formula: string }) {
  // Formula fields are plain text from the API. Render digit runs as subscripts,
  // leaving all other characters untouched and escaped by React.
  return <span className="chemicalFormula">{formula.split(/(\d+)/).map((part, index) =>
    /^\d+$/.test(part) ? <sub key={index}>{part}</sub> : part
  )}</span>;
}

export function FormulaInText({ text, formula }: { text: string; formula: string }) {
  if (!formula) return <>{text}</>;
  return <>{text.split(formula).map((part, index) => <React.Fragment key={index}>{index > 0 && <ChemicalFormula formula={formula} />}{part}</React.Fragment>)}</>;
}
