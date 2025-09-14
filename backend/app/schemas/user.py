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
