"""Shared evidence semantics for material risk and criticality metrics."""

EVIDENCE_BASIS = "latest_element_risk_profile"

SHARED_EVIDENCE_DIMENSIONS = (
    "supply_risk_score",
    "geopolitical_risk_score",
    "toxicity_score",
)
RISK_EVIDENCE_DIMENSIONS = SHARED_EVIDENCE_DIMENSIONS
CRITICALITY_EVIDENCE_DIMENSIONS = (
    "abundance_score",
    *SHARED_EVIDENCE_DIMENSIONS,
    "recyclability_score",
)

RISK_AGGREGATION_METHOD = (
    "mean_available_dimensions_then_equal_mean_calculable_elements"
)
CRITICALITY_AGGREGATION_METHOD = (
    "mean_available_dimensions_then_composition_weighted_mean"
)


def calculate_element_risk_score(
    values: list[float | None],
) -> float | None:
    available_values = [value for value in values if value is not None]

    if not available_values:
        return None

    return round(sum(available_values) / len(available_values), 3)


def calculate_material_risk_score(
    element_dimension_values: list[list[float | None]],
) -> float | None:
    element_scores = [
        score
        for values in element_dimension_values
        if (score := calculate_element_risk_score(values)) is not None
    ]

    return calculate_material_risk_from_element_scores(element_scores)


def calculate_material_risk_from_element_scores(
    element_scores: list[float],
) -> float | None:
    if not element_scores:
        return None

    return round(sum(element_scores) / len(element_scores), 3)


def evidence_dimension_summary(profile, dimensions: tuple[str, ...]) -> dict:
    expected = len(dimensions)
    available = (
        sum(getattr(profile, name, None) is not None for name in dimensions)
        if profile is not None
        else 0
    )
    return {
        "available": available,
        "expected": expected,
        "coverage": round(available / expected, 4),
        "complete": available == expected,
    }