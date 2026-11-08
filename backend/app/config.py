import os
from datetime import timedelta

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://msaidizi:msaidizi@localhost:5433/msaidizi",
    )


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "development-only-change-this-secret"
    JWT_SECRET_KEY: str = "development-only-change-this-jwt-secret"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=12)
    DATABASE_URL: str = default_database_url()
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:5173,http://127.0.0.1:5173"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_configuration(self):
        app_env = (self.APP_ENV or "development").lower()

        if app_env == "production":
            if not self.SECRET_KEY or self.SECRET_KEY.startswith("development-only"):
                raise ValueError("Set a production SECRET_KEY.")
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production.")
            if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY.startswith("development-only"):
                raise ValueError("Set a production JWT_SECRET_KEY.")
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production.")

        return self


settings = Settings()
