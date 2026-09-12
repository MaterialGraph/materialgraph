import os
from collections.abc import Mapping

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

    model_config = SettingsConfigDict(
        env_file=resolve_settings_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
