# CRIAR: backend/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from core.database import get_db
from core.security import security, get_current_user
from services.auth_service import AuthService
from schemas.auth import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Autenticação via username/password"""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=480)
    )
    
    refresh_token = security.create_refresh_token(user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registro de novo usuário"""
    auth_service = AuthService(db)
    
    # Verificar se usuário existe
    if auth_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    user = auth_service.create_user(user_data)
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Retorna informações do usuário autenticado"""
    return current_user