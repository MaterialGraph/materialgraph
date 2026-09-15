from dataclasses import replace
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.models.element import Element
from app.models.dataset_import import (
    DatasetImportRun,
    MaterialImportEvent,
    MaterialSourceMembership,
    MaterialSourceRecord,
)
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.import_service import (
    DatasetImportRunSpec,
    MaterialImportService,
)
from app.services.material.project_service import MaterialCandidate


def make_candidate(
    mp_id: str | None = None,
    formula: str = "LiFePO4",
    pretty_formula: str = "LiFePO4",
    elements: list[str] | None = None,
    composition_fractions: dict[str, float] | None = None,
) -> MaterialCandidate:
    generated_mp_id = mp_id or f"mp-test-{uuid4()}"
    candidate_elements = elements or ["Li", "Fe", "P", "O"]

    if composition_fractions is None:
        composition_fractions = {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }

    return MaterialCandidate(
        mp_id=generated_mp_id,
        formula=formula,
        pretty_formula=pretty_formula,
        elements=candidate_elements,
        band_gap=1.2,
        energy_above_hull=0.0,
        formation_energy_per_atom=-2.5,
        density=3.6,
        is_stable=True,
        raw_data={
            "material_id": generated_mp_id,
            "formula_pretty": pretty_formula,
            "composition": {
                symbol: fraction
                for symbol, fraction in composition_fractions.items()
            },
        },
        composition_fractions=composition_fractions,
    )


def make_run_spec(
    *,
    run_id: str,
    release: str,
    scope_digest: str = "a" * 64,
) -> DatasetImportRunSpec:
    return DatasetImportRunSpec(
        import_run_id=run_id,
        source="materials_project",
        source_release=release,
        retrieved_at=datetime(2026, 9, 15, tzinfo=timezone.utc),
        manifest_sha256="b" * 64,
        normalization_version="materials-project-summary-v1",
        selection_contract_version="materials-project-selection-v1",
        selection_scope_sha256=scope_digest,
        license_identifier="CC-BY-4.0",
        license_url="https://creativecommons.org/licenses/by/4.0/",
    )


def test_provenance_refresh_records_all_outcomes(db_session):
    service = MaterialImportService(db_session)
    prefix = f"mp-rf-{uuid4().hex[:12]}"
    first_candidates = [
        make_candidate(mp_id=f"{prefix}-{suffix}")
        for suffix in ("a", "b", "c")
    ]
    first_run_id = str(uuid4())
    service.begin_import_run(
        spec=make_run_spec(run_id=first_run_id, release="release-1"),
        rejections=[{"source_id": f"{prefix}-bad", "reason": "normalization_error"}],
    )

    first_result = service.refresh_materials(
        first_candidates,
        import_run_id=first_run_id,
    )
    replayed_first_result = service.refresh_materials(
        first_candidates,
        import_run_id=first_run_id,
    )
    first_completion = service.complete_import_run(
        import_run_id=first_run_id,
        manifest_source_ids={item.mp_id for item in first_candidates},
        outcome_counts={
            "inserted": 3,
            "updated": 0,
            "unchanged": 0,
            "conflicted": 0,
            "rejected": 1,
        },
        allow_retirement=True,
    )

    assert first_result.inserted == 3
    assert replayed_first_result == first_result
    assert first_completion.retired == 0

    legacy = make_candidate(mp_id=f"{prefix}-legacy")
    db_session.add(
        Material(
            mp_id=legacy.mp_id,
            formula=legacy.formula,
            pretty_formula=legacy.pretty_formula,
            band_gap=legacy.band_gap,
            energy_above_hull=legacy.energy_above_hull,
            formation_energy_per_atom=legacy.formation_energy_per_atom,
            density=legacy.density,
            is_stable=legacy.is_stable,
            source="legacy_unknown",
            raw_data=legacy.raw_data,
        )
    )
    db_session.commit()

    updated = replace(
        first_candidates[1],
        band_gap=None,
        raw_data={"material_id": first_candidates[1].mp_id, "band_gap": None},
    )
    inserted = make_candidate(mp_id=f"{prefix}-d")
    second_candidates = [first_candidates[0], updated, inserted, legacy]
    second_run_id = str(uuid4())
    service.begin_import_run(
        spec=make_run_spec(run_id=second_run_id, release="release-2"),
        rejections=[],
    )
    second_result = service.refresh_materials(
        second_candidates,
        import_run_id=second_run_id,
    )
    second_completion = service.complete_import_run(
        import_run_id=second_run_id,
        manifest_source_ids={item.mp_id for item in second_candidates},
        outcome_counts={
            "inserted": second_result.inserted,
            "updated": second_result.updated,
            "unchanged": second_result.unchanged,
            "conflicted": second_result.conflicted,
            "rejected": 0,
        },
        allow_retirement=True,
    )

    assert second_result.inserted == 1
    assert second_result.updated == 1
    assert second_result.unchanged == 1
    assert second_result.conflicted == 1
    assert second_completion.retired == 1

    outcomes = {
        outcome: count
        for outcome, count in db_session.query(
            MaterialImportEvent.outcome,
            func.count(MaterialImportEvent.id),
        )
        .filter(
            MaterialImportEvent.import_run_id.in_([first_run_id, second_run_id])
        )
        .group_by(MaterialImportEvent.outcome)
        .all()
    }
    assert outcomes == {
        "conflicted": 1,
        "inserted": 4,
        "rejected": 1,
        "retired": 1,
        "unchanged": 1,
        "updated": 1,
    }

    changed_material = (
        db_session.query(Material)
        .filter(Material.mp_id == updated.mp_id)
        .one()
    )
    assert changed_material.band_gap is None
    retired_record = (
        db_session.query(MaterialSourceRecord)
        .filter(MaterialSourceRecord.source_id == first_candidates[2].mp_id)
        .one()
    )
    assert retired_record.active is False
    second_run = db_session.get(DatasetImportRun, second_run_id)
    assert second_run.status == "completed_with_conflicts"
    assert second_run.outcome_counts["retired"] == 1


def test_retirement_preserves_membership_in_an_overlapping_scope(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate(mp_id=f"mp-scope-{uuid4().hex[:12]}")
    scope_a = "a" * 64
    scope_b = "c" * 64

    for scope_digest in (scope_a, scope_b):
        run_id = str(uuid4())
        service.begin_import_run(
            spec=make_run_spec(
                run_id=run_id,
                release="release-1",
                scope_digest=scope_digest,
            ),
            rejections=[],
        )
        result = service.refresh_materials([candidate], import_run_id=run_id)
        service.complete_import_run(
            import_run_id=run_id,
            manifest_source_ids={candidate.mp_id},
            outcome_counts={
                "inserted": result.inserted,
                "updated": result.updated,
                "unchanged": result.unchanged,
                "conflicted": result.conflicted,
                "rejected": 0,
            },
            allow_retirement=True,
        )

    retirement_run_id = str(uuid4())
    service.begin_import_run(
        spec=make_run_spec(
            run_id=retirement_run_id,
            release="release-2",
            scope_digest=scope_a,
        ),
        rejections=[],
    )
    completion = service.complete_import_run(
        import_run_id=retirement_run_id,
        manifest_source_ids=set(),
        outcome_counts={
            "inserted": 0,
            "updated": 0,
            "unchanged": 0,
            "conflicted": 0,
            "rejected": 0,
        },
        allow_retirement=True,
    )

    record = (
        db_session.query(MaterialSourceRecord)
        .filter(MaterialSourceRecord.source_id == candidate.mp_id)
        .one()
    )
    memberships = (
        db_session.query(MaterialSourceMembership)
        .filter(MaterialSourceMembership.source_record_id == record.id)
        .all()
    )
    assert completion.retired == 1
    assert record.active is True
    assert sorted(membership.active for membership in memberships) == [False, True]


def test_import_materials_creates_material(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    imported_count = service.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .first()
    )

    assert imported_count == 1
    assert material is not None
    assert material.pretty_formula == "LiFePO4"
    assert material.source == "materials_project"
    assert material.is_stable is True
    assert material.raw_data["material_id"] == candidate.mp_id


def test_import_materials_skips_duplicate_mp_id(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    first_count = service.import_materials([candidate])
    second_count = service.import_materials([candidate])

    material_count = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .count()
    )

    assert first_count == 1
    assert second_count == 0
    assert material_count == 1


def test_import_materials_reports_reconciled_counts(db_session):
    service = MaterialImportService(db_session)
    existing = make_candidate()
    new = make_candidate()
    service.import_materials([existing])

    result = service.import_materials_with_result([existing, new, new])

    assert result.processed == 3
    assert result.imported == 1
    assert result.skipped == 2


def test_import_materials_creates_elements(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    service.import_materials([candidate])

    symbols = {
        element.symbol
        for element in db_session.query(Element).all()
    }

    assert {"Li", "Fe", "P", "O"}.issubset(symbols)


def test_import_materials_creates_material_element_links(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate()

    service.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )

    links = (
        db_session.query(MaterialElement)
        .filter(MaterialElement.material_id == material.id)
        .all()
    )

    elements_by_id = {
        element.id: element.symbol
        for element in db_session.query(Element).all()
    }

    fractions_by_symbol = {
        elements_by_id[link.element_id]: link.fraction
        for link in links
    }

    assert len(links) == 4

    assert fractions_by_symbol == pytest.approx(
        {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }
    )

    assert sum(fractions_by_symbol.values()) == pytest.approx(1.0)


def test_import_materials_persists_normalized_membership_once(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate(
        formula="LiO",
        pretty_formula="LiO",
        elements=[" Li ", "Li", " O "],
        composition_fractions={
            " Li ": 1.0,
            " O ": 1.0,
        },
    )

    imported_count = service.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )
    links = (
        db_session.query(MaterialElement, Element)
        .join(Element, MaterialElement.element_id == Element.id)
        .filter(MaterialElement.material_id == material.id)
        .order_by(Element.symbol)
        .all()
    )

    assert imported_count == 1
    assert [element.symbol for _, element in links] == ["Li", "O"]
    assert [link.fraction for link, _ in links] == pytest.approx([0.5, 0.5])


def test_import_materials_deduplicates_legacy_membership(db_session):
    service = MaterialImportService(db_session)
    candidate = make_candidate(
        formula="LiO",
        pretty_formula="LiO",
        elements=["Li", "Li", "O"],
        composition_fractions={},
    )

    imported_count = service.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )
    links = (
        db_session.query(MaterialElement)
        .filter(MaterialElement.material_id == material.id)
        .all()
    )

    assert imported_count == 1
    assert len(links) == 2
    assert all(link.fraction == 1.0 for link in links)


def test_import_materials_preserves_legacy_fraction_fallback(db_session):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={},
    )

    service.import_materials([candidate])

    material = (
        db_session.query(Material)
        .filter(Material.mp_id == candidate.mp_id)
        .one()
    )

    links = (
        db_session.query(MaterialElement)
        .filter(MaterialElement.material_id == material.id)
        .all()
    )

    assert len(links) == 4
    assert all(link.fraction == 1.0 for link in links)


def test_import_materials_rejects_missing_composition_element(db_session):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={
            "Li": 0.2,
            "Fe": 0.2,
            "P": 0.2,
        }
    )

    with pytest.raises(
        ValueError,
        match="element membership does not match",
    ):
        service.import_materials([candidate])


def test_import_materials_rejects_unexpected_composition_element(db_session):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={
            "Li": 0.1,
            "Fe": 0.1,
            "P": 0.1,
            "O": 0.6,
            "Na": 0.1,
        }
    )

    with pytest.raises(
        ValueError,
        match="element membership does not match",
    ):
        service.import_materials([candidate])


@pytest.mark.parametrize(
    "invalid_fraction",
    [
        0.0,
        -0.1,
        float("nan"),
        float("inf"),
    ],
)
def test_import_materials_rejects_invalid_fraction(
    db_session,
    invalid_fraction: float,
):
    service = MaterialImportService(db_session)

    candidate = make_candidate(
        composition_fractions={
            "Li": invalid_fraction,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        }
    )

    with pytest.raises(
        ValueError,
        match="invalid composition fraction",
    ):
        service.import_materials([candidate])


def test_failed_batch_rolls_back_earlier_candidate_and_reuses_session(
    db_session,
):
    service = MaterialImportService(db_session)
    valid_candidate = make_candidate()
    invalid_candidate = make_candidate(
        composition_fractions={
            "Li": 0.1,
            "Fe": 0.1,
            "P": 0.1,
            "O": 0.6,
            "Na": 0.1,
        }
    )

    with pytest.raises(
        ValueError,
        match="element membership does not match",
    ):
        service.import_materials([valid_candidate, invalid_candidate])

    rolled_back_material = (
        db_session.query(Material)
        .filter(Material.mp_id == valid_candidate.mp_id)
        .first()
    )
    recovery_candidate = make_candidate()

    assert rolled_back_material is None
    assert service.import_materials([recovery_candidate]) == 1


def test_database_failure_rolls_back_and_reuses_session(
    db_session,
    monkeypatch,
):
    service = MaterialImportService(db_session)
    existing_candidate = make_candidate()
    service.import_materials([existing_candidate])

    monkeypatch.setattr(service, "_find_existing_mp_ids", lambda _mp_ids: set())

    with pytest.raises(IntegrityError):
        service.import_materials([existing_candidate])

    recovery_candidate = make_candidate()

    assert service.import_materials([recovery_candidate]) == 1
    assert (
        db_session.query(Material)
        .filter(Material.mp_id == existing_candidate.mp_id)
        .count()
        == 1
    )
