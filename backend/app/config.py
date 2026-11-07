import os
from datetime import timedelta
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Flask
    SECRET_KEY: str = "dev-secret-change-me"
    JWT_SECRET_KEY: str = "jwt-secret-change-me"
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(hours=24)

    # Database
    DATABASE_URL: str = "postgresql://msaidizi:msaidizi@localhost:5432/msaidizi"

    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # App
    WIDGET_ORIGIN: str = "*"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
