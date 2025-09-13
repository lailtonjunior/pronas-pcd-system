"""
Configuration Settings
Configurações centralizadas com Pydantic Settings
"""

import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseSettings,
    EmailStr,
    Field,
    PostgresDsn,
    validator,
)
from pydantic_core import MultiHostUrl


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_debug: bool = Field(default=True, env="API_DEBUG")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Database Settings
    postgres_host: str = Field(env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    postgres_db: str = Field(env="POSTGRES_DB")
    postgres_user: str = Field(env="POSTGRES_USER")
    postgres_password: str = Field(env="POSTGRES_PASSWORD")
    
    # Redis Settings
    redis_host: str = Field(env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # JWT Settings
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = Field(env="JWT_REFRESH_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=30, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # MinIO Settings
    minio_endpoint: str = Field(env="MINIO_ENDPOINT")
    minio_access_key: str = Field(env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(env="MINIO_SECRET_KEY")
    minio_bucket_name: str = Field(default="pronas-pcd-documents", env="MINIO_BUCKET_NAME")
    minio_secure: bool = Field(default=False, env="MINIO_SECURE")
    
    # Email Settings
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_from: Optional[EmailStr] = Field(default=None, env="SMTP_FROM")
    
    # Security Settings
    cors_origins: List[AnyHttpUrl] = Field(default=[], env="CORS_ORIGINS")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(default=60, env="RATE_LIMIT_WINDOW_SECONDS")
    
    # Monitoring
    prometheus_enabled: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    
    # Computed Properties
    @property
    def database_url(self) -> str:
        """URL de conexão com PostgreSQL"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def redis_url(self) -> str:
        """URL de conexão com Redis"""
        auth_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Processar origens CORS"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Obter configurações (cached)"""
    return Settings()
