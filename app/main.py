from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import DBAPIError, TimeoutError as SQLAlchemyTimeoutError

from app.api.v1.api import api_router
from app.core.admission_control import ExpensiveRequestAdmissionMiddleware
from app.core.config import settings
from app.core.database_timeout import (
    database_operation_timeout_handler,
    database_pool_timeout_handler,
)
from app.core.logging import logger
from app.core.request_deadline import ExpensiveRequestDeadlineMiddleware
from app.version import PROJECT_VERSION


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("MaterialGraph starting up")
    logger.info("Environment: {}", settings.environment)

    yield

    logger.info("MaterialGraph shutting down")


app = FastAPI(
    title=settings.project_name,
    version=PROJECT_VERSION,
    description="Graph-based material intelligence platform",
    lifespan=lifespan,
)

app.add_middleware(
    ExpensiveRequestDeadlineMiddleware,
    timeout_seconds=settings.expensive_request_timeout_seconds,
)
app.add_middleware(
    ExpensiveRequestAdmissionMiddleware,
    max_concurrency=settings.expensive_request_concurrency,
)
app.add_exception_handler(SQLAlchemyTimeoutError, database_pool_timeout_handler)
app.add_exception_handler(DBAPIError, database_operation_timeout_handler)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.project_name,
        "version": PROJECT_VERSION,
        "environment": settings.environment,
    }
