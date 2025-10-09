"""
API V1 Router
Router principal que agrega todos os endpoints da API v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, institutions, projects, ai

# Cria a instância principal do roteador da API
api_router = APIRouter()

# Inclui os roteadores de cada funcionalidade com seus respectivos prefixos e tags
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["Institutions"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(ai.router, prefix="/ai", tags=["Artificial Intelligence"])

# Endpoint de health check para a API, não visível na documentação
@api_router.get("/health", include_in_schema=False)
async def health_check_api():
    """Verifica a saúde do roteador da API."""
    return {"status": "api_router_ok"}