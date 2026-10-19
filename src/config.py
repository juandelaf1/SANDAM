from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sandam"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "*"

    aemet_api_key: str = ""
    socib_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        return origins or ["*"]

    @property
    def allow_credentials(self) -> bool:
        # Browsers reject "*" combined with credentials.
        return "*" not in self.cors_origin_list


@lru_cache()
def get_settings() -> Settings:
    return Settings()
