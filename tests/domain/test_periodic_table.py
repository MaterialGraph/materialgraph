import pytest

from app.domain.periodic_table import (
    ELEMENT_SYMBOLS,
    normalize_element_symbol,
)


def test_periodic_table_contains_all_118_elements():
    assert len(ELEMENT_SYMBOLS) == 118


def test_periodic_table_contains_first_and_last_elements():
    assert "H" in ELEMENT_SYMBOLS
    assert "Og" in ELEMENT_SYMBOLS


@pytest.mark.parametrize("symbol", ELEMENT_SYMBOLS)
def test_every_canonical_symbol_normalizes_to_itself(symbol):
    assert normalize_element_symbol(symbol) == symbol


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("li", "Li"),
        ("LI", "Li"),
        ("fe", "Fe"),
        ("FE", "Fe"),
        ("og", "Og"),
        ("OG", "Og"),
    ],
)
def test_element_symbol_normalization(value, expected):
    assert normalize_element_symbol(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "Xx",
        "Ab",
        "Q",
        "NotAnElement",
        "",
    ],
)
def test_unknown_element_symbols_are_rejected(value):
    with pytest.raises(
        ValueError,
        match="Unknown chemical element symbol",
    ):
        normalize_element_symbol(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" Li ", "Li"),
        ("\tFe\n", "Fe"),
    ],
)
def test_element_symbol_normalization_removes_surrounding_whitespace(
    value,
    expected,
):
    assert normalize_element_symbol(value) == expected