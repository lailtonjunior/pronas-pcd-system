"""
Core Configuration - Environment-based Settings
Todas as configurações centralizadas e seguras
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, validator, Field
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with comprehensive environment-based configuration"""
    
    # Application Core
    APP_NAME: str = Field("Sistema PRONAS/PCD", description="Application name")
    APP_VERSION: str = Field("2.0.0", description="Application version")
    ENVIRONMENT: str = Field("production", description="Environment (development/staging/production)")
    DEBUG: bool = Field(False, description="Debug mode")
    
    # Server Configuration
    HOST: str = Field("0.0.0.0", description="Server host")
    PORT: int = Field(8000, description="Server port")
    RELOAD: bool = Field(False, description="Auto-reload on code changes")
    WORKERS: int = Field(4, description="Number of worker processes")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(40, description="Database max overflow connections")
    DATABASE_ECHO: bool = Field(False, description="Echo SQL queries")
    DATABASE_CONNECT_TIMEOUT: int = Field(30, description="Database connection timeout")
    DATABASE_COMMAND_TIMEOUT: int = Field(60, description="Database command timeout")
    
    # Redis Cache Configuration
    REDIS_URL: str = Field("redis://localhost:6379/0", description="Redis connection URL")
    CACHE_TTL_SHORT: int = Field(300, description="Short cache TTL (5 minutes)")
    CACHE_TTL_MEDIUM: int = Field(1800, description="Medium cache TTL (30 minutes)")
    CACHE_TTL_LONG: int = Field(7200, description="Long cache TTL (2 hours)")
    REDIS_MAX_CONNECTIONS: int = Field(100, description="Maximum Redis connections")
    
    # Security & Authentication
    JWT_SECRET_KEY: str = Field(..., description="JWT secret key")
    JWT_ALGORITHM: str = Field("HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(480, description="Access token expiry (8 hours)")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, description="Refresh token expiry")
    PASSWORD_RESET_EXPIRE_MINUTES: int = Field(15, description="Password reset token expiry")
    PASSWORD_MIN_LENGTH: int = Field(8, description="Minimum password length")
    
    # CORS & Security Headers
    ALLOWED_ORIGINS: List[str] = Field(
        ["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        ["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )
    SECURE_COOKIES: bool = Field(True, description="Use secure cookies")
    SAME_SITE_COOKIES: str = Field("strict", description="SameSite cookie policy")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(100, description="Rate limit per minute")
    RATE_LIMIT_BURST: int = Field(200, description="Rate limit burst")
    RATE_LIMIT_ENABLED: bool = Field(True, description="Enable rate limiting")
    
    # File Upload & Storage
    MAX_FILE_SIZE_MB: int = Field(100, description="Maximum file size in MB")
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        ["pdf", "doc", "docx", "xls", "xlsx", "jpg", "jpeg", "png", "zip"],
        description="Allowed file extensions"
    )
    UPLOAD_DIRECTORY: str = Field("uploads", description="Upload directory")
    STORAGE_ENDPOINT: str = Field("localhost:9000", description="MinIO endpoint")
    STORAGE_ACCESS_KEY: str = Field("minioadmin", description="MinIO access key")
    STORAGE_SECRET_KEY: str = Field("minioadmin", description="MinIO secret key")
    STORAGE_BUCKET: str = Field("pronas-pcd-documents", description="Storage bucket")
    STORAGE_SECURE: bool = Field(False, description="Use HTTPS for storage")
    
    # Email Configuration
    SMTP_HOST: str = Field("smtp.gmail.com", description="SMTP host")
    SMTP_PORT: int = Field(587, description="SMTP port")
    SMTP_USER: str = Field("", description="SMTP user")
    SMTP_PASSWORD: str = Field("", description="SMTP password")
    EMAIL_FROM: str = Field("noreply@pronas-pcd.org", description="From email address")
    EMAIL_TEMPLATES_DIR: str = Field("templates/email", description="Email templates directory")
    
    # AI Configuration
    AI_ENABLED: bool = Field(True, description="Enable AI features")
    AI_MODEL: str = Field("gpt-4-turbo-preview", description="AI model name")
    AI_API_KEY: str = Field("", description="OpenAI API key")
    AI_CONFIDENCE_THRESHOLD: float = Field(0.75, description="AI confidence threshold")
    AI_MAX_RETRIES: int = Field(3, description="Maximum AI retries")
    AI_TIMEOUT_SECONDS: int = Field(120, description="AI request timeout")
    AI_MAX_TOKENS: int = Field(4000, description="Maximum AI tokens")
    
    # PRONAS/PCD Business Rules
    MAX_PROJECTS_PER_INSTITUTION: int = Field(3, description="Maximum projects per institution")
    SUBMISSION_PERIOD_DAYS: int = Field(45, description="Submission period in days")
    MIN_CAPTACAO_PERCENTAGE: float = Field(0.6, description="Minimum captacao percentage")
    MAX_CAPTACAO_PERCENTAGE: float = Field(1.2, description="Maximum captacao percentage")
    MAX_CAPTACAO_ABSOLUTE: int = Field(50000, description="Maximum captacao absolute value")
    CREDENTIALING_MONTHS: List[int] = Field([6, 7], description="Credentialing allowed months")
    MIN_PROJECT_TIMELINE_MONTHS: int = Field(6, description="Minimum project timeline")
    MAX_PROJECT_TIMELINE_MONTHS: int = Field(48, description="Maximum project timeline")
    
    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FILE: str = Field("logs/pronas_pcd.log", description="Log file path")
    LOG_MAX_SIZE: int = Field(10485760, description="Maximum log file size (10MB)")
    LOG_BACKUP_COUNT: int = Field(5, description="Number of log backup files")
    LOG_FORMAT: str = Field("detailed", description="Log format type")
    
    # Monitoring & Metrics
    METRICS_ENABLED: bool = Field(True, description="Enable metrics collection")
    HEALTH_CHECK_INTERVAL: int = Field(30, description="Health check interval")
    PROMETHEUS_ENABLED: bool = Field(True, description="Enable Prometheus metrics")
    
    # External APIs
    VIACEP_API_URL: str = Field("https://viacep.com.br/ws", description="ViaCEP API URL")
    RECEITAWS_API_URL: str = Field("https://www.receitaws.com.br/v1", description="ReceitaWS API URL")
    API_TIMEOUT_SECONDS: int = Field(30, description="External API timeout")
    API_MAX_RETRIES: int = Field(3, description="External API max retries")
    
    # Backup Configuration
    BACKUP_ENABLED: bool = Field(True, description="Enable automatic backup")
    BACKUP_RETENTION_DAYS: int = Field(30, description="Backup retention period")
    BACKUP_SCHEDULE: str = Field("0 2 * * *", description="Backup cron schedule")
    BACKUP_S3_ENABLED: bool = Field(False, description="Enable S3 backup")
    BACKUP_S3_BUCKET: str = Field("pronas-pcd-backups", description="S3 backup bucket")
    
    # Default Admin User (Development Only)
    DEFAULT_ADMIN_USERNAME: str = Field("admin", description="Default admin username")
    DEFAULT_ADMIN_PASSWORD: str = Field("PronasPCD@Admin2024!", description="Default admin password")
    DEFAULT_ADMIN_EMAIL: str = Field("admin@pronas-pcd.org", description="Default admin email")
    
    # Feature Flags
    FEATURE_FLAGS: Dict[str, bool] = Field(
        {
            "ai_generation": True,
            "real_time_monitoring": True,
            "advanced_analytics": True,
            "document_ocr": False,
            "mobile_notifications": False,
            "integration_apis": True
        },
        description="Feature flags"
    )
    
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
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production", "testing"]:
            raise ValueError("ENVIRONMENT must be one of: development, staging, production, testing")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        if v.upper() not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("LOG_LEVEL must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "testing"
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Database configuration for SQLAlchemy"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "echo": self.DATABASE_ECHO and self.is_development,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
            "connect_args": {
                "connect_timeout": self.DATABASE_CONNECT_TIMEOUT,
                "command_timeout": self.DATABASE_COMMAND_TIMEOUT,
            }
        }
    
    @property
    def redis_config(self) -> Dict[str, Any]:
        """Redis configuration"""
        return {
            "url": self.REDIS_URL,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }
    
    @property
    def cors_config(self) -> Dict[str, Any]:
        """CORS configuration"""
        return {
            "allow_origins": self.ALLOWED_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["*"],
            "max_age": 86400,  # 24 hours
        }
    
    @property
    def security_headers(self) -> Dict[str, str]:
        """Security headers configuration"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Global settings instance
settings = get_settings()
