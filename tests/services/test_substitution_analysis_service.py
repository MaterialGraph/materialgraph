from types import SimpleNamespace

from app.schemas.substitution import SubstitutionRequest
from app.services.substitution_analysis_service import SubstitutionAnalysisService


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
        return FakeMaterialQuery(self.source, self.candidates)


class FakeRiskService:
    def __init__(self, signals):
        self.signals = signals

    def get_material_risk_signal(self, material_id):
        return self.signals[material_id]


def _material(material_id: int, formula: str, *, stable: bool = True):
    return SimpleNamespace(
        id=material_id,
        formula=formula,
        pretty_formula=formula,
        is_stable=stable,
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
    }


def _service(source, candidates, signals, elements):
    service = SubstitutionAnalysisService(FakeDB(source, candidates))
    service.material_risk_service = FakeRiskService(signals)
    service._get_element_symbols = lambda material_id: elements[material_id]
    return service


def test_substitution_analysis_returns_candidates(db_session):
    service = SubstitutionAnalysisService(db_session)

    result = service.analyze(SubstitutionRequest(material_id=6, top_n=5))

    assert result is not None
    assert result.source_material_id == 6
    assert len(result.substitutes) <= 5
    assert len(result.substitutes) > 0
    assert result.substitutes[0].similarity_score > 0
    assert result.substitutes[0].rank_score > 0


def test_substitution_analysis_returns_none_for_missing_material(db_session):
    service = SubstitutionAnalysisService(db_session)

    result = service.analyze(
        SubstitutionRequest(material_id=999999, top_n=5)
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
            ),
            2: _risk_signal(
                2,
                risk_score=None,
                risk_known=False,
                coverage=0.0,
                complete=False,
                unknown_elements=["C"],
            ),
        },
        {
            1: {"A", "B"},
            2: {"A", "C"},
        },
    )

    result = service.analyze(SubstitutionRequest(material_id=1, top_n=5))
    substitute = result.substitutes[0]

    # Similarity is 1/3: 0.233 after the 0.7 weighting, plus 0.05 stability.
    # No 0.3 maximum-risk benefit is fabricated from missing evidence.
    assert substitute.rank_score == 0.283
    assert substitute.material_risk_score is None
    assert substitute.risk_known is False
    assert substitute.risk_profile_coverage == 0.0
    assert substitute.risk_evidence_complete is False
    assert substitute.unknown_risk_elements == ["C"]
    assert "risk evidence unavailable" in substitute.explanation.lower()
    assert "not treated as low risk" in substitute.explanation.lower()


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
            ),
            2: _risk_signal(
                2,
                risk_score=8.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
            ),
            3: _risk_signal(
                3,
                risk_score=None,
                risk_known=False,
                coverage=0.0,
                complete=False,
                unknown_elements=["B"],
            ),
        },
        {
            1: {"A", "B"},
            2: {"A", "C"},
            3: {"A", "B"},
        },
    )

    result = service.analyze(SubstitutionRequest(material_id=1, top_n=5))

    assert [item.material_id for item in result.substitutes] == [2, 3]
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
                unknown_elements=["B"],
            ),
            2: _risk_signal(
                2,
                risk_score=3.0,
                risk_known=True,
                coverage=1.0,
                complete=True,
            ),
        },
        {
            1: {"A", "B"},
            2: {"A", "C"},
        },
    )

    result = service.analyze(SubstitutionRequest(material_id=1, top_n=5))

    assert result.source_risk_score is None
    assert result.source_risk_known is False
    assert result.source_risk_profile_coverage == 0.0
    assert result.source_risk_evidence_complete is False
    assert result.source_unknown_risk_elements == ["B"]
    assert "source material-risk evidence is unavailable" in (
        result.substitutes[0].explanation.lower()
    )