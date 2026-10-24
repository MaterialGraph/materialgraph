"""Objective Explore mode policy as one executable source (Release 1, contract P).

Drift tests: for each mode, the served policy, the response, the generated
descriptions and the observed behaviour agree. Scope is Objective Explore
only (register entry 37, condition d).
"""

import re

import pytest

from app.domain.objective_mode_policy import MODE_POLICIES, mode_policy
from app.schemas.discovery import ResearchObjective
from app.services.research.objective_coverage import AVOID_POLICY_EXPLANATIONS
from app.services.research.objective_exploration_service import (
    ResearchObjectiveExplorationService,
)

MODES = ("balanced", "exploratory", "strict")
EXPLORE = "/api/v1/materials/5/discovery/objective/explore"


def _objective(**overrides):
    values = {
        "avoid_elements": ["Li"],
        "prefer_elements": ["Na"],
        "preserve_elements": [],
        "target_family": None,
        "max_hops": 2,
        "limit": 20,
        "prefer_lower_criticality": False,
    }
    values.update(overrides)
    return values


def test_served_modes_are_the_policy_objects(client):
    response = client.get("/api/v1/discovery/objective-modes")

    assert response.status_code == 200
    body = response.json()
    assert body["scope"] == "objective_explore"
    assert [item["mode"] for item in body["modes"]] == list(MODES)
    for item in body["modes"]:
        assert item == mode_policy(item["mode"]).exposed()


@pytest.mark.parametrize("mode", MODES)
def test_response_policy_matches_served_policy(client, mode):
    served = {
        item["mode"]: item
        for item in client.get("/api/v1/discovery/objective-modes").json()["modes"]
    }[mode]

    data = client.post(
        EXPLORE,
        json={"objective": _objective(), "mode": mode, "limit": 20},
    ).json()

    assert data["constraint_policy"] == served["constraint_policy"]
    assert data["avoid_policy"] == served["avoid_policy"]
    assert data["prefer_policy"] == served["prefer_policy"]
    assert data["candidate_score_offset"] == served["candidate_score_offset"]
    # P-3: user-facing text is generated from the same object.
    assert data["warnings"] == [served["warning"]]
    assert data["objective_coverage"]["avoid_policy_explanation"] == (
        served["avoid_policy_explanation"]
    )
    assert AVOID_POLICY_EXPLANATIONS[mode] == served["avoid_policy_explanation"]


@pytest.mark.parametrize("mode", MODES)
def test_step_introducing_an_avoided_element_is_rejected(client, mode):
    # Every Na-containing neighbour of LiFePO4 would introduce Na.
    data = client.post(
        EXPLORE,
        json={
            "objective": _objective(avoid_elements=["Na"], prefer_elements=[]),
            "mode": mode,
            "limit": 20,
        },
    ).json()

    assert mode_policy(mode).avoid.introduced == "rejected_at_transition"
    for chain in data["chains"]:
        for material in chain["materials"][1:]:
            assert not re.search(r"Na(?![a-z])", material["formula"])
    for candidate in data["ranked_candidates"]:
        assert not re.search(r"Na(?![a-z])", candidate["formula"])


@pytest.mark.parametrize("mode", MODES)
def test_inherited_avoided_element_is_penalised_by_the_stated_amount(
    db_session,
    mode,
):
    policy = mode_policy(mode)
    service = ResearchObjectiveExplorationService(db_session)
    material = {"material_id": 1, "formula": "LiFe(PO3)3"}
    avoiding = ResearchObjective(**_objective(prefer_elements=[]))
    neutral = ResearchObjective(
        **_objective(avoid_elements=[], prefer_elements=[])
    )

    with_avoid = service._score_material(
        material=material, transitions=[], objective=avoiding, mode=mode,
    )
    without_avoid = service._score_material(
        material=material, transitions=[], objective=neutral, mode=mode,
    )

    assert without_avoid - with_avoid == policy.avoid.candidate_penalty
    assert without_avoid == 50.0 + policy.candidate_score_offset
    if policy.avoid.inherited == "allowed_with_penalty":
        assert f"{int(policy.avoid.candidate_penalty)} points" in (
            policy.avoid_explanation()
        )


def test_strict_excludes_avoided_non_source_materials_and_exempts_the_source(
    client,
):
    data = client.post(
        EXPLORE,
        json={"objective": _objective(), "mode": "strict", "limit": 20},
    ).json()

    assert data["avoid_policy"]["applies_to"] == "non_source"
    assert data["chains"], "fixture should yield Li-free chains from LiFePO4"
    for chain in data["chains"]:
        assert chain["materials"][0]["formula"] == "LiFePO4"
        for material in chain["materials"][1:]:
            assert not re.search(r"Li(?![a-z])", material["formula"])


def test_strict_evidence_split_is_disclosed_and_pinned(db_session):
    """P-7: admission reads element records; the final filter reads formulas."""
    strict = mode_policy("strict")
    assert strict.avoid.admission_evidence == "element_records"
    assert strict.avoid.missing_element_records == "excluded"
    assert strict.avoid.final_filter_evidence == "formula_symbols"

    service = ResearchObjectiveExplorationService(db_session)
    objective = ResearchObjective(**_objective(prefer_elements=[]))
    # The final filter reads formula symbols only: no element records are
    # consulted for these synthetic materials.
    chain = {"materials": [
        {"material_id": 5, "formula": "LiFePO4"},
        {"material_id": 999, "formula": "LiCoO2"},
    ]}

    assert service._apply_mode_constraints([chain], objective, "strict") == []
    assert service._apply_mode_constraints([chain], objective, "balanced") == [
        chain
    ]


def test_balanced_and_exploratory_generate_the_same_chains(client):
    """P-6: the modes differ only in candidate scoring, not in search."""
    results = {
        mode: client.post(
            EXPLORE,
            json={"objective": _objective(), "mode": mode, "limit": 20},
        ).json()
        for mode in ("balanced", "exploratory")
    }

    def paths(data):
        return [
            [material["material_id"] for material in chain["materials"]]
            for chain in data["chains"]
        ]

    assert paths(results["balanced"]) == paths(results["exploratory"])
    for key in ("generated_chain_count", "expanded_state_count",
                "search_truncated"):
        assert (
            results["balanced"]["search_metadata"][key]
            == results["exploratory"]["search_metadata"][key]
        )


@pytest.mark.parametrize("mode", MODES)
def test_no_mode_claims_behaviour_without_a_mechanism(mode):
    """P-5 and P-2: no broader-search claims, no soft-penalty description."""
    exposed = mode_policy(mode).exposed()
    text = " ".join(
        str(exposed[key])
        for key in ("description", "avoid_policy_explanation", "warning")
    ).lower()

    for claim in ("broader", "weaker", "unusual", "soft preference",
                  "soft penalty"):
        assert claim not in text
    assert exposed["constraint_policy"]["avoid_elements"] != "soft_penalty"


def test_policy_values_encode_the_verified_baseline():
    """P-6: values are today's behaviour, not Release 2 behaviour."""
    balanced = MODE_POLICIES["balanced"]
    exploratory = MODE_POLICIES["exploratory"]
    strict = MODE_POLICIES["strict"]

    assert (balanced.avoid.candidate_penalty,
            exploratory.avoid.candidate_penalty,
            strict.avoid.candidate_penalty) == (25.0, 10.0, 25.0)
    assert (balanced.candidate_score_offset,
            exploratory.candidate_score_offset,
            strict.candidate_score_offset) == (0.0, 5.0, 0.0)
    assert [policy.hard_avoid_admission for policy in MODE_POLICIES.values()] == [
        False, False, True,
    ]
    assert all(
        policy.objective_aware_prefer_allocation
        and policy.reject_introduced_avoided
        and policy.prefer.candidate_bonus_per_element == 15.0
        for policy in MODE_POLICIES.values()
    )
