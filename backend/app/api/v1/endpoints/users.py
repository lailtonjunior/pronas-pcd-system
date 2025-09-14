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
