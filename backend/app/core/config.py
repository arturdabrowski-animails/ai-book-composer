from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # App
    APP_NAME: str = "Book Composer"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/bookcomposer"

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://aibookcomposer-frontend.onrender.com"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
