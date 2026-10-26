from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Single .env at the repo root, shared with the frontend
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """App settings loaded from environment variables / the root .env."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    cors_origins: str = "http://localhost:5173"

    snowflake_account: str = ""
    snowflake_user: str = ""
    snowflake_password: str = ""
    snowflake_role: str = ""
    snowflake_warehouse: str = ""
    snowflake_database: str = ""
    snowflake_schema: str = ""

    cortex_model: str = "llama3.1-70b"

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def snowflake_configured(self) -> bool:
        return bool(self.snowflake_account and self.snowflake_user)


@lru_cache
def get_settings() -> Settings:
    return Settings()
