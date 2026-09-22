import type { Candidate } from './api';

const signalLabels: Record<string, string> = {
  family_related: 'Composition rule match',
  shared_chemistry: 'Shared elements',
  alkali_substitution: 'Possible alkali substitution',
  transition_metal_related: 'Shared transition metal element',
  phosphate_related: 'Both contain P and O',
  oxide_related: 'Both contain O',
  preferred_element: 'Preferred element present',
  avoided_element_removed: 'Avoided element absent',
  contains_avoided_element: 'Avoided element present',
};

export function presentCandidate(candidate: Candidate, sourceFormula: string) {
  const signals = new Set(candidate.discovery_path);
  const substitution = candidate.explanation.match(/composition-level alkali-substitution hypothesis from ([A-Z][a-z]?(?:, [A-Z][a-z]?)*) to ([A-Z][a-z]?(?:, [A-Z][a-z]?)*)/);
  const shared = candidate.explanation.match(/shares ([A-Z][a-z]?(?:, [A-Z][a-z]?)*) chemistry with /);
  const sharedElements = shared?.[1].split(', ') ?? [];
  const source = sourceFormula || 'the source material';
  let hypothesis = `Composition-based rules rank this material as a candidate to investigate alongside ${source}.`;
  if (signals.has('alkali_substitution')) {
    hypothesis = substitution
      ? `The ranking flags a possible ${substitution[1]}-to-${substitution[2]} alkali substitution relative to ${source}, based on composition alone.`
      : `The ranking flags a possible alkali substitution relative to ${source}, based on composition alone.`;
  } else if (signals.has('shared_chemistry')) {
    hypothesis = `This candidate shares elemental chemistry with ${source}.`;
  }
  if (sharedElements.length) hypothesis += ` Shared elements: ${sharedElements.join(', ')}.`;

  // The shared-chemistry signal already accounts for element overlap. Avoid
  // separately displaying the narrower phosphate/oxide overlap as new evidence.
  const visibleSignals = candidate.discovery_path.filter(signal =>
    !(signals.has('shared_chemistry') && (signal === 'phosphate_related' || signal === 'oxide_related'))
  );
  const caveats = [];
  if (signals.has('alkali_substitution')) caveats.push('A substitution mechanism has not been demonstrated.');
  caveats.push('Composition-based signals do not establish structural similarity, synthesis feasibility, or performance.');
  return {
    hypothesis,
    signals: visibleSignals.map(signal => ({ key: signal, label: signalLabels[signal] ?? signal.replaceAll('_', ' ') })),
    caveats,
  };
}

export function factorExplanation(name: string, candidate: Candidate, goal: { avoid_element: string | null; prefer_element: string | null }) {
  const signals = new Set(candidate.discovery_path);
  const reasons: Record<string, string> = {
    family_bonus: 'A composition relationship rule added points; it does not establish a shared structure.',
    substitution_bonus: signals.has('alkali_substitution') ? 'A composition-based alkali substitution signal added points; the mechanism is unvalidated.' : 'A substitution-related rule added points; consult the original explanation for context.',
    preferred_element_bonus: goal.prefer_element ? `The candidate contains the preferred element ${goal.prefer_element}.` : 'Preferred element rule contributed to this score.',
    avoided_element_removed_bonus: goal.avoid_element ? `The candidate does not contain ${goal.avoid_element}, the element marked Avoid.` : 'Absence of an avoided element added points.',
    avoided_element_present_penalty: goal.avoid_element ? `The candidate contains the avoided element ${goal.avoid_element}; avoidance is a soft penalty.` : 'Avoided element rule reduced this score.',
  };
  return reasons[name] ?? 'A scoring rule contributed to this result; consult the original explanation for context.';
}

const factorLabels: Record<string, string> = {
  family_bonus: 'Composition relationship',
  substitution_bonus: 'Substitution signal',
  preferred_element_bonus: 'Preferred element present',
  avoided_element_removed_bonus: 'Avoided element absent',
  avoided_element_present_penalty: 'Avoided element present',
};

export function factorLabel(name: string) {
  return factorLabels[name] ?? name.replaceAll('_', ' ');
}
