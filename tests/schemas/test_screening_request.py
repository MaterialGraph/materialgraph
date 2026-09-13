import pytest
from pydantic import ValidationError

from app.schemas.screening import (
    MAX_SCREENING_ELEMENTS,
    CandidateScreeningRequest,
)


def test_normalizes_and_deduplicates_screening_elements():
    request = CandidateScreeningRequest(
        scarce_elements=["li", "LI", " Li ", "Co"],
        avoid_elements=["na", "NA"],
    )

    assert request.scarce_elements == ["Li", "Co"]
    assert request.avoid_elements == ["Na"]


@pytest.mark.parametrize("field_name", ["scarce_elements", "avoid_elements"])
def test_rejects_oversized_screening_elements(field_name):
    with pytest.raises(ValidationError, match="at most 32 entries"):
        CandidateScreeningRequest(
            **{field_name: ["Li"] * (MAX_SCREENING_ELEMENTS + 1)}
        )


@pytest.mark.parametrize("value", ["Lithium", "Xx", ""])
def test_rejects_invalid_screening_elements(value):
    with pytest.raises(ValidationError, match="Unknown chemical element"):
        CandidateScreeningRequest(scarce_elements=[value])
