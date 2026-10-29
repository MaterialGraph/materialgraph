"""Unified material search (Release 2, F12): auto mode, local IDs, scoping."""

import pytest

from app.services.material import search_service
from app.services.material.search_service import (
    AUTO_HINT,
    CompositionIndex,
    detect_mode,
    index_from_rows,
)

SEARCH = "/api/v1/materials/search"
SUMMARY = "/api/v1/materials/dataset-summary"
RESPONSE_KEYS = {
    "interpretation", "dataset", "total_matches", "dataset_total", "limit",
    "offset", "results", "suggestions", "message",
}
ADDED_KEYS = {"requested_mode", "scoped_message", "suggestion_total"}


def _search(client, mode, q, **params):
    return client.get(SEARCH, params={"mode": mode, "q": q, **params})


def _ids(response):
    return [item["material_id"] for item in response.json()["results"]]


def _energy_by_id(client):
    materials = client.get("/api/v1/materials", params={"limit": 100}).json()
    return {item["id"]: item["energy_above_hull"] for item in materials}


def _empty_index(monkeypatch):
    """Exclude every material from the composition index."""
    empty = CompositionIndex(
        fingerprint=(0, None), materials=(), exclusions=(), by_element_set={},
    )
    monkeypatch.setattr(search_service._CACHE, "get", lambda db: empty)


# detect_mode ---------------------------------------------------------------

@pytest.mark.parametrize(
    ("query", "mode"),
    [("Co", "formula"),
     ("CO", "formula"),
     ("co", "formula"),
     ("Fe", "formula"),
     ("LiFePO4", "formula"),
     ("FePO4Li", "formula"),
     ("Li-Fe-P-O", "chemsys"),
     ("li-fe", "chemsys"),
     ("Li-", "formula"),
     ("5", "material_id"),
     ("#5", "material_id"),
     ("0", "material_id"),
     ("mp-19017", "mp_id"),
     ("MP-19017", "mp_id"),
     ("mp-", "mp_id"),
     ("Li,Fe", "formula"),
     ("Li Fe", "formula"),
     ("LiFePO4·H2O", "formula"),
     # ARABIC-INDIC DIGIT FIVE: only ASCII digits are a local ID.
     ("٥", "formula")],
)
def test_detect_mode(query, mode):
    assert detect_mode(query) == mode


# Auto resolves to a concrete mode ------------------------------------------

@pytest.mark.parametrize(
    ("query", "mode", "ids"),
    [("LiFePO4", "formula", [5]),
     ("mp-19017", "mp_id", [5]),
     ("Li-Fe-P-O", "chemsys", [1, 2, 3, 4, 5]),
     ("5", "material_id", [5]),
     ("#5", "material_id", [5]),
     ("  #5  ", "material_id", [5])],
)
def test_auto_reports_the_concrete_mode_and_runs_its_branch(
    client, query, mode, ids,
):
    auto = _search(client, "auto", query)
    explicit = _search(client, mode, query)

    assert auto.status_code == explicit.status_code == 200
    body = auto.json()
    assert body["interpretation"]["mode"] == mode
    assert body["requested_mode"] == "auto"
    assert _ids(auto) == ids
    # The same branch ran: only the echoed request mode differs.
    assert {**body, "requested_mode": mode} == explicit.json()


def test_interpretation_mode_is_never_auto(client):
    for query in ("Co", "li-fe-x", "Ti2C", "7", "mp-1", "Na-Fe"):
        response = _search(client, "auto", query)
        if response.status_code == 200:
            assert response.json()["interpretation"]["mode"] != "auto"
        else:
            assert response.json()["detail"]["mode"] != "auto"


# No fallback between modes --------------------------------------------------

@pytest.mark.parametrize(
    ("mode", "query", "code"),
    [("formula", "mp-19017", "invalid_formula"),
     ("formula", "5", "invalid_formula"),
     ("formula", "#5", "invalid_formula"),
     ("mp_id", "5", "invalid_mp_id"),
     ("mp_id", "LiFePO4", "invalid_mp_id"),
     ("mp_id", "MP-19017", "invalid_mp_id"),
     ("chemsys", "LiFePO4", "unknown_element"),
     ("chemsys", "5", "unknown_element"),
     ("contains", "mp-19017", "unknown_element"),
     ("contains", "#5", "unknown_element"),
     ("material_id", "mp-19017", "invalid_material_id"),
     ("material_id", "LiFePO4", "invalid_material_id"),
     ("material_id", "Li-Fe-P-O", "invalid_material_id")],
)
def test_explicit_mode_returns_its_own_error_without_fallback(
    client, mode, query, code,
):
    response = _search(client, mode, query)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == code
    assert detail["mode"] == mode
    assert detail["requested_mode"] == mode
    assert detail["hint"] is None


# material_id ---------------------------------------------------------------

@pytest.mark.parametrize("mode", ["material_id", "auto"])
@pytest.mark.parametrize("query", ["5", "#5"])
def test_local_id_resolves(client, mode, query):
    body = _search(client, mode, query).json()
    assert [item["material_id"] for item in body["results"]] == [5]
    assert body["results"][0]["mp_id"] == "mp-19017"
    assert body["interpretation"]["material_id"] == 5
    assert body["interpretation"]["mode"] == "material_id"


@pytest.mark.parametrize(
    ("mode", "query"),
    [("material_id", "0"),
     ("auto", "0"),
     ("material_id", "2147483648"),
     ("auto", "2147483648"),
     ("material_id", "#"),
     ("material_id", "#0"),
     ("material_id", "-5"),
     ("material_id", "٥")],
)
def test_invalid_local_id_is_explained(client, mode, query):
    response = _search(client, mode, query)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "invalid_material_id"
    assert detail["mode"] == "material_id"
    assert detail["input"] == query
    assert "2147483647" in detail["explanation"]


@pytest.mark.parametrize("query", ["999999", "#2147483647"])
def test_unknown_local_id_is_zero_matches(client, query):
    body = _search(client, "material_id", query).json()
    assert body["total_matches"] == 0
    assert body["results"] == []
    assert body["interpretation"]["material_id"] == int(query.lstrip("#"))
    assert "local ID" in body["scoped_message"]


def test_identity_modes_find_composition_excluded_materials(
    client, monkeypatch,
):
    energy = _energy_by_id(client)
    _empty_index(monkeypatch)

    for mode, query in (("material_id", "5"), ("mp_id", "mp-19017")):
        results = _search(client, mode, query).json()["results"]
        assert results == [{
            "material_id": 5, "mp_id": "mp-19017", "formula": "LiFePO4",
            "pretty_formula": "LiFePO4", "energy_above_hull": energy[5],
        }]
    assert _ids(_search(client, "formula", "LiFePO4")) == []


# energy_above_hull and suggestion_total -----------------------------------

@pytest.mark.parametrize(
    ("mode", "query"),
    [("formula", "LiFePO4"), ("chemsys", "Li-Fe-P-O"), ("contains", "O"),
     ("mp_id", "mp-19017"), ("material_id", "5")],
)
def test_results_carry_energy_above_hull(client, mode, query):
    energy = _energy_by_id(client)
    results = _search(client, mode, query, limit=100).json()["results"]
    assert results
    for item in results:
        assert item["energy_above_hull"] == energy[item["material_id"]]


def test_suggestions_carry_energy_above_hull_and_a_total(client):
    energy = _energy_by_id(client)
    body = _search(client, "formula", "LiFe2P2O7").json()
    suggestions = body["suggestions"]["results"]
    assert [item["material_id"] for item in suggestions] == [1, 2, 3, 4, 5]
    for item in suggestions:
        assert item["energy_above_hull"] == energy[item["material_id"]]
    assert body["suggestion_total"] == 5

    assert _search(client, "formula", "Ti2C").json()["suggestion_total"] is None
    assert _search(client, "formula", "LiFePO4").json()["suggestion_total"] is None


def test_suggestion_total_counts_before_the_cap(client, monkeypatch):
    rows = [
        (9000 + n, f"mp-{9000 + n}", f"Li{n}O", f"Li{n}O",
         {"Li": float(n), "O": 1.0}, 0.01 * n)
        for n in range(1, 13)
    ]
    index = index_from_rows(rows, (12, 9012))
    monkeypatch.setattr(search_service._CACHE, "get", lambda db: index)

    body = _search(client, "formula", "Li20O").json()
    assert body["total_matches"] == 0
    assert len(body["suggestions"]["results"]) == 10
    assert body["suggestion_total"] == 12
    assert body["suggestions"]["results"][0]["energy_above_hull"] == 0.01


# scoped_message -------------------------------------------------------------

_ZERO_MATCHES = [
    ("formula", "Ti2C", "No material with reduced formula Ti2C"),
    ("chemsys", "Na-Fe", "No material with exactly the elements {Fe, Na}"),
    ("contains", "Og", "No material containing all of {Og}"),
    ("mp_id", "mp-1901", "mp-1901 is not in this dataset"),
    ("material_id", "999999", "No material with local ID 999999"),
]


@pytest.mark.parametrize(
    ("requested", "mode", "query", "subject"),
    [(mode, mode, query, subject) for mode, query, subject in _ZERO_MATCHES]
    # contains is never detected, so it has no auto case.
    + [("auto", mode, query, subject)
       for mode, query, subject in _ZERO_MATCHES if mode != "contains"],
)
def test_every_zero_match_carries_a_scoped_message(
    client, requested, mode, query, subject,
):
    body = _search(client, requested, query).json()
    assert body["total_matches"] == 0
    assert body["interpretation"]["mode"] == mode
    scoped = body["scoped_message"]
    assert scoped.startswith(subject)
    assert "in this dataset" in scoped
    assert "28 materials" in scoped
    assert "release not recorded" in scoped
    assert "does not mean the material does not exist" in scoped
    # The existing message is unchanged.
    assert body["message"] == (
        "No match in this dataset (Materials Project (release not recorded "
        "in this database), 28 materials). The material is not in this "
        "dataset; this does not mean it does not exist."
    )


def test_matches_carry_no_scoped_message(client):
    body = _search(client, "auto", "LiFePO4").json()
    assert body["scoped_message"] is None
    assert body["message"] is None


# Explained errors -----------------------------------------------------------

@pytest.mark.parametrize(
    ("query", "mode", "code"),
    [("co", "formula", "invalid_formula"),
     ("Li-", "formula", "invalid_formula"),
     ("Li,Fe", "formula", "invalid_formula"),
     ("LiFePO4·H2O", "formula", "hydrate_notation_not_supported"),
     ("li-fe", "chemsys", "unknown_element"),
     ("mp-", "mp_id", "invalid_mp_id"),
     ("MP-19017", "mp_id", "invalid_mp_id"),
     ("0", "material_id", "invalid_material_id")],
)
def test_auto_errors_carry_the_resolved_mode_and_a_hint(
    client, query, mode, code,
):
    response = _search(client, "auto", query)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == code
    assert detail["mode"] == mode
    assert detail["requested_mode"] == "auto"
    assert detail["input"] == query
    assert detail["explanation"]
    assert detail["hint"] == AUTO_HINT


def test_query_too_long_under_auto_has_no_mode(client):
    detail = _search(client, "auto", "O" * 101).json()["detail"]
    assert detail["code"] == "query_too_long"
    assert detail["mode"] is None
    assert detail["requested_mode"] == "auto"
    assert detail["hint"] == AUTO_HINT

    explicit = _search(client, "formula", "O" * 101).json()["detail"]
    assert explicit["mode"] == explicit["requested_mode"] == "formula"
    assert explicit["hint"] is None


# Explicit modes are unchanged apart from the added fields ------------------

@pytest.mark.parametrize(
    ("mode", "query"),
    [("formula", "LiFePO4"), ("formula", "LiFe2P2O7"), ("mp_id", "mp-19017"),
     ("chemsys", "Li-Fe-P-O"), ("contains", "Na")],
)
def test_explicit_mode_responses_only_add_fields(client, mode, query):
    body = _search(client, mode, query).json()
    assert set(body) == RESPONSE_KEYS | ADDED_KEYS
    assert body["requested_mode"] == mode
    assert body["interpretation"]["mode"] == mode
    assert body["interpretation"]["material_id"] is None
    for item in body["results"]:
        assert set(item) == {
            "material_id", "mp_id", "formula", "pretty_formula",
            "energy_above_hull",
        }


# dataset-summary ------------------------------------------------------------

def test_dataset_summary_matches_the_search_dataset_block(client):
    response = client.get(SUMMARY)
    assert response.status_code == 200  # not captured by /{material_id}
    assert response.json() == _search(client, "auto", "Ti2C").json()["dataset"]
    assert response.json()["dataset_total"] == 28
