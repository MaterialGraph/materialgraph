import asyncio
import re

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.logging import logger


_EXPENSIVE_EXACT_PATHS = frozenset(
    {
        "/api/v1/comparison/materials",
        "/api/v1/scenarios/rank",
        "/api/v1/screening/candidates",
        "/api/v1/sensitivity/material",
        "/api/v1/substitutions/analyze",
    }
)
_EXPENSIVE_MATERIAL_PATH = re.compile(
    r"^/api/v1/materials/[0-9]+/(?:discovery|research)(?:/|$)"
)


def is_expensive_request(scope: Scope) -> bool:
    if scope.get("type") != "http":
        return False

    path = scope.get("path", "")
    return path in _EXPENSIVE_EXACT_PATHS or bool(
        _EXPENSIVE_MATERIAL_PATH.match(path)
    )


class AdmissionGate:
    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("capacity must be at least one")
        self.capacity = capacity
        self._active = 0
        self._lock = asyncio.Lock()

    async def try_acquire(self) -> bool:
        async with self._lock:
            if self._active >= self.capacity:
                return False
            self._active += 1
            return True

    async def release(self) -> None:
        async with self._lock:
            if self._active < 1:
                raise RuntimeError("admission gate released without acquisition")
            self._active -= 1


class ExpensiveRequestAdmissionMiddleware:
    def __init__(self, app: ASGIApp, max_concurrency: int):
        self.app = app
        self.gate = AdmissionGate(max_concurrency)

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if not is_expensive_request(scope):
            await self.app(scope, receive, send)
            return

        if not await self.gate.try_acquire():
            logger.warning(
                "expensive_request_rejected outcome=capacity_exceeded "
                "route_class=expensive method={} capacity={}",
                scope.get("method", ""),
                self.gate.capacity,
            )
            response = JSONResponse(
                status_code=503,
                content={
                    "detail": {
                        "code": "expensive_request_capacity_exceeded",
                        "message": "Expensive request capacity is currently full.",
                    }
                },
                headers={"Retry-After": "1"},
            )
            await response(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        finally:
            await self.gate.release()
