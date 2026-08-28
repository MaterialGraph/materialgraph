# Independent-Audit Baseline and Chronology Verification

## Purpose

This record resolves the post-freeze applicability of `MG-IA-011` without
rewriting its frozen finding evidence.

## Frozen audit baseline

- Audited commit: `a1605e61f72035890692ab4df63ebd2f7b859069`
- Audit tree: `126dd7478eda3c97d10f5b2930493d3a41ffe622`
- Remediation documentation baseline:
  `2d33273c916771f592200d87bafe1935aa8ec942`

## Chronology evidence

Commit `6545ba7b2838` (`Bound neighborhood traversal by result limit`) predates
the audited commit. At exact audited commit `a1605e61`,
`MaterialNeighborhoodService.get_neighborhood` executes `continue` when the
node budget is exhausted. That control flow occurs before edge emission,
visited-set insertion, and frontier insertion for the rejected neighbor.

The exact repository baseline therefore does not queue or expand a neighbor
that was rejected by the node limit. The premise in frozen `MG-IA-011` came
from supplied source evidence that did not match the controlling immutable
repository revision.

Later commit `118258b72376` added deterministic bounded-neighborhood ordering
for `MG-IA-012`; it did not create the pre-existing admission-before-expansion
behavior used to invalidate `MG-IA-011`.

## Verification evidence

The exact-baseline implementation satisfies the bounded-expansion contract:

- rejected neighbors leave the loop before edge/frontier mutation;
- `limit=1` expands only the root;
- bounded tests assert the precise neighbor-service call sequence;
- subsequent full-suite verification retained those tests.

## Disposition

`MG-IA-011` is **Not actionable** because stronger exact-repository evidence
invalidates its current-code premise. The original finding remains frozen for
traceability and its identifier is not reused.

This is a post-freeze applicability judgment, not a claim that the independent
finding was remediated after the audit.
