from datetime import timedelta
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        case_sensitive=True,
        extra="ignore",          # ← this is the important line
    )

    SECRET_KEY: str = "dev-secret-change-me"
    JWT_SECRET_KEY: str = "jwt-secret-change-me"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=24)

    DATABASE_URL: str = "postgresql://msaidizi:msaidizi@localhost:5432/msaidizi"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-2"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:3001,http://127.0.0.1:3001"
    EMBEDDING_DIM: int = 768
    WIDGET_ORIGIN: str = "*"


settings = Settings()
