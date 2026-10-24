"""The Discovery result-limit warning states what the candidate count covers."""

from app.services.discovery.warning_service import DiscoveryWarningService


def test_limit_warning_states_the_basis_of_the_candidate_count():
    warnings = DiscoveryWarningService().build_warnings(
        candidates=[{"formula": "NaFePO4", "pretty_formula": "NaFePO4"}],
        avoid_element=None,
        prefer_element=None,
        limit=10,
        total_candidate_count=839,
    )

    assert warnings == [
        "Results were limited to 10 candidates from 839 candidates: "
        "composition-related materials plus recommendation and scenario "
        "candidates, before the limit was applied."
    ]
    assert "generated" not in warnings[0]
