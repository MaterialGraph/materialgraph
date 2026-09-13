from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def build_engine_options(database_url: str) -> dict:
    options: dict = {"pool_pre_ping": True}
    if database_url.startswith(("postgresql://", "postgresql+psycopg://")):
        options["pool_timeout"] = settings.database_pool_timeout_seconds
        options["connect_args"] = {
            "connect_timeout": settings.database_pool_timeout_seconds,
        }
    return options


def apply_postgresql_transaction_timeouts(connection) -> None:
    connection.exec_driver_sql(
        f"SET LOCAL lock_timeout = '{settings.database_lock_timeout_ms}ms'"
    )
    connection.exec_driver_sql(
        "SET LOCAL statement_timeout = "
        f"'{settings.database_statement_timeout_ms}ms'"
    )


engine = create_engine(
    settings.database_url,
    **build_engine_options(settings.database_url),
)
if engine.dialect.name == "postgresql":
    event.listen(engine, "begin", apply_postgresql_transaction_timeouts)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
