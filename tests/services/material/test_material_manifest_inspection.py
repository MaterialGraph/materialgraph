import json
from dataclasses import asdict
from pathlib import Path

import pytest

from app.services.material.import_pipeline import (
    MaterialDatasetContract,
    MaterialImportPipeline,
    MaterialImportScope,
)
from app.services.material.manifest_inspection import (
    evaluate_manifest_gates,
    inspect_material_manifest,
)


def candidate(
    mp_id: str,
    *,
    formula: str,
    elements: list[str],
    band_gap: float | None = 1.0,
    stable: bool = True,
) -> dict:
    fraction = 1 / len(elements)
    return {
        "mp_id": mp_id,
        "formula": formula,
        "pretty_formula": formula,
        "elements": elements,
        "band_gap": band_gap,
        "energy_above_hull": 0.0,
        "formation_energy_per_atom": -1.0,
        "density": 2.0,
        "is_stable": stable,
        "raw_data": {"material_id": mp_id},
        "composition_fractions": {
            element: fraction for element in elements
        },
    }


def write_manifest(path: Path, candidates: list[dict]) -> None:
    scope = asdict(
        MaterialImportScope(
            chemical_systems=("Li-Fe-O", "Na-Mn-O"),
            page_size=100,
            max_materials=3_000,
            max_source_records=4_000,
            stable_only=False,
            maximum_energy_above_hull=0.1,
        )
    )
    dataset = asdict(
        MaterialDatasetContract(
            source_release="test-release",
            retrieved_at="2026-09-17T00:00:00+00:00",
        )
    )
    payload = {
        "schema_version": 2,
        "source": "materials_project",
        "dataset": dataset,
        "scope": scope,
        "counts": {
            "accepted": len(candidates),
            "rejected": 0,
            "duplicate_source_ids": 0,
            "pages_fetched": 2,
            "source_records_seen": len(candidates),
            "source_complete": True,
        },
        "duplicate_source_ids": [],
        "rejections": [],
        "candidates": candidates,
    }
    document = {
        "manifest_sha256": MaterialImportPipeline._payload_digest(payload),
        **payload,
    }
    path.write_text(json.dumps(document), encoding="utf-8")


def test_inspection_reports_scientific_coverage_and_polymorphs(tmp_path):
    path = tmp_path / "manifest.json"
    write_manifest(
        path,
        [
            candidate("mp-1", formula="LiFeO2", elements=["Li", "Fe", "O"]),
            candidate(
                "mp-2",
                formula="LiFeO2",
                elements=["Li", "Fe", "O"],
                band_gap=None,
                stable=False,
            ),
            candidate("mp-3", formula="NaMnO2", elements=["Na", "Mn", "O"]),
        ],
    )

    result = inspect_material_manifest(path)

    assert result.accepted == 3
    assert result.stable == 2
    assert result.unstable == 1
    assert result.unique_formulas == 2
    assert result.polymorph_formulas == 1
    assert result.polymorph_materials == 2
    assert result.element_counts == {
        "Fe": 2,
        "Li": 2,
        "Mn": 1,
        "Na": 1,
        "O": 3,
    }
    assert result.property_coverage["band_gap"].present == 2
    assert result.property_coverage["band_gap"].fraction == 0.666667


def test_gate_evaluation_reports_each_unmet_contract(tmp_path):
    path = tmp_path / "manifest.json"
    write_manifest(
        path,
        [candidate("mp-1", formula="LiO", elements=["Li", "O"], band_gap=None)],
    )
    inspection = inspect_material_manifest(path)

    failures = evaluate_manifest_gates(
        inspection,
        minimum_materials=2,
        maximum_materials=10,
        required_elements=("Li", "Na"),
        minimum_property_coverage=1.0,
        require_source_complete=True,
    )

    assert failures == [
        "accepted_material_count",
        "required_element:Na",
        "property_coverage:band_gap",
    ]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda document: document["scope"].update(
                {"chemical_systems": ["Na-Mn-O", "Li-Fe-O"]}
            ),
            "scope is not normalized",
        ),
        (
            lambda document: document["candidates"][0][
                "composition_fractions"
            ].update({"Li": 0.8}),
            "composition is invalid",
        ),
        (
            lambda document: document["candidates"].append(
                document["candidates"][0].copy()
            ),
            "duplicate accepted source identities",
        ),
        (
            lambda document: document["candidates"][0].update(
                {"energy_above_hull": 0.2}
            ),
            "violates the energy-above-hull scope",
        ),
    ],
)
def test_semantic_validation_rejects_redigested_invalid_manifests(
    tmp_path,
    mutation,
    message,
):
    path = tmp_path / "manifest.json"
    write_manifest(
        path,
        [
            candidate("mp-1", formula="LiO", elements=["Li", "O"]),
            candidate("mp-2", formula="NaO", elements=["Na", "O"]),
        ],
    )
    document = json.loads(path.read_text(encoding="utf-8"))
    document.pop("manifest_sha256")
    mutation(document)
    document["counts"]["accepted"] = len(document["candidates"])
    document["counts"]["source_records_seen"] = len(document["candidates"])
    redigested = {
        "manifest_sha256": MaterialImportPipeline._payload_digest(document),
        **document,
    }
    path.write_text(json.dumps(redigested), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        inspect_material_manifest(path)
