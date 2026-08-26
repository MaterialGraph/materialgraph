from types import SimpleNamespace

from app.schemas.substitution import SubstitutionRequest
from app.services.substitution_analysis_service import (
    SubstitutionAnalysisService,
)


class FakeMaterialQuery:
    def __init__(self, source, candidates):
        self.source = source
        self.candidates = candidates

    def filter(self, *args):
        return self

    def first(self):
        return self.source

    def all(self):
        return self.candidates


class FakeDB:
    def __init__(self, source, candidates):
        self.source = source
        self.candidates = candidates

    def query(self, model):
        return FakeMaterialQuery(
            self.source,
            self.candidates,
        )


class FakeRiskService:
    def __init__(self, signals):
        self.signals = signals
        self.bulk_calls = []

    def get_material_risk_signals_bulk(self, material_ids):
        self.bulk_calls.append(material_ids)

        return {
            material_id: self.signals[material_id]
            for material_id in material_ids
        }

    def get_material_risk_signal(self, material_id):
        raise AssertionError(
            "Substitution must not perform single-material risk calls"
        )


def _material(
    material_id: int,
    formula: str,
    *,
    stable: bool = True,
    energy_above_hull: float | None = None,
):
    return SimpleNamespace(
        id=material_id,
        formula=formula,
        pretty_formula=formula,
        is_stable=stable,
        energy_above_hull=energy_above_hull,
    )


def _risk_signal(
    material_id: int,
    *,
    risk_score: float | None,
    risk_known: bool,
    coverage: float,
    complete: bool,
    known_elements: list[str] | None = None,
    unknown_elements: list[str] | None = None,
):
    known_elements = known_elements or []
    unknown_elements = unknown_elements or []

    return {
        "material_id": material_id,
        "risk_score": risk_score,
        "risk_known": risk_known,
        "risk_profile_coverage": coverage,
        "known_risk_element_count": len(known_elements),
        "total_element_count": (
            len(known_elements) + len(unknown_elements)
        ),
        "known_risk_elements": known_elements,
        "unknown_risk_elements": unknown_elements,
        "risk_evidence_complete": complete,
    }


def _service(
    source,
    candidates,
    signals,
):
    service = SubstitutionAnalysisService(
        FakeDB(source, candidates)
    )
    service.material_risk_service = FakeRiskService(signals)

    return service


def test_substitution_analysis_returns_candidates(db_session):
    service = SubstitutionAnalysisService(db_session)

    result = service.analyze(
        SubstitutionRequest(material_id=6, top_n=5)
    )

    assert result is not None
    assert result.source_material_id == 6
    assert len(result.substitutes) <= 5
    assert len(result.substitutes) > 0
    assert result.substitutes[0].similarity_score > 0
    assert result.substitutes[0].rank_score > 0


def test_substitution_analysis_returns_none_for_missing_material(
    db_session,
):
    service = SubstitutionAnalysisService(db_session)

    result = service.analyze(
        SubstitutionRequest(
            material_id=999999,
            top_n=5,
        )
    )

    assert result is None


def test_unknown_risk_is_nullable_and_receives_no_low_risk_component():
    source = _material(1, "AB")
    candidate = _material(2, "AC")

    service = _service(
        source,
        [candidate],
        {
            1: _risk_signal(
                1,
                risk_score=4.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
                known_elements=["A", "B"],
            ),
            2: _risk_signal(
                2,
                risk_score=None,
                risk_known=False,
                coverage=0.0,
                complete=False,
                unknown_elements=["A", "C"],
            ),
        },
    )

    result = service.analyze(
        SubstitutionRequest(material_id=1, top_n=5)
    )

    assert result is not None

    substitute = result.substitutes[0]

    # Similarity is 1/3: 0.233 after the 0.7 weighting,
    # plus 0.025 from incomplete stable-flag fallback evidence.
    # Unknown risk contributes no fabricated low-risk benefit.
    assert substitute.rank_score == 0.258
    assert substitute.stability_rank_contribution == 0.025
    assert substitute.stability_evidence_basis == (
        "imported_is_stable_fallback"
    )
    assert substitute.stability_evidence_complete is False

    assert substitute.material_risk_score is None
    assert substitute.risk_known is False
    assert substitute.risk_profile_coverage == 0.0
    assert substitute.risk_evidence_complete is False
    assert substitute.unknown_risk_elements == ["A", "C"]

    explanation = substitute.explanation.lower()

    assert "risk evidence unavailable" in explanation
    assert "not treated as low risk" in explanation


def test_known_risk_candidate_precedes_otherwise_better_unknown_candidate():
    source = _material(1, "AB")
    known = _material(2, "AC")
    unknown = _material(3, "AB")

    service = _service(
        source,
        [unknown, known],
        {
            1: _risk_signal(
                1,
                risk_score=4.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
                known_elements=["A", "B"],
            ),
            2: _risk_signal(
                2,
                risk_score=8.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
                known_elements=["A", "C"],
            ),
            3: _risk_signal(
                3,
                risk_score=None,
                risk_known=False,
                coverage=0.0,
                complete=False,
                unknown_elements=["A", "B"],
            ),
        },
    )

    result = service.analyze(
        SubstitutionRequest(material_id=1, top_n=5)
    )

    assert result is not None
    assert [
        item.material_id
        for item in result.substitutes
    ] == [2, 3]

    assert result.substitutes[0].risk_known is True
    assert result.substitutes[1].risk_known is False
    assert (
        result.substitutes[1].rank_score
        > result.substitutes[0].rank_score
    )


def test_unknown_source_risk_remains_nullable_in_result_and_explanation():
    source = _material(1, "AB")
    candidate = _material(2, "AC")

    service = _service(
        source,
        [candidate],
        {
            1: _risk_signal(
                1,
                risk_score=None,
                risk_known=False,
                coverage=0.0,
                complete=False,
                unknown_elements=["A", "B"],
            ),
            2: _risk_signal(
                2,
                risk_score=3.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
                known_elements=["A", "C"],
            ),
        },
    )

    result = service.analyze(
        SubstitutionRequest(material_id=1, top_n=5)
    )

    assert result is not None
    assert result.source_risk_score is None
    assert result.source_risk_known is False
    assert result.source_risk_profile_coverage == 0.0
    assert result.source_risk_evidence_complete is False
    assert result.source_unknown_risk_elements == ["A", "B"]

    explanation = result.substitutes[0].explanation.lower()

    assert (
        "source material-risk evidence is unavailable"
        in explanation
    )


def test_substitution_uses_energy_primary_stability_evidence():
    source = _material(1, "AB")
    candidate = _material(
        2,
        "AC",
        stable=True,
        energy_above_hull=0.2,
    )
    signals = {
        1: _risk_signal(
            1,
            risk_score=4.0,
            risk_known=True,
            coverage=1.0,
            complete=True,
            known_elements=["A", "B"],
        ),
        2: _risk_signal(
            2,
            risk_score=4.0,
            risk_known=True,
            coverage=1.0,
            complete=True,
            known_elements=["A", "C"],
        ),
    }

    result = _service(source, [candidate], signals).analyze(
        SubstitutionRequest(material_id=1, top_n=5)
    )

    assert result is not None
    substitute = result.substitutes[0]
    assert substitute.stability_band == "unstable"
    assert substitute.stability_evidence_basis == "energy_above_hull"
    assert substitute.stability_evidence_complete is True
    assert substitute.stability_source_consistency == "inconsistent"
    assert substitute.stability_rank_contribution == 0.0
    assert "energy above hull 0.2" in substitute.explanation.lower()
    assert "sources are inconsistent" in substitute.explanation.lower()
    assert "stable candidate" not in substitute.explanation.lower()


def test_substitution_scales_canonical_fallback_contribution():
    source = _material(1, "AB")
    candidate = _material(2, "AC", stable=True)
    signals = {
        1: _risk_signal(
            1,
            risk_score=4.0,
            risk_known=True,
            coverage=1.0,
            complete=True,
            known_elements=["A", "B"],
        ),
        2: _risk_signal(
            2,
            risk_score=4.0,
            risk_known=True,
            coverage=1.0,
            complete=True,
            known_elements=["A", "C"],
        ),
    }

    result = _service(source, [candidate], signals).analyze(
        SubstitutionRequest(material_id=1, top_n=5)
    )

    assert result is not None
    substitute = result.substitutes[0]
    assert substitute.stability_evidence_basis == (
        "imported_is_stable_fallback"
    )
    assert substitute.stability_evidence_complete is False
    assert substitute.stability_rank_contribution == 0.025
    assert "incomplete fallback evidence" in substitute.explanation.lower()


def test_substitution_bulk_loads_elements_and_risk_once():
    source = _material(1, "AB")
    candidate_2 = _material(2, "AC")
    candidate_3 = _material(3, "AD")

    service = _service(
        source,
        [candidate_2, candidate_3],
        {
            1: _risk_signal(
                1,
                risk_score=4.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
                known_elements=["A", "B"],
            ),
            2: _risk_signal(
                2,
                risk_score=3.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
                known_elements=["A", "C"],
            ),
            3: _risk_signal(
                3,
                risk_score=5.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
                known_elements=["A", "D"],
            ),
        },
    )

    result = service.analyze(
        SubstitutionRequest(material_id=1, top_n=5)
    )

    assert result is not None
    assert service.material_risk_service.bulk_calls == [
        [1, 2, 3]
    ]
    assert {
        substitute.material_id
        for substitute in result.substitutes
    } == {2, 3}