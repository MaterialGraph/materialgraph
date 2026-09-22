import type { Candidate } from './api';

const signalLabels: Record<string, string> = {
  family_related: 'Composition related',
  shared_chemistry: 'Shared elemental chemistry',
  alkali_substitution: 'Alkali substitution hypothesis',
  transition_metal_related: 'Shared transition metal',
  phosphate_related: 'Both contain P and O',
  oxide_related: 'Both contain O',
};

export function presentCandidate(candidate: Candidate, sourceFormula: string) {
  const signals = new Set(candidate.discovery_path);
  const substitution = candidate.explanation.match(/composition-level alkali-substitution hypothesis from ([A-Z][a-z]?(?:, [A-Z][a-z]?)*) to ([A-Z][a-z]?(?:, [A-Z][a-z]?)*)/);
  const shared = candidate.explanation.match(/shares ([A-Z][a-z]?(?:, [A-Z][a-z]?)*) chemistry with /);
  const sharedElements = shared?.[1].split(', ') ?? [];
  const source = sourceFormula || 'the source material';
  let hypothesis = `The backend ranks this material as a composition-level candidate related to ${source}.`;
  if (signals.has('alkali_substitution')) {
    hypothesis = substitution
      ? `The backend proposes a composition-level alkali substitution from ${substitution[1]} to ${substitution[2]} relative to ${source}.`
      : `The backend proposes a composition-level alkali substitution relative to ${source}.`;
  } else if (signals.has('shared_chemistry')) {
    hypothesis = `The backend identifies shared elemental chemistry with ${source}.`;
  }
  if (sharedElements.length) hypothesis += ` Both contain ${sharedElements.join(', ')}.`;

  // The shared-chemistry signal already accounts for element overlap. Avoid
  // separately displaying the narrower phosphate/oxide overlap as new evidence.
  const visibleSignals = candidate.discovery_path.filter(signal =>
    !(signals.has('shared_chemistry') && (signal === 'phosphate_related' || signal === 'oxide_related'))
  );
  const caveats = [];
  if (signals.has('alkali_substitution')) caveats.push('The substitution mechanism has not been validated.');
  if (signals.has('phosphate_related')) caveats.push('A shared structural framework has not been validated.');
  if (signals.has('oxide_related')) caveats.push('Oxide structure similarity has not been validated.');
  if (!caveats.length) caveats.push('These composition-level signals do not confirm a structural relationship.');
  return {
    hypothesis,
    signals: visibleSignals.map(signal => ({ key: signal, label: signalLabels[signal] ?? signal.replaceAll('_', ' ') })),
    caveats,
  };
}

export function factorExplanation(name: string, candidate: Candidate, goal: { avoid_element: string | null; prefer_element: string | null }) {
  const signals = new Set(candidate.discovery_path);
  const reasons: Record<string, string> = {
    family_bonus: 'Backend family or composition relationship contributed to this score.',
    substitution_bonus: signals.has('alkali_substitution') ? 'Alkali substitution is a composition-level hypothesis; its mechanism is unvalidated.' : 'A backend substitution rule contributed to this score.',
    preferred_element_bonus: goal.prefer_element ? `The candidate contains the preferred element ${goal.prefer_element}.` : 'Preferred element rule contributed to this score.',
    avoided_element_removed_bonus: goal.avoid_element ? `The candidate does not contain the avoided element ${goal.avoid_element}.` : 'Avoided element removal rule contributed to this score.',
    avoided_element_present_penalty: goal.avoid_element ? `The candidate contains the avoided element ${goal.avoid_element}; avoidance is a soft penalty.` : 'Avoided element rule reduced this score.',
  };
  return reasons[name] ?? 'Backend scoring factor; consult the original explanation for its context.';
}
