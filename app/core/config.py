from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/job_hunting_assistant"
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg2://postgres:password@localhost:5432/job_hunting_assistant"
    )
    backend_base_url: str = Field(default="http://localhost:8000")
    scraper_webhook_linkedin: str | None = None
    scraper_webhook_indeed: str | None = None
    scraper_webhook_glassdoor: str | None = None
    anthropic_api_key: str = ""
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_refresh_token: str = ""


settings = Settings()
