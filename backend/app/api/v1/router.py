"""
API V1 Router
Router principal da API v1
"""

from fastapi import APIRouter

# Importar os novos endpoints
from app.api.v1.endpoints import auth, users, institutions, projects, ai

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(institutions.router)
api_router.include_router(projects.router)
api_router.include_router(ai.router)


# Health check endpoint
@api_router.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pronas-pcd-api",
        "version": "1.0.0"
    }