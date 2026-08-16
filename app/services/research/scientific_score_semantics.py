def normalize_scientific_usefulness_score(
    value: float | int | None,
) -> float:
    """Return the canonical comparison value for a scientific score."""
    resolved_value = 0.0 if value is None else float(value)
    return round(resolved_value, 2)
