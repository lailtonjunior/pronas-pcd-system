"""
FastAPI Dependencies
Injeção de dependências centralizadas
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.settings import get_settings
from app.core.security.auth import verify_jwt_token
from app.adapters.database.session import get_db_session
from app.adapters.external.cache.redis_client import get_redis_client
from app.domain.entities.user import User
from app.domain.repositories.user import UserRepository
from app.adapters.database.repositories.user_repository import UserRepositoryImpl

settings = get_settings()
security = HTTPBearer()


async def get_redis():
    """Injeção de dependência para cliente Redis"""
    return await get_redis_client()


async def get_user_repository(
    db: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    """Injeção de dependência para repositório de usuários"""
    return UserRepositoryImpl(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Obter usuário atual autenticado"""
    
    # Verificar token JWT
    try:
        payload = verify_jwt_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuário no banco
    user = await user_repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    return user


def require_roles(allowed_roles: list[str]):
    """Decorator para verificar papéis/roles do usuário"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissões insuficientes"
            )
        return current_user
    return role_checker


# Aliases comuns para roles
require_admin = require_roles(["admin"])
require_gestor = require_roles(["admin", "gestor"])
require_auditor = require_roles(["admin", "auditor"])


class RateLimiter:
    """Rate limiting baseado em Redis"""
    
    def __init__(self, requests: int = 100, window: int = 60):
        self.requests = requests
        self.window = window
    
    async def __call__(self, request: Request, redis=Depends(get_redis)):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        current = await redis.get(key)
        if current is None:
            await redis.setex(key, self.window, 1)
            return True
        
        if int(current) >= self.requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit excedido"
            )
        
        await redis.incr(key)
        return True


# Instâncias de rate limiters
standard_rate_limit = RateLimiter(requests=100, window=60)
strict_rate_limit = RateLimiter(requests=10, window=60)
