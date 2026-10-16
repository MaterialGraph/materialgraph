import pytest

from app.utils.chemical_formula import (
    extract_elements,
    parse_formula_elements_strict,
)


@pytest.mark.parametrize(
    ("formula", "expected"),
    [
        ("LiFePO4", {"Li", "Fe", "P", "O"}),
        ("Na3Fe(PO4)2", {"Na", "Fe", "P", "O"}),
        ("NaFe3P3O13", {"Na", "Fe", "P", "O"}),
        ("LiFe(PO3)3", {"Li", "Fe", "P", "O"}),
        ("Co", {"Co"}),
        ("CO", {"C", "O"}),
        ("CaCO3", {"Ca", "C", "O"}),
        ("Na0.5CoO2", {"Na", "Co", "O"}),
        ("((PO4)2)3", {"P", "O"}),
        ("  LiFePO4  ", {"Li", "Fe", "P", "O"}),
    ],
)
def test_strict_parser_returns_elements_of_valid_formulas(formula, expected):
    assert parse_formula_elements_strict(formula) == frozenset(expected)


@pytest.mark.parametrize(
    "formula",
    [
        None,
        "",
        "   ",
        "Xx2O",        # unknown symbol
        "li2O",        # lowercase start
        "LiFe(PO4",    # unbalanced
        "Li)Fe(",      # unbalanced
        "Li()",        # empty group
        "()",
        "Fe2O3·H2O",   # hydrate dot unsupported
        "[Fe(CN)6]",   # brackets unsupported
        "Fe2+",        # charge unsupported
        "2LiFePO4",    # leading count
        42,
    ],
)
def test_strict_parser_returns_none_when_formula_cannot_be_evaluated(formula):
    assert parse_formula_elements_strict(formula) is None


def test_strict_parser_agrees_with_extract_elements_on_valid_formulas():
    for formula in ("LiFePO4", "Na3Fe(PO4)2", "Na9Fe3P8O29", "NaFeP2O7"):
        assert parse_formula_elements_strict(formula) == frozenset(
            extract_elements(formula)
        )


def test_existing_extract_elements_behaviour_is_unchanged():
    # The permissive helper used by ranking is intentionally untouched.
    assert extract_elements("Xx2O") == {"Xx", "O"}
    assert extract_elements(None) == set()
