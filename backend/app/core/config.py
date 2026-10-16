from typing import List, Optional
import os
try:
    from pydantic import BaseSettings, Field
except ImportError:
    try:
        from pydantic_settings import BaseSettings
        from pydantic import Field
    except ImportError:
        from pydantic.v1 import BaseSettings, Field

class Settings(BaseSettings):
    APP_NAME: str = "Sential Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sential-super-secure-production-ready-secret-key-32-chars-min")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    INITIAL_SUPER_ADMIN_EMAIL: str = os.getenv("INITIAL_SUPER_ADMIN_EMAIL", "superadmin@sential.io")
    INITIAL_SUPER_ADMIN_PASSWORD: Optional[str] = os.getenv("INITIAL_SUPER_ADMIN_PASSWORD", None)

    # Primary Database: MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "sential_db")
    
    # Dedicated Relationship Graph Database: Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "sential_neo4j_secret")
    NEO4J_MAX_CONNECTION_LIFETIME: int = int(os.getenv("NEO4J_MAX_CONNECTION_LIFETIME", "300"))
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = int(os.getenv("NEO4J_MAX_CONNECTION_POOL_SIZE", "50"))
    NEO4J_CONNECTION_TIMEOUT: float = float(os.getenv("NEO4J_CONNECTION_TIMEOUT", "5.0"))
    
    # Redis Cache & Background Jobs
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Search Engine Limits & Timeouts
    SEARCH_JOB_TIMEOUT_SECONDS: int = int(os.getenv("SEARCH_JOB_TIMEOUT_SECONDS", "60"))
    PROVIDER_TIMEOUT_SECONDS: int = int(os.getenv("PROVIDER_TIMEOUT_SECONDS", "10"))
    MAX_CONCURRENT_MODULES: int = 10
    
    # OSINT & Social Extraction Limits (Phase 4 Specification)
    MAX_PROFILES_PER_INVESTIGATION: int = int(os.getenv("MAX_PROFILES_PER_INVESTIGATION", "100"))
    MAX_POSTS_PER_PROFILE: int = int(os.getenv("MAX_POSTS_PER_PROFILE", "50"))
    MAX_PAGINATION_DEPTH: int = int(os.getenv("MAX_PAGINATION_DEPTH", "5"))
    MAX_COMMENTS_PER_CONTENT: int = int(os.getenv("MAX_COMMENTS_PER_CONTENT", "20"))
    MAX_CONCURRENT_EXTRACTION_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_EXTRACTION_REQUESTS", "10"))
    COLLECTION_TIMEOUT_SECONDS: int = int(os.getenv("COLLECTION_TIMEOUT_SECONDS", "45"))
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS: int = int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS", "60"))
    ENABLE_HISTORICAL_SNAPSHOTS: bool = os.getenv("ENABLE_HISTORICAL_SNAPSHOTS", "true").lower() == "true"
    SNAPSHOT_RETENTION_DAYS: int = int(os.getenv("SNAPSHOT_RETENTION_DAYS", "90"))
    FAIL_CLOSED_REGIONAL_ROUTING: bool = os.getenv("FAIL_CLOSED_REGIONAL_ROUTING", "true").lower() == "true"

    # External ML Microservice (Operated independently by ML Team)
    ML_SERVICE_URL: Optional[str] = os.getenv("ML_SERVICE_URL", None)
    ML_SERVICE_API_KEY: Optional[str] = os.getenv("ML_SERVICE_API_KEY", None)
    ML_SERVICE_TIMEOUT_SECONDS: int = int(os.getenv("ML_SERVICE_TIMEOUT_SECONDS", "30"))

    # Dynamic Application Security Testing (DAST) - OWASP ZAP
    ZAP_API_URL: str = os.getenv("ZAP_API_URL") or os.getenv("ZAP_API_ENDPOINT") or "http://172.17.0.1:8090"
    ZAP_API_KEY: str = os.getenv("ZAP_API_KEY", "changeme")
    
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

    def validate_production_configuration(self) -> None:
        """
        Validates critical security configuration before production execution.
        Fails fast if production secrets or required bootstrap parameters are missing,
        weak, or default placeholders.
        """
        known_weak_secrets = {
            "sential-super-secure-production-ready-secret-key-32-chars-min",
            "sential-production-ultra-secure-jwt-key-256-bit-signature",
            "change-me",
            "changeme",
            "secret",
            "default",
        }
        known_weak_passwords = {
            "SuperAdmin123!",
            "password",
            "admin",
            "changeme",
            "12345678",
        }

        if self.APP_ENV.lower() in ["production", "prod"]:
            # 1. Validate SECRET_KEY
            lowered_secret = (self.SECRET_KEY or "").strip().lower()
            if (
                not self.SECRET_KEY
                or self.SECRET_KEY.strip() in known_weak_secrets
                or len(self.SECRET_KEY.strip()) < 32
                or "changeme" in lowered_secret
                or "changethis" in lowered_secret
                or "placeholder" in lowered_secret
            ):
                raise RuntimeError(
                    "Production startup failed: SECRET_KEY must be explicitly set to a high-entropy secret "
                    "(at least 32 characters) and cannot be a default placeholder or weak string."
                )

            # 2. Validate INITIAL_SUPER_ADMIN_PASSWORD if platform bootstrap is required
            if self.INITIAL_SUPER_ADMIN_PASSWORD:
                cleaned_pw = self.INITIAL_SUPER_ADMIN_PASSWORD.strip()
                if cleaned_pw in known_weak_passwords or len(cleaned_pw) < 12:
                    raise RuntimeError(
                        "Production startup failed: INITIAL_SUPER_ADMIN_PASSWORD cannot be a default or weak password (minimum 12 characters required)."
                    )

settings = Settings()
