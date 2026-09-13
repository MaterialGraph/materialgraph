import os
from collections.abc import Mapping

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def resolve_settings_env_file(
    environment: Mapping[str, str] = os.environ,
) -> str | None:
    configured_path = environment.get("MATERIALGRAPH_ENV_FILE")
    if configured_path == "":
        return None
    return configured_path or ".env"


class Settings(BaseSettings):
    project_name: str = "MaterialGraph"

    environment: str = "development"

    database_url: str

    materials_project_api_key: str | None = None

    log_level: str = "INFO"

    expensive_request_concurrency: int = Field(default=2, ge=1, le=32)
    expensive_request_timeout_seconds: int = Field(default=20, ge=1, le=120)
    database_pool_timeout_seconds: int = Field(default=3, ge=1, le=30)
    database_lock_timeout_ms: int = Field(default=3_000, ge=100, le=30_000)
    database_statement_timeout_ms: int = Field(default=15_000, ge=1_000, le=120_000)

    model_config = SettingsConfigDict(
        env_file=resolve_settings_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
