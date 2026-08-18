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
