"""User-facing wording for composition relationship identifiers.

Internal identifiers such as ``alkali_substitution`` are API values and stay
unchanged. Text shown to users describes only what the rule compared: the
alkali relationship compares alkali-metal membership, not element ratios,
structure or any substitution mechanism.
"""

from collections.abc import Iterable

from app.domain.element_groups import ALKALI_METALS

DIFFERENT_ALKALI_LABEL = "different alkali metal (composition not compared)"
RATIOS_AND_STRUCTURE_NOT_COMPARED = (
    "element ratios and structure were not compared"
)


def relationship_text(identifier: str | None) -> str:
    """Return the user-facing wording for a relationship identifier."""
    if identifier == "alkali_substitution":
        return DIFFERENT_ALKALI_LABEL
    return identifier or ""


def alkali_difference_text(
    source_elements: Iterable[str],
    target_elements: Iterable[str],
) -> str:
    """Describe an alkali-membership difference without implying removal.

    Alkali metals are listed as sets, so a retained source alkali appears on
    both sides (for example ``Li → Li, Na``).
    """
    source_alkali = sorted(set(source_elements) & ALKALI_METALS)
    target_alkali = sorted(set(target_elements) & ALKALI_METALS)
    return (
        f"alkali metals differ: {', '.join(source_alkali)} → "
        f"{', '.join(target_alkali)}; {RATIOS_AND_STRUCTURE_NOT_COMPARED}"
    )
