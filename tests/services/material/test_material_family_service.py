def test_classify_family_detects_expected_families(db_session):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    relationships = service._classify_relationships(
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Na", "Fe", "P", "O"],
    )

    assert "shared_chemistry" in relationships
    assert "alkali_substitution" in relationships
    assert "transition_metal_related" in relationships
    assert "phosphate_related" in relationships
    assert "oxide_related" in relationships


def test_phosphate_relationship_reason_does_not_claim_shared_framework(
    db_session,
):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    reason = service._build_relationship_reason(
        base_formula="LiFePO4",
        candidate_formula="NaFePO4",
        relationships=["phosphate_related"],
        shared_elements=["Fe", "O", "P"],
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Na", "Fe", "P", "O"],
    )

    assert "both materials contain phosphorus and oxygen" in reason
    assert "structural framework similarity is not validated" in reason
    assert "shares phosphate framework" not in reason


def test_oxide_relationship_reason_does_not_claim_shared_framework(
    db_session,
):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    reason = service._build_relationship_reason(
        base_formula="LiFeO2",
        candidate_formula="NaFeO2",
        relationships=["oxide_related"],
        shared_elements=["Fe", "O"],
        base_elements=["Li", "Fe", "O"],
        candidate_elements=["Na", "Fe", "O"],
    )

    assert "both materials contain oxygen" in reason
    assert "oxide structure similarity is not validated" in reason
    assert "shares oxide chemistry" not in reason


def test_phosphate_reason_matches_asymmetric_classification_evidence(
    db_session,
):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    reason = service._build_relationship_reason(
        base_formula="LiP",
        candidate_formula="NaPO",
        relationships=["phosphate_related"],
        shared_elements=["P"],
        base_elements=["Li", "P"],
        candidate_elements=["Na", "P", "O"],
    )

    assert (
        "both materials contain phosphorus, and the candidate contains oxygen"
        in reason
    )
    assert "structural framework similarity is not validated" in reason


def test_magnesium_is_not_classified_as_an_alkali_substitution(db_session):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    assert service._has_alkali_substitution({"Li", "O"}, {"Mg", "O"}) is False


def test_alkali_reason_is_a_composition_hypothesis(db_session):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)
    reason = service._build_relationship_reason(
        base_formula="LiFePO4",
        candidate_formula="NaFePO4",
        relationships=["alkali_substitution"],
        shared_elements=["Fe", "O", "P"],
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Na", "Fe", "P", "O"],
    )

    assert "composition-level alkali-substitution hypothesis" in reason
    assert "substitution mechanism is not validated" in reason


def test_family_order_ignores_correlated_relationship_label_count(db_session):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)
    candidates = [
        {
            "material_id": 8,
            "shared_elements": ["O", "P"],
            "relationships": ["oxide_related", "phosphate_related"],
        },
        {
            "material_id": 7,
            "shared_elements": ["Fe", "O", "P"],
            "relationships": ["shared_chemistry"],
        },
    ]

    candidates.sort(key=service._related_material_sort_key)

    assert [candidate["material_id"] for candidate in candidates] == [7, 8]


def test_family_order_uses_material_id_as_final_tie_breaker(db_session):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)
    candidates = [
        {"material_id": 9, "shared_elements": ["O", "P"]},
        {"material_id": 4, "shared_elements": ["O", "P"]},
    ]

    candidates.sort(key=service._related_material_sort_key)

    assert [candidate["material_id"] for candidate in candidates] == [4, 9]


def test_family_lookup_scopes_composition_loading_to_overlap_candidates(
    db_session,
):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)
    original_loader = service._get_material_elements_map
    requested_scopes = []

    def recording_loader(material_ids):
        requested_scopes.append(list(material_ids))
        return original_loader(material_ids)

    service._get_material_elements_map = recording_loader

    result, elements_map = service.get_material_families_with_elements(5)

    assert requested_scopes
    assert requested_scopes[0][0] == 5
    assert set(elements_map) <= set(requested_scopes[0])
    assert result["material_id"] == 5


def test_family_sql_prefilter_preserves_strong_relationship_semantics(
    db_session,
):
    from app.models.material import Material
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)
    result, scoped_elements = service.get_material_families_with_elements(5)

    all_material_ids = [
        material_id
        for (material_id,) in db_session.query(Material.id)
        .filter(Material.id != 5)
        .filter(~Material.mp_id.like(f"{service.TEST_MP_PREFIX}%"))
        .all()
    ]
    exhaustive_elements = service._get_material_elements_map(
        [5, *all_material_ids]
    )
    base_elements = exhaustive_elements[5]
    expected_ids = {
        material_id
        for material_id in all_material_ids
        if service._has_strong_relationship(
            service._classify_relationships(
                base_elements,
                exhaustive_elements.get(material_id, []),
            )
        )
    }
    actual_ids = {
        item["material_id"]
        for item in result["related_materials"]
    }

    assert actual_ids == expected_ids
    assert set(scoped_elements) <= {5, *expected_ids}
