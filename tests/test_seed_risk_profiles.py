from types import SimpleNamespace

import pytest

from scripts.seed_core_data import ELEMENTS
from scripts.seed_risk_profiles import (
    RISK_DATA,
    SCORE_FIELDS,
    SOURCE,
    YEAR,
    seed_risk_profiles,
    validate_risk_data,
)


class FakeQuery:
    def __init__(self, db, model):
        self.db = db
        self.model = model

    def filter(self, *conditions):
        return self

    def first(self):
        if self.model.__name__ == "Element":
            element = self.db.elements[self.db.element_query_index]
            self.db.element_query_index += 1
            self.db.current_element_id = element.id
            return element

        return self.db.profiles.get((self.db.current_element_id, YEAR))


class FakeDb:
    def __init__(self):
        self.elements = [
            SimpleNamespace(id=index, symbol=symbol)
            for index, symbol in enumerate(RISK_DATA, start=1)
        ]
        self.profiles = {}
        self.element_query_index = 0
        self.current_element_id = None

    def query(self, model):
        return FakeQuery(self, model)

    def add(self, profile):
        self.profiles[(profile.element_id, profile.year)] = profile

    def rewind(self):
        self.element_query_index = 0
        self.current_element_id = None


def test_canonical_risk_data_uses_declared_scale_and_metadata():
    validate_risk_data()

    core_symbols = {item["symbol"] for item in ELEMENTS}
    assert set(RISK_DATA) == core_symbols
    assert SOURCE == "materialgraph_canonical_risk_profile_v1"
    assert YEAR == 2026

    for scores in RISK_DATA.values():
        assert set(scores) == set(SCORE_FIELDS)
        assert all(1 <= value <= 10 for value in scores.values())


def test_validation_rejects_out_of_range_value(monkeypatch):
    monkeypatch.setitem(RISK_DATA["Li"], "supply_risk_score", 0)

    with pytest.raises(ValueError, match="canonical 1-10 scale"):
        validate_risk_data()


def test_seed_is_deterministic_and_idempotent():
    db = FakeDb()

    assert seed_risk_profiles(db) == (len(RISK_DATA), 0)
    assert len(db.profiles) == len(RISK_DATA)

    first_profile = db.profiles[(1, YEAR)]
    first_profile.supply_risk_score = 0.5
    first_profile.source = "legacy_seed"

    db.rewind()
    assert seed_risk_profiles(db) == (0, len(RISK_DATA))
    assert len(db.profiles) == len(RISK_DATA)
    assert first_profile.supply_risk_score == RISK_DATA["Li"]["supply_risk_score"]
    assert first_profile.source == SOURCE