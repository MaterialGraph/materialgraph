"""SRQ-01 PR-A part 1: formula-correspondence classifier (spec rev 3.6, sections 2-3, AC1)."""

import dataclasses
from typing import get_args

import pytest

from app.domain.element_groups import ALKALI_METALS
from app.services.material.formula_correspondence import (
    EFA_ALKALI_METALS,
    CorrespondenceClass,
    CorrespondenceReason,
    FormulaCorrespondence,
    classify_formula_correspondence,
)
from app.services.material.search_service import TAU, normalise_stored_composition

# X in the 2.2 table stands for an unchanged non-alkali remainder; FeP2O7 here.
X = {"Fe": 1, "P": 2, "O": 7}


def fractions(**amounts):
    """Stored-style amounts -> normalised fractions, as the request path will do."""
    return normalise_stored_composition(dict(amounts))


def classify(source, candidate):
    return classify_formula_correspondence(source, candidate)


def exact(replaced_from, replaced_to):
    return FormulaCorrespondence("exact_alkali_replacement", None, replaced_from, replaced_to)


def not_exact(reason, replaced_from=None, replaced_to=None):
    return FormulaCorrespondence("not_exact_replacement", reason, replaced_from, replaced_to)


LIFEPO4 = fractions(Li=1, Fe=1, P=1, O=4)


# Contract ----------------------------------------------------------------------

def test_alkali_set_excludes_francium_and_hydrogen_d6():
    assert EFA_ALKALI_METALS == frozenset({"Li", "Na", "K", "Rb", "Cs"})
    # The shared element group is unchanged and still includes Fr.
    assert ALKALI_METALS - EFA_ALKALI_METALS == {"Fr"}


def test_class_and_reason_values_match_section_3():
    assert set(get_args(CorrespondenceClass)) == {
        "exact_alkali_replacement", "not_exact_replacement", "not_evaluated",
    }
    assert set(get_args(CorrespondenceReason)) == {
        "ratios_differ", "non_alkali_elements_differ", "replacement_alkali_in_source",
        "replaced_alkali_in_candidate", "multiple_alkali_changes", "formula_unparsed",
    }


def test_result_type_is_frozen_with_four_fields():
    result = exact("Li", "Na")
    assert [field.name for field in dataclasses.fields(result)] == [
        "correspondence_class", "reason", "replaced_from", "replaced_to",
    ]
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.reason = "ratios_differ"


# Section 2.2 table, row by row ---------------------------------------------------

@pytest.mark.parametrize(
    ("source", "candidate", "expected"),
    [
        pytest.param(LIFEPO4, fractions(Na=1, Fe=1, P=1, O=4), exact("Li", "Na"),
                     id="LiFePO4->NaFePO4"),
        pytest.param(fractions(Li=1, Co=1, O=2), fractions(Na=1, Co=1, O=2), exact("Li", "Na"),
                     id="LiCoO2->NaCoO2"),
        pytest.param(fractions(Li=2, Fe=1, Si=1, O=4), fractions(Na=2, Fe=1, Si=1, O=4), exact("Li", "Na"),
                     id="Li2FeSiO4->Na2FeSiO4"),
        pytest.param(fractions(Li=1, K=1, **X), fractions(Na=1, K=1, **X), exact("Li", "Na"),
                     id="LiKX->NaKX_K_retained"),
        pytest.param(LIFEPO4, fractions(Na=3, Fe=1, P=2, O=8), not_exact("ratios_differ", "Li", "Na"),
                     id="LiFePO4->Na3Fe(PO4)2"),
        pytest.param(LIFEPO4, fractions(Na=1, Fe=1, P=2, O=7), not_exact("ratios_differ", "Li", "Na"),
                     id="LiFePO4->NaFeP2O7"),
        pytest.param(LIFEPO4, fractions(Na=2, Fe=1, P=1, O=4, F=1),
                     not_exact("non_alkali_elements_differ", "Li", "Na"),
                     id="LiFePO4->Na2FePO4F"),
        pytest.param(fractions(Li=1, Na=1, **X), fractions(Na=2, **X), not_exact("replacement_alkali_in_source"),
                     id="LiNaX->Na2X"),
        pytest.param(LIFEPO4, fractions(Li=1, Na=1, Fe=2, P=2, O=8), not_exact("replaced_alkali_in_candidate"),
                     id="LiFePO4->LiNaFe2(PO4)2"),
        pytest.param(fractions(Li=1, K=1, **X), fractions(Na=1, Rb=1, **X), not_exact("multiple_alkali_changes"),
                     id="LiKX->NaRbX"),
    ],
)
def test_section_2_2_table(source, candidate, expected):
    assert classify(source, candidate) == expected


# Algorithm steps 1-8 ---------------------------------------------------------------

@pytest.mark.parametrize(
    ("source", "candidate"),
    [(None, LIFEPO4), (LIFEPO4, None), (None, None), ({}, LIFEPO4), (LIFEPO4, {})],
    ids=["source_none", "candidate_none", "both_none", "source_empty", "candidate_empty"],
)
def test_step_1_unusable_composition_is_not_evaluated(source, candidate):
    assert classify(source, candidate) == FormulaCorrespondence("not_evaluated", "formula_unparsed", None, None)


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        (LIFEPO4, fractions(Li=1, Fe=1, P=3, O=9)),          # same alkali set {Li}
        (fractions(Li=1, K=1, **X), fractions(Li=2, K=1, **X)),  # same alkali set {Li, K}
        (fractions(Fe=1, P=1, O=4), fractions(Fe=2, O=3)),   # no alkali on either side
        (LIFEPO4, LIFEPO4),
        # Rev 3.7: one side without any alkali is insertion or removal, not a
        # one-alkali replacement.
        (fractions(Fe=1, P=1, O=4), fractions(Na=1, Fe=1, P=1, O=4)),  # FePO4 -> NaFePO4
        (LIFEPO4, fractions(Fe=1, P=1, O=4)),                          # LiFePO4 -> FePO4
        (fractions(Li=1, K=1, **X), fractions(**X)),                   # two alkalis removed, none left
        (fractions(**X), fractions(Na=1, K=1, **X)),                   # two alkalis inserted
    ],
    ids=["same_single_alkali", "same_two_alkalis", "no_alkali", "identical",
         "FePO4->NaFePO4", "LiFePO4->FePO4", "all_alkalis_removed", "alkalis_inserted"],
)
def test_step_2_produces_no_classification(source, candidate):
    assert classify(source, candidate) is None


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        (fractions(Li=1, K=1, **X), fractions(Na=1, Rb=1, **X)),  # two removed, two added
        (fractions(Li=1, **X), fractions(Li=1, Na=1, K=1, **X)),  # none removed, two added
        (fractions(Li=1, K=1, Na=1, **X), fractions(Na=1, **X)),  # two removed, none added
        (fractions(Li=1, K=1, **X), fractions(Na=1, **X)),        # two removed, one added
    ],
    ids=["two_for_two", "two_added", "two_removed", "two_removed_one_added"],
)
def test_step_4_more_than_one_alkali_change(source, candidate):
    assert classify(source, candidate) == not_exact("multiple_alkali_changes")


def test_step_4_precedes_steps_5_and_6():
    # Two added and none removed would also satisfy step 5; step 4 wins.
    assert classify(fractions(Li=1, **X), fractions(Li=1, Na=1, K=1, **X)).reason == "multiple_alkali_changes"


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        (LIFEPO4, fractions(Li=1, Na=1, Fe=2, P=2, O=8)),
        (fractions(Li=1, **X), fractions(Li=1, K=1, **X)),
    ],
    ids=["LiFePO4->LiNaFe2(PO4)2", "LiX->LiKX"],
)
def test_step_5_alkali_added_while_source_alkalis_remain(source, candidate):
    assert classify(source, candidate) == not_exact("replaced_alkali_in_candidate")


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        (fractions(Li=1, Na=1, **X), fractions(Na=2, **X)),
        (fractions(Li=1, K=1, **X), fractions(K=1, **X)),
    ],
    ids=["LiNaX->Na2X", "LiKX->KX"],
)
def test_step_6_alkali_removed_without_a_new_one(source, candidate):
    assert classify(source, candidate) == not_exact("replacement_alkali_in_source")


@pytest.mark.parametrize(
    ("source", "candidate"),
    [
        (LIFEPO4, fractions(Na=2, Fe=1, P=1, O=4, F=1)),  # element added
        (LIFEPO4, fractions(Na=1, Fe=1, O=2)),             # element missing
        (LIFEPO4, fractions(Na=1, Mn=1, P=1, O=4)),        # element swapped
    ],
    ids=["extra_element", "missing_element", "different_element"],
)
def test_step_7_non_alkali_elements_differ(source, candidate):
    assert classify(source, candidate) == not_exact("non_alkali_elements_differ", "Li", "Na")


def test_step_7_retained_alkali_counts_as_an_other_element():
    # Li -> Na with K kept on the source side but absent from the candidate is a
    # two-alkali change (step 4), not step 7; with K kept on both sides, step 7
    # compares the remaining elements, K included.
    assert classify(fractions(Li=1, K=1, **X), fractions(Na=1, K=1, Fe=1, O=3)) == not_exact(
        "non_alkali_elements_differ", "Li", "Na",
    )


@pytest.mark.parametrize(
    ("source", "candidate", "replaced"),
    [
        (LIFEPO4, fractions(Na=1, Fe=1, P=1, O=4), ("Li", "Na")),
        (fractions(Na=1, Fe=1, P=1, O=4), LIFEPO4, ("Na", "Li")),
        (fractions(K=1, Co=1, O=2), fractions(Cs=1, Co=1, O=2), ("K", "Cs")),
        (fractions(Li=1, K=2, **X), fractions(Rb=1, K=2, **X), ("Li", "Rb")),
    ],
    ids=["Li->Na", "Na->Li", "K->Cs", "Li->Rb_K_retained"],
)
def test_step_8_equal_after_substitution_is_exact(source, candidate, replaced):
    assert classify(source, candidate) == exact(*replaced)


@pytest.mark.parametrize(
    "candidate",
    [fractions(Na=3, Fe=1, P=2, O=8), fractions(Na=2, Fe=1, P=1, O=4), fractions(Na=1, Fe=2, P=2, O=8)],
    ids=["Na3Fe(PO4)2", "Na2FePO4", "NaFe2(PO4)2"],
)
def test_step_8_unequal_after_substitution_is_ratios_differ(candidate):
    assert classify(LIFEPO4, candidate) == not_exact("ratios_differ", "Li", "Na")


def test_retained_alkali_ratio_must_also_match():
    # K is retained but in a different proportion: not an exact analog.
    assert classify(fractions(Li=1, K=1, **X), fractions(Na=1, K=2, **X)) == not_exact(
        "ratios_differ", "Li", "Na",
    )


def test_replaced_alkalis_are_set_only_in_steps_7_and_8():
    unset = [
        classify(None, LIFEPO4),                                                   # step 1
        classify(fractions(Li=1, K=1, **X), fractions(Na=1, Rb=1, **X)),           # step 4
        classify(LIFEPO4, fractions(Li=1, Na=1, Fe=2, P=2, O=8)),                  # step 5
        classify(fractions(Li=1, Na=1, **X), fractions(Na=2, **X)),                # step 6
    ]
    assert all((r.replaced_from, r.replaced_to) == (None, None) for r in unset)
    set_ = [
        classify(LIFEPO4, fractions(Na=2, Fe=1, P=1, O=4, F=1)),                   # step 7
        classify(LIFEPO4, fractions(Na=3, Fe=1, P=2, O=8)),                        # step 8, unequal
        classify(LIFEPO4, fractions(Na=1, Fe=1, P=1, O=4)),                        # step 8, equal
    ]
    assert all((r.replaced_from, r.replaced_to) == ("Li", "Na") for r in set_)


def test_francium_and_hydrogen_are_not_alkali_metals_here():
    # Fr and H are outside the EFA set (D6): the candidate has no alkali, so
    # the pair is not a one-alkali replacement (step 2).
    assert classify(fractions(Li=1, **X), fractions(Fr=1, **X)) is None
    assert classify(fractions(Li=1, **X), fractions(H=1, **X)) is None
    # With an alkali retained on both sides, Fr is an ordinary other element.
    assert classify(fractions(Li=1, Fr=1, **X), fractions(Na=1, Fr=1, **X)) == exact("Li", "Na")


# Stored-style scaled cell compositions (2.1, AC1 reduction) ------------------------

def test_scaled_stored_amounts_reduce_before_comparison():
    stored_lifepo4 = normalise_stored_composition({"Li": 4.0, "Fe": 4.0, "P": 4.0, "O": 16.0})
    stored_nafepo4 = normalise_stored_composition({"Na": 4.0, "Fe": 4.0, "P": 4.0, "O": 16.0})
    stored_na3fe_po4_2 = normalise_stored_composition({"Na": 6.0, "Fe": 2.0, "P": 4.0, "O": 16.0})

    assert classify(stored_lifepo4, stored_nafepo4) == exact("Li", "Na")
    assert classify(stored_lifepo4, stored_na3fe_po4_2) == not_exact("ratios_differ", "Li", "Na")


def test_li2fe2p2o8_is_the_same_reduced_composition_as_lifepo4():
    li2fe2p2o8 = normalise_stored_composition({"Li": 2, "Fe": 2, "P": 2, "O": 8})
    # Same alkali set and equal composition: not an alkali-changing pair.
    assert classify(li2fe2p2o8, LIFEPO4) is None
    # Against the sodium analog it is exact, scaled or not.
    assert classify(li2fe2p2o8, fractions(Na=2, Fe=2, P=2, O=8)) == exact("Li", "Na")


def test_malformed_stored_composition_is_not_evaluated():
    # The request path maps a normalisation failure to None (2.1, AC13).
    for raw in ({}, None, {"Li": 0, "Fe": 1}, {"Xx": 1}, {"Fe": float("nan")}):
        with pytest.raises(ValueError):
            normalise_stored_composition(raw)
    assert classify(None, LIFEPO4) == FormulaCorrespondence("not_evaluated", "formula_unparsed")


# Tolerance (TAU on normalised fractions) -----------------------------------------

def _shifted_nafepo4(delta):
    base = fractions(Na=1, Fe=1, P=1, O=4)
    return {**base, "Na": base["Na"] + delta, "O": base["O"] - delta}


def test_tolerance_just_inside_tau_is_exact():
    assert TAU == 1e-6
    assert classify(LIFEPO4, _shifted_nafepo4(0.9 * TAU)) == exact("Li", "Na")


def test_tolerance_just_outside_tau_is_ratios_differ():
    assert classify(LIFEPO4, _shifted_nafepo4(1.1 * TAU)) == not_exact("ratios_differ", "Li", "Na")
