"""Full-dataset material search (Release 1, R1-5; contract M)."""

import itertools
import math

import pytest

from app.services.material.search_service import (
    TAU,
    compositions_equal,
    index_from_rows,
    normalise_stored_composition,
    parse_formula_query,
    SearchQueryError,
)

SEARCH = "/api/v1/materials/search"


def _search(client, mode, q, **params):
    return client.get(SEARCH, params={"mode": mode, "q": q, **params})


def _ids(response):
    return [item["material_id"] for item in response.json()["results"]]


# M-1 -----------------------------------------------------------------------

def test_mode_is_explicit_and_every_response_carries_an_interpretation(client):
    assert client.get(SEARCH, params={"q": "LiFePO4"}).status_code == 422

    formula = _search(client, "formula", "FePO4Li").json()["interpretation"]
    assert formula["mode"] == "formula"
    assert formula["elements"] == ["Fe", "Li", "O", "P"]
    assert formula["amounts"] == {"Fe": 1.0, "P": 1.0, "O": 4.0, "Li": 1.0}
    assert formula["reduced_formula"] == "LiFePO4"

    identity = _search(client, "mp_id", "mp-19017").json()["interpretation"]
    assert identity["mode"] == "mp_id"
    assert identity["mp_id"] == "mp-19017"

    for mode, query in (("chemsys", "Li-Fe-P-O"), ("contains", "Na, Fe")):
        assert _search(client, mode, query).json()["interpretation"]["mode"] == mode


# M-2 -----------------------------------------------------------------------

@pytest.mark.parametrize(
    ("query", "expected"),
    [("FePO4Li", [5]), ("Na3FeP2O8", [6]), ("Na3Fe(PO4)2", [6]),
     ("NaFePO4", [10]), ("Li2Fe2P2O8", [5])],
)
def test_formula_equality_is_composition_equality(client, query, expected):
    assert _ids(_search(client, "formula", query)) == expected


def test_identical_compositions_of_distinct_identities_are_separate_matches():
    rows = [
        (10, "mp-19226", "NaFePO4", "NaFePO4",
         {"Na": 4.0, "Fe": 4.0, "P": 4.0, "O": 16.0}),
        (384, "mp-1192859", "NaFePO4", "NaFePO4",
         {"Fe": 4.0, "Na": 4.0, "O": 16.0, "P": 4.0}),
    ]
    index = index_from_rows(rows, (2, 384))
    query = parse_formula_query("NaFePO4")["normalized_fractions"]
    matches = [
        item.mp_id for item in index.materials
        if compositions_equal(item.fractions, query)
    ]
    assert matches == ["mp-19226", "mp-1192859"]


def test_tolerance_boundary_is_tau_on_normalised_fractions():
    base = {"Li": 1 / 7, "Fe": 1 / 7, "P": 1 / 7, "O": 4 / 7}
    inside = {**base, "Li": base["Li"] + 0.9 * TAU, "O": base["O"] - 0.9 * TAU}
    outside = {**base, "Li": base["Li"] + 1.1 * TAU, "O": base["O"] - 1.1 * TAU}
    assert TAU == 1e-6
    assert compositions_equal(base, inside)
    assert not compositions_equal(base, outside)
    assert not compositions_equal(base, {**base, "Na": 0.0})


@pytest.mark.parametrize(
    ("raw", "reason"),
    [({"Fe": 0.0, "O": 1.0}, "non-positive"),
     ({"Fe": -1.0, "O": 1.0}, "non-positive"),
     ({"Fe": math.inf, "O": 1.0}, "non-finite"),
     ({"Fe": math.nan, "O": 1.0}, "non-finite"),
     ({"Fe": "2", "O": 1.0}, "non-numeric"),
     ({"Fe": True, "O": 1.0}, "non-numeric"),
     ({"Xx": 1.0}, "unknown element"),
     ({}, "no stored composition"),
     (None, "no stored composition")],
)
def test_invalid_stored_amounts_are_excluded_with_an_explanation(raw, reason):
    with pytest.raises(ValueError, match=reason):
        normalise_stored_composition(raw)

    index = index_from_rows([(1, "mp-1", "X", "X", raw)], (1, 1))
    assert index.materials == ()
    assert index.exclusions[0].material_id == 1
    assert reason in index.exclusions[0].reason


def test_smallest_gap_between_distinct_reference_compositions_is_far_above_tau(
    db_session,
):
    from app.services.material.search_service import build_composition_index

    index = build_composition_index(db_session, (0, None))
    assert len(index.materials) == 28
    assert index.exclusions == ()
    smallest = math.inf
    for group in index.by_element_set.values():
        for first, second in itertools.combinations(group, 2):
            gap = max(
                abs(first.fractions[s] - second.fractions[s])
                for s in first.fractions
            )
            if gap == 0.0:
                continue  # identical compositions: legitimate matches
            smallest = min(smallest, gap)
    assert smallest > 1000 * TAU


# M-3 -----------------------------------------------------------------------

def test_case_is_significant_and_the_interpretation_is_echoed(client):
    response = _search(client, "formula", "LiFePo4")
    assert response.status_code == 200
    data = response.json()
    assert data["interpretation"]["elements"] == ["Fe", "Li", "Po"]
    assert 5 not in _ids(response)
    assert data["total_matches"] == 0

    lowercase = _search(client, "formula", "lifepo4")
    assert lowercase.status_code == 422
    assert lowercase.json()["detail"]["code"] == "invalid_formula"


# M-4 -----------------------------------------------------------------------

def test_chemical_system_is_exact_and_contains_returns_supersets(client):
    exact = _search(client, "chemsys", "Li-Fe-P-O")
    assert _ids(exact) == [1, 2, 3, 4, 5]
    assert exact.json()["interpretation"]["elements"] == ["Fe", "Li", "O", "P"]

    supersets = _search(client, "contains", "Fe, Na", limit=100)
    assert _ids(supersets) == [6, 7, 8, 9, 10]
    assert _ids(_search(client, "chemsys", "Na-Fe")) == []


# M-5 -----------------------------------------------------------------------

def test_mp_id_is_exact(client):
    assert _ids(_search(client, "mp_id", "mp-19017")) == [5]
    assert _ids(_search(client, "mp_id", "mp-1901")) == []
    assert _search(client, "mp_id", "19017").status_code == 422


# M-6 -----------------------------------------------------------------------

@pytest.mark.parametrize(
    ("mode", "query", "code"),
    [("formula", "lifepo4", "invalid_formula"),
     ("formula", "Xx2O", "invalid_formula"),
     ("formula", "LiFe(PO4", "invalid_formula"),
     ("formula", "Fe2+", "invalid_formula"),
     ("formula", "2LiFePO4", "invalid_formula"),
     ("formula", "Fe1e3O", "invalid_formula"),
     ("formula", "Fe0O2", "zero_amount"),
     ("formula", "Li(PO4)0", "zero_amount"),
     ("formula", "Fe2O3.H2O", "hydrate_notation_not_supported"),
     ("formula", "Fe2O3·H2O", "hydrate_notation_not_supported"),
     ("formula", "Fe2O3*H2O", "hydrate_notation_not_supported"),
     ("formula", " ", "invalid_formula"),
     ("chemsys", "Li-Xx", "unknown_element"),
     ("chemsys", "li-fe", "unknown_element"),
     ("chemsys", "Li-Li", "duplicate_element"),
     ("contains", "", "invalid_element_list"),
     ("mp_id", "mp-abc", "invalid_mp_id")],
)
def test_invalid_input_is_explained_not_reported_as_no_results(
    client, mode, query, code,
):
    response = _search(client, mode, query)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == code
    assert detail["mode"] == mode
    assert detail["input"] == query
    assert detail["explanation"]


def test_invalid_input_is_never_corrected():
    with pytest.raises(SearchQueryError):
        parse_formula_query("Fe0O2")
    # Polonium stays polonium; nothing is reread as PO4.
    assert parse_formula_query("LiFePo4")["elements"] == ["Fe", "Li", "Po"]


# M-7 -----------------------------------------------------------------------

def test_zero_results_state_the_dataset_and_offer_labelled_suggestions(client):
    absent = _search(client, "formula", "Ti2C").json()
    assert absent["total_matches"] == 0
    assert absent["suggestions"] is None
    assert "28 materials" in absent["message"]
    assert "not in this dataset" in absent["message"]
    assert absent["dataset"]["dataset_total"] == 28
    assert absent["dataset"]["provenance_note"] == (
        "0 records carry release provenance; 28 curated records predate "
        "provenance tracking."
    )

    near = _search(client, "formula", "LiFe2P2O7").json()
    assert near["results"] == []
    assert near["suggestions"]["basis"] == "same_chemical_system"
    assert "not matches" in near["suggestions"]["explanation"]
    assert [item["material_id"] for item in near["suggestions"]["results"]] == [
        1, 2, 3, 4, 5,
    ]


# M-8 -----------------------------------------------------------------------

def test_paging_and_order_are_stable(client):
    full = _search(client, "contains", "O", limit=100).json()
    first = _search(client, "contains", "O", limit=5, offset=0).json()
    second = _search(client, "contains", "O", limit=5, offset=5).json()

    ids = [item["material_id"] for item in full["results"]]
    assert ids == sorted(ids)
    assert [item["material_id"] for item in first["results"]] == ids[:5]
    assert [item["material_id"] for item in second["results"]] == ids[5:10]
    for page in (first, second):
        assert page["total_matches"] == full["total_matches"] == len(ids)
        assert page["dataset_total"] == 28
        assert page["limit"] == 5
    assert second["offset"] == 5


# M-9 -----------------------------------------------------------------------

def test_every_curated_record_is_searchable_by_formula_and_mp_id(client):
    materials = client.get("/api/v1/materials", params={"limit": 100}).json()
    assert len(materials) == 28
    for material in materials:
        by_formula = _ids(_search(client, "formula", material["pretty_formula"]))
        assert material["id"] in by_formula, material
        assert _ids(_search(client, "mp_id", material["mp_id"])) == [material["id"]]


# Route approval conditions (2026-10-22): bounded input -------------------

def test_query_longer_than_100_characters_is_rejected_before_parsing(
    client, monkeypatch,
):
    from app.services.material import search_service

    def must_not_parse(*_args, **_kwargs):
        raise AssertionError("parsing ran for an over-long query")

    monkeypatch.setattr(search_service, "parse_formula_query", must_not_parse)
    monkeypatch.setattr(search_service, "parse_element_list", must_not_parse)

    for mode in ("formula", "mp_id", "chemsys", "contains"):
        response = _search(client, mode, "O" * 101)
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "query_too_long"
        assert "100 characters" in response.json()["detail"]["explanation"]


def test_query_of_exactly_100_characters_is_accepted(client):
    query = "LiFePO4" + " " * 93
    assert len(query) == 100
    response = _search(client, "formula", query)
    assert response.status_code == 200
    assert _ids(response) == [5]


def test_page_size_is_at_most_100(client):
    assert _search(client, "contains", "O", limit=100).status_code == 200
    assert _search(client, "contains", "O", limit=101).status_code == 422
    assert _search(client, "contains", "O", limit=0).status_code == 422


def test_service_rejects_an_out_of_range_page_size(db_session):
    from app.services.material.search_service import MaterialSearchService

    with pytest.raises(SearchQueryError) as error:
        MaterialSearchService(db_session).search(
            mode="contains", query="O", limit=101, offset=0,
        )
    assert error.value.code == "invalid_limit"
