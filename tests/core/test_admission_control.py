import asyncio
import re
from pathlib import Path

import pytest
from fastapi.routing import APIRoute
from pydantic import ValidationError

from app.core.admission_control import (
    AdmissionGate,
    ExpensiveRequestAdmissionMiddleware,
    is_expensive_request,
)
from app.core.config import Settings
from app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[2]

_EXPENSIVE_ROUTE_POLICY = frozenset(
    {
        ("POST", "/api/v1/comparison/materials"),
        ("POST", "/api/v1/scenarios/rank"),
        ("POST", "/api/v1/screening/candidates"),
        ("POST", "/api/v1/sensitivity/material"),
        ("POST", "/api/v1/substitutions/analyze"),
        ("GET", "/api/v1/materials/{material_id}/criticality"),
        ("GET", "/api/v1/materials/{material_id}/discovery/candidates"),
        ("GET", "/api/v1/materials/{material_id}/discovery/chains"),
        ("POST", "/api/v1/materials/{material_id}/discovery/objective/chains"),
        ("GET", "/api/v1/materials/{material_id}/discovery/graph"),
        ("GET", "/api/v1/materials/{material_id}/discovery/subgraph"),
        ("GET", "/api/v1/materials/{material_id}/discovery/path"),
        (
            "GET",
            "/api/v1/materials/{material_id}/discovery/communities/connected",
        ),
        (
            "GET",
            "/api/v1/materials/{material_id}/discovery/communities/modularity",
        ),
        ("POST", "/api/v1/materials/{material_id}/discovery/objective/explore"),
        ("GET", "/api/v1/materials/{material_id}/neighborhood"),
        ("GET", "/api/v1/materials/{material_id}/neighbors"),
        ("GET", "/api/v1/materials/{material_id}/recommendations"),
        ("GET", "/api/v1/materials/{material_id}/recommendations/scenario"),
        ("POST", "/api/v1/materials/{material_id}/research/scientific-pathways"),
        ("GET", "/api/v1/materials/{material_id}/similar"),
    }
)

_ORDINARY_ROUTE_POLICY = frozenset(
    {
        ("GET", "/health"),
        ("GET", "/api/v1/applications"),
        ("GET", "/api/v1/applications/{application_id}"),
        ("GET", "/api/v1/elements"),
        ("GET", "/api/v1/elements/{element_id}"),
        ("GET", "/api/v1/health"),
        ("GET", "/api/v1/material-risks/{material_id}"),
        ("GET", "/api/v1/materials"),
        ("GET", "/api/v1/materials/{material_id}"),
        ("GET", "/api/v1/materials/{material_id}/detail"),
        ("GET", "/api/v1/materials/{material_id}/families"),
        ("GET", "/api/v1/risks/elements"),
        ("GET", "/api/v1/risks/elements/{risk_profile_id}"),
    }
)


def _scope(path: str, scope_type: str = "http") -> dict:
    return {"type": scope_type, "path": path, "method": "GET"}


def _concrete_path(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "1", path)


def _mounted_route_policy() -> frozenset[tuple[str, str]]:
    return frozenset(
        (method, route.path)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in route.methods
    )


def _nginx_expensive_patterns() -> tuple[re.Pattern[str], ...]:
    nginx = (PROJECT_ROOT / "materialgraph.nginx").read_text(encoding="utf-8")
    return tuple(
        re.compile(line.strip().removeprefix("location ~ ").removesuffix(" {"))
        for line in nginx.splitlines()
        if line.strip().startswith("location ~ ")
    )


def test_classifies_public_expensive_routes():
    assert all(
        is_expensive_request(_scope(_concrete_path(path)))
        for _, path in _EXPENSIVE_ROUTE_POLICY
    )


@pytest.mark.parametrize("material_id", ["+5", "-1", "not-an-integer"])
def test_material_identifier_spelling_cannot_bypass_expensive_class(material_id):
    path = f"/api/v1/materials/{material_id}/recommendations"

    assert is_expensive_request(_scope(path))
    assert any(pattern.search(path) for pattern in _nginx_expensive_patterns())


def test_every_mounted_route_has_an_independent_cost_policy():
    assert _mounted_route_policy() == (
        _EXPENSIVE_ROUTE_POLICY | _ORDINARY_ROUTE_POLICY
    )


def test_nginx_and_application_expensive_route_policies_match():
    nginx_patterns = _nginx_expensive_patterns()

    for _, route_path in _EXPENSIVE_ROUTE_POLICY | _ORDINARY_ROUTE_POLICY:
        path = _concrete_path(route_path)
        proxy_classifies_expensive = any(
            pattern.search(path) for pattern in nginx_patterns
        )
        assert proxy_classifies_expensive == is_expensive_request(_scope(path)), path


def test_health_and_ordinary_reads_are_not_expensive():
    assert not any(
        is_expensive_request(_scope(_concrete_path(path)))
        for _, path in _ORDINARY_ROUTE_POLICY
    )
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


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/screening/candidates",
        "/api/v1/materials/5/neighbors",
        "/api/v1/materials/5/similar",
        "/api/v1/materials/5/neighborhood",
        "/api/v1/materials/5/criticality",
        "/api/v1/materials/5/recommendations",
        "/api/v1/materials/5/recommendations/scenario",
    ],
)
def test_middleware_returns_structured_overload_response(path):
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
            _scope(path),
            receive,
            send,
        )

        assert not downstream_called
        assert messages[0]["status"] == 503
        assert (b"retry-after", b"1") in messages[0]["headers"]
        assert b"expensive_request_capacity_exceeded" in messages[1]["body"]

        await middleware.gate.release()

    asyncio.run(exercise_middleware())
