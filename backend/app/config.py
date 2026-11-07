from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"

    SECRET_KEY: str = "dev-secret-key-for-local-msaidizi-1234567890-abcdefghijklmnopqrstuvwxyz"
    JWT_SECRET_KEY: str = "dev-jwt-secret-for-local-msaidizi-1234567890-abcdefghijklmnopqrstuvwxyz"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=12)

    DATABASE_URL: str = "postgresql+psycopg2://msaidizi:msaidizi@localhost:5432/msaidizi"

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


settings = Settings()
