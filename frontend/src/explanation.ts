/** Format backend prose for scanning without interpreting or changing its claims. */
export function explanationClauses(explanation: string): string[] {
  return explanation.trim().split(/(?<=\.)\s+|(?<=;)\s+/).map(clause => clause.trim()).filter(Boolean);
}
