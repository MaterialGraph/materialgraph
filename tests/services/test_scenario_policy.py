import pytest

from app.services.scenario_policy import (
    ScenarioPolicy,
    ScenarioPolicyEvaluator,
)


@pytest.fixture
def evaluator():
    return ScenarioPolicyEvaluator()


def test_supply_risk_increase_penalizes_candidate_containing_named_element(
    evaluator,
):
    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="LiFePO4",
        policy=ScenarioPolicy(
            element="Li",
            supply_risk_multiplier=1.5,
        ),
    )

    assert result.scenario_score == 90.0
    assert result.scenario_delta == -10.0
    assert (
        "supply risk multiplier 1.5 for element Li, penalty 10.0"
        in result.scenario_reason
    )
    assert "final scenario penalty 10.0" in result.scenario_reason


def test_supply_risk_change_does_not_adjust_unexposed_candidate(evaluator):
    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="NaFePO4",
        policy=ScenarioPolicy(
            element="Li",
            supply_risk_multiplier=1.5,
        ),
    )

    assert result.scenario_score == 100.0
    assert result.scenario_delta == 0.0
    assert result.scenario_reason == "no final scenario adjustment"


def test_supply_risk_adjustment_combines_with_avoid_and_prefer_rules(evaluator):
    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="LiNaFePO4",
        policy=ScenarioPolicy(
            element="Li",
            supply_risk_multiplier=1.5,
            avoid_elements=["Li"],
            prefer_elements=["Na"],
        ),
    )

    assert result.scenario_score == 80.0
    assert result.scenario_delta == -20.0
    assert "element Li, penalty 10.0" in result.scenario_reason
    assert "contains avoided element Li, penalty 20.0" in result.scenario_reason
    assert "contains preferred element Na, bonus 10.0" in result.scenario_reason
    assert "final scenario penalty 20.0" in result.scenario_reason


def test_preferred_element_produces_positive_delta_and_bonus_reason(evaluator):
    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="NaFePO4",
        policy=ScenarioPolicy(
            element="Li",
            prefer_elements=["Na"],
        ),
    )

    assert result.scenario_score == 110.0
    assert result.scenario_delta == 10.0
    assert "contains preferred element Na, bonus 10.0" in result.scenario_reason
    assert "final scenario bonus 10.0" in result.scenario_reason
    assert "final scenario penalty" not in result.scenario_reason


def test_avoided_element_produces_negative_delta_and_penalty_reason(evaluator):
    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="LiFePO4",
        policy=ScenarioPolicy(
            element="Li",
            avoid_elements=["Li"],
        ),
    )

    assert result.scenario_score == 80.0
    assert result.scenario_delta == -20.0
    assert "contains avoided element Li, penalty 20.0" in result.scenario_reason
    assert "final scenario penalty 20.0" in result.scenario_reason


def test_combined_bonus_and_penalty_reports_net_penalty(evaluator):
    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="LiNaFePO4",
        policy=ScenarioPolicy(
            element="Li",
            avoid_elements=["Li"],
            prefer_elements=["Na"],
        ),
    )

    assert result.scenario_score == 90.0
    assert result.scenario_delta == -10.0
    assert "contains avoided element Li, penalty 20.0" in result.scenario_reason
    assert "contains preferred element Na, bonus 10.0" in result.scenario_reason
    assert "final scenario penalty 10.0" in result.scenario_reason


def test_zero_adjustment_has_neutral_reason(evaluator):
    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="FePO4",
        policy=ScenarioPolicy(element="Li"),
    )

    assert result.scenario_score == 100.0
    assert result.scenario_delta == 0.0
    assert result.scenario_reason == "no final scenario adjustment"


def test_scenario_delta_equals_scenario_score_minus_recommendation_score(
    evaluator,
):
    recommendation_score = 131.28

    result = evaluator.evaluate(
        recommendation_score=recommendation_score,
        candidate_formula="NaFePO4",
        policy=ScenarioPolicy(
            element="Li",
            prefer_elements=["Na"],
        ),
    )

    assert result.scenario_delta == round(
        result.scenario_score - recommendation_score,
        2,
    )