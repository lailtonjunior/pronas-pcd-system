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
