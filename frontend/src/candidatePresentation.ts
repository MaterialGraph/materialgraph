import type { Candidate } from './api';

const signalLabels: Record<string, string> = {
  family_related: 'Related composition',
  shared_chemistry: 'Shared elements',
  alkali_substitution: 'Different alkali metal (composition not compared)',
  transition_metal_related: 'Shared transition metal',
  phosphate_related: 'Both contain P and O',
  oxide_related: 'Both contain O',
};

type DiscoveryGoal = { avoid_element: string | null; prefer_element: string | null };

export function presentCandidate(candidate: Candidate, sourceFormula: string, goal: DiscoveryGoal = { avoid_element: null, prefer_element: null }) {
  const signals = new Set(candidate.discovery_path);
  // Alkali metals are reported as sets, so a retained source alkali appears on both sides.
  const alkali = candidate.explanation.match(/alkali metals differ: ([A-Z][a-z]?(?:, [A-Z][a-z]?)*) → ([A-Z][a-z]?(?:, [A-Z][a-z]?)*)/);
  const shared = candidate.explanation.match(/shares ([A-Z][a-z]?(?:, [A-Z][a-z]?)*) chemistry with /);
  const sharedElements = shared?.[1].split(', ') ?? [];
  const source = sourceFormula || 'the source material';
  let hypothesis = `Composition-based rules rank this material as a candidate to investigate alongside ${source}.`;
  if (signals.has('alkali_substitution')) {
    hypothesis = alkali
      ? `Composition rules flag a different alkali metal (${alkali[1]} in ${source}; ${alkali[2]} in this material), based on composition alone. Element ratios and structure were not compared.`
      : `Composition rules flag a different alkali metal relative to ${source}, based on composition alone. Element ratios and structure were not compared.`;
  } else if (signals.has('shared_chemistry')) {
    hypothesis = `This candidate shares elemental chemistry with ${source}.`;
  }
  if (sharedElements.length) hypothesis += ` Shared elements: ${sharedElements.join(', ')}.`;

  // The shared-chemistry signal already accounts for element overlap. Avoid
  // separately displaying the narrower phosphate/oxide overlap as new evidence.
  const visibleSignals = candidate.discovery_path.filter(signal =>
    !(signals.has('shared_chemistry') && ['family_related', 'transition_metal_related', 'phosphate_related', 'oxide_related'].includes(signal))
    && !(signals.has('phosphate_related') && signal === 'oxide_related')
  );
  const elementLabels: Record<string, string | undefined> = {
    preferred_element: goal.prefer_element ? `${goal.prefer_element} present` : undefined,
    avoided_element_removed: goal.avoid_element ? `${goal.avoid_element} absent` : undefined,
    contains_avoided_element: goal.avoid_element ? `Contains ${goal.avoid_element} (avoided)` : undefined,
  };
  const caveats = [];
  if (signals.has('alkali_substitution')) caveats.push('Only alkali-metal membership was compared; element ratios and structure were not.');
  caveats.push('Composition-based signals do not establish structural similarity, synthesis feasibility, or performance.');
  return {
    hypothesis,
    signals: visibleSignals.filter(signal => !(signal in elementLabels) || elementLabels[signal])
      .map(signal => ({ key: signal, label: elementLabels[signal] ?? signalLabels[signal] ?? signal.replaceAll('_', ' ') })),
    caveats,
  };
}

export function factorExplanation(name: string, _candidate: Candidate, goal: { avoid_element: string | null; prefer_element: string | null }) {
  const reasons: Record<string, string> = {
    family_bonus: 'A composition relationship rule added points; it does not establish a shared structure.',
    preferred_element_bonus: goal.prefer_element ? `The candidate contains the preferred element ${goal.prefer_element}.` : 'Preferred element rule contributed to this score.',
    avoided_element_removed_bonus: goal.avoid_element ? `The candidate does not contain ${goal.avoid_element}, the element marked Avoid.` : 'Absence of an avoided element added points.',
    avoided_element_present_penalty: goal.avoid_element ? `The candidate contains the avoided element ${goal.avoid_element}; avoidance is a soft penalty.` : 'Avoided element rule reduced this score.',
  };
  return reasons[name] ?? 'A scoring rule contributed to this result; consult the original explanation for context.';
}

const factorLabels: Record<string, string> = {
  family_bonus: 'Composition relationship',
  preferred_element_bonus: 'Preferred element present',
  avoided_element_removed_bonus: 'Avoided element absent',
  avoided_element_present_penalty: 'Avoided element present',
};

export function factorLabel(name: string) {
  return factorLabels[name] ?? name.replaceAll('_', ' ');
}
