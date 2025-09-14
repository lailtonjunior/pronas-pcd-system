"""
FastAPI Main Application
PRONAS/PCD System - Clean Architecture
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from app.api.v1.router import api_router
from app.core.config.settings import get_settings
from app.adapters.database.session import get_async_session
from app.adapters.external.cache.redis_client import get_redis_client

# Configurar logging estruturado
logger = structlog.get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerenciar ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando PRONAS/PCD System Backend")
    
    # Verificar conexão com banco de dados
    try:
        async with get_async_session() as session:
            await session.execute("SELECT 1")
        logger.info("✅ Conexão com PostgreSQL estabelecida")
    except Exception as e:
        logger.error("❌ Falha na conexão com PostgreSQL", error=str(e))
        raise
    
    # Verificar conexão com Redis
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        logger.info("✅ Conexão com Redis estabelecida")
    except Exception as e:
        logger.error("❌ Falha na conexão com Redis", error=str(e))
        raise
    
    yield
    
    # Shutdown
    logger.info("🔴 Encerrando PRONAS/PCD System Backend")


# Criar aplicação FastAPI
app = FastAPI(
    title="PRONAS/PCD System API",
    description="Sistema de Gestão de Projetos PRONAS/PCD - Conformidade LGPD",
    version="1.0.0",
    docs_url="/docs" if settings.api_debug else None,
    redoc_url="/redoc" if settings.api_debug else None,
    openapi_url="/openapi.json" if settings.api_debug else None,
    lifespan=lifespan,
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router, prefix="/api/v1")

# Métricas Prometheus
if settings.prometheus_enabled:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pronas-pcd-backend",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/ready", tags=["Health"])
async def readiness_check() -> dict:
    """Readiness check com verificação de dependências"""
    checks = {}
    
    # Verificar PostgreSQL
    try:
        async with get_async_session() as session:
            await session.execute("SELECT 1")
        checks["postgres"] = "healthy"
    except Exception as e:
        checks["postgres"] = f"unhealthy: {str(e)}"
    
    # Verificar Redis
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    # Status geral
    is_healthy = all(status == "healthy" for status in checks.values())
    
    return {
        "status": "ready" if is_healthy else "not_ready",
        "checks": checks,
        "service": "pronas-pcd-backend",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info",
    )
