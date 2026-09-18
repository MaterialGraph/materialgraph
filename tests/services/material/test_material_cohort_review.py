import json
from pathlib import Path

from app.services.material.cohort_review import (
    evaluate_review_integrity,
    review_scientific_cohort,
)
from app.services.material.import_pipeline import MaterialImportPipeline
from tests.services.material.test_material_manifest_inspection import (
    candidate,
    write_manifest,
)


def test_review_reports_balance_stability_and_polymorphs(tmp_path: Path):
    path = tmp_path / "manifest.json"
    first = candidate(
        "mp-1", formula="LiFeO2", elements=["Li", "Fe", "O"]
    )
    second = candidate(
        "mp-2",
        formula="LiFeO2",
        elements=["Li", "Fe", "O"],
        stable=False,
    )
    second["energy_above_hull"] = 0.02
    third = candidate(
        "mp-3",
        formula="NaMnO2",
        elements=["Na", "Mn", "O"],
        stable=False,
    )
    third["energy_above_hull"] = 0.04
    write_manifest(path, [first, second, third])

    result = review_scientific_cohort(path, sparse_system_threshold=2)

    assert result.requested_system_count == 2
    assert result.represented_system_count == 2
    assert result.zero_result_systems == ()
    assert result.sparse_systems == {"Na-Mn-O": 1}
    assert result.chemistry_family_counts == {"oxide": 3}
    assert result.stability_counts == {
        "stable_flag": 1,
        "energy_at_zero": 1,
        "energy_above_zero_to_0_025": 1,
        "energy_above_0_025_to_0_05": 1,
    }
    assert result.unique_formulas == 2
    assert result.singleton_formulas == 1
    assert result.polymorph_formulas == 1
    assert result.polymorph_materials == 2
    assert result.maximum_formula_multiplicity == 2
    assert result.formula_multiplicity_counts == {"1": 1, "2": 1}


def test_review_distinguishes_zero_result_systems(tmp_path: Path):
    path = tmp_path / "manifest.json"
    write_manifest(
        path,
        [candidate("mp-1", formula="LiFeO2", elements=["Li", "Fe", "O"])],
    )

    result = review_scientific_cohort(path)

    assert result.represented_system_count == 1
    assert result.zero_result_systems == ("Na-Mn-O",)
    assert result.chemical_system_counts == {"Li-Fe-O": 1, "Na-Mn-O": 0}


def test_review_matches_noncanonical_requested_system_order(tmp_path: Path):
    path = tmp_path / "manifest.json"
    item = candidate(
        "mp-1",
        formula="LiFePO4",
        elements=["Li", "Fe", "P", "O"],
    )
    write_manifest(path, [item])
    document = json.loads(path.read_text(encoding="utf-8"))
    document.pop("manifest_sha256")
    document["scope"]["chemical_systems"] = ["Li-Fe-P-O"]
    redigested = {
        "manifest_sha256": MaterialImportPipeline._payload_digest(document),
        **document,
    }
    path.write_text(json.dumps(redigested), encoding="utf-8")

    result = review_scientific_cohort(path)

    assert result.zero_result_systems == ()
    assert result.chemical_system_counts == {"Li-Fe-P-O": 1}
    assert result.chemistry_family_counts == {"phosphate": 1}


def test_integrity_failures_are_separate_from_scientific_judgment(
    tmp_path: Path,
):
    path = tmp_path / "manifest.json"
    write_manifest(
        path,
        [candidate("mp-1", formula="LiFeO2", elements=["Li", "Fe", "O"])],
    )
    result = review_scientific_cohort(path)

    failures = evaluate_review_integrity(
        result,
        expected_manifest_sha256="wrong",
        expected_source="materials_project",
        expected_selection_contract_version="wrong",
        expected_accepted=2,
    )

    assert failures == [
        "manifest_sha256",
        "selection_contract_version",
        "accepted",
    ]
