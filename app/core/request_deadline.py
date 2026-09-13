import asyncio

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.admission_control import is_expensive_request
from app.core.logging import logger


class ExpensiveRequestDeadlineMiddleware:
    def __init__(self, app: ASGIApp, timeout_seconds: int):
        if timeout_seconds < 1:
            raise ValueError("timeout_seconds must be at least one")
        self.app = app
        self.timeout_seconds = timeout_seconds

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if not is_expensive_request(scope):
            await self.app(scope, receive, send)
            return

        response_started = False

        async def tracked_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            async with asyncio.timeout(self.timeout_seconds):
                await self.app(scope, receive, tracked_send)
        except TimeoutError:
            logger.warning(
                "expensive_request_timed_out outcome=deadline_exceeded "
                "route_class=expensive method={} timeout_seconds={}",
                scope.get("method", ""),
                self.timeout_seconds,
            )
            if response_started:
                return
            response = JSONResponse(
                status_code=504,
                content={
                    "detail": {
                        "code": "expensive_request_deadline_exceeded",
                        "message": "The scientific request exceeded its execution deadline.",
                    }
                },
            )
            await response(scope, receive, send)
