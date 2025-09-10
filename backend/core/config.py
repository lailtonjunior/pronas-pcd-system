"""
Core Configuration - Environment-based Settings
Segurança: Todas as configurações via variáveis de ambiente
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment-based configuration"""
    
    # Application
    APP_NAME: str = "Sistema PRONAS/PCD"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://pronas_user:pronas_password@localhost:5432/pronas_pcd_db"
    )
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    
    # Redis Cache
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL_SHORT: int = int(os.getenv("CACHE_TTL_SHORT", "300"))     # 5 minutes
    CACHE_TTL_MEDIUM: int = int(os.getenv("CACHE_TTL_MEDIUM", "1800"))  # 30 minutes  
    CACHE_TTL_LONG: int = int(os.getenv("CACHE_TTL_LONG", "7200"))      # 2 hours
    
    # Security & JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    PASSWORD_RESET_EXPIRE_MINUTES: int = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "15"))
    
    # CORS & Security
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    ALLOWED_HOSTS: List[str] = os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "200"))
    
    # File Upload
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    ALLOWED_FILE_EXTENSIONS: List[str] = os.getenv(
        "ALLOWED_FILE_EXTENSIONS",
        "pdf,doc,docx,xls,xlsx,jpg,jpeg,png,zip"
    ).split(",")
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "uploads")
    
    # Storage (MinIO/S3)
    STORAGE_ENDPOINT: str = os.getenv("STORAGE_ENDPOINT", "localhost:9000")
    STORAGE_ACCESS_KEY: str = os.getenv("STORAGE_ACCESS_KEY", "minioadmin")
    STORAGE_SECRET_KEY: str = os.getenv("STORAGE_SECRET_KEY", "minioadmin")
    STORAGE_BUCKET: str = os.getenv("STORAGE_BUCKET", "pronas-pcd-files")
    STORAGE_SECURE: bool = os.getenv("STORAGE_SECURE", "false").lower() == "true"
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@pronas-pcd.org")
    
    # AI Configuration
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "true").lower() == "true"
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4-turbo-preview")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.75"))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "3"))
    
    # PRONAS/PCD Business Rules
    SUBMISSION_PERIOD_DAYS: int = int(os.getenv("SUBMISSION_PERIOD_DAYS", "45"))
    MAX_PROJECTS_PER_INSTITUTION: int = int(os.getenv("MAX_PROJECTS_PER_INSTITUTION", "3"))
    MIN_CAPTACAO_PERCENTAGE: float = float(os.getenv("MIN_CAPTACAO_PERCENTAGE", "0.6"))
    MAX_CAPTACAO_PERCENTAGE: float = float(os.getenv("MAX_CAPTACAO_PERCENTAGE", "1.2"))
    MAX_CAPTACAO_ABSOLUTE: int = int(os.getenv("MAX_CAPTACAO_ABSOLUTE", "50000"))
    CREDENTIALING_MONTHS: List[int] = [
        int(month) for month in os.getenv("CREDENTIALING_MONTHS", "6,7").split(",")
    ]
    MIN_PROJECT_TIMELINE_MONTHS: int = int(os.getenv("MIN_PROJECT_TIMELINE_MONTHS", "6"))
    MAX_PROJECT_TIMELINE_MONTHS: int = int(os.getenv("MAX_PROJECT_TIMELINE_MONTHS", "48"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/pronas_pcd.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Monitoring
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    
    # External APIs
    VIACEP_API_URL: str = os.getenv("VIACEP_API_URL", "https://viacep.com.br/ws")
    RECEITAWS_API_URL: str = os.getenv("RECEITAWS_API_URL", "https://www.receitaws.com.br/v1")
    API_TIMEOUT_SECONDS: int = int(os.getenv("API_TIMEOUT_SECONDS", "30"))
    
    # Default User Credentials (ONLY FOR DEVELOPMENT)
    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "PronasPCD@2024")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@pronas-pcd.org")
    
    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v.startswith(("postgresql://", "mysql://", "sqlite:///")):
            raise ValueError("DATABASE_URL must be a valid database URL")
        return v
    
    @validator("ALLOWED_ORIGINS")
    def validate_origins(cls, v):
        return [origin.strip() for origin in v if origin.strip()]
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_config(self) -> dict:
        """Database configuration for SQLAlchemy"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "echo": self.DATABASE_ECHO and self.is_development,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()
