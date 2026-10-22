"""Scoring disposition of the alkali label (Release 1, R1-2; contract S).

S-1: no Discovery bonus. S-2: an alkali step's plausibility equals what the
step would receive with the alkali rule disabled, checked separately for
pathway ranking and for Discovery edge intelligence (each keeps its own
family_expansion calculation). S-3: no score term is keyed on the label.
"""

import pathlib

import pytest

from app.services.discovery.edge_intelligence_service import (
    DiscoveryEdgeIntelligenceService,
)
from app.services.discovery.path_ranking_service import (
    DiscoveryPathRankingService,
)
from app.services.discovery.scoring_service import DiscoveryScoringService
from app.services.discovery.transition_validator import (
    DiscoveryTransitionValidator,
)

# (source elements, target elements, relationships from the family rules)
PAIRS = {
    "phosphate": (
        ["Li", "Fe", "P", "O"], ["Na", "Fe", "P", "O"],
        ["shared_chemistry", "alkali_substitution", "transition_metal_related",
         "phosphate_related", "oxide_related"],
    ),
    "oxide": (
        ["Li", "Mn", "Fe", "O"], ["Na", "Mn", "Fe", "O"],
        ["shared_chemistry", "alkali_substitution", "transition_metal_related",
         "oxide_related"],
    ),
    "no_family": (
        ["Li", "Fe", "Si", "S"], ["Na", "Fe", "Si", "S"],
        ["shared_chemistry", "alkali_substitution", "transition_metal_related"],
    ),
}


def _transitions(pair):
    source, target, relationships = PAIRS[pair]
    validator = DiscoveryTransitionValidator()

    def validate(rels):
        return validator.validate_transition(
            from_material={"material_id": 1, "formula": "A"},
            to_material={"material_id": 2, "formula": "B"},
            from_elements=source,
            to_elements=target,
            relationships=rels,
        )

    with_rule = validate(relationships)
    without_rule = validate([r for r in relationships if r != "alkali_substitution"])
    assert with_rule["transition_type"] == "alkali_substitution"
    assert without_rule["transition_type"] == "family_expansion"
    return with_rule, without_rule


def test_discovery_family_score_has_no_alkali_bonus():
    score, breakdown = DiscoveryScoringService().score_family_candidate(
        ["shared_chemistry", "alkali_substitution", "phosphate_related"]
    )
    assert score == 40.0
    assert breakdown == {"family_bonus": 40.0}


def test_discovery_api_breakdowns_contain_no_alkali_or_substitution_term(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates",
        params={"avoid_element": "Li", "prefer_element": "Na", "limit": 20},
    )
    assert response.status_code == 200
    for candidate in response.json()["candidates"]:
        for key in candidate["score_breakdown"]:
            assert "substitution" not in key and "alkali" not in key


@pytest.mark.parametrize("pair", sorted(PAIRS))
def test_pathway_plausibility_equals_plausibility_without_the_alkali_rule(pair):
    with_rule, without_rule = _transitions(pair)
    ranking = DiscoveryPathRankingService()

    assert ranking._score_transition_plausibility([with_rule]) == (
        ranking._score_transition_plausibility([without_rule])
    )
    expected = {"phosphate": 17.0, "oxide": 17.0, "no_family": 10.0}[pair]
    assert ranking._score_transition_plausibility([with_rule]) == expected


@pytest.mark.parametrize(
    ("pair", "edge_family", "expected"),
    [("phosphate", "phosphate", 0.75),
     ("oxide", "oxide", 0.7),
     # The graph builder labels a non-P, non-O alkali edge "alkali" (kept for
     # compatibility, D1); without the alkali rule it would have no family.
     ("no_family", "alkali", 0.7)],
)
def test_edge_plausibility_equals_plausibility_without_the_alkali_rule(
    pair, edge_family, expected,
):
    with_rule, without_rule = _transitions(pair)
    service = DiscoveryEdgeIntelligenceService()
    family_without_rule = None if edge_family == "alkali" else edge_family

    def edge(transition, family):
        return service.build_edge_intelligence(
            transition_type=transition["transition_type"],
            family=family,
            preserved_framework=transition["preserved_framework"],
            removed_elements=transition["removed_elements"],
            introduced_elements=transition["introduced_elements"],
            scientific_reason=transition["reason"],
        )

    labelled = edge(with_rule, edge_family)
    unlabelled = edge(without_rule, family_without_rule)
    assert labelled["scientific_plausibility"] == expected
    assert labelled["scientific_plausibility"] == (
        unlabelled["scientific_plausibility"]
    )
    assert labelled["edge_score"] == unlabelled["edge_score"]


def test_no_score_term_is_keyed_on_the_alkali_label():
    """S-3 code search over every scoring surface."""
    root = pathlib.Path(__file__).resolve().parents[3] / "app" / "services"
    scoring_files = {
        "discovery/scoring_service.py": False,
        "research/objective_exploration_service.py": False,
        "discovery/path_ranking_service.py": True,
        "discovery/edge_intelligence_service.py": True,
    }
    for relative, normalises in scoring_files.items():
        lines = (root / relative).read_text(encoding="utf-8").splitlines()
        hits = [n for n, line in enumerate(lines) if "alkali_substitution" in line]
        if not normalises:
            assert hits == [], relative
            continue
        # Only the S-2 normalisation may mention the label: it maps the step
        # to family_expansion and confers nothing else.
        assert len(hits) == 1, relative
        assert 'transition_type == "alkali_substitution"' in lines[hits[0]]
        assert 'transition_type = "family_expansion"' in lines[hits[0] + 1]
