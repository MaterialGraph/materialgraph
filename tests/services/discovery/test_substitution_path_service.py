from app.services.discovery.substitution_path_service import (
    DiscoverySubstitutionPathService,
)


def test_shared_element_fallback_does_not_claim_framework_preservation():
    service = DiscoverySubstitutionPathService()

    result = service.build_path(
        base_formula="LiFePO4",
        candidate_formula="LiFe(PO3)4",
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Li", "Fe", "P", "O"],
        relationships=[],
    )

    assert result is not None
    assert result["path_type"] == "shared_element_continuity"
    assert result["shared_elements"] == ["Fe", "Li", "O", "P"]
    assert result["preservation_basis"] == "element_overlap"
    assert result["structural_preservation_validated"] is False
    assert result["relationship_basis"] == "composition_heuristic"
    assert result["substitution_mechanism_validated"] is False
    assert "structural framework preservation is not validated" in result["reason"]

def test_shared_element_continuity_requires_at_least_three_shared_elements():
    service = DiscoverySubstitutionPathService()

    result = service.build_path(
        base_formula="LiFe",
        candidate_formula="LiFeO",
        base_elements=["Li", "Fe"],
        candidate_elements=["Li", "Fe", "O"],
        relationships=[],
    )

    assert result is None


def test_magnesium_is_not_treated_as_an_alkali_substitution():
    service = DiscoverySubstitutionPathService()

    result = service.build_path(
        base_formula="LiFePO4",
        candidate_formula="MgFePO4",
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Mg", "Fe", "P", "O"],
        relationships=["shared_chemistry"],
    )

    assert result is not None
    assert result["path_type"] == "shared_element_continuity"