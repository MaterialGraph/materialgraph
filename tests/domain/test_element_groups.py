from app.domain.element_groups import ALKALI_METALS


def test_alkali_metal_taxonomy_excludes_magnesium():
    assert ALKALI_METALS == {"Li", "Na", "K", "Rb", "Cs", "Fr"}
    assert "Mg" not in ALKALI_METALS
