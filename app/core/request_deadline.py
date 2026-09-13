import asyncio

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.admission_control import is_expensive_request
from app.core.logging import logger


class ExpensiveRequestDeadlineMiddleware:
    def __init__(self, app: ASGIApp, timeout_seconds: float):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.app = app
        self.timeout_seconds = timeout_seconds
        self._abandoned_tasks: set[asyncio.Task] = set()

    def _complete_abandoned_task(self, task: asyncio.Task) -> None:
        self._abandoned_tasks.discard(task)
        try:
            task.result()
        except asyncio.CancelledError:
            return
        except Exception as error:
            logger.error(
                "abandoned_expensive_request_failed error_type={}",
                type(error).__name__,
            )

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
        deadline_exceeded = False

        async def tracked_send(message: Message) -> None:
            nonlocal response_started
            if deadline_exceeded:
                return
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        task = asyncio.create_task(self.app(scope, receive, tracked_send))
        done, _ = await asyncio.wait({task}, timeout=self.timeout_seconds)
        if done:
            await task
            return

        if response_started:
            await task
            return

        deadline_exceeded = True
        self._abandoned_tasks.add(task)
        task.add_done_callback(self._complete_abandoned_task)
        logger.warning(
            "expensive_request_timed_out outcome=deadline_exceeded "
            "route_class=expensive method={} timeout_seconds={}",
            scope.get("method", ""),
            self.timeout_seconds,
        )
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
