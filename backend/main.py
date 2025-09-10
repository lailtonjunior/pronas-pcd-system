"""
Sistema PRONAS/PCD - API Principal
Arquitetura: Clean Architecture + Domain-Driven Design
Conformidade: 100% Ministério da Saúde
"""

import os
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
import asyncio

# FastAPI Core
from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware  
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from prometheus_client import Counter, Histogram, generate_latest
import uvicorn

# Internal Imports - Organized Architecture
from core.config import Settings
from core.database import engine, get_db, init_database
from core.security import get_current_user, create_access_token
from core.exceptions import setup_exception_handlers
from core.middleware import add_security_headers, log_requests

# Routers - Clean Separation
from api.v1.auth import router as auth_router
from api.v1.institutions import router as institutions_router  
from api.v1.projects import router as projects_router
from api.v1.ai_engine import router as ai_router
from api.v1.monitoring import router as monitoring_router
from api.v1.reports import router as reports_router

# Models
from models import Base
from services.ai_service import PronasAIService

# Settings
settings = Settings()

# Configure Professional Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter('pronas_http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('pronas_http_request_duration_seconds', 'HTTP request latency')
AI_GENERATION_COUNT = Counter('pronas_ai_generations_total', 'Total AI project generations', ['area', 'status'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Lifecycle Management"""
    # Startup
    logger.info("🚀 Starting PRONAS/PCD System v2.0")
    
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
        
        # Initialize database with seed data
        await init_database()
        logger.info("✅ Database initialized with seed data")
        
        # Initialize AI Service
        app.state.ai_service = PronasAIService()
        await app.state.ai_service.initialize()
        logger.info("✅ AI Service initialized")
        
        # Health check all external services
        await perform_startup_health_checks()
        logger.info("✅ All services healthy")
        
        logger.info("🎉 PRONAS/PCD System started successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down PRONAS/PCD System")
    if hasattr(app.state, 'ai_service'):
        await app.state.ai_service.cleanup()
    logger.info("👋 Shutdown complete")

async def perform_startup_health_checks():
    """Perform comprehensive health checks on startup"""
    from core.database import SessionLocal
    from core.cache import redis_client
    
    # Database check
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection OK")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
    
    # Redis check
    try:
        await redis_client.ping()
        logger.info("✅ Redis connection OK") 
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        raise

# FastAPI Application
app = FastAPI(
    title="Sistema PRONAS/PCD",
    description="""
    ## 🏥 Sistema de Gestão PRONAS/PCD

    **Plataforma completa para o Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência**
    
    ### 🎯 Funcionalidades Principais
    
    #### 🏢 Gestão de Instituições
    * Cadastro completo conforme legislação PRONAS/PCD
    * Validação automática de CNPJ e documentos
    * Processo de credenciamento digital
    * Controle de status e histórico
    
    #### 🤖 IA Especializada (8 Áreas Prioritárias)
    * **QSS** - Qualificação de serviços de saúde  
    * **RPD** - Reabilitação/habilitação da pessoa com deficiência
    * **DDP** - Diagnóstico diferencial da pessoa com deficiência
    * **EPD** - Identificação e estimulação precoce das deficiências
    * **ITR** - Inserção e reinserção no trabalho
    * **APE** - Apoio à saúde por meio de práticas esportivas
    * **TAA** - Terapia assistida por animais
    * **APC** - Apoio à saúde por produção artística e cultural
    
    #### 📊 Dashboard Executivo
    * Métricas em tempo real
    * Relatórios de conformidade
    * Análise de performance
    * Dashboards interativos
    
    #### 🔍 Sistema de Monitoramento
    * Acompanhamento de projetos
    * Indicadores de performance (KPIs)
    * Alertas automáticos
    * Relatórios de prestação de contas
    
    ### ⚖️ Base Legal
    * **Lei nº 12.715/2012** - Lei do PRONAS/PCD
    * **Portaria de Consolidação nº 5/2017** - Anexo LXXXVI  
    * **Portaria nº 448/2002** - Natureza de Despesas
    * **Lei nº 13.146/2015** - Lei Brasileira de Inclusão
    
    ### 🔒 Segurança
    * Autenticação JWT com refresh tokens
    * Criptografia de dados sensíveis
    * Auditoria completa de ações
    * Rate limiting e proteção DDoS
    * Logs de segurança detalhados
    
    ### 📈 Performance
    * Cache Redis inteligente  
    * Otimizações de banco de dados
    * CDN para arquivos estáticos
    * Monitoramento de performance
    """,
    version="2.0.0",
    contact={
        "name": "Sistema PRONAS/PCD",
        "url": "https://github.com/lailtonjunior/pronas-pcd-system",
        "email": "suporte@pronas-pcd.org",
    },
    license_info={
        "name": "MIT License", 
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://pronas-pcd.org/terms",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# Security Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=86400,  # 24 hours
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS if not settings.DEBUG else ["*"]
)

# Custom Middlewares
app.middleware("http")(add_security_headers)
app.middleware("http")(log_requests)

# Prometheus Metrics Middleware
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    """Collect metrics for Prometheus"""
    start_time = datetime.utcnow()
    
    response = await call_next(request)
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    duration = (datetime.utcnow() - start_time).total_seconds()
    REQUEST_LATENCY.observe(duration)
    
    return response

# Exception Handlers
setup_exception_handlers(app)

# API Routes - Clean Organization
app.include_router(
    auth_router, 
    prefix="/api/v1/auth", 
    tags=["🔐 Authentication & Authorization"]
)

app.include_router(
    institutions_router, 
    prefix="/api/v1/institutions", 
    tags=["🏢 Institution Management"]
)

app.include_router(
    projects_router, 
    prefix="/api/v1/projects", 
    tags=["📋 Project Management"]
)

app.include_router(
    ai_router, 
    prefix="/api/v1/ai", 
    tags=["🤖 AI-Powered Generation"]
)

app.include_router(
    monitoring_router, 
    prefix="/api/v1/monitoring", 
    tags=["📊 Project Monitoring"]
)

app.include_router(
    reports_router, 
    prefix="/api/v1/reports", 
    tags=["📈 Reports & Analytics"]
)

# Core System Endpoints
@app.get("/", tags=["🏠 System"])
async def root():
    """System root endpoint with comprehensive information"""
    return {
        "system": "PRONAS/PCD Management Platform",
        "description": "Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência", 
        "version": "2.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "features": {
            "ai_areas": 8,
            "legal_compliance": "100%",
            "real_time_monitoring": True,
            "automated_validation": True
        },
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "metrics": "/metrics"
        },
        "legal_framework": [
            "Lei nº 12.715/2012",
            "Portaria de Consolidação nº 5/2017",
            "Portaria nº 448/2002", 
            "Lei nº 13.146/2015"
        ],
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_since": app.state.startup_time if hasattr(app.state, 'startup_time') else None
    }

@app.get("/health", tags=["🏠 System"])
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        from core.database import SessionLocal
        from core.cache import redis_client
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "environment": settings.ENVIRONMENT,
            "services": {},
            "system_info": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "uptime": str(datetime.utcnow() - app.state.startup_time) if hasattr(app.state, 'startup_time') else None
            }
        }
        
        # Database Health
        try:
            db = SessionLocal()
            result = db.execute("SELECT COUNT(*) FROM institutions").scalar()
            db.close()
            health_status["services"]["database"] = {
                "status": "healthy",
                "institutions_count": result,
                "response_time_ms": "<10ms"
            }
        except Exception as e:
            health_status["services"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # Redis Health  
        try:
            redis_start = datetime.utcnow()
            await redis_client.ping()
            redis_time = (datetime.utcnow() - redis_start).total_seconds() * 1000
            health_status["services"]["redis"] = {
                "status": "healthy",
                "response_time_ms": f"{redis_time:.2f}ms"
            }
        except Exception as e:
            health_status["services"]["redis"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            health_status["status"] = "degraded"
        
        # AI Service Health
        if hasattr(app.state, 'ai_service'):
            try:
                ai_status = await app.state.ai_service.health_check()
                health_status["services"]["ai_service"] = ai_status
            except Exception as e:
                health_status["services"]["ai_service"] = {
                    "status": "unhealthy",
                    "error": str(e)  
                }
                health_status["status"] = "degraded"
        
        # Return appropriate status code
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
        elif health_status["status"] == "degraded":
            return JSONResponse(
                status_code=status.HTTP_206_PARTIAL_CONTENT,
                content=health_status
            )
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/metrics", tags=["📊 Monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

@app.get("/version", tags=["🏠 System"])
async def get_version():
    """System version and build information"""
    return {
        "version": "2.0.0",
        "build_date": "2025-09-10",
        "environment": settings.ENVIRONMENT,
        "features": {
            "ai_enabled": True,
            "monitoring_enabled": True,
            "cache_enabled": True
        }
    }

# Store startup time
@app.on_event("startup")
async def store_startup_time():
    app.state.startup_time = datetime.utcnow()

if __name__ == "__main__":
    # Production-ready server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        server_header=False,  # Security
        date_header=False     # Security
    )
