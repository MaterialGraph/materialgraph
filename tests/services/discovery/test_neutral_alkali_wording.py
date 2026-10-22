"""Neutral wording for the alkali relationship (Release 1, R1-1; contract S-5).

The ``alkali_substitution`` identifier compares alkali-metal membership only.
User-facing text derived from it must not claim replacement, a substitution
candidate, a mechanism or chemical interpretability, and a retained source
alkali must never read as removed.
"""

import pathlib
import re

from app.domain.relationship_labels import (
    DIFFERENT_ALKALI_LABEL,
    alkali_difference_text,
    relationship_text,
)
from app.services.discovery.substitution_path_service import (
    DiscoverySubstitutionPathService,
)
from app.services.discovery.transition_validator import (
    DiscoveryTransitionValidator,
)

FORBIDDEN = re.compile(
    r"replac|substitution candidate|mechanism|chemically interpretable",
    re.IGNORECASE,
)


def _node(material_id, formula):
    return {"material_id": material_id, "formula": formula}


def _assert_neutral(text):
    assert not FORBIDDEN.search(text), text


def test_alkali_transition_reason_is_neutral_and_states_what_was_compared():
    result = DiscoveryTransitionValidator().validate_transition(
        from_material=_node(1, "LiFePO4"),
        to_material=_node(2, "NaFePO4"),
        from_elements=["Li", "Fe", "O", "P"],
        to_elements=["Na", "Fe", "O", "P"],
        relationships=["alkali_substitution", "shared_chemistry"],
    )

    assert result["transition_type"] == "alkali_substitution"
    assert "alkali metals differ: Li → Na" in result["reason"]
    assert "element ratios and structure were not compared" in result["reason"]
    assert "Li absent in target; Na introduced" in result["reason"]
    _assert_neutral(result["reason"])


def test_retained_source_alkali_is_not_described_as_removed():
    result = DiscoveryTransitionValidator().validate_transition(
        from_material=_node(1, "LiFePO4"),
        to_material=_node(2, "LiNaFePO4"),
        from_elements=["Li", "Fe", "O", "P"],
        to_elements=["Li", "Na", "Fe", "O", "P"],
        relationships=["alkali_substitution", "shared_chemistry"],
    )

    assert "alkali metals differ: Li → Li, Na" in result["reason"]
    assert "absent in target" not in result["reason"]
    _assert_neutral(result["reason"])

    path = DiscoverySubstitutionPathService().build_path(
        "LiFePO4",
        "LiNaFePO4",
        ["Li", "Fe", "O", "P"],
        ["Li", "Na", "Fe", "O", "P"],
        ["alkali_substitution"],
    )
    assert "Li → Li, Na" in path["reason"]
    _assert_neutral(path["reason"])


def test_non_alkali_element_difference_is_neutral():
    result = DiscoveryTransitionValidator().validate_transition(
        from_material=_node(1, "LiFePO4"),
        to_material=_node(2, "LiMnPO4"),
        from_elements=["Li", "Fe", "O", "P"],
        to_elements=["Li", "Mn", "O", "P"],
        relationships=["shared_chemistry", "phosphate_related"],
    )

    assert "Fe absent in target; Mn introduced" in result["reason"]
    _assert_neutral(result["reason"])

    path = DiscoverySubstitutionPathService().build_path(
        "LiFePO4",
        "LiMnPO4",
        ["Li", "Fe", "O", "P"],
        ["Li", "Mn", "O", "P"],
        ["shared_chemistry"],
    )
    assert path["path_type"] == "transition_metal_substitution"
    _assert_neutral(path["reason"])


def test_family_relationship_reason_is_neutral(db_session):
    from app.services.material.family_service import MaterialFamilyService

    reason = MaterialFamilyService(db_session)._build_relationship_reason(
        base_formula="LiFePO4",
        candidate_formula="Na3Fe(PO4)2",
        relationships=["shared_chemistry", "alkali_substitution"],
        shared_elements=["Fe", "O", "P"],
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Na", "Fe", "P", "O"],
    )

    assert "alkali metals differ: Li → Na" in reason
    _assert_neutral(reason)


def test_identifier_is_shown_with_its_neutral_label():
    assert relationship_text("alkali_substitution") == DIFFERENT_ALKALI_LABEL
    assert relationship_text("family_expansion") == "family_expansion"
    assert alkali_difference_text({"Li", "Fe"}, {"K", "Na", "Fe"}) == (
        "alkali metals differ: Li → K, Na; "
        "element ratios and structure were not compared"
    )


def test_pathway_analysis_lists_the_alkali_step_as_a_tradeoff_not_a_strength(
    db_session,
):
    from app.services.research.scientific_pathway_analysis_service import (
        ScientificPathwayAnalysisService,
    )

    service = ScientificPathwayAnalysisService(db_session)
    transitions = [{
        "transition_type": "alkali_substitution",
        "removed_elements": ["Li"],
        "introduced_elements": ["Na"],
        "shared_elements": ["Fe", "O", "P"],
    }]
    chain = {"transitions": transitions, "score_breakdown": {}}

    strengths = service._strengths(chain=chain, transitions=transitions)
    tradeoffs = service._tradeoffs(chain=chain, transitions=transitions, quality=[])

    assert not any("alkali" in item.lower() for item in strengths)
    for item in strengths:
        _assert_neutral(item)
    assert (
        "Includes a different-alkali step; element ratios and structure "
        "were not compared."
    ) in tradeoffs


def test_no_forbidden_alkali_wording_remains_in_application_strings():
    """Code search (S-5): no user-facing literal claims replacement."""
    phrases = re.compile(
        r"is replaced by|substitution candidate|chemically interpretable|"
        r"alkali-substitution hypothesis|alkali substitution logic|"
        r"possible alkali",
        re.IGNORECASE,
    )
    root = pathlib.Path(__file__).resolve().parents[3] / "app"
    offenders = [
        f"{path.relative_to(root)}:{number}"
        for path in root.rglob("*.py")
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if phrases.search(line)
    ]
    assert offenders == []
