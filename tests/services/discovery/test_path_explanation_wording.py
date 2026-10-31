"""Path explanation wording (Release 1, R1-fix-21; contract S-5).

The path explanation states element differences as composition facts,
attributes only endpoint matches to the stated objective, and never calls
a path "scientifically useful".
"""

import itertools
import pathlib
import re

from app.services.discovery.path_ranking_service import DiscoveryPathRankingService

DISCLAIMER = (
    "These are composition-level relationships, not evidence of a "
    "feasible chemical transformation."
)
NEUTRAL_LEAD_IN = "Composition-level relationships along this path: "
OBJECTIVE_LEAD_IN = "In line with the stated objective: "

ENDPOINTS = (
    {"material_id": 2, "formula": "NaFePO4"},
    {"material_id": 2, "formula": "LiCoO2"},
    {"material_id": 2, "formula": None, "pretty_formula": None},
)
TRANSITIONS = (
    [{
        "transition_type": "alkali_substitution",
        "shared_elements": ["Fe", "O", "P"],
        "removed_elements": ["Li"],
        "introduced_elements": ["Na"],
    }],
    [{"transition_type": None, "removed_elements": [], "introduced_elements": []}],
    [],
)
ELEMENT_SETS = ([], ["Li"], ["Li", "Co"], ["Na"], ["Na", "K"])


def _explanations():
    service = DiscoveryPathRankingService()
    for endpoint, transitions, avoid, prefer, criticality, composition in itertools.product(
        ENDPOINTS, TRANSITIONS, ELEMENT_SETS, ELEMENT_SETS,
        (None, True, False), (False, True),
    ):
        result = service.rank_path(
            materials=[{"material_id": 1, "formula": "LiFePO4"}, endpoint],
            transitions=transitions,
            avoid_elements=avoid,
            prefer_elements=prefer,
            prefer_lower_criticality=criticality,
            composition_chain_reason=composition,
        )
        yield (avoid, prefer, endpoint, transitions, composition), result["usefulness_reason"]


def _path_reason(**overrides):
    values = {
        "materials": [
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "NaFePO4"},
        ],
        "transitions": TRANSITIONS[0],
        "avoid_elements": ["Li"],
        "prefer_elements": ["Na"],
    }
    values.update(overrides)
    return DiscoveryPathRankingService().rank_path(**values)["usefulness_reason"]


def test_scientifically_useful_appears_in_no_generated_explanation():
    for case, reason in _explanations():
        assert "scientifically useful" not in reason.lower(), (case, reason)


def test_scientifically_useful_appears_in_no_application_string():
    root = pathlib.Path(__file__).resolve().parents[3] / "app"
    offenders = [
        f"{path.relative_to(root)}:{number}"
        for path in root.rglob("*.py")
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if "scientifically useful" in line.lower()
    ]
    assert offenders == []


def test_path_explanation_states_composition_facts_not_actions():
    for (avoid, prefer, endpoint, transitions, composition), reason in _explanations():
        if composition or not transitions:
            continue
        assert not re.search(r"\b(removes|introduces|removal|introduction)\b", reason), reason
        assert reason.startswith((OBJECTIVE_LEAD_IN, NEUTRAL_LEAD_IN)), reason
        assert DISCLAIMER in reason, reason


def test_objective_lead_in_only_for_endpoint_matches():
    for (avoid, prefer, endpoint, transitions, composition), reason in _explanations():
        if composition or not transitions:
            continue
        formula = endpoint.get("formula") or ""
        symbols = set(re.findall(r"[A-Z][a-z]?", formula))
        matches = bool(formula) and (
            bool(set(avoid) - symbols) or bool(set(prefer) & symbols)
        )
        assert reason.startswith(OBJECTIVE_LEAD_IN) == matches, reason
        lead_in = reason.split(NEUTRAL_LEAD_IN)[0]
        assert "still contains" not in lead_in and "does not contain" not in lead_in


def test_full_wording_with_objective_matches():
    assert _path_reason(prefer_lower_criticality=False) == (
        "In line with the stated objective: endpoint excludes requested "
        "avoided element(s) Li; endpoint contains requested preferred "
        "element(s) Na. Composition-level relationships along this path: "
        "Li is absent from a later composition along the chain; Na appears "
        "along the chain; maintains Fe-O-P shared-element continuity; uses "
        "different alkali metal (composition not compared) transition logic. "
        + DISCLAIMER
        + " Criticality is excluded from objective-specific pathway ranking."
    )


def test_neutral_wording_without_objective_matches():
    reason = _path_reason(
        materials=[
            {"material_id": 1, "formula": "LiFePO4"},
            {"material_id": 2, "formula": "LiCoO2"},
        ],
        avoid_elements=["Co"],
        prefer_elements=["K"],
    )

    assert reason == (
        "Composition-level relationships along this path: no step along the "
        "chain goes from a composition with requested avoided element(s) Co "
        "to one without; no step along the chain goes from a composition "
        "without requested preferred element(s) K to one with; endpoint still "
        "contains requested avoided element(s) Co; endpoint does not contain "
        "requested preferred element(s) K; maintains Fe-O-P shared-element "
        "continuity; uses different alkali metal (composition not compared) "
        "transition logic. " + DISCLAIMER
    )


def test_wording_with_no_reported_relationship():
    reason = _path_reason(
        transitions=TRANSITIONS[1], avoid_elements=[], prefer_elements=[],
    )

    assert reason == (
        "Composition-level relationships along this path: none reported "
        "beyond the listed steps. " + DISCLAIMER
    )


def test_plural_elements_agree():
    reason = _path_reason(
        transitions=[{
            "transition_type": "shared_element_continuity",
            "removed_elements": ["Co", "Li"],
            "introduced_elements": ["K", "Na"],
        }],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert "Co, Li are absent from a later composition along the chain" in reason
    assert "K, Na appear along the chain" in reason
