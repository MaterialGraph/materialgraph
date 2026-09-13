import asyncio

import pytest
from pydantic import ValidationError

from app.core.admission_control import (
    AdmissionGate,
    ExpensiveRequestAdmissionMiddleware,
    is_expensive_request,
)
from app.core.config import Settings


def _scope(path: str, scope_type: str = "http") -> dict:
    return {"type": scope_type, "path": path, "method": "GET"}


def test_classifies_public_expensive_routes():
    paths = (
        "/api/v1/screening/candidates",
        "/api/v1/comparison/materials",
        "/api/v1/scenarios/rank",
        "/api/v1/sensitivity/material",
        "/api/v1/substitutions/analyze",
        "/api/v1/materials/5/discovery/candidates",
        "/api/v1/materials/5/discovery/objective/explore",
        "/api/v1/materials/5/research/scientific-pathways",
    )

    assert all(is_expensive_request(_scope(path)) for path in paths)


def test_health_and_ordinary_reads_are_not_expensive():
    paths = (
        "/health",
        "/api/v1/health",
        "/api/v1/materials/5",
        "/api/v1/elements",
    )

    assert not any(is_expensive_request(_scope(path)) for path in paths)
    assert not is_expensive_request(
        _scope("/api/v1/screening/candidates", "websocket")
    )


def test_gate_rejects_only_while_capacity_is_full():
    async def exercise_gate() -> None:
        gate = AdmissionGate(capacity=2)

        assert await gate.try_acquire()
        assert await gate.try_acquire()
        assert not await gate.try_acquire()

        await gate.release()
        assert await gate.try_acquire()

        await gate.release()
        await gate.release()

    asyncio.run(exercise_gate())


def test_gate_rejects_invalid_capacity():
    with pytest.raises(ValueError, match="capacity must be at least one"):
        AdmissionGate(capacity=0)


@pytest.mark.parametrize("capacity", [0, 33])
def test_settings_bound_expensive_request_concurrency(capacity):
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql://example.invalid/materialgraph_test",
            expensive_request_concurrency=capacity,
            _env_file=None,
        )


def test_middleware_returns_structured_overload_response():
    async def exercise_middleware() -> None:
        downstream_called = False

        async def downstream(scope, receive, send):
            nonlocal downstream_called
            downstream_called = True

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        messages = []

        async def send(message):
            messages.append(message)

        middleware = ExpensiveRequestAdmissionMiddleware(
            downstream,
            max_concurrency=1,
        )
        assert await middleware.gate.try_acquire()

        await middleware(
            _scope("/api/v1/screening/candidates"),
            receive,
            send,
        )

        assert not downstream_called
        assert messages[0]["status"] == 503
        assert (b"retry-after", b"1") in messages[0]["headers"]
        assert b"expensive_request_capacity_exceeded" in messages[1]["body"]

        await middleware.gate.release()

    asyncio.run(exercise_middleware())
