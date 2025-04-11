import os
import secrets
from typing import Any, Dict, Optional

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutos * 24 horas * 8 dias = 8 dias
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://visa-platform.example.com"]
    
    # Database settings - PostgreSQL
    DATABASE_URL: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    USE_SQLITE_FALLBACK: bool = False
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Auth integration with main backend
    AUTH_SERVICE_URL: str = "http://localhost:3001/api/auth/validate-token"
    
    # Service settings
    ENVIRONMENT: str = "dev"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 