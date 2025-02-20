from functools import lru_cache
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(str, Enum):
    DEV = "development"
    PROD = "production"
    TEST = "test"

class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    environment: Environment = Environment.DEV
    database_url: str
    sync_database_url: str
    secret_key: str


@lru_cache()
def get_settings() -> Settings:
    return Settings()
