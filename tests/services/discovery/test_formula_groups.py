"""SRQ-01 PR-B2: exact-analog formula groups at objective-aware admission (spec rev 3.11, R3, D12)."""

from app.domain import ordering
from app.domain.ordering import choose_representative
from app.services.discovery.chain_service import DiscoveryChainService
from app.services.research.formula_correspondence_report import _formula_group

LIFEPO4 = {"Li": 1 / 7, "Fe": 1 / 7, "P": 1 / 7, "O": 4 / 7}
NAFEPO4 = {"Na": 1 / 7, "Fe": 1 / 7, "P": 1 / 7, "O": 4 / 7}
NA3FE_PO4_2 = {"Na": 3 / 14, "Fe": 1 / 14, "P": 2 / 14, "O": 8 / 14}


def _service(fractions, mp_ids, energies):
    service = object.__new__(DiscoveryChainService)
    service.__dict__["_request_compositions"] = (fractions, mp_ids, energies)
    return service


def _candidate(material_id, mp_id, formula):
    return {"material_id": material_id, "mp_id": mp_id, "pretty_formula": formula, "shared_elements": ["Fe", "O", "P"]}


def _fixture():
    # 5 LiFePO4 (expanding); 10, 384, 1094 NaFePO4 records (one stored with a
    # different formula string); 6 Na3Fe(PO4)2 (not an exact analog).
    fractions = {5: LIFEPO4, 10: NAFEPO4, 384: dict(NAFEPO4), 1094: dict(NAFEPO4), 6: NA3FE_PO4_2}
    mp_ids = {5: "mp-19017", 10: "mp-19226", 384: "mp-1192859", 1094: "mp-746030", 6: "mp-19028"}
    energies = {5: 0.0, 10: 0.0, 384: 0.0404, 1094: 0.0049, 6: 0.0}
    candidates = [
        _candidate(6, "mp-19028", "Na3Fe(PO4)2"),
        _candidate(10, "mp-19226", "NaFePO4"),
        _candidate(1094, "mp-746030", "Na4Fe4P4O16"),
        _candidate(384, "mp-1192859", "NaFePO4"),
    ]
    return _service(fractions, mp_ids, energies), candidates


def test_choose_representative_is_the_lowest_numeric_mp_id():
    members = [{"material_id": 384, "mp_id": "mp-1192859"}, {"material_id": 1094, "mp_id": "mp-746030"},
               {"material_id": 10, "mp_id": "mp-19226"}]
    assert choose_representative(members)["mp_id"] == "mp-19226"


def test_exact_analogs_share_one_slot_and_order_is_kept():
    service, candidates = _fixture()
    kept = service._group_exact_analogs(("key",), 5, candidates)
    # Grouped by composition, not formula string: mp-746030 ("Na4Fe4P4O16")
    # joins the NaFePO4 group. Na3Fe(PO4)2 is not an exact analog and stays.
    assert [c["material_id"] for c in kept] == [6, 10]


def test_group_members_are_recorded_with_their_own_records():
    service, candidates = _fixture()
    service._group_exact_analogs(("key",), 5, candidates)
    groups = service.formula_groups_by_representative()
    assert set(groups) == {10}
    assert {m["mp_id"]: m["energy_above_hull"] for m in groups[10]} == {
        "mp-19226": 0.0, "mp-746030": 0.0049, "mp-1192859": 0.0404,
    }


def test_unusable_expanding_composition_groups_nothing():
    service, candidates = _fixture()
    service.__dict__["_request_compositions"][0][5] = None
    kept = service._group_exact_analogs(("key",), 5, candidates)
    assert kept == candidates
    assert service.formula_groups_by_representative() == {}


def test_representative_substitution_mechanism_for_ac11(monkeypatch):
    service, candidates = _fixture()
    monkeypatch.setattr(ordering, "choose_representative",
                        lambda members: next(m for m in members if m["mp_id"] == "mp-746030"))
    kept = service._group_exact_analogs(("key",), 5, candidates)
    assert [c["material_id"] for c in kept] == [6, 1094]
    assert set(service.formula_groups_by_representative()) == {1094}


def test_formula_group_lists_members_by_mp_id_with_one_traversed():
    members = [{"material_id": 384, "mp_id": "mp-1192859", "energy_above_hull": 0.0404},
               {"material_id": 10, "mp_id": "mp-19226", "energy_above_hull": 0.0}]
    group = _formula_group({10: members}, 10)
    assert [(m["mp_id"], m["traversed"]) for m in group] == [("mp-19226", True), ("mp-1192859", False)]


def test_formula_group_is_empty_when_not_reached_through_an_admission_group():
    assert _formula_group({10: [{"material_id": 10, "mp_id": "mp-19226"}]}, 384) == []
    assert _formula_group(None, 10) == []


def test_forced_representative_takes_the_earliest_member_slot(monkeypatch):
    """AC11 finding: the representative never loses the group's admission position."""
    service, _ = _fixture()
    candidates = [
        _candidate(10, "mp-19226", "NaFePO4"),
        _candidate(6, "mp-19028", "Na3Fe(PO4)2"),
        _candidate(1094, "mp-746030", "Na4Fe4P4O16"),
    ]
    monkeypatch.setattr(ordering, "choose_representative",
                        lambda members: next(m for m in members if m["mp_id"] == "mp-746030"))
    kept = service._group_exact_analogs(("key",), 5, candidates)
    assert [c["material_id"] for c in kept] == [1094, 6]


def test_groups_whose_representative_missed_the_cap_are_not_reported():
    """AC11 finding: a group formed before the cap is reported only if admitted."""
    service, candidates = _fixture()
    service._group_exact_analogs(("key",), 5, candidates)
    service._keep_admitted_groups(("key",), [candidates[0]])  # only Na3Fe(PO4)2 admitted
    assert service.formula_groups_by_representative() == {}
    service._group_exact_analogs(("key",), 5, candidates)
    service._keep_admitted_groups(("key",), [candidates[0], candidates[1]])  # NaFePO4 admitted
    assert set(service.formula_groups_by_representative()) == {10}
