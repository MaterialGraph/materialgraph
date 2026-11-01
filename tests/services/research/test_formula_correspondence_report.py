"""SRQ-01 PR-A part 2: formula-correspondence report (spec rev 3.7, 4.0, R7.1, AC6/AC9/AC13)."""

import re
from types import SimpleNamespace
from typing import get_args

import pytest
from sqlalchemy import event, select

from app.core.database import engine
from app.models.material import Material
from app.schemas import research_objective_exploration as schema
from app.services.material import formula_correspondence as classifier
from app.services.material.formula_correspondence import EFA_ALKALI_METALS
from app.services.material.search_service import normalise_stored_composition
from app.services.research import formula_correspondence_report as report_module
from app.services.research.formula_correspondence_report import (
    LIMITATIONS,
    build_formula_correspondence_report,
    load_compositions,
    mp_id_sort_key,
)
from app.services.research.objective_exploration_service import ResearchObjectiveExplorationService

EXPLORE = "/api/v1/materials/{}/discovery/objective/explore"
_BASE = {
    "avoid_elements": [], "prefer_elements": [], "preserve_elements": [], "target_family": None,
    "max_hops": 2, "limit": 10, "prefer_lower_criticality": True, "require_stable_materials": False,
}
CS01 = {"objective": {**_BASE, "avoid_elements": ["Li", "Co"], "prefer_elements": ["Na", "K"],
                      "preserve_elements": ["Fe", "P", "O"], "target_family": "phosphate"},
        "mode": "balanced", "limit": 10}
OBJECTIVE_AWARE = [
    (5, CS01),
    (28, {"objective": {**_BASE, "avoid_elements": ["Li"], "prefer_elements": ["Na"]}, "mode": "balanced", "limit": 10}),
    (5, {"objective": {**_BASE, "avoid_elements": ["Li"]}, "mode": "strict", "limit": 10}),
    (28, {"objective": {**_BASE, "prefer_elements": ["Na"]}, "mode": "exploratory", "limit": 5}),
]
FROZEN = [
    (5, {"objective": _BASE, "mode": "balanced", "limit": 10}),
    (5, {"objective": _BASE, "mode": "exploratory", "limit": 10}),
    (28, {"objective": _BASE, "mode": "strict", "limit": 10}),
    (5, {"objective": {**_BASE, "avoid_elements": ["Li", "Co"], "preserve_elements": ["Fe", "P", "O"],
                       "target_family": "phosphate"}, "mode": "balanced", "limit": 10}),
    (28, {"objective": {**_BASE, "avoid_elements": ["Li"]}, "mode": "exploratory", "limit": 10}),
]
SECTION_3_FORBIDDEN = ("validated", "same structure", "equivalent", "drop-in", "substitution mechanism")
# The existing neutral-alkali wording rules (tests/services/discovery/test_neutral_alkali_wording.py).
NEUTRAL_ALKALI_FORBIDDEN = re.compile(
    r"replac|substitution candidate|mechanism|chemically interpretable|is replaced by|"
    r"alkali-substitution hypothesis|alkali substitution logic|possible alkali",
    re.IGNORECASE,
)


def _explore(client, source, body):
    response = client.post(EXPLORE.format(source), json=body)
    assert response.status_code == 200, response.text
    return response.json()


def _alkali(fractions):
    return EFA_ALKALI_METALS.intersection(fractions or {})


# Scope (4.0) and key absence (R7.1, AC6) ---------------------------------------

@pytest.mark.parametrize(
    ("prefer", "avoid", "mode", "expected"),
    [
        (["Na"], [], "balanced", True),
        (["Na"], [], "exploratory", True),
        (["Na"], ["Li"], "strict", True),
        ([], ["Li"], "strict", True),
        ([], [], "strict", False),
        ([], ["Li"], "balanced", False),
        ([], ["Li"], "exploratory", False),
        ([], [], "balanced", False),
    ],
)
def test_objective_aware_scope(prefer, avoid, mode, expected):
    request = SimpleNamespace(objective=SimpleNamespace(prefer_elements=prefer, avoid_elements=avoid), mode=mode)
    assert ResearchObjectiveExplorationService.is_objective_aware(request) is expected


@pytest.mark.parametrize(("source", "body"), FROZEN)
def test_frozen_requests_carry_no_key_at_all(client, source, body):
    response = client.post(EXPLORE.format(source), json=body)
    assert response.status_code == 200
    assert "formula_correspondence" not in response.json()
    assert b"formula_correspondence" not in response.content


@pytest.mark.parametrize(("source", "body"), OBJECTIVE_AWARE)
def test_objective_aware_requests_always_carry_the_report(client, source, body):
    report = _explore(client, source, body)["formula_correspondence"]
    assert report["contract_version"] == "1"
    assert report["basis"] == "stored_composition_fractions"
    assert report["tolerance"] == 1e-6
    assert report["formula_grouping_available"] is False
    assert report["admission_reporting_available"] is False
    assert report["expansions"] == []
    assert all(entry["formula_group"] == [] for entry in report["source_correspondence"])
    assert report["not_evaluated_count"] == len(report["not_evaluated_material_ids"])
    assert report["limitations"] == LIMITATIONS


def test_schema_literals_match_the_classifier():
    assert get_args(schema.CorrespondenceClass) == get_args(classifier.CorrespondenceClass)
    assert get_args(schema.CorrespondenceReason) == get_args(classifier.CorrespondenceReason)


# Guard: one-alkali replacement pairs only ---------------------------------------

@pytest.mark.parametrize(("source", "body"), OBJECTIVE_AWARE)
def test_no_entry_has_a_side_without_alkali(client, db_session, source, body):
    data = _explore(client, source, body)
    report = data["formula_correspondence"]
    involved = {source}
    involved.update(entry["from_material_id"] for entry in report["transitions"])
    involved.update(entry["to_material_id"] for entry in report["transitions"])
    involved.update(entry["material_id"] for entry in report["source_correspondence"])
    fractions, _ = load_compositions(db_session, involved)
    for entry in report["transitions"]:
        from_alkali = _alkali(fractions[entry["from_material_id"]])
        to_alkali = _alkali(fractions[entry["to_material_id"]])
        assert from_alkali and to_alkali and from_alkali != to_alkali, entry
    for entry in report["source_correspondence"]:
        assert _alkali(fractions[source]) and _alkali(fractions[entry["material_id"]]), entry


def test_pairs_that_are_not_one_alkali_replacements_are_omitted(db_session):
    # Reference IDs: 5 LiFePO4, 1 LiFe(PO3)3, 6 Na3Fe(PO4)2, 28 LiMnO2,
    # 22 MgMn2O4 (no alkali), 19 NaMnO2.
    chains = [
        {"materials": [{"material_id": 5}, {"material_id": 1}, {"material_id": 6}],
         "transitions": [_transition(5, 1, ["Fe", "Li", "O", "P"], [], []),       # same alkali: None
                         _transition(1, 6, ["Fe", "O", "P"], ["Li"], ["Na"])]},    # Li -> Na: kept
        {"materials": [{"material_id": 28}, {"material_id": 22}, {"material_id": 19}],
         "transitions": [_transition(28, 22, ["Mn", "O"], ["Li"], ["Mg"]),         # alkali removed
                         _transition(22, 19, ["Mn", "O"], ["Mg"], ["Na"])]},       # alkali inserted
    ]
    report = build_formula_correspondence_report(
        db_session, source_material_id=28, chains=chains,
        ranked_candidates=[{"material_id": 22}, {"material_id": 19}],
    )
    assert [(t["from_material_id"], t["to_material_id"]) for t in report["transitions"]] == [(1, 6)]
    assert report["transitions"][0]["chain_position"] == 1
    assert report["transitions"][0]["transition_index"] == 1
    assert report["transitions"][0]["correspondence"]["reason"] == "ratios_differ"
    # MgMn2O4 has no alkali; NaMnO2 is LiMnO2's exact analog.
    assert [entry["material_id"] for entry in report["source_correspondence"]] == [19]
    assert report["not_evaluated_material_ids"] == []


def _transition(from_id, to_id, shared, removed, introduced):
    return {"from_material_id": from_id, "to_material_id": to_id, "shared_elements": shared,
            "removed_elements": removed, "introduced_elements": introduced}


# None versus not_evaluated --------------------------------------------------------

def _break_composition(db_session, material_id):
    material = db_session.get(Material, material_id)
    material.raw_data = {**(material.raw_data or {}), "composition": {"Fe": 0}}
    db_session.flush()


def test_unusable_composition_is_reported_only_where_it_was_examined(db_session):
    _break_composition(db_session, 10)   # NaFePO4
    _break_composition(db_session, 7)    # Na3Fe3(PO4)4
    chains = [{"materials": [{"material_id": 5}, {"material_id": 10}, {"material_id": 6}],
               "transitions": [
                   # Li -> Na by element records, NaFePO4 unusable: examined, not evaluated.
                   _transition(5, 10, ["Fe", "O", "P"], ["Li"], ["Na"]),
                   _transition(10, 6, ["Fe", "Na", "O", "P"], [], []),
               ]},
              {"materials": [{"material_id": 6}, {"material_id": 7}],
               # Na -> Na: not alkali-changing, so the unusable 7 is never examined.
               "transitions": [_transition(6, 7, ["Fe", "Na", "O", "P"], [], [])]}]
    ranked = [{"material_id": 6}, {"material_id": 10}]
    report = build_formula_correspondence_report(
        db_session, source_material_id=5, chains=chains, ranked_candidates=ranked,
    )
    assert report["not_evaluated_material_ids"] == [10]
    assert report["not_evaluated_count"] == 1
    # The unusable candidate is not listed as a source analog.
    assert report["source_correspondence"] == []
    # The examined alkali-changing pair is serialized as not_evaluated, never dropped.
    assert report["transitions"] == [{
        "chain_position": 1, "transition_index": 0, "from_material_id": 5, "to_material_id": 10,
        "correspondence": {"correspondence_class": "not_evaluated", "reason": "formula_unparsed",
                           "replaced_from": None, "replaced_to": None},
    }]


def test_not_evaluated_ids_are_ordered_by_numeric_mp_id(db_session):
    for material_id in (8, 7, 9):   # mp-761065, mp-556540, mp-752506
        _break_composition(db_session, material_id)
    ranked = [{"material_id": 8}, {"material_id": 7}, {"material_id": 9}]
    report = build_formula_correspondence_report(
        db_session, source_material_id=5, chains=[], ranked_candidates=ranked,
    )
    assert report["not_evaluated_material_ids"] == [7, 9, 8]
    assert mp_id_sort_key("mp-19226", 10) < mp_id_sort_key("mp-1192859", 384)
    # Non-numeric and missing MP IDs follow every numeric one, by MP ID string
    # (a missing ID as the empty string), then by local ID.
    assert mp_id_sort_key("mp-999", 1) < mp_id_sort_key(None, 3) < mp_id_sort_key("mvc-1", 2)
    assert mp_id_sort_key(None, 3) < mp_id_sort_key(None, 4)


# Compositions: one query, always normalised (AC13) -----------------------------------

def test_compositions_load_in_one_query(db_session):
    statements = []

    def count(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", count)
    try:
        load_compositions(db_session, range(1, 29))
    finally:
        event.remove(engine, "before_cursor_execute", count)
    assert len([s for s in statements if "materials" in s]) == 1


@pytest.mark.parametrize(("source", "body"), OBJECTIVE_AWARE)
def test_every_classified_composition_was_normalised(client, monkeypatch, source, body):
    normalised = []
    seen = []
    real_normalise = report_module.normalise_stored_composition
    real_classify = report_module.classify_formula_correspondence

    def spy_normalise(raw):
        result = real_normalise(raw)
        normalised.append(result)
        return result

    def spy_classify(source_fractions, candidate_fractions, *args, **kwargs):
        seen.extend([source_fractions, candidate_fractions])
        return real_classify(source_fractions, candidate_fractions, *args, **kwargs)

    monkeypatch.setattr(report_module, "normalise_stored_composition", spy_normalise)
    monkeypatch.setattr(report_module, "classify_formula_correspondence", spy_classify)
    _explore(client, source, body)
    assert seen, "the classifier was not called"
    for fractions in seen:
        assert fractions is None or any(fractions is item for item in normalised)


# Case Study 01 on the reference data -----------------------------------------------

def test_case_study_01_report_on_reference_data(client, db_session):
    data = _explore(client, 5, CS01)
    report = data["formula_correspondence"]
    mp_by_id = dict(db_session.execute(select(Material.id, Material.mp_id)).all())

    ranked = [mp_by_id[candidate["material_id"]] for candidate in data["ranked_candidates"]]
    assert "mp-19226" in ranked
    assert report["source_correspondence"] == [{
        "candidate_rank": ranked.index("mp-19226") + 1,
        "material_id": 10,
        "correspondence": {"correspondence_class": "exact_alkali_replacement", "reason": None,
                           "replaced_from": "Li", "replaced_to": "Na"},
        "formula_group": [],
    }]
    pairs = {
        (mp_by_id[t["from_material_id"]], mp_by_id[t["to_material_id"]],
         t["correspondence"]["correspondence_class"], t["correspondence"]["reason"])
        for t in report["transitions"]
    }
    assert pairs == {
        (source, target, "not_exact_replacement", "ratios_differ")
        for source in ("mp-19017", "mp-26003", "mp-25977", "mp-27007", "mp-19294")
        for target in ("mp-19028", "mp-556540")
    }
    assert report["not_evaluated_material_ids"] == []


def test_nafepo4_is_exact_against_lifepo4_whenever_ranked(client):
    for source, body in OBJECTIVE_AWARE:
        if source != 5:
            continue
        data = _explore(client, source, body)
        if 10 in [candidate["material_id"] for candidate in data["ranked_candidates"]]:
            entries = [e for e in data["formula_correspondence"]["source_correspondence"] if e["material_id"] == 10]
            assert entries and entries[0]["correspondence"]["correspondence_class"] == "exact_alkali_replacement"


def test_stored_composition_of_lifepo4_normalises_as_expected(db_session):
    raw = db_session.execute(select(Material.raw_data["composition"]).where(Material.id == 5)).scalar_one()
    assert set(normalise_stored_composition(raw)) == {"Li", "Fe", "P", "O"}


# Wording (AC9) ------------------------------------------------------------------

def test_report_strings_use_no_forbidden_wording():
    for text in LIMITATIONS:
        lowered = text.lower()
        assert not any(phrase in lowered for phrase in SECTION_3_FORBIDDEN), text
        assert not NEUTRAL_ALKALI_FORBIDDEN.search(text), text


def test_limitations_state_sections_2_3_and_2_5():
    joined = " ".join(LIMITATIONS)
    assert "crystal structure" in joined and "oxidation states" in joined
    assert "distinct materials" in joined
    assert "not reachable" in joined and "candidate pool" in joined
