#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 2 - PARTE 4
# PRONAS/PCD System - API Layer (FastAPI Routers + Schemas)
# Execute na raiz do projeto após aplicar as Partes 1, 2 e 3

set -e

echo "🚀 LOTE 2 PARTE 4: Implementando API Layer (FastAPI)"
echo "==================================================="

# Verificar se backend existe
if [ ! -d "backend" ]; then
    echo "❌ Diretório backend não encontrado. Execute Lotes anteriores primeiro."
    exit 1
fi

cd backend

echo "📝 Criando Pydantic Schemas..."

# app/schemas/base.py
cat > app/schemas/base.py << 'EOF'
"""
Base Pydantic Schemas
Schemas base para requests e responses
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Schema base com configuração padrão"""
    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseSchema):
    """Response base com campos de auditoria"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class PaginationParams(BaseSchema):
    """Parâmetros de paginação"""
    skip: int = 0
    limit: int = 100
    
    def validate_limit(self):
        if self.limit > 100:
            self.limit = 100
        return self


class PaginatedResponse(BaseSchema):
    """Response paginado"""
    items: list
    total: int
    skip: int
    limit: int
    has_more: bool
    
    @classmethod
    def create(cls, items: list, total: int, skip: int, limit: int):
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + len(items) < total
        )
EOF

# app/schemas/user.py
cat > app/schemas/user.py << 'EOF'
"""
User Pydantic Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field, validator
from app.schemas.base import BaseSchema, BaseResponse
from app.domain.entities.user import UserRole, UserStatus


class UserBase(BaseSchema):
    """Schema base para usuário"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole
    institution_id: Optional[int] = None


class UserCreate(UserBase):
    """Schema para criação de usuário"""
    password: str = Field(..., min_length=8, max_length=128)
    consent_given: bool = Field(default=False)
    
    @validator('password')
    def validate_password(cls, v):
        """Validar força da senha"""
        if len(v) < 8:
            raise ValueError('Senha deve ter pelo menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('Senha deve ter pelo menos uma letra maiúscula')
        if not any(c.islower() for c in v):
            raise ValueError('Senha deve ter pelo menos uma letra minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve ter pelo menos um número')
        return v


class UserUpdate(BaseSchema):
    """Schema para atualização de usuário"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    is_active: Optional[bool] = None
    institution_id: Optional[int] = None


class UserResponse(BaseResponse):
    """Schema de response para usuário"""
    email: EmailStr
    full_name: str
    role: UserRole
    status: UserStatus
    is_active: bool
    institution_id: Optional[int] = None
    last_login: Optional[datetime] = None
    consent_given: bool
    consent_date: Optional[datetime] = None


class UserLogin(BaseSchema):
    """Schema para login"""
    email: EmailStr
    password: str


class UserLoginResponse(BaseSchema):
    """Schema de response para login"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseSchema):
    """Schema para mudança de senha"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validar força da nova senha"""
        if len(v) < 8:
            raise ValueError('Nova senha deve ter pelo menos 8 caracteres')
        if not any(c.isupper() for c in v):
            raise ValueError('Nova senha deve ter pelo menos uma letra maiúscula')
        if not any(c.islower() for c in v):
            raise ValueError('Nova senha deve ter pelo menos uma letra minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Nova senha deve ter pelo menos um número')
        return v
EOF

# app/schemas/project.py
cat > app/schemas/project.py << 'EOF'
"""
Project Pydantic Schemas
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from pydantic import Field, validator
from app.schemas.base import BaseSchema, BaseResponse
from app.domain.entities.project import ProjectStatus, ProjectType


class ProjectBase(BaseSchema):
    """Schema base para projeto"""
    title: str = Field(..., min_length=10, max_length=255)
    description: str = Field(..., min_length=50)
    type: ProjectType
    institution_id: int
    
    # Cronograma
    start_date: date
    end_date: date
    
    # Financeiro
    total_budget: Decimal = Field(..., gt=0, max_digits=15, decimal_places=2)
    pronas_funding: Decimal = Field(..., ge=0, max_digits=15, decimal_places=2)
    own_funding: Decimal = Field(..., ge=0, max_digits=15, decimal_places=2)
    other_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Técnico
    target_population: str = Field(..., min_length=10, max_length=500)
    expected_beneficiaries: int = Field(..., gt=0)
    objectives: str = Field(..., min_length=50)
    methodology: str = Field(..., min_length=50)
    
    # Responsável técnico
    technical_manager_name: str = Field(..., min_length=5, max_length=255)
    technical_manager_cpf: str = Field(..., regex=r'^\d{11}$')
    technical_manager_email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Validar datas do projeto"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('Data de fim deve ser posterior à data de início')
        return v
    
    @validator('total_budget')
    def validate_budget_consistency(cls, v, values):
        """Validar consistência do orçamento"""
        pronas = values.get('pronas_funding', Decimal('0'))
        own = values.get('own_funding', Decimal('0'))
        other = values.get('other_funding', Decimal('0'))
        
        total_funding = pronas + own + other
        if abs(total_funding - v) > Decimal('0.01'):
            raise ValueError('Soma dos financiamentos deve ser igual ao orçamento total')
        
        # PRONAS não pode exceder 80%
        if pronas > v * Decimal('0.8'):
            raise ValueError('Financiamento PRONAS não pode exceder 80% do orçamento total')
        
        return v


class ProjectCreate(ProjectBase):
    """Schema para criação de projeto"""
    pass


class ProjectUpdate(BaseSchema):
    """Schema para atualização de projeto"""
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    description: Optional[str] = Field(None, min_length=50)
    type: Optional[ProjectType] = None
    
    # Cronograma
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Financeiro
    total_budget: Optional[Decimal] = Field(None, gt=0, max_digits=15, decimal_places=2)
    pronas_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    own_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    other_funding: Optional[Decimal] = Field(None, ge=0, max_digits=15, decimal_places=2)
    
    # Técnico
    target_population: Optional[str] = Field(None, min_length=10, max_length=500)
    expected_beneficiaries: Optional[int] = Field(None, gt=0)
    objectives: Optional[str] = Field(None, min_length=50)
    methodology: Optional[str] = Field(None, min_length=50)


class ProjectResponse(BaseResponse):
    """Schema de response para projeto"""
    title: str
    description: str
    type: ProjectType
    status: ProjectStatus
    institution_id: int
    
    # Cronograma
    start_date: date
    end_date: date
    
    # Financeiro
    total_budget: Decimal
    pronas_funding: Decimal
    own_funding: Decimal
    other_funding: Optional[Decimal] = None
    
    # Técnico
    target_population: str
    expected_beneficiaries: int
    objectives: str
    methodology: str
    
    # Responsável técnico
    technical_manager_name: str
    technical_manager_cpf: str
    technical_manager_email: str
    
    # Workflow
    submitted_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
    review_notes: Optional[str] = None
    
    created_by: int


class ProjectReview(BaseSchema):
    """Schema para revisão de projeto"""
    decision: ProjectStatus = Field(..., regex="^(approved|rejected)$")
    review_notes: str = Field(..., min_length=10, max_length=1000)


class ProjectStatusUpdate(BaseSchema):
    """Schema para atualização de status"""
    status: ProjectStatus
    notes: Optional[str] = None
EOF

echo "✅ Pydantic Schemas criados!"

echo "📝 Criando FastAPI Routers..."

# app/api/v1/endpoints/auth.py
cat > app/api/v1/endpoints/auth.py << 'EOF'
"""
Authentication Endpoints
Endpoints para autenticação e autorização
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserLogin, UserLoginResponse, UserResponse, PasswordChange
from app.adapters.database.session import get_db_session
from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.adapters.database.repositories.audit_log_repository import AuditLogRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.core.security.auth import create_access_token, create_refresh_token
from app.dependencies import get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=UserLoginResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Fazer login no sistema"""
    
    # Repositories
    user_repo = UserRepositoryImpl(db)
    audit_repo = AuditLogRepositoryImpl(db)
    
    # Service
    auth_service = AuthService(user_repo, audit_repo)
    
    # Extrair informações da requisição
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "")
    session_id = request.headers.get("x-session-id", "")
    
    # Autenticar usuário
    user = await auth_service.authenticate_user(
        email=login_data.email,
        password=login_data.password,
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar tokens JWT
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return UserLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Fazer logout do sistema"""
    
    audit_repo = AuditLogRepositoryImpl(db)
    
    # Log de logout
    await audit_repo.create_log(
        action="logout",
        resource="system",
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        session_id=request.headers.get("x-session-id", ""),
        description="Logout realizado",
        success=True
    )
    
    return {"message": "Logout realizado com sucesso"}


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Alterar senha do usuário"""
    
    # Repositories
    user_repo = UserRepositoryImpl(db)
    audit_repo = AuditLogRepositoryImpl(db)
    
    # Service
    auth_service = AuthService(user_repo, audit_repo)
    
    # Alterar senha
    success = await auth_service.change_password(
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
        requesting_user=current_user,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        session_id=request.headers.get("x-session-id", "")
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    return {"message": "Senha alterada com sucesso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return UserResponse.from_orm(current_user)
EOF

# app/api/v1/endpoints/users.py
cat > app/api/v1/endpoints/users.py << 'EOF'
"""
Users Endpoints
Endpoints para gerenciamento de usuários
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.base import PaginatedResponse, PaginationParams
from app.adapters.database.session import get_db_session
from app.adapters.database.repositories.user_repository import UserRepositoryImpl
from app.adapters.database.repositories.audit_log_repository import AuditLogRepositoryImpl
from app.domain.services.auth_service import AuthService
from app.dependencies import get_current_user, require_admin, require_gestor
from app.domain.entities.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Criar novo usuário (apenas admin)"""
    
    # Repositories
    user_repo = UserRepositoryImpl(db)
    audit_repo = AuditLogRepositoryImpl(db)
    
    # Service
    auth_service = AuthService(user_repo, audit_repo)
    
    # Verificar se email já existe
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    new_user = await auth_service.create_user(
        user_data=user_data.dict(),
        created_by_user=current_user,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        session_id=request.headers.get("x-session-id", "")
    )
    
    return UserResponse.from_orm(new_user)


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(require_gestor),
    db: AsyncSession = Depends(get_db_session)
):
    """Listar usuários com paginação"""
    
    user_repo = UserRepositoryImpl(db)
    
    # Filtros baseados no papel do usuário
    filters = {}
    if current_user.role != "admin":
        # Gestores veem apenas usuários da sua instituição
        if current_user.institution_id:
            filters["institution_id"] = current_user.institution_id
    
    # Buscar usuários
    users = await user_repo.get_all(
        skip=pagination.skip,
        limit=pagination.limit,
        filters=filters
    )
    
    # Contar total
    total = await user_repo.count(filters)
    
    return PaginatedResponse.create(
        items=[UserResponse.from_orm(user) for user in users],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Obter usuário por ID"""
    
    user_repo = UserRepositoryImpl(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar permissões
    if current_user.role not in ["admin", "auditor"]:
        if current_user.role == "gestor":
            if user.institution_id != current_user.institution_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sem permissão para acessar este usuário"
                )
        else:
            # Operadores só veem a si mesmos
            if user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sem permissão para acessar este usuário"
                )
    
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(require_gestor),
    db: AsyncSession = Depends(get_db_session)
):
    """Atualizar usuário"""
    
    user_repo = UserRepositoryImpl(db)
    audit_repo = AuditLogRepositoryImpl(db)
    
    # Buscar usuário
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Verificar permissões
    if current_user.role != "admin":
        if current_user.role == "gestor":
            if user.institution_id != current_user.institution_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Sem permissão para editar este usuário"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para editar usuários"
            )
    
    # Atualizar usuário
    updated_user = await user_repo.update(
        user_id=user_id,
        update_data=user_data.dict(exclude_unset=True)
    )
    
    # Log da operação
    await audit_repo.create_log(
        action="update",
        resource="user",
        resource_id=user_id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        session_id=request.headers.get("x-session-id", ""),
        description=f"Usuário atualizado: {user.email}",
        new_values=user_data.dict(exclude_unset=True),
        success=True,
        data_sensitivity="confidential"
    )
    
    return UserResponse.from_orm(updated_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Desativar usuário (soft delete)"""
    
    user_repo = UserRepositoryImpl(db)
    audit_repo = AuditLogRepositoryImpl(db)
    
    # Buscar usuário
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Não permitir auto-exclusão
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar seu próprio usuário"
        )
    
    # Desativar usuário
    success = await user_repo.delete(user_id)
    
    # Log da operação
    await audit_repo.create_log(
        action="delete",
        resource="user",
        resource_id=user_id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent", ""),
        session_id=request.headers.get("x-session-id", ""),
        description=f"Usuário desativado: {user.email}",
        success=success,
        data_sensitivity="confidential"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desativar usuário"
        )
    
    return {"message": "Usuário desativado com sucesso"}
EOF

echo "✅ FastAPI Routers criados!"

echo "📝 Criando API Router principal e Dependencies..."

# app/api/v1/router.py
cat > app/api/v1/router.py << 'EOF'
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
EOF

# app/dependencies.py (atualizado)
cat > app/dependencies.py << 'EOF'
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
EOF

# app/main.py (atualizado)
cat > app/main.py << 'EOF'
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
EOF

echo "✅ FastAPI Application criada!"

cd ..

echo ""
echo "🎉 LOTE 2 PARTE 4 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Pydantic Schemas para User e Project com validações avançadas"
echo "• FastAPI Routers para Auth e Users com endpoints completos"
echo "• Sistema de autenticação JWT com login/logout/change-password"
echo "• Gerenciamento de usuários com RBAC (Admin, Gestor, Auditor, Operador)"
echo "• Dependencies para injeção de dependência e controle de acesso"
echo "• Main Application com health checks e CORS configurado"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 2 Parte 5 (Final - Alembic + Seeds + Testes)"
echo "2. Depois execute testes: cd backend && pytest tests/ -v"
echo "3. Inicie aplicação: cd backend && uvicorn app.main:app --reload"
echo ""
echo "📊 Status atual:"
echo "• Lote 1: ✅ Estrutura monorepo"
echo "• Lote 2.1: ✅ Configuração Python base"
echo "• Lote 2.2: ✅ Domain Layer (Entidades, Repositórios)"
echo "• Lote 2.3: ✅ Adapters Layer (SQLAlchemy, Redis)"  
echo "• Lote 2.4: ✅ API Layer (FastAPI Routers, Schemas)"
echo "• Lote 2.5: ⏳ Database Final (Alembic + Seeds - próximo)"
echo ""
echo "🔧 Para testar agora:"
echo "cd backend"
echo "export $(cat ../.env | grep -v '^#' | xargs)"
echo "python -c \"from app.main import app; print('✅ FastAPI App OK')\""
echo ""