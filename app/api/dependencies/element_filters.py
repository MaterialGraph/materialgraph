from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status

from app.domain.periodic_table import normalize_element_symbol


@dataclass(frozen=True)
class ElementFilters:
    avoid_element: str | None
    prefer_element: str | None


def _normalize_optional_symbol(
    value: str | None,
    parameter_name: str,
) -> str | None:
    if value is None:
        return None

    try:
        return normalize_element_symbol(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "unknown_element_symbol",
                "parameter": parameter_name,
                "value": value,
                "message": str(exc),
            },
        ) from exc


def get_element_filters(
    avoid_element: Annotated[
        str | None,
        Query(min_length=1, max_length=3),
    ] = None,
    prefer_element: Annotated[
        str | None,
        Query(min_length=1, max_length=3),
    ] = None,
) -> ElementFilters:
    return ElementFilters(
        avoid_element=_normalize_optional_symbol(
            avoid_element,
            "avoid_element",
        ),
        prefer_element=_normalize_optional_symbol(
            prefer_element,
            "prefer_element",
        ),
    )


ElementFiltersDependency = Annotated[
    ElementFilters,
    Depends(get_element_filters),
]