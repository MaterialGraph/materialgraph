from app.services.material.real_data_qualification import (
    APPROVED_MANIFEST_SHA256,
    evaluate_collision_event,
    evaluate_curated_preservation,
    evaluate_manifest_contract,
    extract_identity_formula_pairs,
    summarize_formula_crowding,
)


def approved_manifest():
    return {
        "manifest_sha256": APPROVED_MANIFEST_SHA256,
        "source": "materials_project",
        "dataset": {
            "selection_contract_version": "materials-project-selection-v3"
        },
        "counts": {
            "accepted": 1727,
            "source_complete": True,
            "duplicate_source_ids": 0,
        },
    }


def test_approved_manifest_contract_is_exact_and_fail_closed():
    manifest = approved_manifest()

    assert evaluate_manifest_contract(manifest) == []

    manifest["counts"]["accepted"] = 1726
    manifest["counts"]["source_complete"] = False
    assert evaluate_manifest_contract(manifest) == [
        "accepted",
        "source_complete",
    ]


def test_curated_preservation_requires_exact_ids_and_record_digest():
    before = {
        "material_count": 28,
        "material_ids": list(range(1, 29)),
        "records_sha256": "before",
    }
    after = dict(before)

    assert evaluate_curated_preservation(before, after) == []

    after["records_sha256"] = "after"
    assert evaluate_curated_preservation(before, after) == ["records_sha256"]


def test_mp_19017_must_be_an_explained_conflict_for_material_five():
    event = {
        "source_id": "mp-19017",
        "outcome": "conflicted",
        "material_id": 5,
        "reason": "existing material is not owned by this dataset scope",
    }

    assert evaluate_collision_event(event) == []
    assert evaluate_collision_event({**event, "outcome": "unchanged"}) == [
        "mp_19017_outcome"
    ]


def test_formula_crowding_keeps_identities_and_reports_formula_diversity():
    summary = summarize_formula_crowding(
        [
            ("mp-1", "LiFePO4"),
            ("mp-2", "LiFePO4"),
            ("mp-3", "NaFePO4"),
        ]
    )

    assert summary.result_count == 3
    assert summary.unique_identity_count == 3
    assert summary.unique_formula_count == 2
    assert summary.formula_multiplicities == {"LiFePO4": 2}
    assert summary.formula_diversity_fraction == 0.666667


def test_identity_formula_extraction_is_recursive_and_non_destructive():
    document = {
        "items": [
            {"mp_id": "mp-1", "formula": "LiO"},
            {"material_id": 7, "pretty_formula": "NaO"},
            {"metadata": {"count": 2}},
        ]
    }

    assert extract_identity_formula_pairs(document) == [
        ("mp-1", "LiO"),
        ("7", "NaO"),
    ]
