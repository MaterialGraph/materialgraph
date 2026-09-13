from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def build_engine_options(database_url: str) -> dict:
    options: dict = {"pool_pre_ping": True}
    if database_url.startswith(("postgresql://", "postgresql+psycopg://")):
        options["pool_timeout"] = settings.database_pool_timeout_seconds
        options["connect_args"] = {
            "connect_timeout": settings.database_pool_timeout_seconds,
            "options": (
                f"-c lock_timeout={settings.database_lock_timeout_ms} "
                f"-c statement_timeout={settings.database_statement_timeout_ms}"
            ),
        }
    return options


engine = create_engine(
    settings.database_url,
    **build_engine_options(settings.database_url),
)

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
