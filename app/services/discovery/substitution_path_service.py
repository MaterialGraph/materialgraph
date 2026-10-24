from app.domain.element_groups import ALKALI_METALS
from app.domain.relationship_labels import alkali_difference_text


ALKALI_ELEMENTS = ALKALI_METALS
TRANSITION_METALS = {"Fe", "Mn", "Co", "Ni", "Ti", "V", "Cr"}


class DiscoverySubstitutionPathService:
    def build_path(
        self,
        base_formula: str,
        candidate_formula: str,
        base_elements: list[str],
        candidate_elements: list[str],
        relationships: list[str],
    ) -> dict | None:
        base_set = set(base_elements)
        candidate_set = set(candidate_elements)

        replaced_elements = sorted(base_set - candidate_set)
        introduced_elements = sorted(candidate_set - base_set)
        shared_elements = sorted(base_set & candidate_set)
        preserved_framework = shared_elements  # Backward-compatible alias.

        if "alkali_substitution" in relationships:
            return {
                "path_type": "alkali_substitution",
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "replaced_elements": [
                    element
                    for element in replaced_elements
                    if element in ALKALI_ELEMENTS
                ],
                "introduced_elements": [
                    element
                    for element in introduced_elements
                    if element in ALKALI_ELEMENTS
                ],
                "shared_elements": shared_elements,
                "preserved_framework": preserved_framework,
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "relationship_basis": "composition_heuristic",
                "substitution_mechanism_validated": False,
                "reason": self._build_alkali_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    base_set=base_set,
                    candidate_set=candidate_set,
                    shared_elements=shared_elements,
                ),
            }

        if self._has_transition_metal_substitution(
            base_set=base_set,
            candidate_set=candidate_set,
        ):
            return {
                "path_type": "transition_metal_substitution",
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "replaced_elements": [
                    element
                    for element in replaced_elements
                    if element in TRANSITION_METALS
                ],
                "introduced_elements": [
                    element
                    for element in introduced_elements
                    if element in TRANSITION_METALS
                ],
                "shared_elements": shared_elements,
                "preserved_framework": preserved_framework,
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "relationship_basis": "composition_heuristic",
                "substitution_mechanism_validated": False,
                "reason": self._build_transition_metal_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    replaced_elements=replaced_elements,
                    introduced_elements=introduced_elements,
                    shared_elements=shared_elements,
                ),
            }

        if len(shared_elements) >= 3:
            return {
                "path_type": "shared_element_continuity",
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "replaced_elements": replaced_elements,
                "introduced_elements": introduced_elements,
                "shared_elements": shared_elements,
                # Backward-compatible field name; values represent shared elements.
                "preserved_framework": preserved_framework,
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "relationship_basis": "composition_heuristic",
                "substitution_mechanism_validated": False,
                "reason": (
                    f"{candidate_formula} shares {', '.join(shared_elements)} elements "
                    f"with {base_formula}; structural framework preservation is not "
                    "validated."
                ),
            }

        return None

    def _has_transition_metal_substitution(
        self,
        base_set: set[str],
        candidate_set: set[str],
    ) -> bool:
        base_transition_metals = base_set & TRANSITION_METALS
        candidate_transition_metals = candidate_set & TRANSITION_METALS

        return bool(base_transition_metals or candidate_transition_metals) and (
            base_transition_metals != candidate_transition_metals
        )

    def _build_alkali_reason(
        self,
        base_formula: str,
        candidate_formula: str,
        base_set: set[str],
        candidate_set: set[str],
        shared_elements: list[str],
    ) -> str:
        difference = alkali_difference_text(
            source_elements=base_set,
            target_elements=candidate_set,
        )
        return (
            f"{candidate_formula} relative to {base_formula}: {difference}. "
            f"Shared elements: {', '.join(shared_elements)}."
        )

    def _build_transition_metal_reason(
        self,
        base_formula: str,
        candidate_formula: str,
        replaced_elements: list[str],
        introduced_elements: list[str],
        shared_elements: list[str],
    ) -> str:
        replaced_transition_metals = [
            element for element in replaced_elements if element in TRANSITION_METALS
        ]
        introduced_transition_metals = [
            element for element in introduced_elements if element in TRANSITION_METALS
        ]

        return (
            f"{candidate_formula} differs from {base_formula} in transition "
            f"metals: {', '.join(replaced_transition_metals) or 'none'} absent "
            f"in target; {', '.join(introduced_transition_metals) or 'none'} "
            f"introduced, while sharing {', '.join(shared_elements)} elements; "
            "element ratios and structure were not compared."
        )