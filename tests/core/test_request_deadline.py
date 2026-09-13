import asyncio

import pytest

from app.core.request_deadline import ExpensiveRequestDeadlineMiddleware


def _scope(path: str) -> dict:
    return {"type": "http", "path": path, "method": "POST"}


async def _receive():
    return {"type": "http.request", "body": b"", "more_body": False}


def test_expensive_request_timeout_is_structured_and_recovers():
    async def exercise() -> None:
        delay = 0.03

        async def downstream(scope, receive, send):
            await asyncio.sleep(delay)
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b'{}'})

        middleware = ExpensiveRequestDeadlineMiddleware(downstream, timeout_seconds=0.01)

        for _ in range(2):
            messages = []

            async def send(message):
                messages.append(message)

            await middleware(
                _scope("/api/v1/screening/candidates"),
                _receive,
                send,
            )

            assert messages[0]["status"] == 504
            assert b"expensive_request_deadline_exceeded" in messages[1]["body"]

        delay = 0
        messages = []

        async def send(message):
            messages.append(message)

        await middleware(
            _scope("/api/v1/screening/candidates"),
            _receive,
            send,
        )
        assert messages[0]["status"] == 200

    asyncio.run(exercise())


def test_ordinary_request_is_not_subject_to_expensive_deadline():
    async def exercise() -> None:
        called = False

        async def downstream(scope, receive, send):
            nonlocal called
            called = True

        middleware = ExpensiveRequestDeadlineMiddleware(downstream, timeout_seconds=1)
        await middleware(_scope("/health"), _receive, lambda message: None)
        assert called

    asyncio.run(exercise())


def test_deadline_rejects_invalid_timeout():
    with pytest.raises(ValueError, match="timeout_seconds must be positive"):
        ExpensiveRequestDeadlineMiddleware(lambda scope, receive, send: None, 0)
