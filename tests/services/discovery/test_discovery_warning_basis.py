"""The Discovery result-limit warning states what the candidate count covers.

Updated by R1-fix-839: the count is stated by source, from what each source
supplied for the request; recommendation and scenario candidates are named
only when they were requested (the route default is off).
"""

from app.services.discovery.warning_service import DiscoveryWarningService


def test_limit_warning_states_the_basis_of_the_candidate_count():
    warnings = DiscoveryWarningService().build_warnings(
        candidates=[{"formula": "NaFePO4", "pretty_formula": "NaFePO4"}],
        avoid_element=None,
        prefer_element=None,
        limit=10,
        total_candidate_count=839,
        pool_basis={"composition": 839, "recommendation": None, "scenario": None},
    )

    assert warnings == [
        "Results were limited to 10 candidates from 839 distinct candidates "
        "before the final result limit was applied: composition-related "
        "materials supplied 839 candidates (the source material excluded); "
        "recommendation candidates were not requested; scenario candidates "
        "were not requested."
    ]
    assert "generated" not in warnings[0]


def test_limit_warning_names_requested_sources_with_their_caps():
    warnings = DiscoveryWarningService().build_warnings(
        candidates=[{"formula": "NaFePO4", "pretty_formula": "NaFePO4"}],
        avoid_element=None,
        prefer_element=None,
        limit=10,
        total_candidate_count=850,
        pool_basis={
            "composition": 839,
            "recommendation": {"supplied": 20, "cap": 20},
            "scenario": {"supplied": 0, "cap": 20, "needs_element": False},
        },
    )

    assert warnings == [
        "Results were limited to 10 candidates from 850 distinct candidates "
        "before the final result limit was applied: composition-related "
        "materials supplied 839 candidates (the source material excluded); "
        "recommendation candidates supplied 20 candidates (this source is "
        "capped at 20 for this request); scenario candidates were enabled but "
        "none were generated for this request. A candidate supplied by more "
        "than one source is counted once in the total."
    ]
