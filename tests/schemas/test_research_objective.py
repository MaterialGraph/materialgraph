import pytest
from pydantic import ValidationError

from app.schemas.discovery import (
    MAX_RESEARCH_OBJECTIVE_ELEMENTS,
    ResearchObjective,
)


def test_normalizes_and_deduplicates_element_collections():
    objective = ResearchObjective(
        avoid_elements=["li", "LI", " Li ", "Co"],
        prefer_elements=["na", "NA"],
        preserve_elements=["fe", "P", "o", "Fe"],
    )

    assert objective.avoid_elements == ["Li", "Co"]
    assert objective.prefer_elements == ["Na"]
    assert objective.preserve_elements == ["Fe", "P", "O"]


@pytest.mark.parametrize(
    "field_name",
    ["avoid_elements", "prefer_elements", "preserve_elements"],
)
def test_rejects_oversized_element_collections(field_name):
    with pytest.raises(ValidationError, match="at most 32 entries"):
        ResearchObjective(
            **{field_name: ["Li"] * (MAX_RESEARCH_OBJECTIVE_ELEMENTS + 1)}
        )


@pytest.mark.parametrize("value", ["Lithium", "Xx", ""])
def test_rejects_noncanonical_element_values(value):
    with pytest.raises(ValidationError, match="Unknown chemical element"):
        ResearchObjective(avoid_elements=[value])


def test_accepts_maximum_valid_element_collection():
    symbols = [
        "H", "He", "Li", "Be", "B", "C", "N", "O",
        "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S",
        "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr",
        "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge",
    ]

    objective = ResearchObjective(avoid_elements=symbols)

    assert objective.avoid_elements == symbols
