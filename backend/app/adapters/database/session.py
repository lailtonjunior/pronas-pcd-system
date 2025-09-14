"""
Database Session Management
Gerenciamento de sessões assíncronas com SQLAlchemy
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config.settings import get_settings

settings = get_settings()

# Criar engine assíncrono
engine = create_async_engine(
    settings.database_url,
    echo=settings.api_debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    poolclass=NullPool if settings.environment == "test" else None,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager para obter sessão assíncrona"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection para FastAPI"""
    async with get_async_session() as session:
        yield session
