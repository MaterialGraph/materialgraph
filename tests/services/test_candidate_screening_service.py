from types import SimpleNamespace

from app.schemas.screening import CandidateScreeningRequest
from app.services.candidate_screening_service import (
    CandidateScreeningService,
)


class FakeMaterialQuery:
    def __init__(self, materials):
        self.materials = materials

    def all(self):
        return self.materials


class FakeDB:
    def __init__(self, materials):
        self.materials = materials

    def query(self, model):
        return FakeMaterialQuery(self.materials)


class FakeRiskService:
    def __init__(self, signals):
        self.signals = signals

    def get_material_risk_signal(self, material_id):
        return self.signals[material_id]

    def get_material_risk_signals_bulk(self, material_ids):
        return {
            material_id: self.signals[material_id]
            for material_id in material_ids
        }


def _material(
    material_id: int,
    *,
    formula: str,
    is_stable: bool = True,
    energy_above_hull: float | None = 0.0,
):
    return SimpleNamespace(
        id=material_id,
        mp_id=f"test-{material_id}",
        formula=formula,
        pretty_formula=formula,
        is_stable=is_stable,
        energy_above_hull=energy_above_hull,
    )


def _risk_signal(
    material_id: int,
    *,
    risk_score: float | None,
    risk_known: bool,
    coverage: float,
    complete: bool,
    unknown_elements: list[str] | None = None,
):
    return {
        "material_id": material_id,
        "risk_score": risk_score,
        "risk_known": risk_known,
        "risk_profile_coverage": coverage,
        "known_risk_element_count": 1 if risk_known else 0,
        "total_element_count": 1,
        "known_risk_elements": ["A"] if risk_known else [],
        "unknown_risk_elements": unknown_elements or [],
        "risk_evidence_complete": complete,
        "selected_profile_ids": [101] if risk_known else [],
        "selected_profile_years": [2026] if risk_known else [],
        "selected_profile_sources": ["screening_test"] if risk_known else [],
    }

def test_known_risk_applies_numeric_penalty():
    material = _material(1, formula="A")

    service = CandidateScreeningService(FakeDB([material]))
    service.material_risk_service = FakeRiskService(
        {
            1: _risk_signal(
                1,
                risk_score=2.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
            )
        }
    )
    service._get_material_element_symbols_bulk = lambda material_ids: {
        1: {"A"}
    }

    result = service.screen_candidates(
        CandidateScreeningRequest(
            require_stable=True,
        )
    )[0]

    assert result.material_risk_score == 2.0
    assert result.risk_penalty == 10.0
    assert result.score_before_risk_penalty == 70.0
    assert result.score == 60.0
    assert result.selected_risk_profile_ids == [101]
    assert result.selected_risk_profile_years == [2026]
    assert result.selected_risk_profile_sources == ["screening_test"]


def test_risk_penalty_recomputation_uses_unclipped_pre_risk_score():
    service = CandidateScreeningService(FakeDB([]))

    score, penalty = service.apply_material_risk_penalty(
        score_before_risk_penalty=10.0,
        material_risk_score=4.0,
    )

    assert score == 0.0
    assert penalty == 20.0

def test_unknown_risk_is_not_reported_as_low_numeric_risk():
    material = _material(1, formula="A")

    service = CandidateScreeningService(FakeDB([material]))
    service.material_risk_service = FakeRiskService(
        {
            1: _risk_signal(
                1,
                risk_score=None,
                risk_known=False,
                coverage=0.0,
                complete=False,
                unknown_elements=["A"],
            )
        }
    )
    service._get_material_element_symbols_bulk = lambda material_ids: {
        1: {"A"}
    }

    result = service.screen_candidates(
        CandidateScreeningRequest(
            require_stable=True,
        )
    )[0]

    assert result.material_risk_score is None
    assert result.risk_known is False
    assert result.risk_penalty == 0.0
    assert result.risk_profile_coverage == 0.0
    assert result.risk_evidence_complete is False
    assert result.unknown_risk_elements == ["A"]

    assert any(
        "risk evidence unavailable" in reason.lower()
        for reason in result.reasons
    )

    assert not any(
        "risk score 0" in reason.lower()
        for reason in result.reasons
    )

def test_unknown_risk_does_not_gain_a_false_low_risk_explanation():
    known_material = _material(1, formula="A")
    unknown_material = _material(2, formula="B")

    service = CandidateScreeningService(
        FakeDB([known_material, unknown_material])
    )
    service.material_risk_service = FakeRiskService(
        {
            1: _risk_signal(
                1,
                risk_score=2.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
            ),
            2: _risk_signal(
                2,
                risk_score=None,
                risk_known=False,
                coverage=0.0,
                complete=False,
                unknown_elements=["B"],
            ),
        }
    )
    service._get_material_element_symbols_bulk = lambda material_ids: {
        1: {"A"},
        2: {"B"},
    }

    results = service.screen_candidates(
        CandidateScreeningRequest(
            require_stable=True,
        )
    )

    assert [result.material_id for result in results] == [1, 2]

    by_id = {
        result.material_id: result
        for result in results
    }

    assert by_id[1].risk_known is True
    assert by_id[1].risk_penalty == 10.0
    
    assert by_id[2].risk_known is False
    assert by_id[2].risk_penalty == 0.0
    assert by_id[2].material_risk_score is None


def test_screening_uses_material_id_for_deterministic_final_order():
    material_a = _material(2, formula="A")
    material_b = _material(1, formula="B")

    service = CandidateScreeningService(
        FakeDB([material_a, material_b])
    )
    service.material_risk_service = FakeRiskService(
        {
            1: _risk_signal(
                1,
                risk_score=2.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
            ),
            2: _risk_signal(
                2,
                risk_score=2.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
            ),
        }
    )
    service._get_material_element_symbols_bulk = lambda material_ids: {
        1: {"B"},
        2: {"A"},
    }

    results = service.screen_candidates(
        CandidateScreeningRequest(require_stable=True)
    )

    assert [result.material_id for result in results] == [1, 2]


def test_screening_bulk_loads_elements_and_risk_once():
    materials = [
        _material(1, formula="A"),
        _material(2, formula="B"),
    ]
    service = CandidateScreeningService(FakeDB(materials))

    element_calls = []
    risk_calls = []

    service._get_material_element_symbols_bulk = lambda material_ids: (
        element_calls.append(list(material_ids)) or {1: {"A"}, 2: {"B"}}
    )
    service.material_risk_service.get_material_risk_signals_bulk = (
        lambda material_ids: risk_calls.append(list(material_ids))
        or {
            material_id: _risk_signal(
                material_id,
                risk_score=1.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
            )
            for material_id in material_ids
        }
    )

    service.screen_candidates(CandidateScreeningRequest(require_stable=True))

    assert element_calls == [[1, 2]]
    assert risk_calls == [[1, 2]]