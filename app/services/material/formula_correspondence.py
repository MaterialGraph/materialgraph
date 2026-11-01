"""Formula correspondence between two stored compositions (SRQ-01, spec rev 3.6).

Classifies an alkali-changing pair as an exact alkali formula analog (EFA) or
not, following the classification algorithm in section 3 of the SRQ-01 S2
specification. The comparison uses stored composition fractions only (2.1,
D8): no formula-string parsing and no pymatgen.

An EFA establishes only that two reduced formulas correspond under one alkali
replacement. It establishes nothing about crystal structure or framework,
oxidation states, stability, synthesizability or whether any reaction is
possible (2.3).

Pure functions only; not yet called by any service, route or schema.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from app.services.material.search_service import TAU, compositions_equal

# D6: H and Fr are excluded. Deliberately separate from
# app.domain.element_groups.ALKALI_METALS, which still includes Fr.
EFA_ALKALI_METALS = frozenset({"Li", "Na", "K", "Rb", "Cs"})

CorrespondenceClass = Literal[
    "exact_alkali_replacement",
    "not_exact_replacement",
    "not_evaluated",
]
CorrespondenceReason = Literal[
    "ratios_differ",
    "non_alkali_elements_differ",
    "replacement_alkali_in_source",
    "replaced_alkali_in_candidate",
    "multiple_alkali_changes",
    "formula_unparsed",
]


@dataclass(frozen=True)
class FormulaCorrespondence:
    correspondence_class: CorrespondenceClass
    # None only for exact_alkali_replacement.
    reason: CorrespondenceReason | None
    # Set only in steps 7-8, where exactly one alkali A (removed) and one
    # alkali B (added) differ between source and candidate.
    replaced_from: str | None = None
    replaced_to: str | None = None


def _not_exact(reason: CorrespondenceReason, replaced_from=None, replaced_to=None):
    return FormulaCorrespondence("not_exact_replacement", reason, replaced_from, replaced_to)


def classify_formula_correspondence(
    source: Mapping[str, float] | None,
    candidate: Mapping[str, float] | None,
    tau: float = TAU,
) -> FormulaCorrespondence | None:
    """Classify the pair (source S, candidate C) by the section 3 algorithm.

    Both arguments are normalised composition fractions (as returned by
    ``normalise_stored_composition``), or None when the stored composition is
    unusable. Returns None when the alkali sets are equal: the pair is not
    alkali-changing and no classification is produced (step 2).
    """
    # Step 1: an unusable stored composition is never compared.
    if not source or not candidate:
        return FormulaCorrespondence("not_evaluated", "formula_unparsed")

    # Step 2.
    source_alkali = EFA_ALKALI_METALS.intersection(source)
    candidate_alkali = EFA_ALKALI_METALS.intersection(candidate)
    if source_alkali == candidate_alkali:
        return None

    # Step 3.
    removed = source_alkali - candidate_alkali
    added = candidate_alkali - source_alkali

    # Steps 4-6, in this order.
    if len(removed) > 1 or len(added) > 1:
        return _not_exact("multiple_alkali_changes")
    if not removed:
        return _not_exact("replaced_alkali_in_candidate")
    if not added:
        return _not_exact("replacement_alkali_in_source")

    # Step 7: removed = {A}, added = {B}.
    (replaced_from,) = removed
    (replaced_to,) = added
    if set(source) - {replaced_from} != set(candidate) - {replaced_to}:
        return _not_exact("non_alkali_elements_differ", replaced_from, replaced_to)

    # Step 8: move A's amount to B, normalise, compare within tau.
    substituted = {
        (replaced_to if symbol == replaced_from else symbol): amount
        for symbol, amount in source.items()
    }
    total = sum(substituted.values())
    substituted = {symbol: amount / total for symbol, amount in substituted.items()}
    if compositions_equal(substituted, dict(candidate), tau=tau):
        return FormulaCorrespondence("exact_alkali_replacement", None, replaced_from, replaced_to)
    return _not_exact("ratios_differ", replaced_from, replaced_to)
