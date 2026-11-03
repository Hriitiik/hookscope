from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HOOKSCOPE_", env_file=".env", extra="ignore"
    )

    env: str = "dev"
    max_body_bytes: int = 1_048_576


@lru_cache
def get_settings() -> Settings:
    return Settings()
