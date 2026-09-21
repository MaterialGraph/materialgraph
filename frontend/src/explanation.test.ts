import { expect, it } from 'vitest';
import { explanationClauses } from './explanation';

it('keeps the backend clauses and their order without splitting decimal values', () => {
  const prose = 'Candidate A has score 1.25. Composition heuristic; structure is not validated. Validate experimentally.';
  const clauses = explanationClauses(prose);
  expect(clauses).toEqual([
    'Candidate A has score 1.25.',
    'Composition heuristic;',
    'structure is not validated.',
    'Validate experimentally.',
  ]);
  expect(clauses.join(' ')).toBe(prose);
});
