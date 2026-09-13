from app.core.config import settings
from app.core.database import build_engine_options, get_db
from app.core.database_timeout import is_database_operation_timeout


def test_postgresql_engine_has_bounded_waits():
    options = build_engine_options("postgresql+psycopg://example.invalid/test")

    assert options["pool_pre_ping"] is True
    assert options["pool_timeout"] == settings.database_pool_timeout_seconds
    assert options["connect_args"]["connect_timeout"] == 3
    assert "lock_timeout=3000" in options["connect_args"]["options"]
    assert "statement_timeout=15000" in options["connect_args"]["options"]


def test_non_postgresql_engine_does_not_receive_postgresql_options():
    options = build_engine_options("sqlite:///test.db")

    assert "connect_args" not in options
    assert "pool_timeout" not in options


def test_database_dependency_rolls_back_and_closes_after_failure(monkeypatch):
    events = []

    class FakeSession:
        def rollback(self):
            events.append("rollback")

        def close(self):
            events.append("close")

    monkeypatch.setattr("app.core.database.SessionLocal", FakeSession)
    dependency = get_db()
    next(dependency)

    try:
        dependency.throw(RuntimeError("query timed out"))
    except RuntimeError:
        pass

    assert events == ["rollback", "close"]


def test_postgresql_cancellation_and_lock_timeout_are_classified():
    class OriginalError(Exception):
        def __init__(self, sqlstate):
            self.sqlstate = sqlstate

    from sqlalchemy.exc import DBAPIError

    for sqlstate in ("57014", "55P03"):
        error = DBAPIError("statement", {}, OriginalError(sqlstate), False)
        assert is_database_operation_timeout(error)

    error = DBAPIError("statement", {}, OriginalError("23505"), False)
    assert not is_database_operation_timeout(error)
