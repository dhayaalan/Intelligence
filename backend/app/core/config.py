from typing import List, Optional
import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    APP_NAME: str = "Sential Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sential-super-secure-production-ready-secret-key-32-chars-min")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Primary Database: MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "sential_db")
    
    # Redis Cache & Background Jobs
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Search Engine Limits & Timeouts
    SEARCH_JOB_TIMEOUT_SECONDS: int = int(os.getenv("SEARCH_JOB_TIMEOUT_SECONDS", "60"))
    PROVIDER_TIMEOUT_SECONDS: int = int(os.getenv("PROVIDER_TIMEOUT_SECONDS", "10"))
    MAX_CONCURRENT_MODULES: int = 10
    
    # External ML Microservice (Operated independently by ML Team)
    ML_SERVICE_URL: Optional[str] = os.getenv("ML_SERVICE_URL", None)
    ML_SERVICE_API_KEY: Optional[str] = os.getenv("ML_SERVICE_API_KEY", None)
    ML_SERVICE_TIMEOUT_SECONDS: int = int(os.getenv("ML_SERVICE_TIMEOUT_SECONDS", "30"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    class Config:
        case_sensitive = True

settings = Settings()
