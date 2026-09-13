from sqlalchemy.exc import DBAPIError, TimeoutError as SQLAlchemyTimeoutError
from starlette.responses import JSONResponse

from app.core.logging import logger


_POSTGRESQL_TIMEOUT_STATES = frozenset({"55P03", "57014"})


def is_database_operation_timeout(error: DBAPIError) -> bool:
    original = error.orig
    return getattr(original, "sqlstate", None) in _POSTGRESQL_TIMEOUT_STATES


async def database_pool_timeout_handler(request, error: SQLAlchemyTimeoutError):
    logger.warning("database_request_rejected outcome=pool_timeout")
    return JSONResponse(
        status_code=503,
        content={
            "detail": {
                "code": "database_capacity_timeout",
                "message": "Database capacity is temporarily unavailable.",
            }
        },
        headers={"Retry-After": "1"},
    )


async def database_operation_timeout_handler(request, error: DBAPIError):
    if not is_database_operation_timeout(error):
        raise error

    logger.warning("database_request_timed_out outcome=database_deadline_exceeded")
    return JSONResponse(
        status_code=504,
        content={
            "detail": {
                "code": "database_operation_timeout",
                "message": "The database operation exceeded its execution deadline.",
            }
        },
    )
