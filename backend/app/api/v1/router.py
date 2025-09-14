"""
API V1 Router
Router principal da API v1
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pronas-pcd-api",
        "version": "1.0.0"
    }
