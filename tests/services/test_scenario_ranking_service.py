from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.scenario_ranking import ScenarioRankingRequest
from app.services.candidate_screening_service import CandidateScreeningService
from app.services.scenario_ranking_service import ScenarioRankingService


def test_scenario_ranking_request_uses_bounded_default():
    request = ScenarioRankingRequest(
        scenario_name="lithium_supply_shock",
    )

    assert request.top_n == 10


@pytest.mark.parametrize("top_n", [1, 20])
def test_scenario_ranking_request_accepts_result_limit_boundaries(top_n):
    request = ScenarioRankingRequest(
        scenario_name="lithium_supply_shock",
        top_n=top_n,
    )

    assert request.top_n == top_n


@pytest.mark.parametrize("top_n", [-1, 0, 21])
def test_scenario_ranking_request_rejects_invalid_result_limits(top_n):
    with pytest.raises(ValidationError):
        ScenarioRankingRequest(
            scenario_name="lithium_supply_shock",
            top_n=top_n,
        )


def test_lithium_supply_shock_ranking_returns_top_candidates(db_session):
    screening_service = CandidateScreeningService(db_session)
    service = ScenarioRankingService(screening_service)

    result = service.rank_for_scenario(
        ScenarioRankingRequest(
            scenario_name="lithium_supply_shock",
            top_n=5,
        )
    )

    assert len(result) <= 5
    assert len(result) > 0
    assert result[0].rank == 1
    assert result[0].scenario_name == "lithium_supply_shock"
    assert result[0].score >= 0


def test_unknown_scenario_raises_error(db_session):
    screening_service = CandidateScreeningService(db_session)
    service = ScenarioRankingService(screening_service)

    with pytest.raises(ValueError):
        service.rank_for_scenario(
            ScenarioRankingRequest(
                scenario_name="unknown_scenario",
                top_n=5,
            )
        )


def test_unknown_risk_is_preserved_and_explained():
    screening_result = SimpleNamespace(
        material_id=101,
        mp_id="mp-unknown-risk",
        formula="NaFePO4",
        pretty_formula="NaFePO4",
        score=70.0,
        material_risk_score=None,
        risk_penalty=0.0,
        risk_known=False,
        elements=["Fe", "Na", "O", "P"],
        reasons=[
            "Material risk evidence unavailable; risk penalty not applied"
        ],
    )
    screening_service = SimpleNamespace(
        screen_candidates=lambda request: [screening_result]
    )
    service = ScenarioRankingService(screening_service)

    result = service.rank_for_scenario(
        ScenarioRankingRequest(
            scenario_name="lithium_supply_shock",
            top_n=1,
        )
    )[0]

    assert result.material_risk_score is None
    assert result.risk_penalty == 0.0
    assert any(
        "risk is unknown" in explanation.lower()
        for explanation in result.ranking_explanation
    )
    assert not any(
        risk_label in explanation.lower()
        for explanation in result.ranking_explanation
        for risk_label in (
            "low aggregate material risk",
            "moderate aggregate material risk",
            "high aggregate material risk",
        )
    )