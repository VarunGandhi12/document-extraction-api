"""Runtime configuration via environment variables.

All tunables live here as a single typed object. Twelve-factor: config comes
from the environment, never hard-coded, never committed.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DOCEXTRACT_", env_file=".env")

    app_name: str = "document-extraction-api"
    version: str = "0.1.0"
    log_level: str = "INFO"

    #: Reject uploads larger than this (bytes). Default 10 MiB.
    max_upload_bytes: int = 10 * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
