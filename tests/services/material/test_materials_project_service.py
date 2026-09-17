import pytest

from app.services.material import project_service
from app.services.material.project_service import MaterialsProjectService


class FakeComposition:
    reduced_formula = "LiFePO4"

    def get_el_amt_dict(self) -> dict[str, float]:
        return {
            "Li": 1.0,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        }


class FakeDocument:
    material_id = "mp-19017"
    formula_pretty = "LiFePO4"
    composition = FakeComposition()
    elements = ["Li", "Fe", "P", "O"]
    band_gap = 1.2
    energy_above_hull = 0.0
    formation_energy_per_atom = -2.5
    density = 3.6
    is_stable = True

    def model_dump(self, mode: str) -> dict:
        assert mode == "json"

        return {
            "material_id": "mp-19017",
            "formula_pretty": "LiFePO4",
            "composition": {
                "Li": 1.0,
                "Fe": 1.0,
                "P": 1.0,
                "O": 4.0,
            },
        }


def make_service() -> MaterialsProjectService:
    # Avoid requiring a real MP API key or network request.
    return MaterialsProjectService(api_key="test-api-key")


def test_normalize_doc_preserves_normalized_composition():
    service = make_service()

    candidate = service._normalize_doc(FakeDocument())

    assert candidate.mp_id == "mp-19017"
    assert candidate.formula == "LiFePO4"

    assert candidate.composition_fractions == pytest.approx(
        {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }
    )

    assert sum(candidate.composition_fractions.values()) == pytest.approx(1.0)


def test_fetch_page_uses_deterministic_source_paging(monkeypatch):
    captured = {}

    class FakeSummary:
        def search(self, **kwargs):
            captured.update(kwargs)
            return [FakeDocument()]

    class FakeMPRester:
        def __init__(self, api_key):
            assert api_key == "test-api-key"
            self.materials = type("Materials", (), {"summary": FakeSummary()})()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(project_service, "MPRester", FakeMPRester)

    result = make_service().fetch_materials_page(
        chemsys="Li-Fe-P-O",
        page=3,
        page_size=50,
        stable_only=True,
    )

    assert len(result.candidates) == 1
    assert result.rejections == []
    assert captured["num_chunks"] == 1
    assert captured["chunk_size"] == 50
    assert captured["_page"] == 3
    assert captured["_sort_fields"] == "material_id"
    assert captured["is_stable"] is True
    assert captured["energy_above_hull"] is None
    assert captured["deprecated"] is False
    assert captured["include_gnome"] is False


def test_fetch_page_applies_explicit_near_stable_bound(monkeypatch):
    captured = {}

    class FakeSummary:
        def search(self, **kwargs):
            captured.update(kwargs)
            return []

    class FakeMPRester:
        def __init__(self, _api_key):
            self.materials = type("Materials", (), {"summary": FakeSummary()})()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(project_service, "MPRester", FakeMPRester)

    make_service().fetch_materials_page(
        chemsys="Li-Fe-O",
        page=1,
        page_size=50,
        stable_only=False,
        maximum_energy_above_hull=0.1,
    )

    assert captured["is_stable"] is None
    assert captured["energy_above_hull"] == (0, 0.1)


def test_fetch_page_verifies_the_declared_database_release(monkeypatch):
    class FakeSummary:
        def search(self, **_kwargs):
            return []

    class FakeMPRester:
        def __init__(self, api_key):
            assert api_key == "test-api-key"
            self.materials = type("Materials", (), {"summary": FakeSummary()})()

        @staticmethod
        def get_database_version():
            return "2026.09.01"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(project_service, "MPRester", FakeMPRester)
    service = MaterialsProjectService(
        api_key="test-api-key",
        database_version="2026.09.01",
    )

    service.fetch_materials_page(
        chemsys="Li-O",
        page=1,
        page_size=10,
        stable_only=True,
    )


def test_get_database_version_returns_authoritative_release(monkeypatch):
    class FakeMPRester:
        def __init__(self, api_key):
            assert api_key == "test-api-key"

        @staticmethod
        def get_database_version():
            return "2026.09.01"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(project_service, "MPRester", FakeMPRester)

    assert make_service().get_database_version() == "2026.09.01"


def test_get_database_version_rejects_invalid_response(monkeypatch):
    class FakeMPRester:
        def __init__(self, _api_key):
            pass

        @staticmethod
        def get_database_version():
            return None

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(project_service, "MPRester", FakeMPRester)

    with pytest.raises(ValueError, match="invalid database version"):
        make_service().get_database_version()


def test_fetch_page_rejects_a_database_release_mismatch(monkeypatch):
    class FakeMPRester:
        def __init__(self, _api_key):
            self.materials = type("Materials", (), {})()

        @staticmethod
        def get_database_version():
            return "2026.09.02"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(project_service, "MPRester", FakeMPRester)
    service = MaterialsProjectService(
        api_key="test-api-key",
        database_version="2026.09.01",
    )

    with pytest.raises(ValueError, match="does not match"):
        service.fetch_materials_page(
            chemsys="Li-O",
            page=1,
            page_size=10,
            stable_only=True,
        )


def test_fetch_page_records_sanitized_normalization_rejection(monkeypatch):
    invalid = type("InvalidDocument", (), {"material_id": "mp-invalid"})()

    class FakeSummary:
        def search(self, **_kwargs):
            return [invalid]

    class FakeMPRester:
        def __init__(self, _api_key):
            self.materials = type("Materials", (), {"summary": FakeSummary()})()

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    monkeypatch.setattr(project_service, "MPRester", FakeMPRester)

    result = make_service().fetch_materials_page(
        chemsys="Li-O",
        page=1,
        page_size=10,
        stable_only=True,
    )

    assert result.candidates == []
    assert len(result.rejections) == 1
    assert result.rejections[0].source_id == "mp-invalid"
    assert result.rejections[0].reason == "normalization_error"
