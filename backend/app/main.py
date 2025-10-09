"""
FastAPI Main Application
PRONAS/PCD System - Clean Architecture
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.v1.router import api_router
from app.core.config.settings import get_settings
from app.adapters.database.session import engine
from app.adapters.external.cache.redis_client import get_redis_client, close_redis_client
from app.adapters.database.models.base import Base

logger = structlog.get_logger(__name__)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação (startup e shutdown)."""
    logger.info("🚀 Iniciando PRONAS/PCD System Backend")

    # Em ambiente de desenvolvimento, cria as tabelas se não existirem.
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Tabelas do banco de dados verificadas/criadas.")

    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        logger.info("✅ Conexão com Redis estabelecida")
    except Exception as e:
        logger.error("❌ Falha na conexão com Redis", error=str(e))

    yield
    
    await close_redis_client()
    logger.info("🔴 Encerrando PRONAS/PCD System Backend")

# Instancia a aplicação FastAPI
app = FastAPI(
    title="PRONAS/PCD System API",
    description="Sistema de Gestão de Projetos PRONAS/PCD - Conformidade LGPD",
    version="2.0.0",
    docs_url="/docs" if settings.api_debug else None,
    redoc_url="/redoc" if settings.api_debug else None,
    openapi_url="/openapi.json" if settings.api_debug else None,
    lifespan=lifespan,
)

# Adiciona o middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui todas as rotas da API a partir do roteador principal
app.include_router(api_router, prefix="/api/v1")

# Adiciona o endpoint de métricas para o Prometheus
if settings.prometheus_enabled:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# Endpoint de verificação de saúde
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    return {
        "status": "healthy",
        "service": "pronas-pcd-backend",
        "version": "2.0.0",
        "environment": settings.environment
    }

# Bloco para permitir a execução direta do arquivo (para desenvolvimento)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level="info",
    )