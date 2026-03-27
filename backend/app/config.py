"""
Application configuration loaded from environment variables.

Owner: Owner 2 — Backend
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    roboflow_api_key: str = ""
    roboflow_model_url: str = ""
    roboflow_timeout: int = 30

    # Comma-separated list of allowed CORS origins
    cors_origins: str = "http://localhost:3000"

    app_version: str = "0.1.0"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
