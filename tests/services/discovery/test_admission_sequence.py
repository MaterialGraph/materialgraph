"""SRQ-01 PR-B3: R2 admission sequence on objective-aware requests (AC7, AC12)."""

from app.services.discovery.chain_service import DiscoveryChainService
from app.services.discovery.transition_validator import DiscoveryTransitionValidator

KEY = ("key",)
SOURCE = 5


def _service(groups, limit=None):
    service = object.__new__(DiscoveryChainService)
    service.transition_validator = object.__new__(DiscoveryTransitionValidator)
    service.__dict__["_efa_groups"] = {KEY: [{"representative_id": g, "members": [{"material_id": g, "mp_id": f"mp-{g}"}]}
                                            for g in groups]}
    if limit is not None:
        service.EXPANSION_LIMIT = limit
    return service


def _select(service, candidates, elements, prefer=(), avoid=()):
    return service._formula_aware_selection(
        cache_key=KEY, material_id=SOURCE, elements_map=elements,
        eligible_candidates=[{"material_id": c, "pretty_formula": f"F{c}"} for c in candidates],
        prefer_elements=set(prefer), avoid_elements=set(avoid), reject_introduced_avoided=True,
    )


def _ids(selected):
    return [c["material_id"] for c in selected]


LI = ["Li", "Fe", "P", "O"]
NA = ["Na", "Fe", "P", "O"]
K = ["K", "Fe", "P", "O"]


def test_preferred_exact_analog_is_admitted_first_and_covers_its_element():
    # Six four-element Li neighbours come first in family order; NaFePO4 (10)
    # is an exact analog containing the preferred Na.
    candidates = [1, 2, 3, 4, 6, 7, 10, 11]
    elements = {SOURCE: LI, **{c: LI for c in [1, 2, 3, 4, 6, 7]}, 10: NA, 11: NA}
    selected = _ids(_select(_service([10]), candidates, elements, prefer=["Na"]))
    assert selected[0] == 10
    assert 11 not in selected  # Na already covered: no second Na reservation
    assert len(selected) == 6


def test_preferred_element_without_exact_analog_keeps_its_reservation():
    candidates = [1, 2, 3, 4, 6, 7, 20]
    elements = {SOURCE: LI, **{c: LI for c in [1, 2, 3, 4, 6, 7]}, 20: K}
    selected = _ids(_select(_service([]), candidates, elements, prefer=["K"]))
    assert selected[0] == 20
    assert len(selected) == 6


def test_exact_analog_groups_beyond_the_budget_are_reported():
    groups = [31, 32, 33, 34, 35]
    candidates = [1, 2] + groups
    elements = {SOURCE: LI, 1: LI, 2: LI, **{g: NA for g in groups}}
    service = _service(groups)
    selected = _ids(_select(service, candidates, elements))
    assert selected[:4] == [31, 32, 33, 34]
    assert selected[4:] == [1, 2]
    record = service.efa_expansions()[0]
    assert (record["groups_found"], record["groups_admitted"]) == (5, 4)
    assert [(e["display_formula"], e["reason"]) for e in record["excluded"]] == [("F35", "efa_budget")]


def test_cap_reached_during_the_exact_analog_step_is_reported_as_cap():
    groups = [31, 32, 33]
    candidates = [20, 21] + groups
    elements = {SOURCE: LI, 20: K, 21: LI, **{g: NA for g in groups}}
    service = _service(groups, limit=3)
    selected = _ids(_select(service, candidates, elements, prefer=["K", "Na"]))
    # step 1: Na analog 31; step 2: K reservation 20; step 3: one slot left -> 32
    assert selected == [31, 20, 32]
    assert [e["reason"] for e in service.efa_expansions()[0]["excluded"]] == ["cap"]


def test_exact_analog_introducing_an_avoided_element_gets_no_priority():
    # Source NaFePO4-like; candidate 40 (Li analog) would introduce avoided Li.
    candidates = [1, 2, 3, 4, 6, 7, 40]
    elements = {SOURCE: NA, **{c: NA for c in [1, 2, 3, 4, 6, 7]}, 40: LI}
    service = _service([40])
    selected = _ids(_select(service, candidates, elements, avoid=["Li"]))
    assert 40 not in selected
    assert service.efa_expansions()[0]["excluded"] == []


def test_without_exact_analogs_admission_is_reservation_then_order():
    candidates = [1, 2, 3, 20, 4, 6, 7]
    elements = {SOURCE: LI, **{c: LI for c in [1, 2, 3, 4, 6, 7]}, 20: K}
    selected = _ids(_select(_service([]), candidates, elements, prefer=["K"]))
    assert selected == [20, 1, 2, 3, 4, 6]


def test_exact_analog_introducing_an_avoided_element_stays_a_general_candidate():
    """No priority is not exclusion: with a general slot free, step 4 still admits it (D10 unchanged)."""
    candidates = [1, 2, 40]
    elements = {SOURCE: NA, 1: NA, 2: NA, 40: LI}
    service = _service([40])
    selected = _ids(_select(service, candidates, elements, avoid=["Li"]))
    assert selected == [1, 2, 40]
    assert service.efa_expansions()[0]["excluded"] == []
